"""
Tests for CostScope Gold modelling.
"""

import pandas as pd

from data_pipeline.model.private_rent_gold import (
    build_dim_date,
    build_dim_location,
    build_dim_metric,
    stable_integer_key,
)


def sample_silver() -> pd.DataFrame:
    """Return a small representative Silver dataset."""

    return pd.DataFrame(
        {
            "time_period": pd.to_datetime(
                [
                    "2026-07-01",
                    "2026-08-01",
                ]
            ),
            "location_id": [
                "E06000015",
                "E06000015",
            ],
            "area_code": [
                "E06000015",
                "E06000015",
            ],
            "area_name": [
                "Derby",
                "Derby",
            ],
            "region_or_country_name": [
                "East Midlands",
                "East Midlands",
            ],
        }
    )


def test_stable_integer_key_is_deterministic() -> None:
    """Same source value should always produce the same key."""

    first = stable_integer_key(
        "location",
        "E06000015",
    )

    second = stable_integer_key(
        "location",
        "E06000015",
    )

    assert first == second


def test_dim_location_has_one_derby_record() -> None:
    """Repeated Silver observations should create one location."""

    result = build_dim_location(
        sample_silver()
    )

    assert len(result) == 1

    assert (
        result.iloc[0][
            "official_area_code"
        ]
        == "E06000015"
    )


def test_dim_date_contains_unique_months() -> None:
    """Reporting periods should create unique date rows."""

    result = build_dim_date(
        sample_silver()
    )

    assert len(result) == 2

    assert result[
        "date_key"
    ].is_unique


def test_metric_codes_are_unique() -> None:
    """Gold metric definitions must have unique codes."""

    result = build_dim_metric()

    assert result[
        "metric_code"
    ].is_unique

    assert (
        "RENT_MONTHLY"
        in set(
            result[
                "metric_code"
            ]
        )
    )