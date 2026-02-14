"""Health-check endpoint."""

from __future__ import annotations

from fastapi import APIRouter

from app.core.config import settings
from app.schemas.common import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Return service health including DB and Redis connectivity status.

    In Phase 1 we report ``db_connected`` and ``redis_connected`` as
    best-effort checks.  If the services are unreachable the endpoint
    still returns 200 but with the flags set to ``False``.
    """
    db_ok = False
    redis_ok = False

    # ── DB check ──────────────────────────────────────────────────────
    try:
        from sqlalchemy import text

        from app.db.session import engine

        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        pass

    # ── Redis check ───────────────────────────────────────────────────
    try:
        import redis.asyncio as aioredis

        r = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
        await r.ping()
        await r.aclose()
        redis_ok = True
    except Exception:
        pass

    return HealthResponse(
        status="ok",
        db_connected=db_ok,
        redis_connected=redis_ok,
        version=settings.APP_VERSION,
    )
