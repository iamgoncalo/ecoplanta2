"""Authentication endpoints (dev-mode friendly)."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.api.deps import get_current_user
from app.core.security import create_access_token
from app.schemas.common import UserResponse

router = APIRouter(tags=["auth"])


# ── Request / response schemas ────────────────────────────────────────────────


class TokenRequest(BaseModel):
    """Minimal dev-mode login request."""

    email: str = "admin@ecoplanta.dev"
    name: str = "Dev Admin"
    role: str = "admin"

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

    model_config = {"from_attributes": True}


# ── Endpoints ─────────────────────────────────────────────────────────────────


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: dict[str, Any] = Depends(get_current_user),
) -> UserResponse:
    """Return the current authenticated user (auto-resolves in dev mode)."""
    return UserResponse(**current_user)


@router.post("/auth/token", response_model=TokenResponse)
async def dev_login(body: TokenRequest) -> TokenResponse:
    """Issue a JWT token for development / testing.

    In production this endpoint should be protected or replaced by a
    proper OAuth2 / OIDC flow.
    """
    token = create_access_token(
        data={
            "sub": "dev-admin-001",
            "email": body.email,
            "name": body.name,
            "role": body.role,
        }
    )
    return TokenResponse(access_token=token)
