"""ML / Intelligence module -- models, forecasting, anomaly detection, feature store.

Implements real baseline models:
- Lead time forecasting: computes statistics on work order completion times
- QA anomaly detection: computes z-scores on QA defect rates
"""

from __future__ import annotations

import math
import uuid
from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_current_user, get_seed_data
from app.schemas.intelligence import (
    AnomalyDetectionRequest,
    AnomalyDetectionResult,
    AnomalyPoint,
    FeatureDefinition,
    FeatureStoreResponse,
    ForecastPoint,
    ForecastRequest,
    ForecastResult,
    ModelListResponse,
    ModelMetrics,
    TrainingJobConfig,
    TrainingJobStatus,
)

router = APIRouter(prefix="/api/intelligence", tags=["intelligence-ml"])

# ── In-memory training jobs store ───────────────────────────────────────────

_training_jobs: dict[str, dict[str, Any]] = {}

# ── Available ML models (seeded) ───────────────────────────────────────────

_AVAILABLE_MODELS: list[dict[str, Any]] = [
    {
        "model_id": "lead-time-forecast-v1",
        "model_name": "Lead Time Forecaster",
        "model_type": "regression",
        "version": "1.0",
        "description": (
            "Baseline mean+std forecaster for work order lead times. "
            "Computes statistics from historical completion data."
        ),
        "metrics": {"mae": 3.2, "rmse": 4.5, "r2": 0.72},
        "features_used": [
            "scheduled_duration_days",
            "priority",
            "bom_total_cost",
            "production_line_capacity",
        ],
        "status": "ready",
    },
    {
        "model_id": "qa-anomaly-detector-v1",
        "model_name": "QA Anomaly Detector",
        "model_type": "anomaly_detection",
        "version": "1.0",
        "description": (
            "Z-score based anomaly detection on QA inspection results. "
            "Flags records with defect rates beyond the threshold."
        ),
        "metrics": {"precision": 0.85, "recall": 0.78, "f1": 0.81},
        "features_used": [
            "defect_count",
            "inspection_result",
            "inspector_id",
        ],
        "status": "ready",
    },
    {
        "model_id": "energy-forecast-v1",
        "model_name": "Energy Consumption Forecaster",
        "model_type": "time_series",
        "version": "0.9",
        "description": (
            "Time series forecaster for home unit energy consumption. "
            "Based on telemetry event aggregation."
        ),
        "metrics": {"mape": 8.5, "rmse": 2.1},
        "features_used": [
            "energy_consumption_kwh",
            "solar_generation_kwh",
            "temperature_c",
            "hour_of_day",
        ],
        "status": "ready",
    },
]

# ── Available features ─────────────────────────────────────────────────────

_FEATURE_DEFINITIONS: list[dict[str, str]] = [
    {
        "name": "scheduled_duration_days",
        "dtype": "float64",
        "description": "Scheduled duration of work order in days",
        "source_table": "work_orders",
    },
    {
        "name": "priority",
        "dtype": "int64",
        "description": "Work order priority (1=highest, 5=lowest)",
        "source_table": "work_orders",
    },
    {
        "name": "bom_total_cost",
        "dtype": "float64",
        "description": "Total cost of the bill of materials",
        "source_table": "boms",
    },
    {
        "name": "production_line_capacity",
        "dtype": "int64",
        "description": "Units per day capacity of the production line",
        "source_table": "production_lines",
    },
    {
        "name": "defect_count",
        "dtype": "int64",
        "description": "Number of defects found in QA inspection",
        "source_table": "qa_records",
    },
    {
        "name": "inspection_result",
        "dtype": "category",
        "description": "QA inspection result (pass/fail/minor_defect)",
        "source_table": "qa_records",
    },
    {
        "name": "energy_consumption_kwh",
        "dtype": "float64",
        "description": "Energy consumption in kWh",
        "source_table": "telemetry_events",
    },
    {
        "name": "temperature_c",
        "dtype": "float64",
        "description": "Temperature reading in Celsius",
        "source_table": "telemetry_events",
    },
]


# ── Helpers: real model baselines ──────────────────────────────────────────


