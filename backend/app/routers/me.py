from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.config import get_settings
from app.deps import get_current_user, get_store
from app.store import Store, User

router = APIRouter(tags=["me"])


@router.get("/me")
def me(user: User = Depends(get_current_user)) -> dict:
    return {"id": user.id, "email": user.email, "plan": user.plan, "credits": user.credits}


@router.post("/me/credits/refill")
def refill_credits(
    credits: int = Query(default=25, ge=0, le=100000),
    store: Store = Depends(get_store),
    user: User = Depends(get_current_user),
) -> dict:
    """Dev/admin helper to reset credits. Disabled in production."""
    if get_settings().environment == "production":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Disabled in production")
    updated = store.set_credits(user.id, credits)
    return {"credits": updated.credits}
