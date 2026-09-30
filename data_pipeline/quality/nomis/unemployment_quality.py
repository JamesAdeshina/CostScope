"""
Silver data-quality checks for model-based unemployment.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from data_pipeline.utils.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class UnemploymentQualityCheck:
    """Result of one unemployment quality check."""

    check_name: str
    status: str
    details: str


def validate_unemployment_silver(
    dataframe: pd.DataFrame,
) -> list[UnemploymentQualityCheck]:
    """Validate CostScope Silver unemployment data."""

    checks: list[UnemploymentQualityCheck] = []

    required = {
        "reference_period",
        "location_id",
        "location_name",
        "unemployment_rate",
    }

    missing = required - set(dataframe.columns)

    checks.append(
        UnemploymentQualityCheck(
            check_name="required_columns",
            status=("PASS" if not missing else "FAIL"),
            details=(
                "All required columns are present."
                if not missing
                else (f"Missing columns: {sorted(missing)}")
            ),
        )
    )

    duplicates = int(
        dataframe.duplicated(
            subset=[
                "reference_period",
                "location_id",
            ],
            keep=False,
        ).sum()
    )

    checks.append(
        UnemploymentQualityCheck(
            check_name="observation_uniqueness",
            status=("PASS" if duplicates == 0 else "FAIL"),
            details=(f"{duplicates:,} rows participate in duplicate observations."),
        )
    )

    published = dataframe["unemployment_rate"].dropna()

    invalid = int(((published < 0) | (published > 100)).sum())

    checks.append(
        UnemploymentQualityCheck(
            check_name="rate_validity",
            status=("PASS" if invalid == 0 else "FAIL"),
            details=(f"{invalid:,} unemployment rates fall outside 0-100%."),
        )
    )

    derby = dataframe.loc[dataframe["location_id"] == "E06000015"]

    checks.append(
        UnemploymentQualityCheck(
            check_name="derby_geography",
            status=("PASS" if len(derby) == 1 else "FAIL"),
            details=(f"Derby E06000015 exists {len(derby)} time(s)."),
        )
    )

    missing_values = int(dataframe["unemployment_rate"].isna().sum())

    checks.append(
        UnemploymentQualityCheck(
            check_name="published_rate_availability",
            status=("PASS" if missing_values == 0 else "WARN"),
            details=(
                f"{missing_values:,} geographies have no published unemployment rate."
            ),
        )
    )

    for check in checks:
        logger.info(
            "%-32s %-5s %s",
            check.check_name,
            check.status,
            check.details,
        )

    failures = [check for check in checks if check.status == "FAIL"]

    if failures:
        names = ", ".join(check.check_name for check in failures)

        raise ValueError(f"Critical unemployment Silver checks failed: {names}")

    return checks
