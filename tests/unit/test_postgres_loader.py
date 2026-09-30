"""
Unit tests for CostScope PostgreSQL preparation logic.

These tests do not require a running PostgreSQL instance.
"""

import pandas as pd

from data_pipeline.load.postgres import (
    prepare_dim_date,
    prepare_dim_metric,
    prepare_dim_source,
    prepare_fact_cost_metric,
)


def test_source_dimension_has_four_sources() -> None:
    """All current CostScope source systems should be defined."""

    sources = prepare_dim_source()

    assert len(sources) == 4

    assert set(sources["source_code"]) == {
        "ONS_PIPR",
        "ONS_ASHE",
        "ONS_CPI_MM23",
        "NOMIS_UNEMPLOYMENT_MODEL",
    }


def test_prepare_metric_adds_missing_category() -> None:
    """Older Gold metric tables may not contain category."""

    source = pd.DataFrame(
        {
            "metric_key": [
                1,
            ],
            "metric_code": [
                "RENT_MONTHLY",
            ],
            "metric_name": [
                "Average monthly private rent",
            ],
            "unit": [
                "GBP/month",
            ],
        }
    )

    result = prepare_dim_metric(source)

    assert "category" in result.columns


def test_prepare_date_converts_to_date() -> None:
    """PostgreSQL date values should not retain timestamps."""

    source = pd.DataFrame(
        {
            "date_key": [
                20260801,
            ],
            "date": [
                pd.Timestamp("2026-08-01"),
            ],
            "year": [
                2026,
            ],
            "quarter": [
                3,
            ],
            "month": [
                8,
            ],
            "month_name": [
                "August",
            ],
        }
    )

    result = prepare_dim_date(source)

    assert str(result.iloc[0]["date"]) == "2026-08-01"


def test_prepare_fact_preserves_missing_value() -> None:
    """Unpublished observations must remain NULL, not become zero."""

    source = pd.DataFrame(
        {
            "fact_id": [
                1,
            ],
            "date_key": [
                20260801,
            ],
            "location_key": [
                123,
            ],
            "metric_key": [
                1,
            ],
            "value": [
                None,
            ],
            "is_published": [
                False,
            ],
            "source_id": [
                1,
            ],
            "loaded_at": [
                pd.Timestamp("2026-09-30T12:00:00Z"),
            ],
        }
    )

    result = prepare_fact_cost_metric(source)

    assert pd.isna(result.iloc[0]["value"])

    assert not bool(result.iloc[0]["is_published"])
