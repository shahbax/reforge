import asyncio
import json

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse

from app.deps import get_current_user, get_jobs, get_store, owned_project
from app.jobs import JobManager
from app.routers.views import analysis_view
from app.schemas import AnalyzeRequest, JobStatus
from app.services.ingestion import youtube
from app.store import InsufficientCredits, Project, Store, User

router = APIRouter(tags=["analyses"])

_TERMINAL = {JobStatus.AWAITING_CONCEPT_SELECTION, JobStatus.COMPLETED, JobStatus.FAILED}


@router.post("/analyses", status_code=status.HTTP_202_ACCEPTED)
def create_analysis(
    body: AnalyzeRequest,
    store: Store = Depends(get_store),
    jobs: JobManager = Depends(get_jobs),
    user: User = Depends(get_current_user),
) -> dict:
    url = str(body.url)
    try:
        platform, external_id = youtube.validate_url(url)
    except youtube.IngestionError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))

    # Idempotency / transcript reuse: return an existing non-failed run for this video.
    existing = store.find_active_by_video(user.id, platform, external_id)
    if existing is not None:
        return {"project_id": existing.id, "status": existing.status.value, "deduped": True}

    try:
        store.debit_credits(user.id, 1)
    except InsufficientCredits:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Not enough credits for a new analysis",
        )

    project = store.create_project(user.id, url, platform, external_id)
    jobs.enqueue_analysis(project.id)
    return {"project_id": project.id, "status": project.status.value}


@router.get("/analyses/{project_id}")
def get_analysis(project: Project = Depends(owned_project)) -> dict:
    return analysis_view(project)


@router.get("/analyses/{project_id}/events")
async def analysis_events(project: Project = Depends(owned_project)) -> StreamingResponse:
    """Server-sent events: emit stage transitions until the analysis settles."""

    async def event_stream():
        last = None
        # ~60s ceiling so a stuck/dev job can't hold the connection forever.
        for _ in range(240):
            snapshot = (project.status, project.stage_detail)
            if snapshot != last:
                last = snapshot
                payload = {
                    "status": project.status.value,
                    "stage": project.stage_detail,
                    "error_reason": project.error_reason,
                }
                yield f"data: {json.dumps(payload)}\n\n"
            if project.status in _TERMINAL:
                return
            await asyncio.sleep(0.25)

    return StreamingResponse(event_stream(), media_type="text/event-stream")
