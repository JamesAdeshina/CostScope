"""
Gold-layer data-quality checks for CostScope earnings.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from data_pipeline.utils.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class GoldQualityCheck:
    """Result of one Gold-layer quality rule."""

    check_name: str
    status: str
    details: str


def validate_earnings_gold(
    tables: dict[
        str,
        pd.DataFrame,
    ],
) -> list[GoldQualityCheck]:
    """Validate earnings integration into CostScope Gold."""

    locations = tables["dim_location"]

    dates = tables["dim_date"]

    metrics = tables["dim_metric"]

    facts = tables["fact_cost_metric"]

    checks: list[GoldQualityCheck] = []

    earnings_metrics = {
        "EARNINGS_ANNUAL",
        "EARNINGS_ANNUAL_CHANGE",
    }

    present_metrics = set(metrics["metric_code"].astype(str))

    missing_metrics = earnings_metrics - present_metrics

    checks.append(
        GoldQualityCheck(
            check_name=("earnings_metrics_present"),
            status=("PASS" if not missing_metrics else "FAIL"),
            details=(
                "All earnings metrics are present."
                if not missing_metrics
                else (f"Missing earnings metrics: {sorted(missing_metrics)}")
            ),
        )
    )

    derby = locations.loc[locations["location_id"] == "E06000015"]

    checks.append(
        GoldQualityCheck(
            check_name=("derby_location_unique"),
            status=("PASS" if len(derby) == 1 else "FAIL"),
            details=(
                f"Derby exists exactly once in dim_location: {len(derby)} row(s)."
            ),
        )
    )

    duplicate_facts = int(
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
        GoldQualityCheck(
            check_name="fact_grain_unique",
            status=("PASS" if duplicate_facts == 0 else "FAIL"),
            details=(
                f"{duplicate_facts:,} rows participate in duplicate Gold fact grains."
            ),
        )
    )

    valid_location_keys = set(locations["location_key"])

    missing_location_fk = int((~facts["location_key"].isin(valid_location_keys)).sum())

    checks.append(
        GoldQualityCheck(
            check_name=("location_fk_integrity"),
            status=("PASS" if missing_location_fk == 0 else "FAIL"),
            details=(f"{missing_location_fk:,} fact rows have invalid location keys."),
        )
    )

    valid_date_keys = set(dates["date_key"])

    missing_date_fk = int((~facts["date_key"].isin(valid_date_keys)).sum())

    checks.append(
        GoldQualityCheck(
            check_name="date_fk_integrity",
            status=("PASS" if missing_date_fk == 0 else "FAIL"),
            details=(f"{missing_date_fk:,} fact rows have invalid date keys."),
        )
    )

    valid_metric_keys = set(metrics["metric_key"])

    missing_metric_fk = int((~facts["metric_key"].isin(valid_metric_keys)).sum())

    checks.append(
        GoldQualityCheck(
            check_name="metric_fk_integrity",
            status=("PASS" if missing_metric_fk == 0 else "FAIL"),
            details=(f"{missing_metric_fk:,} fact rows have invalid metric keys."),
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

        raise ValueError(f"Critical earnings Gold quality checks failed: {names}")

    return checks
