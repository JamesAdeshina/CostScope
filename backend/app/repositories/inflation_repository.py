"""
Repository functions for CostScope inflation metrics.

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
from backend.app.repositories.private_rent_repository import (
    GoldDataNotBuiltError,
    load_gold_tables,
)

UK_LOCATION_ID = "K02000001"


def _get_parquet_inflation_overview() -> dict[str, object] | None:
    """Return CPI overview from Gold Parquet."""

    tables = load_gold_tables()

    locations = tables["dim_location"]
    dates = tables["dim_date"]
    metrics = tables["dim_metric"]
    facts = tables["fact_cost_metric"]

    uk = locations.loc[locations["location_id"] == UK_LOCATION_ID]

    if uk.empty:
        return None

    location_key = int(uk.iloc[0]["location_key"])

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
        (joined["metric_code"] == "CPI_ANNUAL_RATE") & joined["is_published"]
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
            (same_period["metric_code"] == metric_code) & same_period["is_published"]
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


def get_latest_inflation_overview() -> dict[str, object] | None:
    """
    Return latest published UK CPI headline measures.

    CPI remains explicitly attached to United Kingdom geography even
    when displayed alongside local CostScope metrics.
    """

    if not database_configured():
        return _get_parquet_inflation_overview()

    try:
        with get_engine().connect() as connection:
            rows = (
                connection.execute(
                    text(
                        """
                    SELECT
                        metric_code,
                        value,
                        reference_period

                    FROM costscope.vw_cost_metrics

                    WHERE
                        location_id = :location_id
                        AND metric_code IN (
                            'CPI_ANNUAL_RATE',
                            'CPI_MONTHLY_RATE',
                            'CPI_INDEX'
                        )
                        AND is_published = TRUE

                    ORDER BY reference_period DESC
                    """
                    ),
                    {
                        "location_id": (UK_LOCATION_ID),
                    },
                )
                .mappings()
                .all()
            )

    except SQLAlchemyError as exc:
        raise GoldDataNotBuiltError(
            "CostScope PostgreSQL serving warehouse is unavailable."
        ) from exc

    annual_rows = [row for row in rows if row["metric_code"] == "CPI_ANNUAL_RATE"]

    if not annual_rows:
        return None

    latest_annual = annual_rows[0]

    reference_period = latest_annual["reference_period"]

    period_rows = {
        str(row["metric_code"]): row
        for row in rows
        if row["reference_period"] == reference_period
    }

    def metric_value(
        metric_code: str,
    ) -> float | None:
        row = period_rows.get(metric_code)

        if row is None or row["value"] is None:
            return None

        return float(row["value"])

    return {
        "annual_rate_percent": float(latest_annual["value"]),
        "monthly_rate_percent": (metric_value("CPI_MONTHLY_RATE")),
        "index_value": metric_value("CPI_INDEX"),
        "index_base": "2015=100",
        "reference_period": (reference_period),
        "geography_name": ("United Kingdom"),
        "geography_code": (UK_LOCATION_ID),
    }
