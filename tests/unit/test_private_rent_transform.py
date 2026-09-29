"""
Unit tests for ONS Private Rent Silver transformation.
"""

import pandas as pd

from data_pipeline.transform.ons.private_rent import (
    convert_numeric_columns,
    create_location_id,
    normalise_column_name,
    parse_dates,
    standardise_columns,
    standardise_text_columns,
)


def test_normalise_column_name() -> None:
    """Source headings should become snake_case."""

    assert normalise_column_name("Rental price one bed") == "rental_price_one_bed"


def test_standardise_columns() -> None:
    """Dataframe headings should be standardised."""

    dataframe = pd.DataFrame(
        columns=[
            "Time period",
            "Area code",
            "Rental price",
        ]
    )

    result = standardise_columns(dataframe)

    assert list(result.columns) == [
        "time_period",
        "area_code",
        "rental_price",
    ]


def test_parse_dates() -> None:
    """Valid source dates should become datetime values."""

    dataframe = pd.DataFrame({"time_period": ["2026-08-01"]})

    result = parse_dates(dataframe)

    assert pd.api.types.is_datetime64_any_dtype(result["time_period"])


def test_ons_markers_become_missing_numeric_values() -> None:
    """ONS statistical markers must never become zero."""

    dataframe = pd.DataFrame(
        {
            "time_period": [
                "2026-01-01",
                "2026-02-01",
            ],
            "area_code": [
                "TEST1",
                "TEST1",
            ],
            "area_name": [
                "Test Area",
                "Test Area",
            ],
            "region_or_country_name": [
                "Test Region",
                "Test Region",
            ],
            "rental_price": [
                1000,
                "[x]",
            ],
        }
    )

    result = convert_numeric_columns(dataframe)

    assert (
        result.loc[
            0,
            "rental_price",
        ]
        == 1000
    )

    assert pd.isna(
        result.loc[
            1,
            "rental_price",
        ]
    )


def test_geography_marker_becomes_missing() -> None:
    """ONS [z] geography markers should not be treated as codes."""

    dataframe = pd.DataFrame(
        {
            "area_code": [
                "[z]",
            ],
            "area_name": [
                "Belfast BRMA",
            ],
            "region_or_country_name": [
                "Northern Ireland",
            ],
        }
    )

    result = standardise_text_columns(dataframe)

    assert pd.isna(
        result.loc[
            0,
            "area_code",
        ]
    )


def test_location_id_uses_official_area_code() -> None:
    """Official geography codes should be preferred."""

    dataframe = pd.DataFrame(
        {
            "area_code": [
                "E06000015",
            ],
            "area_name": [
                "Derby",
            ],
            "region_or_country_name": [
                "East Midlands",
            ],
        }
    )

    result = create_location_id(dataframe)

    assert (
        result.loc[
            0,
            "location_id",
        ]
        == "E06000015"
    )


def test_location_id_falls_back_to_geography_name() -> None:
    """Uncoded source geographies should receive an internal ID."""

    dataframe = pd.DataFrame(
        {
            "area_code": [
                pd.NA,
            ],
            "area_name": [
                "Belfast BRMA",
            ],
            "region_or_country_name": [
                "Northern Ireland",
            ],
        }
    )

    result = create_location_id(dataframe)

    assert (
        result.loc[
            0,
            "location_id",
        ]
        == "name:Northern Ireland:Belfast BRMA"
    )
