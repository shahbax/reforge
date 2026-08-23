"""Stripe billing — subscription Checkout + a webhook that grants credits.

Each plan maps to a monthly credit allotment. Stripe Prices are created
idempotently via `lookup_key`, so there's no manual dashboard product setup.
On a successful payment we add the plan's monthly credits to the user's balance
and set their plan; renewals top up again; cancellation drops them to free.

Stripe's objects are dict subclasses, so dict-style access works whether the
event came from the verified SDK or the dev JSON fallback.
"""
from __future__ import annotations

import json
import logging

from app.config import get_settings
from app.store import Store

log = logging.getLogger("reforge.billing")

# plan key -> (display name, monthly price in cents, monthly credit allotment)
PLANS: dict[str, dict] = {
    "creator": {"name": "Reforge Creator", "amount": 1900, "credits": 60},
    "pro": {"name": "Reforge Pro", "amount": 3900, "credits": 200},
    "agency": {"name": "Reforge Agency", "amount": 9900, "credits": 400},
}


def _client():
    import stripe

    s = get_settings()
    if not s.stripe_secret_key:
        raise RuntimeError("STRIPE_SECRET_KEY not configured")
    stripe.api_key = s.stripe_secret_key
    return stripe


def _price_id(stripe, plan_key: str) -> str:
    plan = PLANS[plan_key]
    lookup = f"reforge_{plan_key}_monthly"
    existing = stripe.Price.list(lookup_keys=[lookup], limit=1)
    if existing.data:
        return existing.data[0].id
    product = stripe.Product.create(name=plan["name"])
    price = stripe.Price.create(
        product=product.id,
        unit_amount=plan["amount"],
        currency="usd",
        recurring={"interval": "month"},
        lookup_key=lookup,
    )
    log.info("Created Stripe price %s for plan %s", price.id, plan_key)
    return price.id


def create_checkout_url(user, plan_key: str) -> str:
    if plan_key not in PLANS:
        raise ValueError(f"Unknown plan: {plan_key}")
    stripe = _client()
    s = get_settings()
    price_id = _price_id(stripe, plan_key)
    session = stripe.checkout.Session.create(
        mode="subscription",
        line_items=[{"price": price_id, "quantity": 1}],
        client_reference_id=str(user.id),
        customer_email=user.email or None,
        metadata={"user_id": str(user.id), "plan": plan_key},
        subscription_data={"metadata": {"user_id": str(user.id), "plan": plan_key}},
        success_url=f"{s.frontend_url}/dashboard?checkout=success",
        cancel_url=f"{s.frontend_url}/dashboard?checkout=cancel",
        allow_promotion_codes=True,
    )
    return session.url


def construct_event(payload: bytes, sig_header: str):
    stripe = _client()
    s = get_settings()
    if s.stripe_webhook_secret:
        return stripe.Webhook.construct_event(payload, sig_header, s.stripe_webhook_secret)
    if s.environment == "production":
        raise RuntimeError("STRIPE_WEBHOOK_SECRET is required in production")
    log.warning("Stripe webhook signature NOT verified (no secret configured; dev only)")
    return json.loads(payload)


def handle_event(event, store: Store) -> None:
    etype = event["type"]
    data = event["data"]["object"]

    if etype == "checkout.session.completed":
        meta = data.get("metadata") or {}
        _grant(store, data.get("client_reference_id") or meta.get("user_id"), meta.get("plan"))
    elif etype == "invoice.paid":
        # Renewals only — the first invoice is handled by checkout.session.completed.
        if data.get("billing_reason") == "subscription_cycle":
            uid, plan = _resolve_from_subscription(data)
            _grant(store, uid, plan)
    elif etype == "customer.subscription.deleted":
        meta = data.get("metadata") or {}
        if meta.get("user_id"):
            store.set_plan(meta["user_id"], "free")
            log.info("Subscription cancelled; user=%s set to free", meta["user_id"])


def _grant(store: Store, user_id, plan_key) -> None:
    plan = PLANS.get(plan_key or "")
    if not plan or not user_id:
        log.warning("Cannot grant credits (user_id=%s plan=%s)", user_id, plan_key)
        return
    store.refund_credits(str(user_id), plan["credits"])  # atomic add
    store.set_plan(str(user_id), plan_key)
    log.info("Granted %s credits (plan=%s) to user=%s", plan["credits"], plan_key, user_id)


def _resolve_from_subscription(invoice) -> tuple:
    sub_id = invoice.get("subscription")
    if not sub_id:
        return None, None
    stripe = _client()
    sub = stripe.Subscription.retrieve(sub_id)
    meta = sub.get("metadata") or {}
    return meta.get("user_id"), meta.get("plan")
