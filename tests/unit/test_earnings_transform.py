"""
Unit tests for the ONS ASHE Silver transformation.
"""

import pandas as pd

from data_pipeline.transform.ons.earnings import (
    clean_numeric_series,
    normalise_column_name,
    standardise_earnings,
)


def test_normalise_earnings_column_name() -> None:
    """ASHE headings should become snake_case."""

    assert (
        normalise_column_name("Annual percentage change") == "annual_percentage_change"
    )


def test_suppression_markers_become_missing() -> None:
    """ONS suppression markers must never become zero."""

    series = pd.Series(
        [
            "36428",
            "x",
            "..",
            ":",
            "-",
        ]
    )

    result = clean_numeric_series(series)

    assert result.iloc[0] == 36428
    assert result.iloc[1:].isna().all()


def test_standardise_earnings_keeps_derby() -> None:
    """The transformer should retain Derby and its official GSS code."""

    source = pd.DataFrame(
        {
            "Description": [
                "Derby UA",
            ],
            "Code": [
                "E06000015",
            ],
            "(thousand)": [
                65,
            ],
            "Median": [
                36428,
            ],
            "change": [
                4.1,
            ],
            "Mean": [
                41621,
            ],
            "change.1": [
                2.8,
            ],
        }
    )

    result = standardise_earnings(source)

    assert len(result) == 1

    derby = result.iloc[0]

    assert derby["area_code"] == "E06000015"

    assert derby["area_name"] == "Derby UA"

    assert derby["median_annual_pay"] == 36428


def test_standardise_earnings_filters_non_geography_rows() -> None:
    """Notes and footer rows should not enter Silver."""

    source = pd.DataFrame(
        {
            "Description": [
                "Derby UA",
                "Source note",
            ],
            "Code": [
                "E06000015",
                "Notes",
            ],
            "(thousand)": [
                65,
                None,
            ],
            "Median": [
                36428,
                None,
            ],
            "change": [
                4.1,
                None,
            ],
            "Mean": [
                41621,
                None,
            ],
            "change.1": [
                2.8,
                None,
            ],
        }
    )

    result = standardise_earnings(source)

    assert len(result) == 1

    assert result.iloc[0]["area_code"] == "E06000015"
