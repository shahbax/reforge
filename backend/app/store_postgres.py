"""PostgreSQL implementation of the Store interface (production persistence).

Design: one row per user, one row per project. The project's rich nested objects
(source video, transcript, analysis, viral DNA, concepts, script, originality,
etc.) are stored as JSONB columns and (de)serialized via their Pydantic models —
so this maps 1:1 onto the same domain objects the in-memory store uses.

Schema is created idempotently on startup (CREATE TABLE IF NOT EXISTS), so no
external migration step is required. RLS is enabled with no policies, which blocks
the anon/authenticated PostgREST API from touching these tables; the backend
connects as the table owner and bypasses RLS. Only the trusted API writes here.
"""
from __future__ import annotations

import logging
import uuid
from typing import Optional

from app.schemas import (
    ConceptSet,
    ContentAnalysis,
    JobStatus,
    OriginalityReport,
    Platform,
    ProductionPackage,
    ResearchBrief,
    Script,
    ScriptControls,
    SourceVideoMeta,
    Transcript,
    ViralDNA,
)
from app.store import InsufficientCredits, Project, Store, User

log = logging.getLogger("reforge.store.postgres")

_SCHEMA: list[str] = [
    """
    CREATE TABLE IF NOT EXISTS reforge_users (
        id          uuid PRIMARY KEY,
        email       text NOT NULL DEFAULT '',
        plan        text NOT NULL DEFAULT 'free',
        credits     integer NOT NULL DEFAULT 0,
        created_at  timestamptz NOT NULL DEFAULT now()
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS reforge_projects (
        id                     uuid PRIMARY KEY,
        user_id                uuid NOT NULL,
        url                    text NOT NULL,
        platform               text NOT NULL,
        external_id            text NOT NULL,
        status                 text NOT NULL DEFAULT 'QUEUED',
        stage_detail           text NOT NULL DEFAULT '',
        error_reason           text,
        source_video           jsonb,
        transcript             jsonb,
        analysis               jsonb,
        viral_dna              jsonb,
        concepts               jsonb,
        script_id              uuid,
        script_status          text,
        script_stage_detail    text NOT NULL DEFAULT '',
        script_error_reason    text,
        selected_concept_index integer,
        controls               jsonb,
        research               jsonb,
        script                 jsonb,
        originality            jsonb,
        package                jsonb,
        stage_costs            jsonb NOT NULL DEFAULT '[]'::jsonb,
        created_at             timestamptz NOT NULL DEFAULT now(),
        updated_at             timestamptz NOT NULL DEFAULT now()
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_reforge_projects_user_created ON reforge_projects (user_id, created_at DESC)",
    "CREATE INDEX IF NOT EXISTS idx_reforge_projects_script ON reforge_projects (script_id)",
    "CREATE INDEX IF NOT EXISTS idx_reforge_projects_video ON reforge_projects (user_id, platform, external_id)",
    "ALTER TABLE reforge_users ENABLE ROW LEVEL SECURITY",
    "ALTER TABLE reforge_projects ENABLE ROW LEVEL SECURITY",
]

_PROJECT_COLUMNS = [
    "id", "user_id", "url", "platform", "external_id", "status", "stage_detail",
    "error_reason", "source_video", "transcript", "analysis", "viral_dna", "concepts",
    "script_id", "script_status", "script_stage_detail", "script_error_reason",
    "selected_concept_index", "controls", "research", "script", "originality",
    "package", "stage_costs",
]


def _dump(model):
    from psycopg.types.json import Jsonb

    return Jsonb(model.model_dump(mode="json")) if model is not None else None


def _load(model_cls, data):
    return model_cls.model_validate(data) if data is not None else None


def _project_params(p: Project) -> dict:
    from psycopg.types.json import Jsonb

    return {
        "id": str(p.id),
        "user_id": str(p.user_id),
        "url": p.url,
        "platform": p.platform.value,
        "external_id": p.external_id,
        "status": p.status.value,
        "stage_detail": p.stage_detail,
        "error_reason": p.error_reason,
        "source_video": _dump(p.source_video),
        "transcript": _dump(p.transcript),
        "analysis": _dump(p.analysis),
        "viral_dna": _dump(p.viral_dna),
        "concepts": _dump(p.concepts),
        "script_id": str(p.script_id) if p.script_id else None,
        "script_status": p.script_status.value if p.script_status else None,
        "script_stage_detail": p.script_stage_detail,
        "script_error_reason": p.script_error_reason,
        "selected_concept_index": p.selected_concept_index,
        "controls": _dump(p.controls),
        "research": _dump(p.research),
        "script": _dump(p.script),
        "originality": _dump(p.originality),
        "package": _dump(p.package),
        "stage_costs": Jsonb(p.stage_costs or []),
    }


def _row_to_project(r: dict) -> Project:
    return Project(
        id=str(r["id"]),
        user_id=str(r["user_id"]),
        url=r["url"],
        platform=Platform(r["platform"]),
        external_id=r["external_id"],
        status=JobStatus(r["status"]),
        stage_detail=r["stage_detail"] or "",
        error_reason=r["error_reason"],
        source_video=_load(SourceVideoMeta, r["source_video"]),
        transcript=_load(Transcript, r["transcript"]),
        analysis=_load(ContentAnalysis, r["analysis"]),
        viral_dna=_load(ViralDNA, r["viral_dna"]),
        concepts=_load(ConceptSet, r["concepts"]),
        script_id=str(r["script_id"]) if r["script_id"] else None,
        script_status=JobStatus(r["script_status"]) if r["script_status"] else None,
        script_stage_detail=r["script_stage_detail"] or "",
        script_error_reason=r["script_error_reason"],
        selected_concept_index=r["selected_concept_index"],
        controls=_load(ScriptControls, r["controls"]),
        research=_load(ResearchBrief, r["research"]),
        script=_load(Script, r["script"]),
        originality=_load(OriginalityReport, r["originality"]),
        package=_load(ProductionPackage, r["package"]),
        stage_costs=r["stage_costs"] or [],
        created_at=r["created_at"],
        updated_at=r["updated_at"],
    )


def _row_to_user(r: dict) -> User:
    return User(id=str(r["id"]), email=r["email"], plan=r["plan"], credits=r["credits"], created_at=r["created_at"])


class PostgresStore(Store):
    def __init__(self, dsn: str) -> None:
        try:
            from psycopg.rows import dict_row
            from psycopg_pool import ConnectionPool
        except ImportError as e:  # pragma: no cover
            raise RuntimeError(
                "psycopg is required for the Postgres store. Install with "
                "`pip install -r requirements.txt` (psycopg[binary], psycopg-pool)."
            ) from e

        self._pool = ConnectionPool(
            conninfo=dsn,
            min_size=1,
            max_size=10,
            kwargs={"autocommit": True, "prepare_threshold": None, "row_factory": dict_row},
            open=True,
        )
        self._init_schema()
        log.info("PostgresStore ready (pool opened, schema ensured)")

    def _init_schema(self) -> None:
        with self._pool.connection() as conn:
            for stmt in _SCHEMA:
                conn.execute(stmt)

    # ---- users ----
    def upsert_user(self, user_id: str, email: str = "", default_credits: int = 0) -> User:
        sql = """
            INSERT INTO reforge_users (id, email, credits) VALUES (%s, %s, %s)
            ON CONFLICT (id) DO UPDATE
              SET email = CASE WHEN reforge_users.email = '' THEN EXCLUDED.email ELSE reforge_users.email END
            RETURNING id, email, plan, credits, created_at
        """
        with self._pool.connection() as conn:
            row = conn.execute(sql, (user_id, email, default_credits)).fetchone()
        return _row_to_user(row)

    def get_user(self, user_id: str) -> Optional[User]:
        with self._pool.connection() as conn:
            row = conn.execute(
                "SELECT id, email, plan, credits, created_at FROM reforge_users WHERE id = %s", (user_id,)
            ).fetchone()
        return _row_to_user(row) if row else None

    def debit_credits(self, user_id: str, amount: int = 1) -> None:
        with self._pool.connection() as conn:
            row = conn.execute(
                "UPDATE reforge_users SET credits = credits - %s WHERE id = %s AND credits >= %s RETURNING credits",
                (amount, user_id, amount),
            ).fetchone()
        if row is None:
            raise InsufficientCredits("Not enough credits")

    def refund_credits(self, user_id: str, amount: int = 1) -> None:
        with self._pool.connection() as conn:
            conn.execute("UPDATE reforge_users SET credits = credits + %s WHERE id = %s", (amount, user_id))

    def set_credits(self, user_id: str, credits: int) -> User:
        sql = """
            INSERT INTO reforge_users (id, credits) VALUES (%s, %s)
            ON CONFLICT (id) DO UPDATE SET credits = EXCLUDED.credits
            RETURNING id, email, plan, credits, created_at
        """
        with self._pool.connection() as conn:
            row = conn.execute(sql, (user_id, credits)).fetchone()
        return _row_to_user(row)

    # ---- projects ----
    def create_project(self, user_id: str, url: str, platform: Platform, external_id: str) -> Project:
        project = Project(id=str(uuid.uuid4()), user_id=user_id, url=url, platform=platform, external_id=external_id)
        cols = ", ".join(_PROJECT_COLUMNS)
        placeholders = ", ".join(f"%({c})s" for c in _PROJECT_COLUMNS)
        with self._pool.connection() as conn:
            row = conn.execute(
                f"INSERT INTO reforge_projects ({cols}) VALUES ({placeholders}) RETURNING *",
                _project_params(project),
            ).fetchone()
        return _row_to_project(row)

    def get_project(self, project_id: str) -> Optional[Project]:
        with self._pool.connection() as conn:
            row = conn.execute("SELECT * FROM reforge_projects WHERE id = %s", (project_id,)).fetchone()
        return _row_to_project(row) if row else None

    def get_project_by_script_id(self, script_id: str) -> Optional[Project]:
        with self._pool.connection() as conn:
            row = conn.execute(
                "SELECT * FROM reforge_projects WHERE script_id = %s LIMIT 1", (script_id,)
            ).fetchone()
        return _row_to_project(row) if row else None

    def find_active_by_video(self, user_id: str, platform: Platform, external_id: str) -> Optional[Project]:
        with self._pool.connection() as conn:
            row = conn.execute(
                """SELECT * FROM reforge_projects
                   WHERE user_id = %s AND platform = %s AND external_id = %s AND status <> 'FAILED'
                   ORDER BY created_at DESC LIMIT 1""",
                (user_id, platform.value, external_id),
            ).fetchone()
        return _row_to_project(row) if row else None

    def list_projects(self, user_id: str, limit: int = 20, cursor: Optional[str] = None) -> tuple[list[Project], Optional[str]]:
        params: list = [user_id]
        where = "user_id = %s"
        if cursor:
            where += " AND created_at < (SELECT created_at FROM reforge_projects WHERE id = %s)"
            params.append(cursor)
        params.append(limit + 1)
        with self._pool.connection() as conn:
            rows = conn.execute(
                f"SELECT * FROM reforge_projects WHERE {where} ORDER BY created_at DESC LIMIT %s", params
            ).fetchall()
        has_more = len(rows) > limit
        page = [_row_to_project(r) for r in rows[:limit]]
        next_cursor = page[-1].id if has_more and page else None
        return page, next_cursor

    def delete_project(self, project_id: str) -> None:
        with self._pool.connection() as conn:
            conn.execute("DELETE FROM reforge_projects WHERE id = %s", (project_id,))

    def touch(self, project: Project) -> None:
        # Persist the full current state of the (in-memory-mutated) project.
        assignments = ", ".join(f"{c} = %({c})s" for c in _PROJECT_COLUMNS if c != "id")
        with self._pool.connection() as conn:
            conn.execute(
                f"UPDATE reforge_projects SET {assignments}, updated_at = now() WHERE id = %(id)s",
                _project_params(project),
            )