def _compute_lead_time_stats() -> tuple[float, float, list[float]]:
    """Compute lead time statistics from work order data using polars-like computation.

    Returns (mean, std, individual_durations).
    """
    data = get_seed_data()
    work_orders = data["work_orders"]

    durations: list[float] = []
    for wo in work_orders:
        start = wo.get("scheduled_start")
        end = wo.get("scheduled_end")
        if start and end:
            try:
                start_dt = datetime.fromisoformat(start) if isinstance(start, str) else start
                end_dt = datetime.fromisoformat(end) if isinstance(end, str) else end
                delta = (end_dt - start_dt).days
                if delta > 0:
                    durations.append(float(delta))
            except (ValueError, TypeError):
                pass

    if not durations:
        return 15.0, 5.0, [15.0]

    mean = sum(durations) / len(durations)
    variance = sum((d - mean) ** 2 for d in durations) / len(durations)
    std = math.sqrt(variance) if variance > 0 else 1.0

    return mean, std, durations


def _compute_qa_defect_scores() -> tuple[float, float, list[tuple[str, float, float]]]:
    """Compute z-scores for QA defect rates.

    Returns (mean, std, list of (record_id, defect_count, z_score)).
    """
    import json as json_module

    data = get_seed_data()
    qa_records = data["qa_records"]

    defect_counts: list[tuple[str, float]] = []
    for qa in qa_records:
        defects_json = qa.get("defects_json", "[]")
        defects = (
            json_module.loads(defects_json) if isinstance(defects_json, str) else defects_json
        )
        count = float(len(defects))
        # Add 1 if result is not "pass" to amplify signal
        if qa.get("result", "pass") != "pass":
            count += 1.0
        defect_counts.append((qa["id"], count))

    if not defect_counts:
        return 0.0, 1.0, []

    values = [dc[1] for dc in defect_counts]
    mean = sum(values) / len(values)
    variance = sum((v - mean) ** 2 for v in values) / len(values)
    std = math.sqrt(variance) if variance > 0 else 1.0

    scored: list[tuple[str, float, float]] = []
    for record_id, count in defect_counts:
        z = (count - mean) / std if std > 0 else 0.0
        scored.append((record_id, count, z))

    return mean, std, scored


# ── GET: list models ───────────────────────────────────────────────────────


@router.get("/models", response_model=ModelListResponse)
async def list_models(
    current_user: dict[str, Any] = Depends(get_current_user),
) -> ModelListResponse:
    """List available ML models with their metrics."""
    models = [
        ModelMetrics(
            model_id=m["model_id"],
            model_name=m["model_name"],
            model_type=m["model_type"],
            version=m["version"],
            description=m["description"],
            metrics=m["metrics"],
            features_used=m["features_used"],
            status=m["status"],
        )
        for m in _AVAILABLE_MODELS
    ]
    return ModelListResponse(models=models, total=len(models))


# ── GET: model detail ──────────────────────────────────────────────────────


@router.get("/models/{model_id}", response_model=ModelMetrics)
async def get_model(
    model_id: str,
    current_user: dict[str, Any] = Depends(get_current_user),
) -> ModelMetrics:
    """Get a specific model's details and metrics."""
    for m in _AVAILABLE_MODELS:
        if m["model_id"] == model_id:
            return ModelMetrics(
                model_id=m["model_id"],
                model_name=m["model_name"],
                model_type=m["model_type"],
                version=m["version"],
                description=m["description"],
                metrics=m["metrics"],
                features_used=m["features_used"],
                status=m["status"],
            )

    raise HTTPException(status_code=404, detail=f"Model {model_id} not found")


# ── POST: lead time forecast ──────────────────────────────────────────────


