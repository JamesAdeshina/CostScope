"""
API response schemas for CostScope locations.
"""

from datetime import date

from pydantic import BaseModel


class LocationSummary(BaseModel):
    """Location metadata returned by CostScope."""

    location_id: str
    location_code: str
    name: str
    region_or_country: str | None


class RentOverview(BaseModel):
    """Latest published headline private-rent metrics."""

    monthly_rent: float
    unit: str
    reference_period: date
    monthly_change_percent: float | None
    annual_change_percent: float | None


class SourceMetadata(BaseModel):
    """Source information for a CostScope metric."""

    source_code: str
    publisher: str
    dataset: str


class LocationOverviewResponse(BaseModel):
    """Latest CostScope overview for one location."""

    location: LocationSummary
    rent: RentOverview
    source: SourceMetadata


class LocationSearchResult(BaseModel):
    """One result from location search."""

    location_id: str
    location_code: str
    name: str
    region_or_country: str | None


class MetricHistoryObservation(BaseModel):
    """One historical metric observation."""

    reference_period: date
    value: float


class MetricHistoryResponse(BaseModel):
    """Historical CostScope metric series."""

    location: LocationSummary
    metric_code: str
    metric_name: str
    unit: str
    observations: list[MetricHistoryObservation]
    source: SourceMetadata
