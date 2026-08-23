import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel

from app.config import get_settings
from app.deps import get_current_user, get_store
from app.services import billing
from app.store import Store, User

router = APIRouter(prefix="/billing", tags=["billing"])
log = logging.getLogger("reforge.billing")


class CheckoutRequest(BaseModel):
    plan: str


@router.get("/config")
def billing_config() -> dict:
    s = get_settings()
    return {
        "enabled": bool(s.stripe_secret_key),
        "publishable_key": s.stripe_publishable_key,
        "plans": {
            k: {"name": v["name"], "price_usd": v["amount"] / 100, "credits": v["credits"]}
            for k, v in billing.PLANS.items()
        },
    }


@router.post("/checkout")
def create_checkout(body: CheckoutRequest, user: User = Depends(get_current_user)) -> dict:
    if not get_settings().stripe_secret_key:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Billing is not configured")
    try:
        url = billing.create_checkout_url(user, body.plan)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:  # noqa: BLE001 - surface Stripe/network errors cleanly
        log.exception("Checkout creation failed")
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Stripe error: {e}")
    return {"url": url}


@router.post("/webhook")
async def stripe_webhook(request: Request, store: Store = Depends(get_store)) -> dict:
    payload = await request.body()
    sig = request.headers.get("stripe-signature", "")
    try:
        event = billing.construct_event(payload, sig)
    except Exception as e:  # noqa: BLE001 - invalid/unsigned payloads
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid webhook: {e}")
    try:
        billing.handle_event(event, store)
    except Exception:  # noqa: BLE001 - never fail the webhook ack on a handler bug
        log.exception("Webhook handling failed")
    return {"received": True}
