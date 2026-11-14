"""
Tests for the PostgreSQL repository dispatch layer.

These tests intentionally do not require a live database.
"""

from backend.app.repositories import (
    database_repository,
)


def test_search_uses_parquet_when_database_not_configured(
    monkeypatch,
) -> None:
    """No DB URL should retain the existing Parquet behaviour."""

    monkeypatch.setattr(
        database_repository,
        "database_configured",
        lambda: False,
    )

    expected = [
        {
            "location_id": ("E06000015"),
            "location_code": ("E06000015"),
            "name": "Derby",
            "region_or_country": ("East Midlands"),
        }
    ]

    monkeypatch.setattr(
        database_repository.parquet_repository,
        "search_locations",
        lambda query, limit=20: expected,
    )

    result = database_repository.search_locations("Derby")

    assert result == expected


def test_find_location_uses_parquet_when_database_not_configured(
    monkeypatch,
) -> None:
    """Location lookup should retain Parquet fallback."""

    monkeypatch.setattr(
        database_repository,
        "database_configured",
        lambda: False,
    )

    sentinel = object()

    monkeypatch.setattr(
        database_repository.parquet_repository,
        "find_location",
        lambda location_code: sentinel,
    )

    result = database_repository.find_location("E06000015")

    assert result is sentinel
