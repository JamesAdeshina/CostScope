"""
Transform Nomis model-based unemployment into CostScope Silver.

Dataset
-------
NM_127_1
    model-based estimates of unemployment

Nomis currently returns blank TIME and TIME_NAME fields when CostScope
requests `time=latest`. The extraction is nevertheless a latest-period
snapshot.

The current Nomis dataset reference period is:
    Apr 2025-Mar 2026

CostScope records that reference period explicitly and does not infer
dates from row order or geography IDs.
"""

from __future__ import annotations

import calendar
import re
from pathlib import Path

import pandas as pd

from data_pipeline.config.settings import settings
from data_pipeline.utils.logging_config import get_logger
from data_pipeline.utils.unemployment import (
    find_latest_unemployment_file,
)

logger = get_logger(__name__)


SILVER_FILENAME = "unemployment.parquet"

LATEST_REFERENCE_PERIOD_LABEL = "Apr 2025-Mar 2026"

LATEST_REFERENCE_PERIOD_END = pd.Timestamp("2026-03-31")


KNOWN_LOCATION_CODES = {
    "derby": "E06000015",
}


MONTH_LOOKUP = {
    month[:3].lower(): number
    for number, month in enumerate(calendar.month_name)
    if month
}


def normalise_column_name(
    value: object,
) -> str:
    """Convert source column names to snake_case."""

    text = str(value).strip().lower()

    text = re.sub(
        r"[^a-z0-9]+",
        "_",
        text,
    )

    return text.strip("_")


def normalise_location_name(
    value: object,
) -> str:
    """Normalise location names for deterministic matching."""

    text = str(value).strip().lower()

    return re.sub(
        r"\s+",
        " ",
        text,
    )


def parse_reference_period_end(
    value: object,
) -> pd.Timestamp:
    """
    Convert a Nomis annual-period label to its period-end date.

    Example
    -------
    Apr 2025-Mar 2026 -> 2026-03-31
    """

    if pd.isna(value):
        raise ValueError("Nomis unemployment period is missing.")

    text = str(value).strip()

    pattern = re.compile(
        r"([A-Za-z]{3})\s+\d{4}\s*-\s*"
        r"([A-Za-z]{3})\s+(\d{4})"
    )

    match = pattern.search(text)

    if match is None:
        raise ValueError(f"Unexpected Nomis unemployment period: {text!r}")

    end_month_name = match.group(2).lower()

    end_year = int(match.group(3))

    end_month = MONTH_LOOKUP[end_month_name]

    last_day = calendar.monthrange(
        end_year,
        end_month,
    )[1]

    return pd.Timestamp(
        year=end_year,
        month=end_month,
        day=last_day,
    )


def load_raw_unemployment(
    path: Path | None = None,
) -> pd.DataFrame:
    """Load latest unemployment Bronze CSV."""

    if path is None:
        path = find_latest_unemployment_file()

    logger.info(
        "Reading Nomis unemployment Bronze: %s",
        path,
    )

    dataframe = pd.read_csv(path)

    logger.info(
        "Raw Nomis unemployment loaded: %s rows x %s columns",
        f"{len(dataframe):,}",
        len(dataframe.columns),
    )

    logger.info(
        "Raw Nomis columns: %s",
        ", ".join(str(column) for column in dataframe.columns),
    )

    return dataframe


def resolve_location_id(
    geography_name: object,
) -> str | None:
    """Resolve supported Nomis names to official CostScope IDs."""

    key = normalise_location_name(geography_name)

    return KNOWN_LOCATION_CODES.get(key)


def standardise_unemployment(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Create CostScope Silver model-based unemployment observations.

    Because the Bronze request uses `time=latest`, blank TIME fields are
    not treated as missing observations. Instead, the verified current
    Nomis latest reference period is attached explicitly.
    """

    result = dataframe.copy()

    result.columns = [normalise_column_name(column) for column in result.columns]

    required = {
        "geography",
        "geography_name",
        "item",
        "item_name",
        "obs_value",
    }

    missing = required - set(result.columns)

    if missing:
        raise ValueError(
            f"Nomis unemployment response is missing columns: {sorted(missing)}"
        )

    result = result.dropna(
        subset=[
            "geography",
            "geography_name",
            "item",
            "item_name",
        ]
    ).copy()

    result["item_name"] = result["item_name"].astype("string").str.strip()

    result = result.loc[
        result["item_name"].str.lower().eq("unemployment rate (model based)")
    ].copy()

    if result.empty:
        raise ValueError(
            "Model-based unemployment-rate observations "
            "were not found in the Nomis response."
        )

    logger.info(
        "Selected %s model-based unemployment-rate rows",
        f"{len(result):,}",
    )

    result["nomis_geography_id"] = result["geography"].astype("string").str.strip()

    result["location_name"] = result["geography_name"].astype("string").str.strip()

    result["location_id"] = result["location_name"].map(resolve_location_id)

    unresolved = int(result["location_id"].isna().sum())

    if unresolved:
        logger.warning(
            "%s unemployment rows are not yet mapped "
            "to official CostScope location IDs.",
            f"{unresolved:,}",
        )

    result = result.dropna(
        subset=[
            "location_id",
        ]
    ).copy()

    result["unemployment_rate"] = pd.to_numeric(
        result["obs_value"],
        errors="coerce",
    )

    result["reference_period_label"] = LATEST_REFERENCE_PERIOD_LABEL

    result["reference_period"] = LATEST_REFERENCE_PERIOD_END

    result["metric_code"] = "UNEMPLOYMENT_RATE"

    result["unit"] = "percent"

    result["methodology"] = "model-based"

    result["population"] = "aged 16 and over; percentage of economically active"

    selected_columns = [
        "reference_period",
        "reference_period_label",
        "location_id",
        "location_name",
        "nomis_geography_id",
        "unemployment_rate",
        "metric_code",
        "unit",
        "methodology",
        "population",
    ]

    for optional_column in (
        "obs_status",
        "obs_conf",
    ):
        if optional_column in result.columns:
            selected_columns.append(optional_column)

    result = result[selected_columns]

    # Nomis publishes multiple geography vintages carrying the same
    # latest observation. Once mapped to the same official GSS code,
    # keep one deterministic observation per CostScope grain.
    result = result.sort_values(
        [
            "location_id",
            "nomis_geography_id",
        ]
    )

    result = result.drop_duplicates(
        subset=[
            "reference_period",
            "location_id",
        ],
        keep="first",
    )

    result = result.reset_index(drop=True)

    logger.info(
        "Unemployment Silver standardised: %s rows x %s columns",
        f"{len(result):,}",
        len(result.columns),
    )

    return result


def get_silver_unemployment_path() -> Path:
    """Return unemployment Silver path."""

    return settings.silver_path / "nomis" / "unemployment" / SILVER_FILENAME


def write_silver_unemployment(
    dataframe: pd.DataFrame,
) -> Path:
    """Write unemployment Silver Parquet."""

    destination = get_silver_unemployment_path()

    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    dataframe.to_parquet(
        destination,
        index=False,
    )

    logger.info(
        "Silver unemployment written: %s",
        destination,
    )

    return destination
