"""
API response schemas for CostScope locations.
"""

from datetime import date

from pydantic import BaseModel


class LocationSummary(BaseModel):
    """Location metadata returned by the API."""

    location_id: str
    location_code: str
    name: str
    region_or_country: str | None


class RentOverview(BaseModel):
    """Latest published private-rent metrics."""

    monthly_rent: float
    unit: str
    reference_period: date
    monthly_change_percent: float | None
    annual_change_percent: float | None


class SourceMetadata(BaseModel):
    """Source information for an API metric."""

    source_code: str
    publisher: str
    dataset: str


class LocationOverviewResponse(BaseModel):
    """CostScope location overview response."""

    location: LocationSummary
    rent: RentOverview
    source: SourceMetadata


class LocationSearchResult(BaseModel):
    """One result from location search."""

    location_id: str
    location_code: str
    name: str
    region_or_country: str | None