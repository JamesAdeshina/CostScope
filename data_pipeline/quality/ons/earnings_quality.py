"""
Data-quality checks for the CostScope ASHE earnings Silver dataset.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from data_pipeline.utils.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class QualityCheck:
    """Result of one Silver earnings quality rule."""

    check_name: str
    status: str
    details: str


REQUIRED_COLUMNS = {
    "reference_year",
    "reference_period",
    "area_code",
    "area_name",
    "median_annual_pay",
    "median_annual_change_percent",
    "unit",
}


def check_required_columns(
    dataframe: pd.DataFrame,
) -> QualityCheck:
    """Verify required analytical columns exist."""

    missing = REQUIRED_COLUMNS - set(dataframe.columns)

    if missing:
        return QualityCheck(
            check_name="required_columns",
            status="FAIL",
            details=(f"Missing columns: {sorted(missing)}"),
        )

    return QualityCheck(
        check_name="required_columns",
        status="PASS",
        details="All required columns are present.",
    )


def check_area_code_completeness(
    dataframe: pd.DataFrame,
) -> QualityCheck:
    """Verify every Silver row has a geography code."""

    missing = int(dataframe["area_code"].isna().sum())

    status = "PASS" if missing == 0 else "FAIL"

    return QualityCheck(
        check_name="area_code_completeness",
        status=status,
        details=(f"{missing:,} rows have missing area codes."),
    )


def check_unique_geography(
    dataframe: pd.DataFrame,
) -> QualityCheck:
    """Verify one row per geography in the release."""

    duplicate_count = int(
        dataframe.duplicated(
            subset=[
                "reference_year",
                "area_code",
            ],
            keep=False,
        ).sum()
    )

    status = "PASS" if duplicate_count == 0 else "FAIL"

    return QualityCheck(
        check_name="observation_uniqueness",
        status=status,
        details=(
            f"{duplicate_count:,} rows participate in duplicate observation keys."
        ),
    )


def check_median_pay_availability(
    dataframe: pd.DataFrame,
) -> QualityCheck:
    """
    Report missing published median-pay values.

    Missing values may be legitimate where ONS suppresses unreliable or
    disclosive estimates, so this is a warning rather than a failure.
    """

    missing = int(dataframe["median_annual_pay"].isna().sum())

    status = "PASS" if missing == 0 else "WARN"

    return QualityCheck(
        check_name="median_pay_availability",
        status=status,
        details=(f"{missing:,} geographies have no published median annual pay."),
    )


def check_positive_median_pay(
    dataframe: pd.DataFrame,
) -> QualityCheck:
    """Verify published median-pay observations are positive."""

    published = dataframe["median_annual_pay"].dropna()

    invalid = int((published <= 0).sum())

    status = "PASS" if invalid == 0 else "FAIL"

    return QualityCheck(
        check_name="median_pay_validity",
        status=status,
        details=(f"{invalid:,} published median-pay values are zero or negative."),
    )


def check_derby_record(
    dataframe: pd.DataFrame,
) -> QualityCheck:
    """
    Confirm the expected Derby geography exists.

    This checks identity only. It deliberately does not hardcode the
    published earnings value into production validation.
    """

    derby = dataframe.loc[dataframe["area_code"] == "E06000015"]

    if len(derby) != 1:
        return QualityCheck(
            check_name="derby_geography",
            status="FAIL",
            details=(
                f"Expected exactly one Derby E06000015 record, found {len(derby)}."
            ),
        )

    return QualityCheck(
        check_name="derby_geography",
        status="PASS",
        details=("Derby E06000015 is present."),
    )


def validate_earnings_silver(
    dataframe: pd.DataFrame,
) -> list[QualityCheck]:
    """
    Execute ASHE Silver quality rules.

    Raises
    ------
    ValueError
        If any critical check fails.
    """

    checks = [
        check_required_columns(dataframe),
        check_area_code_completeness(dataframe),
        check_unique_geography(dataframe),
        check_median_pay_availability(dataframe),
        check_positive_median_pay(dataframe),
        check_derby_record(dataframe),
    ]

    logger.info("ASHE Silver data-quality results")

    for check in checks:
        logger.info(
            "%-30s %-5s %s",
            check.check_name,
            check.status,
            check.details,
        )

    failures = [check for check in checks if check.status == "FAIL"]

    if failures:
        names = ", ".join(check.check_name for check in failures)

        raise ValueError(f"Critical ASHE Silver data-quality checks failed: {names}")

    return checks
