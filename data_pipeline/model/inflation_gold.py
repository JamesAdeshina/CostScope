"""
Extend CostScope Gold with ONS CPI inflation metrics.

Inflation is modelled at United Kingdom level using geography code
K02000001. Local authority overview responses may display the UK metric,
but it remains explicitly labelled as UK-level data.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

from data_pipeline.config.settings import settings
from data_pipeline.model.private_rent_gold import (
    stable_integer_key,
)
from data_pipeline.transform.ons.inflation import (
    get_silver_inflation_path,
)
from data_pipeline.utils.logging_config import get_logger

logger = get_logger(__name__)


SOURCE_ID = 3
SOURCE_CODE = "ONS_CPI_MM23"

UK_LOCATION_ID = "K02000001"
UK_LOCATION_NAME = "United Kingdom"

GOLD_DIRECTORY = settings.gold_path / "cost_scope"

METRIC_DEFINITIONS = [
    {
        "metric_key": 201,
        "metric_code": "CPI_ANNUAL_RATE",
        "metric_name": ("Consumer Price Index annual rate"),
        "unit": "percent",
        "category": "inflation",
    },
    {
        "metric_key": 202,
        "metric_code": "CPI_MONTHLY_RATE",
        "metric_name": ("Consumer Price Index monthly rate"),
        "unit": "percent",
        "category": "inflation",
    },
    {
        "metric_key": 203,
        "metric_code": "CPI_INDEX",
        "metric_name": ("Consumer Price Index"),
        "unit": "index",
        "category": "inflation",
    },
]


def load_silver_inflation(
    path: Path | None = None,
) -> pd.DataFrame:
    """Load CostScope Silver CPI data."""

    if path is None:
        path = get_silver_inflation_path()

    if not path.exists():
        raise FileNotFoundError(
            "Silver inflation dataset not found: "
            f"{path}. Run "
            "`python -m scripts.build_inflation_silver` first."
        )

    dataframe = pd.read_parquet(path)

    logger.info(
        "Loaded Silver inflation: %s rows",
        f"{len(dataframe):,}",
    )

    return dataframe


def build_inflation_location() -> pd.DataFrame:
    """Build the United Kingdom Gold geography row."""

    return pd.DataFrame(
        [
            {
                "location_key": (
                    stable_integer_key(
                        "location",
                        UK_LOCATION_ID,
                    )
                ),
                "location_id": UK_LOCATION_ID,
                "official_area_code": (UK_LOCATION_ID),
                "location_name": (UK_LOCATION_NAME),
                "region_or_country_name": (UK_LOCATION_NAME),
                "has_official_code": True,
            }
        ]
    )


def build_inflation_dates(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """Build Gold date rows from CPI monthly periods."""

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


def build_inflation_metrics() -> pd.DataFrame:
    """Return CPI Gold metric definitions."""

    return pd.DataFrame(METRIC_DEFINITIONS)


def build_inflation_facts(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """Convert CPI Silver columns into long-form Gold facts."""

    loaded_at = datetime.now(UTC)

    location_key = stable_integer_key(
        "location",
        UK_LOCATION_ID,
    )

    metric_map = {
        "cpi_annual_rate": 201,
        "cpi_monthly_rate": 202,
        "cpi_index": 203,
    }

    records: list[dict[str, object]] = []

    for row in dataframe.itertuples(index=False):
        reference_period = pd.Timestamp(row.reference_period)

        date_key = int(reference_period.strftime("%Y%m%d"))

        for (
            source_column,
            metric_key,
        ) in metric_map.items():
            raw_value = getattr(
                row,
                source_column,
            )

            published = pd.notna(raw_value)

            fact_identity = f"{date_key}|{location_key}|{metric_key}|{SOURCE_ID}"

            records.append(
                {
                    "fact_id": stable_integer_key(
                        "fact",
                        fact_identity,
                    ),
                    "date_key": date_key,
                    "location_key": (location_key),
                    "metric_key": (metric_key),
                    "value": (float(raw_value) if published else None),
                    "is_published": (published),
                    "source_id": (SOURCE_ID),
                    "loaded_at": (loaded_at),
                }
            )

    return pd.DataFrame(records)


def read_gold_table(
    filename: str,
) -> pd.DataFrame:
    """Read a CostScope Gold table."""

    path = GOLD_DIRECTORY / filename

    if not path.exists():
        return pd.DataFrame()

    return pd.read_parquet(path)


def merge_dimension(
    existing: pd.DataFrame,
    incoming: pd.DataFrame,
    key: str,
) -> pd.DataFrame:
    """Idempotently merge dimension rows."""

    if existing.empty:
        return incoming.reset_index(drop=True)

    if incoming.empty:
        return existing.reset_index(drop=True)

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


def merge_facts(
    existing: pd.DataFrame,
    incoming: pd.DataFrame,
) -> pd.DataFrame:
    """Replace previous CPI facts with the latest CPI build."""

    if existing.empty:
        return incoming.reset_index(drop=True)

    existing_without_cpi = existing.loc[existing["source_id"] != SOURCE_ID].copy()

    combined = pd.concat(
        [
            existing_without_cpi,
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


def build_inflation_gold() -> dict[
    str,
    pd.DataFrame,
]:
    """Extend CostScope Gold with CPI metrics."""

    silver = load_silver_inflation()

    locations = merge_dimension(
        read_gold_table("dim_location.parquet"),
        build_inflation_location(),
        "location_key",
    )

    dates = merge_dimension(
        read_gold_table("dim_date.parquet"),
        build_inflation_dates(silver),
        "date_key",
    )

    metrics = merge_dimension(
        read_gold_table("dim_metric.parquet"),
        build_inflation_metrics(),
        "metric_key",
    )

    facts = merge_facts(
        read_gold_table("fact_cost_metric.parquet"),
        build_inflation_facts(silver),
    )

    return {
        "dim_location": locations,
        "dim_date": dates,
        "dim_metric": metrics,
        "fact_cost_metric": facts,
    }


def write_inflation_gold(
    tables: dict[
        str,
        pd.DataFrame,
    ],
) -> dict[str, Path]:
    """Write updated CostScope Gold tables."""

    GOLD_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    paths: dict[str, Path] = {}

    for (
        table_name,
        dataframe,
    ) in tables.items():
        path = GOLD_DIRECTORY / f"{table_name}.parquet"

        dataframe.to_parquet(
            path,
            index=False,
        )

        paths[table_name] = path

        logger.info(
            "Gold table written: %s | %s rows",
            path,
            f"{len(dataframe):,}",
        )

    return paths
