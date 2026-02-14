"""FastAPI application factory for EcoContainer + Planta Smart Homes Brain."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, Any

import structlog
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import (
    auth,
    deploy,
    fabric,
    factory,
    frameworks,
    health,
    intelligence,
    partners,
    sales,
)
from app.core.config import settings
from app.core.logging import setup_logging

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

logger = structlog.stdlib.get_logger(__name__)


# ── Lifespan (startup / shutdown) ─────────────────────────────────────────────


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan: runs once on startup and once on shutdown."""
    setup_logging()
    logger.info(
        "starting_ecoplanta_backend",
        version=settings.APP_VERSION,
        dev_mode=settings.DEV_MODE,
    )

    # Pre-warm seed data cache so first request is fast
    from app.api.deps import get_seed_data

    seed_data = get_seed_data()
    logger.info(
        "seed_data_loaded",
        entities=len(seed_data),
        seed=settings.SEED,
    )

    yield  # ← application runs here

    logger.info("shutting_down_ecoplanta_backend")


# ── App factory ───────────────────────────────────────────────────────────────


def create_app() -> FastAPI:
    """Build and return the configured FastAPI application instance."""
    app = FastAPI(
        title="EcoContainer + Planta Smart Homes API",
        description=(
            "Production-grade API for the EcoContainer Technologies OS "
            "and Planta Smart Homes Brain platform."
        ),
        version=settings.APP_VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # ── CORS ──────────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Security headers middleware ───────────────────────────────────
    @app.middleware("http")
    async def security_headers(request: Request, call_next: Any) -> Response:
        response: Response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        return response

    # ── Routers ───────────────────────────────────────────────────────
    app.include_router(health.router)
    app.include_router(auth.router)
    app.include_router(fabric.router)
    app.include_router(factory.router)
    app.include_router(frameworks.router)
    app.include_router(sales.router)
    app.include_router(intelligence.router)
    app.include_router(deploy.router)
    app.include_router(partners.router)

    return app


app = create_app()
