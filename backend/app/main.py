"""Reforge API — FastAPI application entrypoint.

Assembles the store, job manager, routers, CORS, and error handling. Runs with
zero external services in development (mock AI, dev-stub ingestion, in-memory
store, in-process jobs); configure .env to point at real providers.
"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.jobs import build_job_manager
from app.routers import analyses, health, me, projects, scripts, usage
from app.store import build_store

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
log = logging.getLogger("reforge")


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    app.state.store = build_store()
    app.state.jobs = build_job_manager(app.state.store)
    log.info(
        "Reforge API started (env=%s, ai_provider=%s, mock=%s, jobs_inline=%s)",
        settings.environment,
        settings.ai_provider,
        settings.use_mock_ai,
        settings.jobs_inline,
    )
    try:
        yield
    finally:
        app.state.jobs.shutdown()


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="Reforge API", version="0.1.0", lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Health at the root (no auth, no prefix).
    app.include_router(health.router)

    # Everything else under the versioned prefix.
    prefix = settings.api_prefix
    app.include_router(me.router, prefix=prefix)
    app.include_router(analyses.router, prefix=prefix)
    app.include_router(projects.router, prefix=prefix)
    app.include_router(scripts.router, prefix=prefix)
    app.include_router(usage.router, prefix=prefix)

    _install_error_handlers(app)
    return app


def _install_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(HTTPException)
    async def http_exc(_: Request, exc: HTTPException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": {"code": exc.status_code, "message": exc.detail}},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exc(_: Request, exc: RequestValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": 422,
                    "message": "Validation error",
                    "details": jsonable_encoder(exc.errors()),
                }
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exc(_: Request, exc: Exception) -> JSONResponse:  # pragma: no cover
        log.exception("Unhandled error")
        return JSONResponse(
            status_code=500,
            content={"error": {"code": 500, "message": "Internal server error"}},
        )


app = create_app()
