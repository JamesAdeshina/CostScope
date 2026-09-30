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
    """Latest private-rent metrics."""

    monthly_rent: float
    unit: str
    reference_period: date
    monthly_change_percent: float | None
    annual_change_percent: float | None


class EarningsOverview(BaseModel):
    """Latest ASHE earnings metrics."""

    median_annual_pay: float
    unit: str
    reference_period: date
    annual_change_percent: float | None


class InflationOverview(BaseModel):
    """Latest UK CPI metrics."""

    annual_rate_percent: float
    monthly_rate_percent: float | None
    index_value: float | None
    index_base: str
    reference_period: date
    geography_name: str
    geography_code: str


class UnemploymentOverview(BaseModel):
    """Latest model-based unemployment estimate."""

    rate_percent: float
    unit: str
    reference_period: date
    geography_name: str
    geography_code: str
    methodology: str


class SourceMetadata(BaseModel):
    """Source metadata."""

    source_code: str
    publisher: str
    dataset: str


class LocationOverviewResponse(BaseModel):
    """Latest available CostScope metrics."""

    location: LocationSummary

    rent: RentOverview | None = None

    earnings: EarningsOverview | None = None

    inflation: InflationOverview | None = None

    unemployment: UnemploymentOverview | None = None

    sources: list[SourceMetadata]


class LocationSearchResult(BaseModel):
    """One location-search result."""

    location_id: str
    location_code: str
    name: str
    region_or_country: str | None


class MetricHistoryObservation(BaseModel):
    """One historical observation."""

    reference_period: date
    value: float


class MetricHistoryResponse(BaseModel):
    """Historical metric series."""

    location: LocationSummary
    metric_code: str
    metric_name: str
    unit: str
    observations: list[MetricHistoryObservation]
    source: SourceMetadata
