"""
Build CostScope Gold earnings structures from ONS ASHE Silver data.

The earnings Gold build extends the existing CostScope dimensional model
rather than creating a separate warehouse.

Source
------
ONS Annual Survey of Hours and Earnings (ASHE)
Table 8.7a - Annual pay - Gross
Full-Time employees
Place of residence

Metrics
-------
EARNINGS_ANNUAL
    Median annual gross pay for full-time employee jobs.

EARNINGS_ANNUAL_CHANGE
    Annual percentage change in median annual gross pay.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

from data_pipeline.config.settings import settings
from data_pipeline.model.private_rent_gold import (
    stable_integer_key,
)
from data_pipeline.transform.ons.earnings import (
    get_silver_earnings_path,
)
from data_pipeline.utils.logging_config import get_logger

logger = get_logger(__name__)


SOURCE_ID = 2
SOURCE_CODE = "ONS_ASHE"

GOLD_DIRECTORY = settings.gold_path / "cost_scope"

METRIC_DEFINITIONS = [
    {
        "metric_key": 101,
        "metric_code": "EARNINGS_ANNUAL",
        "metric_name": "Median annual gross pay",
        "unit": "GBP/year",
        "category": "earnings",
    },
    {
        "metric_key": 102,
        "metric_code": "EARNINGS_ANNUAL_CHANGE",
        "metric_name": ("Annual change in median annual gross pay"),
        "unit": "percent",
        "category": "earnings",
    },
]


def load_silver_earnings(
    path: Path | None = None,
) -> pd.DataFrame:
    """Load the CostScope Silver ASHE earnings dataset."""

    if path is None:
        path = get_silver_earnings_path()

    if not path.exists():
        raise FileNotFoundError(
            "Silver earnings dataset not found: "
            f"{path}. Run "
            "`python -m scripts.build_earnings_silver` first."
        )

    dataframe = pd.read_parquet(path)

    logger.info(
        "Loaded Silver earnings: %s rows",
        f"{len(dataframe):,}",
    )

    return dataframe


def build_earnings_dim_location(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Build location-dimension rows required by earnings.

    Stable keys use the same algorithm as the rent Gold pipeline, so
    geography E06000015 receives the same location_key everywhere.
    """

    locations = dataframe[
        [
            "area_code",
            "area_name",
        ]
    ].drop_duplicates(
        subset=[
            "area_code",
        ]
    )

    locations = locations.rename(
        columns={
            "area_code": "location_id",
            "area_name": "location_name",
        }
    )

    locations["official_area_code"] = locations["location_id"]

    locations["region_or_country_name"] = pd.NA

    locations["has_official_code"] = True

    locations["location_key"] = locations["location_id"].map(
        lambda value: stable_integer_key(
            "location",
            str(value),
        )
    )

    return locations[
        [
            "location_key",
            "location_id",
            "official_area_code",
            "location_name",
            "region_or_country_name",
            "has_official_code",
        ]
    ].reset_index(drop=True)


