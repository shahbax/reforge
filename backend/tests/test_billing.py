"""Webhook credit-granting logic (no network — synthetic Stripe events)."""
from app.services import billing
from app.store import InMemoryStore


def test_checkout_completed_grants_plan_credits():
    store = InMemoryStore()
    store.upsert_user("u1", default_credits=0)
    event = {
        "type": "checkout.session.completed",
        "data": {"object": {"client_reference_id": "u1", "metadata": {"user_id": "u1", "plan": "creator"}}},
    }
    billing.handle_event(event, store)
    user = store.get_user("u1")
    assert user.credits == 60  # Creator monthly allotment
    assert user.plan == "creator"


def test_first_invoice_does_not_double_grant():
    store = InMemoryStore()
    store.upsert_user("u2", default_credits=5)
    # The initial invoice (subscription_create) must NOT grant — checkout.session
    # already did. Only subscription_cycle (renewals) grant.
    event = {
        "type": "invoice.paid",
        "data": {"object": {"billing_reason": "subscription_create", "subscription": "sub_x"}},
    }
    billing.handle_event(event, store)
    assert store.get_user("u2").credits == 5


def test_subscription_deleted_downgrades_to_free():
    store = InMemoryStore()
    store.upsert_user("u3", default_credits=10)
    store.set_plan("u3", "pro")
    event = {"type": "customer.subscription.deleted", "data": {"object": {"metadata": {"user_id": "u3"}}}}
    billing.handle_event(event, store)
    assert store.get_user("u3").plan == "free"


def test_plans_are_well_formed():
    for key, plan in billing.PLANS.items():
        assert plan["amount"] > 0 and plan["credits"] > 0 and plan["name"]
