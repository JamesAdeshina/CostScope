"""
Quality checks for CostScope Gold analytical tables.
"""

from __future__ import annotations

import pandas as pd

from data_pipeline.utils.logging_config import get_logger


logger = get_logger(__name__)


def validate_gold_tables(
    tables: dict[str, pd.DataFrame],
) -> None:
    """
    Validate Gold-table integrity.

    Raises
    ------
    ValueError
        If a critical dimensional-model constraint fails.
    """

    locations = tables[
        "dim_location"
    ]

    dates = tables[
        "dim_date"
    ]

    metrics = tables[
        "dim_metric"
    ]

    facts = tables[
        "fact_cost_metric"
    ]

    checks: dict[str, bool] = {
        "location_key_unique": (
            locations["location_key"].is_unique
        ),
        "location_id_unique": (
            locations["location_id"].is_unique
        ),
        "date_key_unique": (
            dates["date_key"].is_unique
        ),
        "metric_key_unique": (
            metrics["metric_key"].is_unique
        ),
        "metric_code_unique": (
            metrics["metric_code"].is_unique
        ),
        "fact_id_unique": (
            facts["fact_id"].is_unique
        ),
        "fact_grain_unique": (
            not facts.duplicated(
                subset=[
                    "date_key",
                    "location_key",
                    "metric_key",
                    "source_id",
                ]
            ).any()
        ),
        "location_fk_valid": (
            facts["location_key"]
            .isin(
                locations["location_key"]
            )
            .all()
        ),
        "date_fk_valid": (
            facts["date_key"]
            .isin(
                dates["date_key"]
            )
            .all()
        ),
        "metric_fk_valid": (
            facts["metric_key"]
            .isin(
                metrics["metric_key"]
            )
            .all()
        ),
    }

    failed = [
        name
        for name, passed in checks.items()
        if not passed
    ]

    for name, passed in checks.items():
        logger.info(
            "%-30s | %s",
            name,
            "PASS" if passed else "FAIL",
        )

    if failed:
        raise ValueError(
            "Gold quality checks failed: "
            + ", ".join(failed)
        )