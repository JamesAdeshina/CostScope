"""
Silver-layer data-quality checks for ONS CPI inflation data.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from data_pipeline.utils.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class InflationQualityCheck:
    """Result of one CPI Silver quality check."""

    check_name: str
    status: str
    details: str


REQUIRED_COLUMNS = {
    "reference_period",
    "location_id",
    "location_name",
    "cpi_annual_rate",
    "cpi_monthly_rate",
    "cpi_index",
}


def validate_inflation_silver(
    dataframe: pd.DataFrame,
) -> list[InflationQualityCheck]:
    """Run CostScope Silver CPI quality checks."""

    checks: list[InflationQualityCheck] = []

    missing_columns = REQUIRED_COLUMNS - set(dataframe.columns)

    checks.append(
        InflationQualityCheck(
            check_name="required_columns",
            status=("PASS" if not missing_columns else "FAIL"),
            details=(
                "All required columns are present."
                if not missing_columns
                else (f"Missing columns: {sorted(missing_columns)}")
            ),
        )
    )

    duplicate_periods = int(
        dataframe.duplicated(
            subset=[
                "reference_period",
                "location_id",
            ],
            keep=False,
        ).sum()
    )

    checks.append(
        InflationQualityCheck(
            check_name="observation_uniqueness",
            status=("PASS" if duplicate_periods == 0 else "FAIL"),
            details=(
                f"{duplicate_periods:,} rows participate "
                "in duplicate monthly observations."
            ),
        )
    )

    invalid_locations = int((dataframe["location_id"] != "K02000001").sum())

    checks.append(
        InflationQualityCheck(
            check_name="uk_geography",
            status=("PASS" if invalid_locations == 0 else "FAIL"),
            details=(
                f"{invalid_locations:,} rows do not use "
                "United Kingdom geography K02000001."
            ),
        )
    )

    published_index = dataframe["cpi_index"].dropna()

    invalid_index = int((published_index <= 0).sum())

    checks.append(
        InflationQualityCheck(
            check_name="cpi_index_validity",
            status=("PASS" if invalid_index == 0 else "FAIL"),
            details=(
                f"{invalid_index:,} published CPI index values are zero or negative."
            ),
        )
    )

    latest = dataframe.sort_values("reference_period").iloc[-1]

    latest_complete = all(
        pd.notna(latest[column])
        for column in (
            "cpi_annual_rate",
            "cpi_monthly_rate",
            "cpi_index",
        )
    )

    checks.append(
        InflationQualityCheck(
            check_name="latest_period_completeness",
            status=("PASS" if latest_complete else "WARN"),
            details=(
                "Latest period "
                f"{latest['reference_period'].date()} "
                "contains all three headline CPI measures."
                if latest_complete
                else (
                    "Latest CPI period contains one or more "
                    "unpublished headline measures."
                )
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

        raise ValueError(f"Critical CPI Silver quality checks failed: {names}")

    return checks
