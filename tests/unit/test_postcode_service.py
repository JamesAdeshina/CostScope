"""
Tests for CostScope postcode resolution utilities.
"""

from backend.app.services.postcode_service import (
    normalise_postcode,
)


def test_normalise_postcode_removes_spaces() -> None:
    """UK postcodes should be suitable for API lookup."""

    assert normalise_postcode("DE1 1AA") == "DE11AA"


def test_normalise_postcode_uppercases_input() -> None:
    """Postcode matching should be case insensitive."""

    assert normalise_postcode("de1 1aa") == "DE11AA"