def build_earnings_dim_date(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """Build Gold date rows for ASHE reference periods."""

    dates = (
        dataframe[
            [
                "reference_period",
            ]
        ]
        .drop_duplicates()
        .rename(
            columns={
                "reference_period": "date",
            }
        )
        .copy()
    )

    dates["date"] = pd.to_datetime(dates["date"])

    dates["date_key"] = dates["date"].dt.strftime("%Y%m%d").astype(int)

    dates["year"] = dates["date"].dt.year

    dates["quarter"] = dates["date"].dt.quarter

    dates["month"] = dates["date"].dt.month

    dates["month_name"] = dates["date"].dt.month_name()

    return dates[
        [
            "date_key",
            "date",
            "year",
            "quarter",
            "month",
            "month_name",
        ]
    ].reset_index(drop=True)


def build_earnings_dim_metric() -> pd.DataFrame:
    """Build earnings metric definitions."""

    return pd.DataFrame(METRIC_DEFINITIONS)


def build_earnings_fact(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Build long-form earnings facts.

    Suppressed ONS values remain rows with:
        value = null
        is_published = False

    They are never converted to zero.
    """

    loaded_at = datetime.now(UTC)

    metric_map = {
        "median_annual_pay": {
            "metric_key": 101,
            "metric_code": "EARNINGS_ANNUAL",
        },
        "median_annual_change_percent": {
            "metric_key": 102,
            "metric_code": "EARNINGS_ANNUAL_CHANGE",
        },
    }

    records: list[dict[str, object]] = []

    for row in dataframe.itertuples(index=False):
        location_id = str(row.area_code)

        location_key = stable_integer_key(
            "location",
            location_id,
        )

        reference_period = pd.Timestamp(row.reference_period)

        date_key = int(reference_period.strftime("%Y%m%d"))

        for (
            source_column,
            definition,
        ) in metric_map.items():
            raw_value = getattr(
                row,
                source_column,
            )

            published = pd.notna(raw_value)

            value = float(raw_value) if published else None

            metric_key = int(definition["metric_key"])

            fact_identity = f"{date_key}|{location_key}|{metric_key}|{SOURCE_ID}"

            records.append(
                {
                    "fact_id": stable_integer_key(
                        "fact",
                        fact_identity,
                    ),
                    "date_key": date_key,
                    "location_key": location_key,
                    "metric_key": metric_key,
                    "value": value,
                    "is_published": published,
                    "source_id": SOURCE_ID,
                    "loaded_at": loaded_at,
                }
            )

    return pd.DataFrame(records)


def merge_dimension(
    existing: pd.DataFrame,
    incoming: pd.DataFrame,
    key: str,
) -> pd.DataFrame:
    """
    Idempotently merge new dimension rows.

    Existing CostScope dimension values take precedence where the key is
    already known. This preserves richer rent-derived region metadata for
    shared local-authority geographies such as Derby.
    """

    combined = pd.concat(
        [
            existing,
            incoming,
        ],
        ignore_index=True,
    )

    combined = combined.drop_duplicates(
        subset=[
            key,
        ],
        keep="first",
    )

    return combined.reset_index(drop=True)


def merge_fact(
    existing: pd.DataFrame,
    incoming: pd.DataFrame,
) -> pd.DataFrame:
    """
    Idempotently merge earnings facts into the Gold fact table.
    """

    if existing.empty:
        return incoming.reset_index(drop=True)

    # Remove previous copies of earnings facts before replacing them with
    # the latest build.
    existing_without_earnings = existing.loc[existing["source_id"] != SOURCE_ID].copy()

    combined = pd.concat(
        [
            existing_without_earnings,
            incoming,
        ],
        ignore_index=True,
    )

    combined = combined.drop_duplicates(
        subset=[
            "date_key",
            "location_key",
            "metric_key",
            "source_id",
        ],
        keep="last",
    )

    return combined.reset_index(drop=True)


def read_gold_table(
    filename: str,
) -> pd.DataFrame:
    """Read an existing Gold table if present."""

    path = GOLD_DIRECTORY / filename

    if not path.exists():
        return pd.DataFrame()

    return pd.read_parquet(path)


def write_gold_table(
    dataframe: pd.DataFrame,
    filename: str,
) -> Path:
    """Write one CostScope Gold table."""

    GOLD_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    path = GOLD_DIRECTORY / filename

    dataframe.to_parquet(
        path,
        index=False,
    )

    logger.info(
        "Gold table written: %s | %s rows",
        path,
        f"{len(dataframe):,}",
    )

    return path


def build_earnings_gold() -> dict[str, pd.DataFrame]:
    """
    Extend the existing CostScope Gold warehouse with earnings data.
    """

    silver = load_silver_earnings()

    incoming_locations = build_earnings_dim_location(silver)

    incoming_dates = build_earnings_dim_date(silver)

    incoming_metrics = build_earnings_dim_metric()

    incoming_facts = build_earnings_fact(silver)

    existing_locations = read_gold_table("dim_location.parquet")

    existing_dates = read_gold_table("dim_date.parquet")

    existing_metrics = read_gold_table("dim_metric.parquet")

    existing_facts = read_gold_table("fact_cost_metric.parquet")

    locations = merge_dimension(
        existing_locations,
        incoming_locations,
        "location_key",
    )

    dates = merge_dimension(
        existing_dates,
        incoming_dates,
        "date_key",
    )

    metrics = merge_dimension(
        existing_metrics,
        incoming_metrics,
        "metric_key",
    )

    facts = merge_fact(
        existing_facts,
        incoming_facts,
    )

    return {
        "dim_location": locations,
        "dim_date": dates,
        "dim_metric": metrics,
        "fact_cost_metric": facts,
    }


def write_earnings_gold(
    tables: dict[
        str,
        pd.DataFrame,
    ],
) -> dict[str, Path]:
    """Write all updated CostScope Gold tables."""

    paths = {
        "dim_location": write_gold_table(
            tables["dim_location"],
            "dim_location.parquet",
        ),
        "dim_date": write_gold_table(
            tables["dim_date"],
            "dim_date.parquet",
        ),
        "dim_metric": write_gold_table(
            tables["dim_metric"],
            "dim_metric.parquet",
        ),
        "fact_cost_metric": write_gold_table(
            tables["fact_cost_metric"],
            "fact_cost_metric.parquet",
        ),
    }

    return paths
