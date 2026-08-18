"""Shared FastAPI dependencies."""
from __future__ import annotations

from fastapi import Depends, HTTPException, Request, status

from app.auth import get_current_user  # re-exported for routers
from app.jobs import JobManager
from app.store import Project, Store, User

__all__ = ["get_store", "get_jobs", "get_current_user", "owned_project"]


def get_store(request: Request) -> Store:
    return request.app.state.store


def get_jobs(request: Request) -> JobManager:
    return request.app.state.jobs


def owned_project(
    project_id: str,
    store: Store = Depends(get_store),
    user: User = Depends(get_current_user),
) -> Project:
    """Fetch a project and enforce ownership (404 if missing or not owned)."""
    project = store.get_project(project_id)
    if project is None or project.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project
