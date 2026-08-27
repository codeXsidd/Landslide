"""
NER-SAGE — Pydantic models for Locations, Roads, Villages, Infrastructure.
"""

from datetime import datetime

from pydantic import BaseModel, Field


class GeoPoint(BaseModel):
    type: str = "Point"
    coordinates: list[float] = Field(..., description="[longitude, latitude] WGS84")


class GeoPolygon(BaseModel):
    type: str = "Polygon"
    coordinates: list[list[list[float]]]


class LocationModel(BaseModel):
    id: str = Field(alias="_id")
    name: str
    location_type: str  # road | village | hospital | junction | facility
    state: str
    district: str
    geometry: GeoPoint
    properties: dict = Field(default_factory=dict)
    is_simulated: bool = True
    created_at: datetime

    class Config:
        populate_by_name = True


class RoadModel(BaseModel):
    id: str = Field(alias="_id")
    name: str
    road_type: str  # national_highway | state_highway | district_road | village_road
    geometry: dict  # GeoJSON LineString
    length_km: float
    surface_type: str  # paved | unpaved | dirt
    is_critical: bool = False
    connects: list[str] = Field(default_factory=list, description="Connected location IDs")
    current_status: str = "OPEN"  # OPEN | CLOSED | DEGRADED | UNKNOWN
    last_status_update: datetime | None = None
    is_simulated: bool = True

    class Config:
        populate_by_name = True


class VillageModel(BaseModel):
    id: str = Field(alias="_id")
    name: str
    state: str
    district: str
    geometry: GeoPoint
    population: int
    households: int
    primary_road_id: str
    alternate_road_ids: list[str] = Field(default_factory=list)
    nearest_hospital_id: str | None = None
    hospital_distance_km: float | None = None
    is_simulated: bool = True

    class Config:
        populate_by_name = True


class HospitalModel(BaseModel):
    id: str = Field(alias="_id")
    name: str
    hospital_type: str  # district | sub_district | CHC | PHC
    geometry: GeoPoint
    beds: int
    emergency_services: bool
    serves_population: int
    access_roads: list[str] = Field(default_factory=list)
    is_simulated: bool = True

    class Config:
        populate_by_name = True
