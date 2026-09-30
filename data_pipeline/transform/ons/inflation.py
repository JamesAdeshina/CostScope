"""
Transform ONS MM23 CPI time-series JSON into CostScope Silver.

CostScope uses the monthly observations from three official ONS series:

D7G7
    CPI annual rate, all items.

D7OE
    CPI monthly rate, all items.

D7BT
    CPI index, all items, 2015=100.

Inflation is a United Kingdom level metric. CostScope does not fabricate
local-authority CPI values.
"""

from __future__ import annotations

import calendar
import json
from pathlib import Path
from typing import Any

import pandas as pd

from data_pipeline.config.settings import settings
from data_pipeline.config.sources import (
    ONS_CPI_SERIES,
)
from data_pipeline.utils.inflation import (
    find_latest_inflation_run,
)
from data_pipeline.utils.logging_config import get_logger

logger = get_logger(__name__)


SILVER_FILENAME = "inflation.parquet"

UK_LOCATION_ID = "K02000001"
UK_LOCATION_NAME = "United Kingdom"


MONTH_NUMBER = {
    month_name.lower(): month_number
    for month_number, month_name in enumerate(calendar.month_name)
    if month_name
}


def load_json(
    path: Path,
) -> dict[str, Any]:
    """Load one ONS Bronze JSON document."""

    with path.open(
        "r",
        encoding="utf-8",
    ) as file_handle:
        payload = json.load(file_handle)

    if not isinstance(
        payload,
        dict,
    ):
        raise ValueError(f"Expected JSON object in {path}")

    return payload


def parse_monthly_series(
    payload: dict[str, Any],
    *,
    value_column: str,
    series_id: str,
) -> pd.DataFrame:
    """
    Convert one ONS CPI `months` array into a monthly dataframe.

    Parameters
    ----------
    payload:
        Raw ONS API response.

    value_column:
        Silver column name for the series.

    series_id:
        Expected ONS CDID.

    Returns
    -------
    pandas.DataFrame
        One row per monthly observation.
    """

    description = payload.get("description", {})

    actual_series_id = str(
        description.get(
            "cdid",
            "",
        )
    ).upper()

    if actual_series_id != series_id.upper():
        raise ValueError(
            f"Unexpected CPI series. Expected {series_id}, received {actual_series_id}."
        )

    months = payload.get("months", [])

    records: list[dict[str, object]] = []

    for item in months:
        if not isinstance(
            item,
            dict,
        ):
            continue

        year_text = str(
            item.get(
                "year",
                "",
            )
        ).strip()

        month_text = str(
            item.get(
                "month",
                "",
            )
        ).strip()

        if not year_text or not month_text:
            continue

        month_number = MONTH_NUMBER.get(month_text.lower())

        if month_number is None:
            raise ValueError(f"Unexpected month name in ONS CPI data: {month_text}")

        reference_period = pd.Timestamp(
            year=int(year_text),
            month=month_number,
            day=1,
        )

        raw_value = item.get("value")

        numeric_value = pd.to_numeric(
            pd.Series([raw_value]),
            errors="coerce",
        ).iloc[0]

        records.append(
            {
                "reference_period": reference_period,
                value_column: (
                    float(numeric_value) if pd.notna(numeric_value) else None
                ),
                f"{value_column}_updated_at": (item.get("updateDate")),
            }
        )

    dataframe = pd.DataFrame(records)

    if dataframe.empty:
        raise ValueError(f"No monthly observations found for {series_id}.")

    dataframe = dataframe.drop_duplicates(
        subset=[
            "reference_period",
        ],
        keep="last",
    )

    dataframe = dataframe.sort_values("reference_period").reset_index(drop=True)

    return dataframe


def load_bronze_series(
    run_directory: Path | None = None,
) -> dict[str, pd.DataFrame]:
    """
    Load and parse all configured CPI series from the latest Bronze run.
    """

    if run_directory is None:
        run_directory = find_latest_inflation_run()

    results: dict[str, pd.DataFrame] = {}

    for (
        series_name,
        definition,
    ) in ONS_CPI_SERIES.items():
        series_id = str(definition["series_id"])

        filename = f"{series_name}_{series_id.lower()}.json"

        path = run_directory / filename

        if not path.exists():
            raise FileNotFoundError(f"Missing CPI Bronze file: {path}")

        payload = load_json(path)

        value_column = {
            "annual_rate": ("cpi_annual_rate"),
            "monthly_rate": ("cpi_monthly_rate"),
            "index": ("cpi_index"),
        }[series_name]

        results[series_name] = parse_monthly_series(
            payload,
            value_column=value_column,
            series_id=series_id,
        )

    return results


def build_silver_inflation(
    run_directory: Path | None = None,
) -> pd.DataFrame:
    """
    Build one monthly Silver table from all configured CPI series.
    """

    series = load_bronze_series(run_directory)

    annual = series["annual_rate"]

    monthly = series["monthly_rate"]

    index = series["index"]

    result = annual.merge(
        monthly,
        on="reference_period",
        how="outer",
        validate="one_to_one",
    )

    result = result.merge(
        index,
        on="reference_period",
        how="outer",
        validate="one_to_one",
    )

    result = result.sort_values("reference_period").reset_index(drop=True)

    result["location_id"] = UK_LOCATION_ID

    result["location_name"] = UK_LOCATION_NAME

    result["geography_level"] = "country"

    result["frequency"] = "monthly"

    result["annual_rate_unit"] = "percent"

    result["monthly_rate_unit"] = "percent"

    result["index_unit"] = "index"

    result["index_base"] = "2015=100"

    ordered_columns = [
        "reference_period",
        "location_id",
        "location_name",
        "geography_level",
        "frequency",
        "cpi_annual_rate",
        "cpi_monthly_rate",
        "cpi_index",
        "annual_rate_unit",
        "monthly_rate_unit",
        "index_unit",
        "index_base",
        "cpi_annual_rate_updated_at",
        "cpi_monthly_rate_updated_at",
        "cpi_index_updated_at",
    ]

    result = result[ordered_columns]

    logger.info(
        "CPI Silver standardised: %s rows x %s columns",
        f"{len(result):,}",
        len(result.columns),
    )

    return result


def get_silver_inflation_path() -> Path:
    """Return the CostScope Silver CPI output path."""

    return settings.silver_path / "ons" / "inflation" / SILVER_FILENAME


def write_silver_inflation(
    dataframe: pd.DataFrame,
) -> Path:
    """Write CPI Silver data to Parquet."""

    destination = get_silver_inflation_path()

    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    dataframe.to_parquet(
        destination,
        index=False,
    )

    logger.info(
        "Silver inflation written: %s",
        destination,
    )

    return destination
