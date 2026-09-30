"""
Tests for unemployment Silver transformation.
"""

import pandas as pd

from data_pipeline.transform.nomis.unemployment import (
    parse_reference_period_end,
    resolve_location_id,
    standardise_unemployment,
)


def test_parse_unemployment_period() -> None:
    """Nomis annual period should map to its end date."""

    assert parse_reference_period_end("Apr 2025-Mar 2026") == pd.Timestamp("2026-03-31")


def test_resolve_derby_location() -> None:
    """Derby should resolve to its official GSS code."""

    assert resolve_location_id("Derby") == "E06000015"


def test_standardise_selects_model_rate() -> None:
    """Silver should retain only the model-based rate."""

    source = pd.DataFrame(
        {
            "GEOGRAPHY": [
                123,
                123,
            ],
            "GEOGRAPHY_NAME": [
                "Derby",
                "Derby",
            ],
            "ITEM": [
                1,
                2,
            ],
            "ITEM_NAME": [
                ("Unemployment count (model based)"),
                ("Unemployment rate (model based)"),
            ],
            "TIME": [
                202603,
                202603,
            ],
            "TIME_NAME": [
                "Apr 2025-Mar 2026",
                "Apr 2025-Mar 2026",
            ],
            "OBS_VALUE": [
                7700,
                5.8,
            ],
        }
    )

    result = standardise_unemployment(source)

    assert len(result) == 1

    assert result.iloc[0]["unemployment_rate"] == 5.8


def test_standardise_preserves_derby_code() -> None:
    """Derby should enter Silver with E06000015."""

    source = pd.DataFrame(
        {
            "GEOGRAPHY": [
                123,
            ],
            "GEOGRAPHY_NAME": [
                "Derby",
            ],
            "ITEM": [
                2,
            ],
            "ITEM_NAME": [
                ("Unemployment rate (model based)"),
            ],
            "TIME": [
                202603,
            ],
            "TIME_NAME": [
                "Apr 2025-Mar 2026",
            ],
            "OBS_VALUE": [
                5.8,
            ],
        }
    )

    result = standardise_unemployment(source)

    assert result.iloc[0]["location_id"] == "E06000015"
