import uuid
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field

from app.deps import get_current_user, get_jobs, get_store, owned_project
from app.jobs import JobManager
from app.routers.views import script_view
from app.schemas import DISCLAIMER, JobStatus, ScriptControls
from app.store import InsufficientCredits, Project, Store, User

router = APIRouter(tags=["scripts"])


class ScriptJobRequest(BaseModel):
    concept_index: int = 0
    controls: ScriptControls = Field(default_factory=ScriptControls)


class RewriteRequest(BaseModel):
    target: Literal["flagged", "all"] = "flagged"


@router.post("/projects/{project_id}/script", status_code=status.HTTP_202_ACCEPTED)
def start_script(
    body: ScriptJobRequest,
    project: Project = Depends(owned_project),
    store: Store = Depends(get_store),
    jobs: JobManager = Depends(get_jobs),
    user: User = Depends(get_current_user),
) -> dict:
    if project.concepts is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Analysis has not produced concepts yet",
        )
    n = len(project.concepts.concepts)
    if not (0 <= body.concept_index < n):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"concept_index out of range (0..{n - 1})",
        )

    try:
        store.debit_credits(user.id, 1)
    except InsufficientCredits:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Not enough credits for script generation",
        )

    project.selected_concept_index = body.concept_index
    project.controls = body.controls
    project.script_id = project.script_id or str(uuid.uuid4())
    project.script_status = JobStatus.QUEUED
    project.script_stage_detail = "queued"
    project.script_error_reason = None
    store.touch(project)  # persist concept/controls selection before the job reads it
    jobs.enqueue_script(project.id)
    return {
        "script_job": "queued",
        "script_id": project.script_id,
        "status": project.script_status.value,
    }


@router.get("/projects/{project_id}/script")
def get_script(project: Project = Depends(owned_project)) -> dict:
    return script_view(project)


@router.post("/scripts/{script_id}/rewrite", status_code=status.HTTP_202_ACCEPTED)
def rewrite_script(
    script_id: str,
    body: RewriteRequest,
    store: Store = Depends(get_store),
    jobs: JobManager = Depends(get_jobs),
    user: User = Depends(get_current_user),
) -> dict:
    project = store.get_project_by_script_id(script_id)
    if project is None or project.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Script not found")
    if project.script is None or project.originality is None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="No script to rewrite")
    jobs.enqueue_rewrite(project.id, body.target)
    return {"status": "queued", "script_id": script_id}


@router.get("/projects/{project_id}/export")
def export_script(
    fmt: Literal["md", "txt"] = Query(default="md", alias="format"),
    project: Project = Depends(owned_project),
) -> PlainTextResponse:
    if project.script is None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="No script to export")

    document = _render_markdown(project) if fmt == "md" else _render_plain(project)
    filename = f"viralreverse-script-{project.id[:8]}.{fmt}"
    return PlainTextResponse(
        content=document,
        media_type="text/markdown" if fmt == "md" else "text/plain",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# --------------------------------------------------------------------------- #
# Export renderers
# --------------------------------------------------------------------------- #
def _render_markdown(project: Project) -> str:
    s = project.script
    pkg = project.package
    orig = project.originality
    lines = [f"# {s.title}", ""]
    if project.controls:
        c = project.controls
        lines += [
            f"> Platform: {c.platform.value} · Tone: {c.tone} · "
            f"~{c.duration_seconds}s (~{c.target_word_count} words) · Language: {c.language}",
            "",
        ]
    for section in s.sections:
        lines += [f"## {section.label}", "", section.content, ""]
    lines += [f"_Word count: {s.word_count}_", ""]

    if pkg:
        lines += ["---", "", "## Production package", ""]
        if pkg.titles:
            lines += ["**Title options**", *[f"- {t}" for t in pkg.titles], ""]
        if pkg.thumbnail_prompts:
            lines += ["**Thumbnail prompts**", *[f"- {t}" for t in pkg.thumbnail_prompts], ""]
        if pkg.description:
            lines += ["**Description**", "", pkg.description, ""]
        if pkg.hashtags:
            lines += ["**Hashtags**", "", " ".join(pkg.hashtags), ""]

    if orig:
        lines += [
            "---",
            "",
            "## Originality analysis",
            "",
            f"- Originality score: **{orig.originality_score}/100**",
            f"- Phrase overlap: {orig.phrase_overlap.band}",
            f"- Distinctive phrase overlap: {orig.distinctive_phrase_overlap.band}",
            f"- Semantic similarity: {orig.semantic_similarity.band}",
            f"- Structural similarity: {orig.structural_similarity.band}",
            "",
            f"> {DISCLAIMER}",
            "",
        ]
    return "\n".join(lines)


def _render_plain(project: Project) -> str:
    s = project.script
    parts = [s.title, ""]
    for section in s.sections:
        parts += [section.label.upper(), section.content, ""]
    parts += [f"[{DISCLAIMER}]"]
    return "\n".join(parts)