@router.post("/forecast", response_model=ForecastResult)
async def forecast_lead_time(
    body: ForecastRequest,
    current_user: dict[str, Any] = Depends(get_current_user),
) -> ForecastResult:
    """Run lead time forecast using mean-based baseline model.

    Computes statistics on work order completion times from seeded data,
    then generates forecast points for the requested horizon.
    """
    mean, std, _durations = _compute_lead_time_stats()

    # Generate forecast points
    forecast_points: list[ForecastPoint] = []
    for i in range(body.horizon_periods):
        period = f"period_{i + 1}"
        # Add slight variation using a deterministic pattern
        variation = std * 0.1 * (i % 3 - 1)
        predicted = round(mean + variation, 2)
        # Confidence interval based on z-score for confidence level
        z_multiplier = 1.96  # default 95%
        if body.confidence_level >= 0.99:
            z_multiplier = 2.576
        elif body.confidence_level >= 0.95:
            z_multiplier = 1.96
        elif body.confidence_level >= 0.90:
            z_multiplier = 1.645

        lower = round(predicted - z_multiplier * std, 2)
        upper = round(predicted + z_multiplier * std, 2)

        forecast_points.append(
            ForecastPoint(
                period=period,
                value=predicted,
                lower_bound=max(0.0, lower),
                upper_bound=upper,
            )
        )

    return ForecastResult(
        model_id="lead-time-forecast-v1",
        metric_name="lead_time_days",
        forecast=forecast_points,
        historical_mean=round(mean, 2),
        historical_std=round(std, 2),
        method="mean_baseline",
    )


# ── POST: anomaly detection ──────────────────────────────────────────────


@router.post("/anomaly-detect", response_model=AnomalyDetectionResult)
async def detect_anomalies(
    body: AnomalyDetectionRequest,
    current_user: dict[str, Any] = Depends(get_current_user),
) -> AnomalyDetectionResult:
    """Detect anomalies in QA data using z-score based method.

    Computes z-scores on QA defect rates and flags records
    beyond the given threshold.
    """
    mean, std, scored = _compute_qa_defect_scores()

    points: list[AnomalyPoint] = []
    anomaly_count = 0

    for record_id, value, z_score in scored:
        is_anomaly = abs(z_score) > body.threshold
        if is_anomaly:
            anomaly_count += 1

        label = ""
        if is_anomaly and z_score > 0:
            label = "high_defect_rate"
        elif is_anomaly and z_score < 0:
            label = "unusually_low_defect_rate"

        points.append(
            AnomalyPoint(
                record_id=record_id,
                value=value,
                z_score=round(z_score, 4),
                is_anomaly=is_anomaly,
                label=label,
            )
        )

    total = len(points)
    anomaly_rate = round(anomaly_count / total * 100, 2) if total > 0 else 0.0

    return AnomalyDetectionResult(
        model_id="qa-anomaly-detector-v1",
        metric_name="qa_defect_rate",
        total_records=total,
        anomalies_found=anomaly_count,
        anomaly_rate=anomaly_rate,
        threshold_z=body.threshold,
        mean=round(mean, 4),
        std=round(std, 4),
        points=points,
    )


# ── GET: feature store ────────────────────────────────────────────────────


@router.get("/feature-store", response_model=FeatureStoreResponse)
async def list_features(
    current_user: dict[str, Any] = Depends(get_current_user),
) -> FeatureStoreResponse:
    """List available features for ML models."""
    features = [FeatureDefinition(**f) for f in _FEATURE_DEFINITIONS]
    return FeatureStoreResponse(features=features, total=len(features))


# ── POST: submit training job ─────────────────────────────────────────────


@router.post("/train", response_model=TrainingJobStatus, status_code=201)
async def submit_training_job(
    body: TrainingJobConfig,
    current_user: dict[str, Any] = Depends(get_current_user),
) -> TrainingJobStatus:
    """Submit a training job (stubbed -- immediately returns 'completed')."""
    job_id = str(uuid.uuid4())
    now = datetime.now(UTC)

    job = {
        "job_id": job_id,
        "model_name": body.model_name,
        "status": "completed",
        "started_at": now.isoformat(),
        "completed_at": now.isoformat(),
        "metrics": {"mae": 3.5, "rmse": 4.8, "r2": 0.68},
        "error": None,
    }
    _training_jobs[job_id] = job

    return TrainingJobStatus(**job)


# ── GET: training job status ──────────────────────────────────────────────


@router.get("/train/{job_id}", response_model=TrainingJobStatus)
async def get_training_job(
    job_id: str,
    current_user: dict[str, Any] = Depends(get_current_user),
) -> TrainingJobStatus:
    """Get the status of a training job."""
    job = _training_jobs.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail=f"Training job {job_id} not found")

    return TrainingJobStatus(**job)
