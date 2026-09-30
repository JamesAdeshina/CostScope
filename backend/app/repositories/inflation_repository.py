"""
Repository functions for CostScope inflation metrics.
"""

from __future__ import annotations

import pandas as pd

from backend.app.repositories.private_rent_repository import (
    load_gold_tables,
)

UK_LOCATION_ID = "K02000001"


def get_latest_inflation_overview() -> (
    dict[
        str,
        object,
    ]
    | None
):
    """
    Return the latest published UK CPI headline measures.

    Inflation remains explicitly attached to United Kingdom geography,
    even when presented alongside a local-authority CostScope overview.
    """

    tables = load_gold_tables()

    locations = tables["dim_location"]

    dates = tables["dim_date"]

    metrics = tables["dim_metric"]

    facts = tables["fact_cost_metric"]

    uk = locations.loc[locations["location_id"] == UK_LOCATION_ID]

    if uk.empty:
        return None

    uk_row = uk.iloc[0]

    location_key = int(uk_row["location_key"])

    inflation_metrics = metrics.loc[
        metrics["metric_code"].isin(
            [
                "CPI_ANNUAL_RATE",
                "CPI_MONTHLY_RATE",
                "CPI_INDEX",
            ]
        )
    ][
        [
            "metric_key",
            "metric_code",
        ]
    ]

    if inflation_metrics.empty:
        return None

    joined = facts.loc[facts["location_key"] == location_key].merge(
        inflation_metrics,
        on="metric_key",
        how="inner",
    )

    joined = joined.merge(
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

    annual = joined.loc[
        (joined["metric_code"] == "CPI_ANNUAL_RATE") & (joined["is_published"])
    ].sort_values(
        "date",
        ascending=False,
    )

    if annual.empty:
        return None

    latest_annual = annual.iloc[0]

    reference_date = latest_annual["date"]

    same_period = joined.loc[joined["date"] == reference_date]

    def metric_value(
        metric_code: str,
    ) -> float | None:
        rows = same_period.loc[
            (same_period["metric_code"] == metric_code) & (same_period["is_published"])
        ]

        if rows.empty:
            return None

        return float(rows.iloc[0]["value"])

    return {
        "annual_rate_percent": float(latest_annual["value"]),
        "monthly_rate_percent": (metric_value("CPI_MONTHLY_RATE")),
        "index_value": metric_value("CPI_INDEX"),
        "index_base": "2015=100",
        "reference_period": (pd.Timestamp(reference_date).date()),
        "geography_name": ("United Kingdom"),
        "geography_code": (UK_LOCATION_ID),
    }
