"""
Data-quality checks for the ONS Private Rent Silver dataset.

Quality dimensions:

- required schema
- geography identity completeness
- observation-key completeness
- observation uniqueness
- reporting-period validity
- headline rent availability

Missing published statistics are warnings rather than automatically
being treated as pipeline failures.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from data_pipeline.utils.logging_config import get_logger

logger = get_logger(__name__)


REQUIRED_COLUMNS = {
    "time_period",
    "location_id",
    "area_code",
    "area_name",
    "region_or_country_name",
    "index",
    "monthly_change",
    "annual_change",
    "rental_price",
}


OBSERVATION_KEY = [
    "time_period",
    "location_id",
]


@dataclass
class QualityCheckResult:
    """Result from one data-quality check."""

    check_name: str
    status: str
    failed_records: int
    message: str


def check_required_columns(
    dataframe: pd.DataFrame,
) -> QualityCheckResult:
    """Verify the required Silver schema."""

    missing = REQUIRED_COLUMNS.difference(dataframe.columns)

    if missing:
        return QualityCheckResult(
            check_name="required_columns",
            status="FAIL",
            failed_records=len(missing),
            message=("Missing required columns: " + ", ".join(sorted(missing))),
        )

    return QualityCheckResult(
        check_name="required_columns",
        status="PASS",
        failed_records=0,
        message="All required columns are present.",
    )


def check_location_id_completeness(
    dataframe: pd.DataFrame,
) -> QualityCheckResult:
    """Verify every observation has a CostScope geography identifier."""

    failures = int(dataframe["location_id"].isna().sum())

    return QualityCheckResult(
        check_name="location_id_completeness",
        status="PASS" if failures == 0 else "FAIL",
        failed_records=failures,
        message=(
            "Every observation has a location identifier."
            if failures == 0
            else (f"{failures} observations have no location identifier.")
        ),
    )


def check_key_completeness(
    dataframe: pd.DataFrame,
) -> QualityCheckResult:
    """Verify observation-key fields are populated."""

    failure_mask = dataframe[OBSERVATION_KEY].isna().any(axis=1)

    failures = int(failure_mask.sum())

    return QualityCheckResult(
        check_name="key_completeness",
        status="PASS" if failures == 0 else "FAIL",
        failed_records=failures,
        message=(
            "No missing observation keys."
            if failures == 0
            else (f"{failures} rows contain missing observation-key values.")
        ),
    )


def check_observation_uniqueness(
    dataframe: pd.DataFrame,
) -> QualityCheckResult:
    """
    Verify one record exists per location and reporting period.

    CostScope uses ``location_id`` rather than raw ``area_code`` because
    the ONS source does not provide area codes for every geography.
    """

    duplicate_mask = dataframe.duplicated(
        subset=OBSERVATION_KEY,
        keep=False,
    )

    failures = int(duplicate_mask.sum())

    return QualityCheckResult(
        check_name="observation_uniqueness",
        status="PASS" if failures == 0 else "FAIL",
        failed_records=failures,
        message=(
            "Location-period observations are unique."
            if failures == 0
            else (f"{failures} rows belong to duplicated location-period observations.")
        ),
    )


def check_time_period_validity(
    dataframe: pd.DataFrame,
) -> QualityCheckResult:
    """Verify source reporting periods parsed successfully."""

    failures = int(dataframe["time_period"].isna().sum())

    return QualityCheckResult(
        check_name="time_period_validity",
        status="PASS" if failures == 0 else "FAIL",
        failed_records=failures,
        message=(
            "All time periods parsed successfully."
            if failures == 0
            else (f"{failures} invalid time periods found.")
        ),
    )


def check_rental_price_availability(
    dataframe: pd.DataFrame,
) -> QualityCheckResult:
    """
    Report missing headline rental prices.

    A missing source statistic is retained as missing and never converted
    to zero or estimated by CostScope.
    """

    failures = int(dataframe["rental_price"].isna().sum())

    return QualityCheckResult(
        check_name="rental_price_availability",
        status="PASS" if failures == 0 else "WARN",
        failed_records=failures,
        message=(
            "All observations contain rental prices."
            if failures == 0
            else (f"{failures} observations have no published headline rental price.")
        ),
    )


def run_private_rent_quality_checks(
    dataframe: pd.DataFrame,
) -> list[QualityCheckResult]:
    """Run all ONS Private Rent Silver checks."""

    logger.info("=" * 70)
    logger.info("Running ONS Private Rent data-quality checks")
    logger.info("=" * 70)

    checks = [
        check_required_columns,
        check_location_id_completeness,
        check_key_completeness,
        check_observation_uniqueness,
        check_time_period_validity,
        check_rental_price_availability,
    ]

    results = [check(dataframe) for check in checks]

    for result in results:
        logger.info(
            "%-30s | %-4s | failed=%s | %s",
            result.check_name,
            result.status,
            result.failed_records,
            result.message,
        )

    return results


def assert_no_critical_failures(
    results: list[QualityCheckResult],
) -> None:
    """Stop the pipeline if any FAIL-level quality checks exist."""

    failures = [result for result in results if result.status == "FAIL"]

    if not failures:
        return

    failed_names = ", ".join(result.check_name for result in failures)

    raise ValueError(f"Critical data-quality checks failed: {failed_names}")
