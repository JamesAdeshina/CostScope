"""
Unit tests for ONS CPI Silver transformation.
"""

import pandas as pd

from data_pipeline.transform.ons.inflation import (
    build_silver_inflation,
    parse_monthly_series,
)


def sample_payload(
    series_id: str,
    value: str,
) -> dict[str, object]:
    """Create a representative ONS time-series payload."""

    return {
        "description": {
            "cdid": series_id,
        },
        "months": [
            {
                "date": "2026 AUG",
                "value": value,
                "year": "2026",
                "month": "August",
                "updateDate": ("2026-09-15T23:00:00.000Z"),
            }
        ],
    }


def test_parse_monthly_cpi_series() -> None:
    """ONS month records should become dated numeric observations."""

    result = parse_monthly_series(
        sample_payload(
            "D7G7",
            "3.1",
        ),
        value_column="cpi_annual_rate",
        series_id="D7G7",
    )

    assert len(result) == 1

    assert result.iloc[0]["reference_period"] == pd.Timestamp("2026-08-01")

    assert result.iloc[0]["cpi_annual_rate"] == 3.1


def test_parse_monthly_series_rejects_wrong_cdid() -> None:
    """A mismatched ONS series identifier must be rejected."""

    payload = sample_payload(
        "WRONG",
        "3.1",
    )

    try:
        parse_monthly_series(
            payload,
            value_column=("cpi_annual_rate"),
            series_id="D7G7",
        )

    except ValueError:
        pass

    else:
        raise AssertionError("Expected ValueError for mismatched CDID.")


def test_build_silver_uses_uk_geography(
    monkeypatch,
) -> None:
    """Inflation must remain explicitly UK-level."""

    series = {
        "annual_rate": pd.DataFrame(
            {
                "reference_period": [pd.Timestamp("2026-08-01")],
                "cpi_annual_rate": [3.1],
                "cpi_annual_rate_updated_at": [None],
            }
        ),
        "monthly_rate": pd.DataFrame(
            {
                "reference_period": [pd.Timestamp("2026-08-01")],
                "cpi_monthly_rate": [0.5],
                "cpi_monthly_rate_updated_at": [None],
            }
        ),
        "index": pd.DataFrame(
            {
                "reference_period": [pd.Timestamp("2026-08-01")],
                "cpi_index": [143.6],
                "cpi_index_updated_at": [None],
            }
        ),
    }

    monkeypatch.setattr(
        "data_pipeline.transform.ons.inflation.load_bronze_series",
        lambda run_directory=None: series,
    )

    result = build_silver_inflation()

    assert result.iloc[0]["location_id"] == "K02000001"

    assert result.iloc[0]["location_name"] == "United Kingdom"
