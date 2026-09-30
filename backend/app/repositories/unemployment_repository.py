"""
Repository functions for CostScope unemployment data.
"""

from __future__ import annotations

import pandas as pd

from backend.app.repositories.private_rent_repository import (
    find_location,
    load_gold_tables,
)


def get_latest_unemployment_overview(
    location_code: str,
) -> dict[str, object] | None:
    """Return latest model-based unemployment for a location."""

    tables = load_gold_tables()

    location = find_location(location_code)

    metrics = tables["dim_metric"]

    facts = tables["fact_cost_metric"]

    dates = tables["dim_date"]

    metric = metrics.loc[metrics["metric_code"] == "UNEMPLOYMENT_RATE"]

    if metric.empty:
        return None

    metric_key = int(metric.iloc[0]["metric_key"])

    rows = facts.loc[
        (facts["location_key"] == int(location["location_key"]))
        & (facts["metric_key"] == metric_key)
        & (facts["is_published"])
    ].copy()

    if rows.empty:
        return None

    rows = rows.merge(
        dates[
            [
                "date_key",
                "date",
            ]
        ],
        on="date_key",
        how="left",
        validate="many_to_one",
    )

    latest = rows.sort_values(
        "date",
        ascending=False,
    ).iloc[0]

    return {
        "rate_percent": float(latest["value"]),
        "unit": "percent",
        "reference_period": (pd.Timestamp(latest["date"]).date()),
        "geography_name": str(location["location_name"]),
        "geography_code": str(location["location_id"]),
        "methodology": ("model-based"),
    }
