"""
Extend CostScope Gold with model-based unemployment.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

from data_pipeline.config.settings import settings
from data_pipeline.model.private_rent_gold import (
    stable_integer_key,
)
from data_pipeline.transform.nomis.unemployment import (
    get_silver_unemployment_path,
)
from data_pipeline.utils.logging_config import get_logger

logger = get_logger(__name__)


SOURCE_ID = 4

GOLD_DIRECTORY = settings.gold_path / "cost_scope"

METRIC_KEY = 301

METRIC_DEFINITION = {
    "metric_key": METRIC_KEY,
    "metric_code": ("UNEMPLOYMENT_RATE"),
    "metric_name": ("Model-based unemployment rate"),
    "unit": "percent",
    "category": "employment",
}


def load_silver_unemployment() -> pd.DataFrame:
    """Load unemployment Silver data."""

    path = get_silver_unemployment_path()

    if not path.exists():
        raise FileNotFoundError(
            "Silver unemployment dataset does not exist. "
            "Run `python -m scripts.build_unemployment_silver` first."
        )

    dataframe = pd.read_parquet(path)

    logger.info(
        "Loaded Silver unemployment: %s rows",
        f"{len(dataframe):,}",
    )

    return dataframe


def build_unemployment_locations(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """Build Gold location rows from Nomis GSS codes."""

    locations = dataframe[
        [
            "location_id",
            "location_name",
        ]
    ].drop_duplicates(
        subset=[
            "location_id",
        ]
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


def build_unemployment_dates(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """Build Gold date rows."""

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


def build_unemployment_metric() -> pd.DataFrame:
    """Return the unemployment Gold metric definition."""

    return pd.DataFrame([METRIC_DEFINITION])


def build_unemployment_facts(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """Build unemployment Gold facts."""

    loaded_at = datetime.now(UTC)

    records: list[dict[str, object]] = []

    for row in dataframe.itertuples(index=False):
        location_key = stable_integer_key(
            "location",
            str(row.location_id),
        )

        date = pd.Timestamp(row.reference_period)

        date_key = int(date.strftime("%Y%m%d"))

        published = pd.notna(row.unemployment_rate)

        identity = f"{date_key}|{location_key}|{METRIC_KEY}|{SOURCE_ID}"

        records.append(
            {
                "fact_id": stable_integer_key(
                    "fact",
                    identity,
                ),
                "date_key": date_key,
                "location_key": (location_key),
                "metric_key": (METRIC_KEY),
                "value": (float(row.unemployment_rate) if published else None),
                "is_published": (published),
                "source_id": (SOURCE_ID),
                "loaded_at": (loaded_at),
            }
        )

    return pd.DataFrame(records)


def read_gold_table(
    filename: str,
) -> pd.DataFrame:
    """Read an existing Gold table."""

    path = GOLD_DIRECTORY / filename

    if not path.exists():
        return pd.DataFrame()

    return pd.read_parquet(path)


def merge_dimension(
    existing: pd.DataFrame,
    incoming: pd.DataFrame,
    key: str,
) -> pd.DataFrame:
    """Idempotently extend a dimension."""

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

    return combined.drop_duplicates(
        subset=[
            key,
        ],
        keep="first",
    ).reset_index(drop=True)


def merge_facts(
    existing: pd.DataFrame,
    incoming: pd.DataFrame,
) -> pd.DataFrame:
    """Replace previous unemployment facts."""

    if existing.empty:
        return incoming.reset_index(drop=True)

    previous_removed = existing.loc[existing["source_id"] != SOURCE_ID].copy()

    combined = pd.concat(
        [
            previous_removed,
            incoming,
        ],
        ignore_index=True,
    )

    return combined.drop_duplicates(
        subset=[
            "date_key",
            "location_key",
            "metric_key",
            "source_id",
        ],
        keep="last",
    ).reset_index(drop=True)


def build_unemployment_gold() -> dict[
    str,
    pd.DataFrame,
]:
    """Extend CostScope Gold with unemployment."""

    silver = load_silver_unemployment()

    locations = merge_dimension(
        read_gold_table("dim_location.parquet"),
        build_unemployment_locations(silver),
        "location_key",
    )

    dates = merge_dimension(
        read_gold_table("dim_date.parquet"),
        build_unemployment_dates(silver),
        "date_key",
    )

    metrics = merge_dimension(
        read_gold_table("dim_metric.parquet"),
        build_unemployment_metric(),
        "metric_key",
    )

    facts = merge_facts(
        read_gold_table("fact_cost_metric.parquet"),
        build_unemployment_facts(silver),
    )

    return {
        "dim_location": locations,
        "dim_date": dates,
        "dim_metric": metrics,
        "fact_cost_metric": facts,
    }


def write_unemployment_gold(
    tables: dict[
        str,
        pd.DataFrame,
    ],
) -> dict[str, Path]:
    """Write updated CostScope Gold."""

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
