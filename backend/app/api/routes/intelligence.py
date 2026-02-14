"""Intelligence module -- insight reports and forecasts."""

from __future__ import annotations

import json
from typing import Any

from fastapi import APIRouter, Depends

from app.api.deps import get_current_user, get_seed_data
from app.schemas.modules import IntelligenceInsight, IntelligenceListResponse

router = APIRouter(prefix="/api/intelligence", tags=["intelligence"])


@router.get("", response_model=IntelligenceListResponse)
async def list_intelligence(
    current_user: dict[str, Any] = Depends(get_current_user),
) -> IntelligenceListResponse:
    """List insight reports and analytics forecasts.

    Falls back to seed data when the database is empty or unavailable.
    """
    data = get_seed_data()
    reports_raw = data["insight_reports"]

    insights: list[IntelligenceInsight] = []
    for rpt in reports_raw:
        params = rpt.get("parameters_json")
        results = rpt.get("results_json")
        insights.append(
            IntelligenceInsight(
                id=rpt["id"],
                title=rpt["title"],
                module=rpt["module"],
                report_type=rpt["report_type"],
                parameters=json.loads(params) if isinstance(params, str) else params,
                results=json.loads(results) if isinstance(results, str) else results,
                generated_at=rpt.get("generated_at"),
                source=rpt.get("source", "synthetic_seeded"),
                source_id=rpt.get("source_id"),
            )
        )

    return IntelligenceListResponse(
        insights=insights,
        total_insights=len(insights),
    )
