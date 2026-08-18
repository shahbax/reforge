"""Authentication.

Production: verify a Supabase-issued JWT (HS256) with SUPABASE_JWT_SECRET.
Development: when no secret is configured, attribute every request to a single
dev user (overridable with the `X-Dev-User` header) so the app is runnable with
zero setup. Users are provisioned on first sight with the free-plan credits.
"""
from __future__ import annotations

import logging
from typing import Optional

from fastapi import Header, HTTPException, Request, status

from app.config import get_settings
from app.store import Store, User

log = logging.getLogger("reforge.auth")

# Dev users get a comfortable credit balance so local exploration isn't blocked;
# production users get the configured free-plan allotment.
_DEV_CREDITS = 25


def _unauthorized(detail: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


def _decode_supabase_jwt(token: str, secret: str) -> dict:
    import jwt  # PyJWT

    try:
        return jwt.decode(
            token,
            secret,
            algorithms=["HS256"],
            options={"verify_aud": False},  # Supabase aud is "authenticated"
        )
    except Exception as e:  # noqa: BLE001 - normalize all decode failures
        raise _unauthorized(f"Invalid token: {e}") from e


def get_current_user(
    request: Request,
    authorization: Optional[str] = Header(default=None),
    x_dev_user: Optional[str] = Header(default=None),
) -> User:
    settings = get_settings()
    store: Store = request.app.state.store

    if not settings.supabase_jwt_secret:
        uid = (x_dev_user or "dev-user").strip()
        return store.upsert_user(uid, email=f"{uid}@dev.local", default_credits=_DEV_CREDITS)

    if not authorization or not authorization.lower().startswith("bearer "):
        raise _unauthorized("Missing bearer token")
    token = authorization.split(" ", 1)[1].strip()
    payload = _decode_supabase_jwt(token, settings.supabase_jwt_secret)
    uid = payload.get("sub")
    if not uid:
        raise _unauthorized("Token has no subject")
    return store.upsert_user(
        uid, email=payload.get("email", ""), default_credits=settings.free_plan_credits
    )
