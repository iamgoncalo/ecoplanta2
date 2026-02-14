"""Shared / base Pydantic v2 schemas used across modules."""

from __future__ import annotations

import enum
from datetime import datetime
from typing import Generic, TypeVar

from pydantic import BaseModel, Field

# ── Data source enum (mirrors the ORM enum) ──────────────────────────────────


class DataSourceEnum(enum.StrEnum):
    synthetic_seeded = "synthetic_seeded"
    integration_stub = "integration_stub"
    real = "real"


# ── Base schema with provenance ───────────────────────────────────────────────


class BaseSchema(BaseModel):
    """Every API response object carries provenance metadata."""

    source: DataSourceEnum = DataSourceEnum.synthetic_seeded
    source_id: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


# ── Health ────────────────────────────────────────────────────────────────────


class HealthResponse(BaseModel):
    status: str = "ok"
    db_connected: bool = False
    redis_connected: bool = False
    version: str = "0.1.0"

    model_config = {"from_attributes": True}


# ── Auth / User ───────────────────────────────────────────────────────────────


class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    role: str

    model_config = {"from_attributes": True}


# ── Pagination generic ───────────────────────────────────────────────────────

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Wraps a list of items with pagination metadata."""

    items: list[T] = Field(default_factory=list)
    total: int = 0
    page: int = 1
    page_size: int = 50
    has_next: bool = False

    model_config = {"from_attributes": True}
