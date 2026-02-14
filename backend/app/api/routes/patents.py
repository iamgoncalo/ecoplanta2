"""Patents module -- patent listing, detail, experiment results."""

from __future__ import annotations

import json
import uuid
from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_current_user, get_seed_data
from app.schemas.materials import (
    PatentDetail,
    PatentExperimentResult,
    PatentListResponse,
)

router = APIRouter(prefix="/api/patents", tags=["patents"])

# ── In-memory store for additional experiments ──────────────────────────────

_additional_experiments: dict[str, list[dict[str, Any]]] = {}


def _build_patent_detail(p: dict[str, Any]) -> PatentDetail:
    """Build a PatentDetail from raw seed data."""
    claims_raw = p.get("claims_json")
    claims = json.loads(claims_raw) if isinstance(claims_raw, str) else claims_raw

    exp_raw = p.get("experiment_results_json")
    experiment_results = json.loads(exp_raw) if isinstance(exp_raw, str) else exp_raw

    # Include any additional experiments added via API
    additional = _additional_experiments.get(p["id"], [])
    additional_parsed = [PatentExperimentResult(**e) for e in additional]

    return PatentDetail(
        id=p["id"],
        title=p["title"],
        filing_number=p["filing_number"],
        status=p["status"],
        filing_date=p.get("filing_date"),
        claims=claims,
        experiment_results=experiment_results,
        inventors=p.get("inventors", ""),
        novelty_notes=p.get("novelty_notes", ""),
        additional_experiments=additional_parsed,
        source=p.get("source", "synthetic_seeded"),
        source_id=p.get("source_id"),
    )


# ── GET: list patents ──────────────────────────────────────────────────────


@router.get("", response_model=PatentListResponse)
async def list_patents(
    status: str | None = None,
    current_user: dict[str, Any] = Depends(get_current_user),
) -> PatentListResponse:
    """List patents with optional status filter."""
    data = get_seed_data()
    patents_raw = data["patents"]

    if status:
        patents_raw = [p for p in patents_raw if p["status"] == status]

    patents = [_build_patent_detail(p) for p in patents_raw]

    return PatentListResponse(patents=patents, total=len(patents))


# ── GET: patent detail ─────────────────────────────────────────────────────


@router.get("/{patent_id}", response_model=PatentDetail)
async def get_patent(
    patent_id: str,
    current_user: dict[str, Any] = Depends(get_current_user),
) -> PatentDetail:
    """Get patent detail with claims and experiment results."""
    data = get_seed_data()

    for p in data["patents"]:
        if p["id"] == patent_id:
            return _build_patent_detail(p)

    raise HTTPException(status_code=404, detail=f"Patent {patent_id} not found")


# ── POST: add experiment result ────────────────────────────────────────────


@router.post("/{patent_id}/experiments", response_model=PatentDetail, status_code=201)
async def add_experiment(
    patent_id: str,
    body: PatentExperimentResult,
    current_user: dict[str, Any] = Depends(get_current_user),
) -> PatentDetail:
    """Add an experiment result to a patent."""
    data = get_seed_data()

    patent_raw = None
    for p in data["patents"]:
        if p["id"] == patent_id:
            patent_raw = p
            break

    if patent_raw is None:
        raise HTTPException(status_code=404, detail=f"Patent {patent_id} not found")

    experiment = {
        "id": str(uuid.uuid4()),
        "description": body.description,
        "result": body.result,
        "date": body.date or datetime.now(UTC).isoformat(),
    }

    if patent_id not in _additional_experiments:
        _additional_experiments[patent_id] = []
    _additional_experiments[patent_id].append(experiment)

    return _build_patent_detail(patent_raw)
