"""
Gold modelling for the ONS Private Rent dataset.

Transforms the validated Silver dataset into analytical tables:

    dim_location
    dim_date
    dim_metric
    fact_cost_metric

The model intentionally converts the wide ONS source into a long
metric-based fact table. This allows CostScope to add earnings,
inflation, employment, energy and transport metrics later without
redesigning the analytical model.
"""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

from data_pipeline.config.settings import settings
from data_pipeline.utils.logging_config import get_logger


logger = get_logger(__name__)


SOURCE_ID = 1
SOURCE_CODE = "ONS_PIPR"


METRIC_DEFINITIONS = [
    {
        "metric_key": 1,
        "metric_code": "RENT_MONTHLY",
        "metric_name": "Average monthly private rent",
        "source_column": "rental_price",
        "category": "Housing",
        "unit": "GBP/month",
        "description": "Average monthly private rental price.",
    },
    {
        "metric_key": 2,
        "metric_code": "RENT_MONTHLY_CHANGE",
        "metric_name": "Monthly private rent change",
        "source_column": "monthly_change",
        "category": "Housing",
        "unit": "percent",
        "description": "Monthly percentage change in private rent.",
    },
    {
        "metric_key": 3,
        "metric_code": "RENT_ANNUAL_CHANGE",
        "metric_name": "Annual private rent change",
        "source_column": "annual_change",
        "category": "Housing",
        "unit": "percent",
        "description": "Annual percentage change in private rent.",
    },
    {
        "metric_key": 4,
        "metric_code": "RENT_ONE_BED",
        "metric_name": "One-bedroom monthly rent",
        "source_column": "rental_price_one_bed",
        "category": "Housing",
        "unit": "GBP/month",
        "description": "Average monthly private rent for one-bedroom properties.",
    },
    {
        "metric_key": 5,
        "metric_code": "RENT_TWO_BED",
        "metric_name": "Two-bedroom monthly rent",
        "source_column": "rental_price_two_bed",
        "category": "Housing",
        "unit": "GBP/month",
        "description": "Average monthly private rent for two-bedroom properties.",
    },
    {
        "metric_key": 6,
        "metric_code": "RENT_THREE_BED",
        "metric_name": "Three-bedroom monthly rent",
        "source_column": "rental_price_three_bed",
        "category": "Housing",
        "unit": "GBP/month",
        "description": "Average monthly private rent for three-bedroom properties.",
    },
    {
        "metric_key": 7,
        "metric_code": "RENT_FOUR_PLUS_BED",
        "metric_name": "Four-plus-bedroom monthly rent",
        "source_column": "rental_price_four_or_more_bed",
        "category": "Housing",
        "unit": "GBP/month",
        "description": (
            "Average monthly private rent for properties with "
            "four or more bedrooms."
        ),
    },
    {
        "metric_key": 8,
        "metric_code": "RENT_DETACHED",
        "metric_name": "Detached property monthly rent",
        "source_column": "rental_price_detached",
        "category": "Housing",
        "unit": "GBP/month",
        "description": "Average monthly private rent for detached properties.",
    },
    {
        "metric_key": 9,
        "metric_code": "RENT_SEMIDETACHED",
        "metric_name": "Semi-detached property monthly rent",
        "source_column": "rental_price_semidetached",
        "category": "Housing",
        "unit": "GBP/month",
        "description": "Average monthly private rent for semi-detached properties.",
    },
    {
        "metric_key": 10,
        "metric_code": "RENT_TERRACED",
        "metric_name": "Terraced property monthly rent",
        "source_column": "rental_price_terraced",
        "category": "Housing",
        "unit": "GBP/month",
        "description": "Average monthly private rent for terraced properties.",
    },
    {
        "metric_key": 11,
        "metric_code": "RENT_FLAT_MAISONETTE",
        "metric_name": "Flat or maisonette monthly rent",
        "source_column": "rental_price_flat_maisonette",
        "category": "Housing",
        "unit": "GBP/month",
        "description": "Average monthly private rent for flats and maisonettes.",
    },
]


def stable_integer_key(
    namespace: str,
    value: str,
) -> int:
    """
    Create a deterministic positive 63-bit surrogate key.

    Unlike row numbers, the key remains stable when new source
    locations are introduced in later pipeline runs.
    """

    payload = f"{namespace}:{value}".encode()

    digest = hashlib.sha256(
        payload
    ).digest()

    key = int.from_bytes(
        digest[:8],
        byteorder="big",
        signed=False,
    )

    # Keep within PostgreSQL signed BIGINT range.
    key &= (1 << 63) - 1

    return key or 1


def load_silver_private_rent() -> pd.DataFrame:
    """Load the validated ONS Private Rent Silver dataset."""

    source_path = (
        settings.silver_path
        / "ons"
        / "private_rent"
        / "private_rent.parquet"
    )

    if not source_path.exists():
        raise FileNotFoundError(
            "Private Rent Silver dataset does not exist. "
            "Run `python -m scripts.build_private_rent_silver` first."
        )

    logger.info(
        "Loading Silver dataset: %s",
        source_path,
    )

    return pd.read_parquet(
        source_path,
        engine="pyarrow",
    )


def build_dim_location(
    silver: pd.DataFrame,
) -> pd.DataFrame:
    """Build the Gold location dimension."""

    dimension = (
        silver[
            [
                "location_id",
                "area_code",
                "area_name",
                "region_or_country_name",
            ]
        ]
        .drop_duplicates()
        .copy()
    )

    dimension["location_key"] = (
        dimension["location_id"]
        .astype(str)
        .map(
            lambda value: stable_integer_key(
                "location",
                value,
            )
        )
    )

    dimension["has_official_code"] = (
        dimension["area_code"].notna()
    )

    dimension = dimension.rename(
        columns={
            "area_code": "official_area_code",
            "area_name": "location_name",
        }
    )

    dimension = dimension[
        [
            "location_key",
            "location_id",
            "official_area_code",
            "location_name",
            "region_or_country_name",
            "has_official_code",
        ]
    ]

    return dimension.sort_values(
        [
            "location_name",
            "location_id",
        ]
    ).reset_index(
        drop=True
    )


