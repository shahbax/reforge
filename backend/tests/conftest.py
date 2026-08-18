"""Test configuration.

Force a hermetic, keyless environment BEFORE any app module is imported:
mock AI provider, inline jobs (so POSTs complete synchronously), dev auth.
"""
import os

os.environ["AI_PROVIDER"] = "mock"
os.environ["JOBS_INLINE"] = "true"
os.environ["SUPABASE_JWT_SECRET"] = ""
os.environ["SUPABASE_URL"] = ""
os.environ["SUPABASE_ANON_KEY"] = ""
os.environ["ENVIRONMENT"] = "development"
os.environ["DATABASE_URL"] = ""
os.environ["REDIS_URL"] = ""

import pytest
from fastapi.testclient import TestClient

from app.config import get_settings
from app.main import create_app


@pytest.fixture()
def client():
    get_settings.cache_clear()
    app = create_app()
    with TestClient(app) as c:
        yield c
