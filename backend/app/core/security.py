"""JWT token handling, password hashing, and dev-mode auth stub."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

# ── Password hashing ─────────────────────────────────────────────────────────

_pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Return a bcrypt hash of *password*."""
    return str(_pwd_ctx.hash(password))


def verify_password(plain: str, hashed: str) -> bool:
    """Verify *plain* text against a bcrypt *hashed* value."""
    return bool(_pwd_ctx.verify(plain, hashed))


# ── JWT tokens ────────────────────────────────────────────────────────────────


def create_access_token(data: dict[str, Any]) -> str:
    """Create a signed JWT access token.

    *data* is embedded as claims.  An ``exp`` claim is added automatically.
    """
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(
        minutes=settings.AUTH_ACCESS_TOKEN_EXPIRE_MINUTES,
    )
    to_encode.update({"exp": expire})
    return str(
        jwt.encode(
            to_encode,
            settings.AUTH_SECRET_KEY,
            algorithm=settings.AUTH_ALGORITHM,
        )
    )


def verify_token(token: str) -> dict[str, Any]:
    """Decode and verify a JWT token, returning its claims.

    Raises ``HTTPException(401)`` on any verification failure.
    """
    try:
        payload: dict[str, Any] = jwt.decode(
            token,
            settings.AUTH_SECRET_KEY,
            algorithms=[settings.AUTH_ALGORITHM],
        )
        return payload
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired token: {exc}",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


# ── Dev-mode default user ─────────────────────────────────────────────────────

_DEV_USER: dict[str, Any] = {
    "id": "dev-admin-001",
    "email": "admin@ecoplanta.dev",
    "name": "Dev Admin",
    "role": "admin",
}

# ── FastAPI dependency ────────────────────────────────────────────────────────

_bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> dict[str, Any]:
    """Return the authenticated user dict.

    In **dev mode** (``settings.DEV_MODE is True``) a default admin user is
    returned when no ``Authorization`` header is provided, allowing
    front-end development without a real auth flow.
    """
    if credentials is None or credentials.credentials == "":
        if settings.DEV_MODE:
            return _DEV_USER
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = verify_token(credentials.credentials)
    return {
        "id": payload.get("sub", _DEV_USER["id"]),
        "email": payload.get("email", _DEV_USER["email"]),
        "name": payload.get("name", _DEV_USER["name"]),
        "role": payload.get("role", _DEV_USER["role"]),
    }