def build_dim_date(
    silver: pd.DataFrame,
) -> pd.DataFrame:
    """Build the reporting-period date dimension."""

    dates = (
        silver[
            [
                "time_period",
            ]
        ]
        .drop_duplicates()
        .rename(
            columns={
                "time_period": "date",
            }
        )
        .sort_values("date")
        .reset_index(drop=True)
    )

    dates["date_key"] = (
        dates["date"].dt.strftime(
            "%Y%m%d"
        )
        .astype(int)
    )

    dates["year"] = (
        dates["date"].dt.year
    )

    dates["quarter"] = (
        dates["date"].dt.quarter
    )

    dates["month"] = (
        dates["date"].dt.month
    )

    dates["month_name"] = (
        dates["date"].dt.month_name()
    )

    return dates[
        [
            "date_key",
            "date",
            "year",
            "quarter",
            "month",
            "month_name",
        ]
    ]


def build_dim_metric() -> pd.DataFrame:
    """Build CostScope's rent metric dimension."""

    dimension = pd.DataFrame(
        METRIC_DEFINITIONS
    )

    return dimension[
        [
            "metric_key",
            "metric_code",
            "metric_name",
            "category",
            "unit",
            "description",
            "source_column",
        ]
    ]


def build_fact_cost_metric(
    silver: pd.DataFrame,
    dim_location: pd.DataFrame,
    dim_metric: pd.DataFrame,
) -> pd.DataFrame:
    """
    Convert the wide Silver dataset into the Gold metric fact table.

    Missing published statistics remain explicit through the
    ``is_published`` field rather than being converted to zero.
    """

    metric_lookup = {
        row["source_column"]: row["metric_key"]
        for _, row in dim_metric.iterrows()
    }

    source_columns = list(
        metric_lookup
    )

    missing_columns = (
        set(source_columns)
        - set(silver.columns)
    )

    if missing_columns:
        raise ValueError(
            "Silver dataset is missing metric columns: "
            + ", ".join(
                sorted(missing_columns)
            )
        )

    fact = silver[
        [
            "time_period",
            "location_id",
            *source_columns,
        ]
    ].melt(
        id_vars=[
            "time_period",
            "location_id",
        ],
        value_vars=source_columns,
        var_name="source_column",
        value_name="value",
    )

    fact["metric_key"] = (
        fact["source_column"]
        .map(metric_lookup)
        .astype(int)
    )

    location_lookup = (
        dim_location.set_index(
            "location_id"
        )["location_key"]
    )

    fact["location_key"] = (
        fact["location_id"]
        .map(location_lookup)
    )

    fact["date_key"] = (
        fact["time_period"]
        .dt.strftime("%Y%m%d")
        .astype(int)
    )

    fact["source_id"] = SOURCE_ID

    fact["is_published"] = (
        fact["value"].notna()
    )

    loaded_at = datetime.now(
        UTC
    )

    fact["loaded_at"] = loaded_at

    fact["fact_id"] = [
        stable_integer_key(
            "fact",
            (
                f"{location_key}:"
                f"{date_key}:"
                f"{metric_key}:"
                f"{SOURCE_ID}"
            ),
        )
        for location_key, date_key, metric_key in zip(
            fact["location_key"],
            fact["date_key"],
            fact["metric_key"],
            strict=True,
        )
    ]

    return fact[
        [
            "fact_id",
            "date_key",
            "location_key",
            "metric_key",
            "value",
            "is_published",
            "source_id",
            "loaded_at",
        ]
    ]


def build_gold_tables() -> dict[str, pd.DataFrame]:
    """Build all Private Rent Gold tables."""

    logger.info("=" * 70)
    logger.info("Building CostScope Private Rent Gold model")
    logger.info("=" * 70)

    silver = load_silver_private_rent()

    dim_location = build_dim_location(
        silver
    )

    dim_date = build_dim_date(
        silver
    )

    dim_metric = build_dim_metric()

    fact_cost_metric = build_fact_cost_metric(
        silver,
        dim_location,
        dim_metric,
    )

    logger.info(
        "dim_location: %s rows",
        f"{len(dim_location):,}",
    )

    logger.info(
        "dim_date: %s rows",
        f"{len(dim_date):,}",
    )

    logger.info(
        "dim_metric: %s rows",
        f"{len(dim_metric):,}",
    )

    logger.info(
        "fact_cost_metric: %s rows",
        f"{len(fact_cost_metric):,}",
    )

    return {
        "dim_location": dim_location,
        "dim_date": dim_date,
        "dim_metric": dim_metric,
        "fact_cost_metric": fact_cost_metric,
    }


def write_gold_tables(
    tables: dict[str, pd.DataFrame],
) -> dict[str, Path]:
    """Write Gold tables as Parquet files."""

    output_directory = (
        settings.gold_path
        / "cost_scope"
    )

    output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_paths: dict[str, Path] = {}

    for table_name, dataframe in tables.items():
        output_path = (
            output_directory
            / f"{table_name}.parquet"
        )

        dataframe.to_parquet(
            output_path,
            index=False,
            engine="pyarrow",
        )

        output_paths[
            table_name
        ] = output_path

        logger.info(
            "Gold table written: %s",
            output_path,
        )

    return output_paths