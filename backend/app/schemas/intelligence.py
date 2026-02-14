"""Intelligence layer schemas -- ML models, forecasting, anomaly detection."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

# ── Feature definition ──────────────────────────────────────────────────────


class FeatureDefinition(BaseModel):
    """Feature for ML model."""

    name: str
    dtype: str = "float64"
    description: str = ""
    source_table: str = ""

    model_config = {"from_attributes": True}


# ── Training job ────────────────────────────────────────────────────────────


class TrainingJobConfig(BaseModel):
    """Training job specification."""

    model_name: str
    features: list[str] = Field(default_factory=list)
    target: str = ""
    hyperparameters: dict[str, float | int | str] = Field(default_factory=dict)

    model_config = {"from_attributes": True}


class TrainingJobStatus(BaseModel):
    """Training job status."""

    job_id: str
    model_name: str
    status: str = "queued"  # queued, running, completed, failed
    started_at: datetime | None = None
    completed_at: datetime | None = None
    metrics: dict[str, float] = Field(default_factory=dict)
    error: str | None = None

    model_config = {"from_attributes": True}


# ── Inference ───────────────────────────────────────────────────────────────


class InferenceRequest(BaseModel):
    """Prediction request."""

    model_id: str
    features: dict[str, float | int | str] = Field(default_factory=dict)

    model_config = {"from_attributes": True}


class InferenceResponse(BaseModel):
    """Prediction response."""

    model_id: str
    prediction: float | str = 0.0
    confidence: float = 0.0
    metadata: dict[str, float | int | str] = Field(default_factory=dict)

    model_config = {"from_attributes": True}


# ── Model metrics ──────────────────────────────────────────────────────────


class ModelMetrics(BaseModel):
    """Evaluation metrics for a trained model."""

    model_id: str
    model_name: str
    model_type: str = "regression"
    version: str = "1.0"
    description: str = ""
    metrics: dict[str, float] = Field(default_factory=dict)
    features_used: list[str] = Field(default_factory=list)
    trained_at: datetime | None = None
    status: str = "ready"

    model_config = {"from_attributes": True}


class ModelListResponse(BaseModel):
    """Response for listing available ML models."""

    models: list[ModelMetrics] = Field(default_factory=list)
    total: int = 0

    model_config = {"from_attributes": True}


# ── Forecast result ─────────────────────────────────────────────────────────


class ForecastPoint(BaseModel):
    """Single point in a time series forecast."""

    period: str
    value: float = 0.0
    lower_bound: float = 0.0
    upper_bound: float = 0.0

    model_config = {"from_attributes": True}


class ForecastRequest(BaseModel):
    """Request body for lead time forecast."""

    horizon_periods: int = 6
    confidence_level: float = 0.95

    model_config = {"from_attributes": True}


class ForecastResult(BaseModel):
    """Time series forecast result."""

    model_id: str
    metric_name: str
    forecast: list[ForecastPoint] = Field(default_factory=list)
    historical_mean: float = 0.0
    historical_std: float = 0.0
    method: str = "mean_baseline"

    model_config = {"from_attributes": True}


# ── Anomaly detection ──────────────────────────────────────────────────────


class AnomalyPoint(BaseModel):
    """Single anomaly detection result."""

    record_id: str
    value: float = 0.0
    z_score: float = 0.0
    is_anomaly: bool = False
    label: str = ""

    model_config = {"from_attributes": True}


class AnomalyDetectionRequest(BaseModel):
    """Request body for anomaly detection."""

    threshold: float = 2.0

    model_config = {"from_attributes": True}


class AnomalyDetectionResult(BaseModel):
    """Anomaly detection result."""

    model_id: str
    metric_name: str
    total_records: int = 0
    anomalies_found: int = 0
    anomaly_rate: float = 0.0
    threshold_z: float = 2.0
    mean: float = 0.0
    std: float = 0.0
    points: list[AnomalyPoint] = Field(default_factory=list)

    model_config = {"from_attributes": True}


# ── Feature store ──────────────────────────────────────────────────────────


class FeatureStoreResponse(BaseModel):
    """Response for listing available features."""

    features: list[FeatureDefinition] = Field(default_factory=list)
    total: int = 0

    model_config = {"from_attributes": True}
