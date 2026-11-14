"""
Repository functions for CostScope unemployment data.

PostgreSQL is used when configured.
Gold Parquet remains the development fallback.
"""

from __future__ import annotations

import pandas as pd
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from backend.app.core.database import (
    database_configured,
    get_engine,
)
from backend.app.repositories.database_repository import (
    find_location,
)
from backend.app.repositories.private_rent_repository import (
    GoldDataNotBuiltError,
    load_gold_tables,
)


def _get_parquet_unemployment_overview(
    location_code: str,
) -> dict[str, object] | None:
    """Return unemployment from Gold Parquet."""

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
        & facts["is_published"]
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


def get_latest_unemployment_overview(
    location_code: str,
) -> dict[str, object] | None:
    """Return latest model-based unemployment for one location."""

    if not database_configured():
        return _get_parquet_unemployment_overview(location_code)

    location = find_location(location_code)

    try:
        with get_engine().connect() as connection:
            row = (
                connection.execute(
                    text(
                        """
                    SELECT
                        value,
                        unit,
                        reference_period

                    FROM costscope.vw_cost_metrics

                    WHERE
                        location_key = :location_key
                        AND metric_code = 'UNEMPLOYMENT_RATE'
                        AND is_published = TRUE

                    ORDER BY reference_period DESC

                    LIMIT 1
                    """
                    ),
                    {
                        "location_key": int(location["location_key"]),
                    },
                )
                .mappings()
                .first()
            )

    except SQLAlchemyError as exc:
        raise GoldDataNotBuiltError(
            "CostScope PostgreSQL serving warehouse is unavailable."
        ) from exc

    if row is None:
        return None

    return {
        "rate_percent": float(row["value"]),
        "unit": str(row["unit"]),
        "reference_period": (row["reference_period"]),
        "geography_name": str(location["location_name"]),
        "geography_code": str(location["location_id"]),
        "methodology": ("model-based"),
    }
