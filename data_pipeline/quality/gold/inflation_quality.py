"""
Gold-layer quality checks for CostScope CPI inflation data.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from data_pipeline.utils.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class InflationGoldCheck:
    """Result of one inflation Gold quality check."""

    check_name: str
    status: str
    details: str


def validate_inflation_gold(
    tables: dict[
        str,
        pd.DataFrame,
    ],
) -> list[InflationGoldCheck]:
    """Validate CPI integration into CostScope Gold."""

    locations = tables["dim_location"]

    dates = tables["dim_date"]

    metrics = tables["dim_metric"]

    facts = tables["fact_cost_metric"]

    checks: list[InflationGoldCheck] = []

    required_metrics = {
        "CPI_ANNUAL_RATE",
        "CPI_MONTHLY_RATE",
        "CPI_INDEX",
    }

    present_metrics = set(metrics["metric_code"].astype(str))

    missing_metrics = required_metrics - present_metrics

    checks.append(
        InflationGoldCheck(
            check_name="inflation_metrics_present",
            status=("PASS" if not missing_metrics else "FAIL"),
            details=(
                "All inflation metrics are present."
                if not missing_metrics
                else (f"Missing inflation metrics: {sorted(missing_metrics)}")
            ),
        )
    )

    uk_rows = locations.loc[locations["location_id"] == "K02000001"]

    checks.append(
        InflationGoldCheck(
            check_name="uk_location_unique",
            status=("PASS" if len(uk_rows) == 1 else "FAIL"),
            details=(f"United Kingdom K02000001 exists {len(uk_rows)} time(s)."),
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
        InflationGoldCheck(
            check_name="fact_grain_unique",
            status=("PASS" if duplicates == 0 else "FAIL"),
            details=(f"{duplicates:,} rows participate in duplicate Gold fact grains."),
        )
    )

    valid_locations = set(locations["location_key"])

    invalid_location_fk = int((~facts["location_key"].isin(valid_locations)).sum())

    checks.append(
        InflationGoldCheck(
            check_name="location_fk_integrity",
            status=("PASS" if invalid_location_fk == 0 else "FAIL"),
            details=(f"{invalid_location_fk:,} fact rows have invalid location keys."),
        )
    )

    valid_dates = set(dates["date_key"])

    invalid_date_fk = int((~facts["date_key"].isin(valid_dates)).sum())

    checks.append(
        InflationGoldCheck(
            check_name="date_fk_integrity",
            status=("PASS" if invalid_date_fk == 0 else "FAIL"),
            details=(f"{invalid_date_fk:,} fact rows have invalid date keys."),
        )
    )

    valid_metrics = set(metrics["metric_key"])

    invalid_metric_fk = int((~facts["metric_key"].isin(valid_metrics)).sum())

    checks.append(
        InflationGoldCheck(
            check_name="metric_fk_integrity",
            status=("PASS" if invalid_metric_fk == 0 else "FAIL"),
            details=(f"{invalid_metric_fk:,} fact rows have invalid metric keys."),
        )
    )

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

        raise ValueError(f"Critical inflation Gold checks failed: {names}")

    return checks
