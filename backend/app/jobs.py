"""Background job manager.

Drives the two-phase pipeline (analysis, then script) off the request path.
With REDIS_URL unset we use an in-process thread pool; JOBS_INLINE=true runs
jobs synchronously (used by tests and easy debugging). A Redis/RQ or Celery
worker implementing `enqueue_*` is a later milestone — routers depend only on
this manager.

Credit policy: routers debit 1 credit before enqueue; a job that FAILS refunds
it here so users are never charged for a broken run.
"""
from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Optional

from app.schemas import JobStatus, ScriptControls
from app.services.ai.provider import BaseProvider, get_provider
from app.services.pipeline import rewrite_flagged, run_analysis_job, run_script_job
from app.store import Project, Store

log = logging.getLogger("reforge.jobs")


class JobManager:
    def __init__(self, store: Store, inline: bool = False, max_workers: int = 4) -> None:
        self.store = store
        self.inline = inline
        self._executor = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="reforge-job")

    def shutdown(self) -> None:
        self._executor.shutdown(wait=False, cancel_futures=True)

    def _submit(self, fn: Callable, *args) -> None:
        if self.inline:
            fn(*args)
        else:
            self._executor.submit(self._guard(fn), *args)

    @staticmethod
    def _guard(fn: Callable) -> Callable:
        def wrapped(*args):
            try:
                fn(*args)
            except Exception:  # noqa: BLE001 - never let a worker thread die silently
                log.exception("Unhandled error in background job %s", fn.__name__)

        return wrapped

    # ------------------------------------------------------------------ #
    # Public enqueue API
    # ------------------------------------------------------------------ #
    def enqueue_analysis(self, project_id: str, niche_hint: str = "", audience_hint: str = "") -> None:
        self._submit(self._run_analysis, project_id, niche_hint, audience_hint)

    def enqueue_script(self, project_id: str) -> None:
        self._submit(self._run_script, project_id)

    def enqueue_rewrite(self, project_id: str, target: str = "flagged") -> None:
        self._submit(self._run_rewrite, project_id, target)

    # ------------------------------------------------------------------ #
    # Workers
    # ------------------------------------------------------------------ #
    def _run_analysis(self, project_id: str, niche_hint: str, audience_hint: str) -> None:
        project = self.store.get_project(project_id)
        if project is None:
            return
        provider = get_provider()

        def on_status(status: JobStatus, detail: Optional[str] = None) -> None:
            # The terminal state is set after outputs are persisted (avoids a
            # window where status=AWAITING but concepts aren't stored yet).
            if status == JobStatus.AWAITING_CONCEPT_SELECTION:
                return
            project.status = status
            project.stage_detail = detail or ""
            self.store.touch(project)

        try:
            result = run_analysis_job(
                project.url,
                niche_hint=niche_hint,
                audience_hint=audience_hint,
                on_status=on_status,
                provider=provider,
            )
            project.source_video = result.meta
            project.transcript = result.transcript
            project.analysis = result.analysis
            project.viral_dna = result.dna
            project.concepts = result.concepts
            self._record_usage(project, provider, "analysis")
            project.status = JobStatus.AWAITING_CONCEPT_SELECTION
            project.stage_detail = "ready for concept selection"
        except Exception as e:  # noqa: BLE001
            log.exception("Analysis job failed for project %s", project_id)
            project.status = JobStatus.FAILED
            project.error_reason = str(e)
            self.store.refund_credits(project.user_id, 1)
        finally:
            self.store.touch(project)

    def _run_script(self, project_id: str) -> None:
        project = self.store.get_project(project_id)
        if project is None:
            return
        if project.viral_dna is None or project.concepts is None or project.controls is None:
            return
        provider = get_provider()

        def on_status(status: JobStatus, detail: Optional[str] = None) -> None:
            if status == JobStatus.COMPLETED:
                return
            project.script_status = status
            project.script_stage_detail = detail or ""
            self.store.touch(project)

        try:
            result = run_script_job(
                dna=project.viral_dna,
                concept_index=project.selected_concept_index or 0,
                concepts=project.concepts,
                controls=project.controls,
                source_transcript=project.transcript,
                on_status=on_status,
                provider=provider,
            )
            project.research = result.research
            project.script = result.script
            project.originality = result.originality
            project.package = result.package
            self._record_usage(project, provider, "script")
            project.script_status = JobStatus.COMPLETED
            project.script_stage_detail = "done"
        except Exception as e:  # noqa: BLE001
            log.exception("Script job failed for project %s", project_id)
            project.script_status = JobStatus.FAILED
            project.script_error_reason = str(e)
            self.store.refund_credits(project.user_id, 1)
        finally:
            self.store.touch(project)

    def _run_rewrite(self, project_id: str, target: str) -> None:
        project = self.store.get_project(project_id)
        if project is None or project.script is None or project.originality is None:
            return
        provider = get_provider()
        try:
            revised, report = rewrite_flagged(
                script=project.script,
                originality=project.originality,
                source_transcript=project.transcript,
                provider=provider,
            )
            project.script = revised
            project.originality = report
            self._record_usage(project, provider, "rewrite")
        except Exception:  # noqa: BLE001
            log.exception("Rewrite failed for project %s", project_id)
        finally:
            self.store.touch(project)

    # ------------------------------------------------------------------ #
    def _record_usage(self, project: Project, provider: BaseProvider, phase: str) -> None:
        for entry in provider.usage:
            project.stage_costs.append({**entry, "phase": phase})


def build_job_manager(store: Store) -> JobManager:
    from app.config import get_settings

    return JobManager(store, inline=get_settings().jobs_inline)


# Default script controls when the client omits fields.
def default_controls() -> ScriptControls:
    return ScriptControls()
