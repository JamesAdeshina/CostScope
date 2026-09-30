"""
Unit tests for CostScope earnings Gold modelling.
"""

import pandas as pd

from data_pipeline.model.earnings_gold import (
    build_earnings_dim_location,
    build_earnings_dim_metric,
    build_earnings_fact,
)


def sample_earnings() -> pd.DataFrame:
    """Create a representative Silver earnings record."""

    return pd.DataFrame(
        {
            "reference_year": [
                2025,
            ],
            "reference_period": [
                pd.Timestamp("2025-04-05"),
            ],
            "area_code": [
                "E06000015",
            ],
            "area_name": [
                "Derby UA",
            ],
            "median_annual_pay": [
                36428.0,
            ],
            "median_annual_change_percent": [
                4.1,
            ],
        }
    )


def test_earnings_location_uses_official_code() -> None:
    """Earnings geography should use the published GSS code."""

    result = build_earnings_dim_location(sample_earnings())

    assert len(result) == 1

    assert result.iloc[0]["location_id"] == "E06000015"


def test_earnings_metrics_are_defined() -> None:
    """Gold should expose annual earnings and annual change."""

    metrics = build_earnings_dim_metric()

    assert set(metrics["metric_code"]) == {
        "EARNINGS_ANNUAL",
        "EARNINGS_ANNUAL_CHANGE",
    }


def test_earnings_fact_contains_two_metrics() -> None:
    """One ASHE row should produce two Gold metric observations."""

    facts = build_earnings_fact(sample_earnings())

    assert len(facts) == 2

    assert set(facts["metric_key"]) == {
        101,
        102,
    }


def test_earnings_fact_preserves_missing_value() -> None:
    """Suppressed earnings values must remain unpublished, not zero."""

    dataframe = sample_earnings()

    dataframe.loc[
        0,
        "median_annual_pay",
    ] = pd.NA

    facts = build_earnings_fact(dataframe)

    annual = facts.loc[facts["metric_key"] == 101].iloc[0]

    assert pd.isna(annual["value"])

    assert not bool(annual["is_published"])
