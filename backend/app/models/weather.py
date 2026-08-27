"""
NER-SAGE — Pydantic models for Weather Observations and Rainfall Forecasts.
"""

from datetime import datetime

from pydantic import BaseModel, Field


class WeatherObservationModel(BaseModel):
    id: str = Field(alias="_id")
    location_id: str
    station_id: str | None = None
    observed_at: datetime
    rainfall_mm: float = Field(..., ge=0)
    rainfall_24h_mm: float = Field(0.0, ge=0, description="24-hour accumulated rainfall")
    rainfall_72h_mm: float = Field(0.0, ge=0, description="72-hour accumulated rainfall")
    temperature_c: float | None = None
    humidity_pct: float | None = None
    wind_speed_kmh: float | None = None
    source: str = "imd"
    is_simulated: bool = True
    created_at: datetime

    class Config:
        populate_by_name = True


class RainfallForecastModel(BaseModel):
    id: str = Field(alias="_id")
    location_id: str
    issued_at: datetime
    valid_from: datetime
    valid_to: datetime
    forecast_rainfall_mm: float
    intensity: str  # HEAVY | VERY_HEAVY | EXTREMELY_HEAVY | MODERATE | LIGHT
    confidence: float = Field(..., ge=0, le=1)
    source: str = "imd_forecast"
    is_simulated: bool = True
    created_at: datetime

    class Config:
        populate_by_name = True


class SatelliteObservationModel(BaseModel):
    id: str = Field(alias="_id")
    location_id: str
    satellite: str  # sentinel_1 | sentinel_2 | nisar
    product_type: str  # SAR_GRD | L2A | deformation
    acquired_at: datetime
    freshness: str  # HIGH | MEDIUM | LOW
    deformation_mm: float | None = None
    change_detected: bool = False
    change_type: str | None = None
    land_cover_change: bool = False
    ndvi: float | None = None
    coherence: float | None = None
    object_storage_key: str | None = None  # MinIO key for actual raster
    is_simulated: bool = True
    created_at: datetime

    class Config:
        populate_by_name = True
