"""
Gold quality checks for CostScope unemployment.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from data_pipeline.utils.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class UnemploymentGoldCheck:
    """Result of one Gold unemployment check."""

    check_name: str
    status: str
    details: str


def validate_unemployment_gold(
    tables: dict[
        str,
        pd.DataFrame,
    ],
) -> list[UnemploymentGoldCheck]:
    """Validate unemployment Gold integration."""

    locations = tables["dim_location"]

    dates = tables["dim_date"]

    metrics = tables["dim_metric"]

    facts = tables["fact_cost_metric"]

    checks: list[UnemploymentGoldCheck] = []

    metric_count = len(metrics.loc[metrics["metric_code"] == "UNEMPLOYMENT_RATE"])

    checks.append(
        UnemploymentGoldCheck(
            check_name="unemployment_metric_present",
            status=("PASS" if metric_count == 1 else "FAIL"),
            details=(f"UNEMPLOYMENT_RATE exists {metric_count} time(s)."),
        )
    )

    derby_count = len(locations.loc[locations["location_id"] == "E06000015"])

    checks.append(
        UnemploymentGoldCheck(
            check_name="derby_location_unique",
            status=("PASS" if derby_count == 1 else "FAIL"),
            details=(f"Derby exists {derby_count} time(s)."),
        )
    )

    duplicates = int(
        facts.duplicated(
            subset=[
                "date_key",
                "location_key",
                "metric_key",
                "source_id",
            ],
            keep=False,
        ).sum()
    )

    checks.append(
        UnemploymentGoldCheck(
            check_name="fact_grain_unique",
            status=("PASS" if duplicates == 0 else "FAIL"),
            details=(f"{duplicates:,} duplicate fact rows."),
        )
    )

    valid_locations = set(locations["location_key"])

    invalid_location_fk = int((~facts["location_key"].isin(valid_locations)).sum())

    checks.append(
        UnemploymentGoldCheck(
            check_name="location_fk_integrity",
            status=("PASS" if invalid_location_fk == 0 else "FAIL"),
            details=(f"{invalid_location_fk:,} invalid location foreign keys."),
        )
    )

    valid_dates = set(dates["date_key"])

    invalid_date_fk = int((~facts["date_key"].isin(valid_dates)).sum())

    checks.append(
        UnemploymentGoldCheck(
            check_name="date_fk_integrity",
            status=("PASS" if invalid_date_fk == 0 else "FAIL"),
            details=(f"{invalid_date_fk:,} invalid date foreign keys."),
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

        raise ValueError(f"Critical unemployment Gold checks failed: {names}")

    return checks
