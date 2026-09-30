"""
Unit tests for CostScope CPI Gold modelling.
"""

import pandas as pd

from data_pipeline.model.inflation_gold import (
    build_inflation_facts,
    build_inflation_location,
    build_inflation_metrics,
)


def sample_inflation() -> pd.DataFrame:
    """Return one representative CPI Silver row."""

    return pd.DataFrame(
        {
            "reference_period": [
                pd.Timestamp("2026-08-01"),
            ],
            "cpi_annual_rate": [
                3.1,
            ],
            "cpi_monthly_rate": [
                0.5,
            ],
            "cpi_index": [
                143.6,
            ],
        }
    )


def test_inflation_location_is_uk() -> None:
    """Inflation Gold geography must be the United Kingdom."""

    locations = build_inflation_location()

    assert locations.iloc[0]["location_id"] == "K02000001"


def test_inflation_metrics_are_defined() -> None:
    """Gold should expose all three configured CPI metrics."""

    metrics = build_inflation_metrics()

    assert set(metrics["metric_code"]) == {
        "CPI_ANNUAL_RATE",
        "CPI_MONTHLY_RATE",
        "CPI_INDEX",
    }


def test_inflation_fact_creates_three_metrics() -> None:
    """One monthly CPI record should create three Gold facts."""

    facts = build_inflation_facts(sample_inflation())

    assert len(facts) == 3

    assert set(facts["metric_key"]) == {
        201,
        202,
        203,
    }


def test_inflation_fact_preserves_values() -> None:
    """Headline CPI values should survive Gold modelling unchanged."""

    facts = build_inflation_facts(sample_inflation())

    annual = facts.loc[facts["metric_key"] == 201].iloc[0]

    monthly = facts.loc[facts["metric_key"] == 202].iloc[0]

    index = facts.loc[facts["metric_key"] == 203].iloc[0]

    assert annual["value"] == 3.1

    assert monthly["value"] == 0.5

    assert index["value"] == 143.6
