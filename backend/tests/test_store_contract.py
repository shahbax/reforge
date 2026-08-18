"""Behavioral contract every Store implementation must satisfy.

Runs against InMemoryStore always; also against PostgresStore when
TEST_DATABASE_URL is set (opt-in, so CI without a DB stays green). This is the
suite that proves the Postgres persistence layer once a connection string exists:

    TEST_DATABASE_URL="postgresql://...supabase..." pytest tests/test_store_contract.py
"""
import os
import uuid

import pytest

from app.schemas import ConceptSet, JobStatus, Platform, ViralDNA
from app.services.ai.fixtures import fixture_for
from app.store import InMemoryStore, InsufficientCredits

_PARAMS = ["memory"]
if os.environ.get("TEST_DATABASE_URL"):
    _PARAMS.append("postgres")


@pytest.fixture(params=_PARAMS)
def store(request):
    if request.param == "memory":
        return InMemoryStore()
    from app.store_postgres import PostgresStore

    return PostgresStore(os.environ["TEST_DATABASE_URL"])


def test_user_credit_lifecycle(store):
    uid = str(uuid.uuid4())
    u = store.upsert_user(uid, email="a@b.com", default_credits=5)
    assert u.credits == 5
    # idempotent upsert keeps credits, fills empty email only
    assert store.upsert_user(uid, email="ignored@x.com").credits == 5

    store.debit_credits(uid, 2)
    assert store.get_user(uid).credits == 3
    store.refund_credits(uid, 1)
    assert store.get_user(uid).credits == 4
    with pytest.raises(InsufficientCredits):
        store.debit_credits(uid, 999)
    assert store.set_credits(uid, 10).credits == 10


def test_project_persistence_and_roundtrip(store):
    uid = str(uuid.uuid4())
    store.upsert_user(uid, default_credits=5)
    p = store.create_project(uid, "https://www.youtube.com/watch?v=abc123", Platform.YOUTUBE, "abc123")
    assert store.get_project(p.id).status == JobStatus.QUEUED

    # Mutate a freshly-fetched project and persist the rich nested objects.
    fetched = store.get_project(p.id)
    fetched.status = JobStatus.AWAITING_CONCEPT_SELECTION
    fetched.script_id = str(uuid.uuid4())
    fetched.viral_dna = ViralDNA.model_validate(fixture_for("ViralDNA", ""))
    fetched.concepts = ConceptSet.model_validate(fixture_for("ConceptSet", ""))
    fetched.stage_costs.append({"stage": "ViralDNA", "model": "mock", "input_tokens": 10, "output_tokens": 5, "cost_usd": 0.0})
    store.touch(fetched)

    got = store.get_project(p.id)
    assert got.status == JobStatus.AWAITING_CONCEPT_SELECTION
    assert got.viral_dna.hook.strength == fetched.viral_dna.hook.strength
    assert len(got.concepts.concepts) == 5
    assert got.stage_costs[0]["stage"] == "ViralDNA"

    # Lookups
    assert store.get_project_by_script_id(fetched.script_id).id == p.id
    assert store.find_active_by_video(uid, Platform.YOUTUBE, "abc123").id == p.id
    items, _ = store.list_projects(uid)
    assert any(x.id == p.id for x in items)

    # Delete
    store.delete_project(p.id)
    assert store.get_project(p.id) is None
