"""
Tests for CostScope unemployment Gold modelling.
"""

import pandas as pd

from data_pipeline.model.unemployment_gold import (
    build_unemployment_facts,
    build_unemployment_metric,
)


def sample_unemployment() -> pd.DataFrame:
    """Create one representative unemployment observation."""

    return pd.DataFrame(
        {
            "reference_period": [
                pd.Timestamp("2026-03-31"),
            ],
            "location_id": [
                "E06000015",
            ],
            "location_name": [
                "Derby",
            ],
            "unemployment_rate": [
                5.8,
            ],
        }
    )


def test_unemployment_metric_definition() -> None:
    """Gold metric code should be stable."""

    metric = build_unemployment_metric()

    assert metric.iloc[0]["metric_code"] == "UNEMPLOYMENT_RATE"


def test_unemployment_fact_preserves_rate() -> None:
    """Gold should preserve the unemployment percentage."""

    facts = build_unemployment_facts(sample_unemployment())

    assert len(facts) == 1

    assert facts.iloc[0]["value"] == 5.8


def test_unemployment_fact_metric_key() -> None:
    """Unemployment should use metric key 301."""

    facts = build_unemployment_facts(sample_unemployment())

    assert facts.iloc[0]["metric_key"] == 301
