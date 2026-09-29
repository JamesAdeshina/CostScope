"""
Pydantic schemas for postcode resolution.
"""

from pydantic import BaseModel

from backend.app.schemas.location import LocationOverviewResponse


class PostcodeGeography(BaseModel):
    """Administrative geography resolved from a UK postcode."""

    postcode: str
    admin_district: str
    admin_district_code: str
    region: str | None
    country: str
    latitude: float | None
    longitude: float | None


class PostcodeOverviewResponse(BaseModel):
    """
    CostScope response combining postcode resolution and local metrics.
    """

    postcode: PostcodeGeography
    overview: LocationOverviewResponse
