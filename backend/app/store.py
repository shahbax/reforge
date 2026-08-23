"""Persistence layer.

`Store` is the interface the API depends on; `InMemoryStore` is the development
implementation (used when DATABASE_URL is empty). A PostgresStore implementing
the same interface is the M2 database milestone (schema in docs/database.md) —
the app depends only on this abstraction, never on a concrete backend.
"""
from __future__ import annotations

import threading
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
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


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _uid() -> str:
    return str(uuid.uuid4())


@dataclass
class User:
    id: str
    email: str = ""
    plan: str = "free"
    credits: int = 0
    created_at: datetime = field(default_factory=_now)


@dataclass
class Project:
    """A single analysis + (optional) script generation, owned by one user."""

    id: str
    user_id: str
    url: str
    platform: Platform
    external_id: str

    status: JobStatus = JobStatus.QUEUED
    stage_detail: str = ""
    error_reason: Optional[str] = None

    # Analysis-job outputs
    source_video: Optional[SourceVideoMeta] = None
    transcript: Optional[Transcript] = None  # internal; not exposed verbatim
    analysis: Optional[ContentAnalysis] = None
    viral_dna: Optional[ViralDNA] = None
    concepts: Optional[ConceptSet] = None

    # Script-job state/outputs
    script_id: Optional[str] = None
    script_status: Optional[JobStatus] = None
    script_stage_detail: str = ""
    script_error_reason: Optional[str] = None
    selected_concept_index: Optional[int] = None
    controls: Optional[ScriptControls] = None
    research: Optional[ResearchBrief] = None
    script: Optional[Script] = None
    originality: Optional[OriginalityReport] = None
    package: Optional[ProductionPackage] = None

    # Accounting
    stage_costs: list[dict] = field(default_factory=list)

    created_at: datetime = field(default_factory=_now)
    updated_at: datetime = field(default_factory=_now)


class InsufficientCredits(RuntimeError):
    pass


class Store(ABC):
    # users
    @abstractmethod
    def upsert_user(self, user_id: str, email: str = "", default_credits: int = 0) -> User: ...
    @abstractmethod
    def get_user(self, user_id: str) -> Optional[User]: ...
    @abstractmethod
    def debit_credits(self, user_id: str, amount: int = 1) -> None: ...
    @abstractmethod
    def refund_credits(self, user_id: str, amount: int = 1) -> None: ...
    @abstractmethod
    def set_credits(self, user_id: str, credits: int) -> User: ...
    @abstractmethod
    def set_plan(self, user_id: str, plan: str) -> None: ...

    # projects
    @abstractmethod
    def create_project(self, user_id: str, url: str, platform: Platform, external_id: str) -> Project: ...
    @abstractmethod
    def get_project(self, project_id: str) -> Optional[Project]: ...
    @abstractmethod
    def get_project_by_script_id(self, script_id: str) -> Optional[Project]: ...
    @abstractmethod
    def find_active_by_video(self, user_id: str, platform: Platform, external_id: str) -> Optional[Project]: ...
    @abstractmethod
    def list_projects(self, user_id: str, limit: int = 20, cursor: Optional[str] = None) -> tuple[list[Project], Optional[str]]: ...
    @abstractmethod
    def delete_project(self, project_id: str) -> None: ...
    @abstractmethod
    def touch(self, project: Project) -> None: ...


class InMemoryStore(Store):
    def __init__(self) -> None:
        self._users: dict[str, User] = {}
        self._projects: dict[str, Project] = {}
        self._lock = threading.RLock()

    # ---- users ----
    def upsert_user(self, user_id: str, email: str = "", default_credits: int = 0) -> User:
        with self._lock:
            user = self._users.get(user_id)
            if user is None:
                user = User(id=user_id, email=email, credits=default_credits)
                self._users[user_id] = user
            elif email and not user.email:
                user.email = email
            return user

    def get_user(self, user_id: str) -> Optional[User]:
        return self._users.get(user_id)

    def debit_credits(self, user_id: str, amount: int = 1) -> None:
        with self._lock:
            user = self._users.get(user_id)
            if user is None or user.credits < amount:
                raise InsufficientCredits("Not enough credits")
            user.credits -= amount

    def refund_credits(self, user_id: str, amount: int = 1) -> None:
        with self._lock:
            user = self._users.get(user_id)
            if user is not None:
                user.credits += amount

    def set_credits(self, user_id: str, credits: int) -> User:
        with self._lock:
            user = self._users.get(user_id)
            if user is None:
                user = User(id=user_id, credits=credits)
                self._users[user_id] = user
            else:
                user.credits = credits
            return user

    def set_plan(self, user_id: str, plan: str) -> None:
        with self._lock:
            user = self._users.get(user_id)
            if user is not None:
                user.plan = plan

    # ---- projects ----
    def create_project(self, user_id: str, url: str, platform: Platform, external_id: str) -> Project:
        with self._lock:
            project = Project(
                id=_uid(), user_id=user_id, url=url, platform=platform, external_id=external_id
            )
            self._projects[project.id] = project
            return project

    def get_project(self, project_id: str) -> Optional[Project]:
        return self._projects.get(project_id)

    def get_project_by_script_id(self, script_id: str) -> Optional[Project]:
        for p in self._projects.values():
            if p.script_id == script_id:
                return p
        return None

    def find_active_by_video(self, user_id: str, platform: Platform, external_id: str) -> Optional[Project]:
        # Newest matching, non-failed project for transcript reuse / idempotency.
        matches = [
            p
            for p in self._projects.values()
            if p.user_id == user_id
            and p.platform == platform
            and p.external_id == external_id
            and p.status != JobStatus.FAILED
        ]
        return max(matches, key=lambda p: p.created_at, default=None)

    def list_projects(self, user_id: str, limit: int = 20, cursor: Optional[str] = None) -> tuple[list[Project], Optional[str]]:
        owned = sorted(
            (p for p in self._projects.values() if p.user_id == user_id),
            key=lambda p: p.created_at,
            reverse=True,
        )
        start = 0
        if cursor:
            ids = [p.id for p in owned]
            start = ids.index(cursor) + 1 if cursor in ids else 0
        page = owned[start : start + limit]
        next_cursor = page[-1].id if len(owned) > start + limit else None
        return page, next_cursor

    def delete_project(self, project_id: str) -> None:
        with self._lock:
            self._projects.pop(project_id, None)

    def touch(self, project: Project) -> None:
        project.updated_at = _now()


def build_store() -> Store:
    from app.config import get_settings

    settings = get_settings()
    if settings.database_url:
        from app.store_postgres import PostgresStore

        return PostgresStore(settings.database_url)
    return InMemoryStore()
