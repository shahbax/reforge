from typing import Optional

from fastapi import APIRouter, Depends, Query, Response, status

from app.deps import get_current_user, get_store, owned_project
from app.routers.views import project_summary
from app.store import Project, Store, User

router = APIRouter(tags=["projects"])


@router.get("/projects")
def list_projects(
    limit: int = Query(default=20, ge=1, le=100),
    cursor: Optional[str] = None,
    store: Store = Depends(get_store),
    user: User = Depends(get_current_user),
) -> dict:
    items, next_cursor = store.list_projects(user.id, limit=limit, cursor=cursor)
    return {"projects": [project_summary(p) for p in items], "next_cursor": next_cursor}


@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project: Project = Depends(owned_project),
    store: Store = Depends(get_store),
) -> Response:
    store.delete_project(project.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
