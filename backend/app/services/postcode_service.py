"""
Postcodes.io integration for CostScope.

Postcodes.io is used only for geography resolution.

No cost-of-living metric is sourced from Postcodes.io. Its role is to
translate a postcode into the administrative geography code used by
CostScope's analytical data.
"""

from __future__ import annotations

import re

import httpx

from backend.app.core.config import settings
from backend.app.core.logging_config import get_api_logger

logger = get_api_logger(__name__)


class InvalidPostcodeError(ValueError):
    """Raised when a postcode is malformed or not found."""


class PostcodeServiceError(RuntimeError):
    """Raised when the external postcode service fails."""


def normalise_postcode(
    postcode: str,
) -> str:
    """
    Normalise a UK postcode for API lookup.

    Spaces are removed and letters are converted to uppercase.
    """

    return re.sub(
        r"\s+",
        "",
        postcode,
    ).upper()


def lookup_postcode(
    postcode: str,
) -> dict[str, object]:
    """
    Resolve a UK postcode through Postcodes.io.

    Returns
    -------
    dict
        Normalised geography information required by CostScope.
    """

    normalised = normalise_postcode(postcode)

    if len(normalised) < 5:
        raise InvalidPostcodeError("The supplied postcode is not valid.")

    url = f"{settings.postcodes_api_url}/postcodes/{normalised}"

    logger.info(
        "Resolving postcode %s",
        normalised,
    )

    try:
        response = httpx.get(
            url,
            timeout=10.0,
        )

    except httpx.HTTPError as exc:
        logger.exception("Postcodes.io request failed")

        raise PostcodeServiceError(
            "The postcode service is currently unavailable."
        ) from exc

    if response.status_code == 404:
        raise InvalidPostcodeError(f"Postcode not found: {postcode}")

    try:
        response.raise_for_status()

    except httpx.HTTPStatusError as exc:
        raise PostcodeServiceError(
            "The postcode service returned an unexpected response."
        ) from exc

    payload = response.json()

    result = payload.get("result")

    if not result:
        raise InvalidPostcodeError(f"Postcode not found: {postcode}")

    codes = result.get("codes") or {}

    admin_district_code = codes.get("admin_district")

    admin_district = result.get("admin_district")

    if not admin_district_code or not admin_district:
        raise PostcodeServiceError(
            "The postcode could not be mapped to an administrative district."
        )

    return {
        "postcode": result.get(
            "postcode",
            normalised,
        ),
        "admin_district": admin_district,
        "admin_district_code": admin_district_code,
        "region": result.get("region"),
        "country": result.get(
            "country",
            "United Kingdom",
        ),
        "latitude": result.get("latitude"),
        "longitude": result.get("longitude"),
    }
