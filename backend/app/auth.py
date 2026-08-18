"""Authentication.

Production: verify a Supabase-issued JWT. Supports both signing schemes:
  * ES256 / RS256 asymmetric keys via the project JWKS (modern Supabase default)
  * HS256 with the legacy shared secret (SUPABASE_JWT_SECRET)
Development: when neither SUPABASE_URL nor SUPABASE_JWT_SECRET is configured,
attribute every request to a single dev user (X-Dev-User header) so the app is
runnable with zero setup. Users are provisioned on first sight with credits.
"""
from __future__ import annotations

import logging
from typing import Optional

from fastapi import Header, HTTPException, Request, status

from app.config import Settings, get_settings
from app.store import Store, User

log = logging.getLogger("reforge.auth")

# Dev users get a comfortable credit balance so local exploration isn't blocked;
# real users get the configured free-plan allotment.
_DEV_CREDITS = 25
_jwks_client = None  # lazily built PyJWKClient, cached across requests


def _unauthorized(detail: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


def _jwks_for(jwks_url: str):
    global _jwks_client
    if _jwks_client is None:
        from jwt import PyJWKClient

        _jwks_client = PyJWKClient(jwks_url)
    return _jwks_client


def _decode_supabase_jwt(token: str, settings: Settings) -> dict:
    import jwt  # PyJWT

    try:
        alg = jwt.get_unverified_header(token).get("alg", "")
        if alg == "HS256":
            if not settings.supabase_jwt_secret:
                raise _unauthorized("HS256 token but SUPABASE_JWT_SECRET is not set")
            return jwt.decode(
                token,
                settings.supabase_jwt_secret,
                algorithms=["HS256"],
                options={"verify_aud": False},  # Supabase aud is "authenticated"
            )
        if alg in ("ES256", "RS256"):
            base = settings.supabase_url.rstrip("/")
            if not base:
                raise _unauthorized("asymmetric token but SUPABASE_URL is not set")
            signing_key = _jwks_for(
                f"{base}/auth/v1/.well-known/jwks.json"
            ).get_signing_key_from_jwt(token)
            return jwt.decode(
                token,
                signing_key.key,
                algorithms=[alg],
                options={"verify_aud": False},
            )
        raise _unauthorized(f"Unsupported token algorithm: {alg or 'none'}")
    except HTTPException:
        raise
    except Exception as e:  # noqa: BLE001 - normalize all decode failures
        raise _unauthorized(f"Invalid token: {e}") from e


def get_current_user(
    request: Request,
    authorization: Optional[str] = Header(default=None),
    x_dev_user: Optional[str] = Header(default=None),
) -> User:
    settings = get_settings()
    store: Store = request.app.state.store

    auth_enabled = bool(settings.supabase_jwt_secret or settings.supabase_url)
    if not auth_enabled:
        uid = (x_dev_user or "dev-user").strip()
        return store.upsert_user(uid, email=f"{uid}@dev.local", default_credits=_DEV_CREDITS)

    if not authorization or not authorization.lower().startswith("bearer "):
        raise _unauthorized("Missing bearer token")
    token = authorization.split(" ", 1)[1].strip()
    payload = _decode_supabase_jwt(token, settings)
    uid = payload.get("sub")
    if not uid:
        raise _unauthorized("Token has no subject")
    return store.upsert_user(
        uid, email=payload.get("email", ""), default_credits=settings.free_plan_credits
    )
