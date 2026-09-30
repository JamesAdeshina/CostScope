"""
Transform ONS ASHE Table 8.7a earnings data into CostScope Silver.

Source
------
ONS Annual Survey of Hours and Earnings (ASHE)
Table 8.7a - Annual pay - Gross
Sheet: Full-Time

The Silver layer preserves published geography identifiers and converts
statistical suppression / quality markers to missing values rather than
fabricating numeric values.
"""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

from data_pipeline.config.settings import settings
from data_pipeline.config.sources import (
    ONS_ASHE_RELEASE_YEAR,
    ONS_ASHE_TARGET_SHEET,
)
from data_pipeline.utils.earnings import (
    find_latest_earnings_workbook,
)
from data_pipeline.utils.logging_config import get_logger

logger = get_logger(__name__)


HEADER_ROW = 4

SOURCE_SHEET = ONS_ASHE_TARGET_SHEET

SILVER_FILENAME = "earnings.parquet"

SUPPRESSION_MARKERS = {
    "x",
    "..",
    ":",
    "-",
    "[x]",
    "[z]",
    "",
}


def normalise_column_name(
    value: object,
) -> str:
    """Convert a source column name to snake_case."""

    text = str(value).strip().lower()

    text = re.sub(
        r"[^a-z0-9]+",
        "_",
        text,
    )

    return text.strip("_")


def clean_numeric_series(
    series: pd.Series,
) -> pd.Series:
    """
    Convert ONS numeric fields to nullable numeric values.

    Published suppression markers become missing values. They are never
    converted to zero.
    """

    cleaned = (
        series.astype("string")
        .str.strip()
        .replace(
            list(SUPPRESSION_MARKERS),
            pd.NA,
        )
    )

    return pd.to_numeric(
        cleaned,
        errors="coerce",
    )


def clean_description(
    series: pd.Series,
) -> pd.Series:
    """Clean geography descriptions without changing their meaning."""

    return (
        series.astype("string")
        .str.strip()
        .replace(
            "",
            pd.NA,
        )
    )


def clean_area_code(
    series: pd.Series,
) -> pd.Series:
    """Clean published ONS geography codes."""

    cleaned = (
        series.astype("string")
        .str.strip()
        .replace(
            "",
            pd.NA,
        )
    )

    return cleaned


def load_raw_earnings(
    workbook_path: Path | None = None,
) -> pd.DataFrame:
    """Read the ASHE Full-Time worksheet using the verified header row."""

    if workbook_path is None:
        workbook_path = find_latest_earnings_workbook()

    logger.info(
        "Reading ASHE earnings workbook: %s",
        workbook_path,
    )

    dataframe = pd.read_excel(
        workbook_path,
        sheet_name=SOURCE_SHEET,
        header=HEADER_ROW,
        engine="openpyxl",
    )

    logger.info(
        "Raw ASHE data loaded: %s rows x %s columns",
        f"{len(dataframe):,}",
        len(dataframe.columns),
    )

    return dataframe


def standardise_earnings(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Standardise the ASHE Table 8.7a Full-Time worksheet.

    Output grain
    ------------
    One row per published geography for the 2025 provisional release.
    """

    result = dataframe.copy()

    result.columns = [normalise_column_name(column) for column in result.columns]

    # The actual worksheet contains columns:
    # Description, Code, (thousand), Median, change, Mean, change, ...
    #
    # Duplicate "change" headings are automatically disambiguated by
    # pandas as change and change_1.
    rename_map = {
        "description": "area_name",
        "code": "area_code",
        "thousand": "number_of_jobs_thousand",
        "median": "median_annual_pay",
        "change": "median_annual_change_percent",
        "mean": "mean_annual_pay",
        "change_1": "mean_annual_change_percent",
    }

    result = result.rename(columns=rename_map)

    required_source_columns = {
        "area_name",
        "area_code",
        "median_annual_pay",
    }

    missing_columns = required_source_columns - set(result.columns)

    if missing_columns:
        raise ValueError(
            f"ASHE workbook is missing required columns: {sorted(missing_columns)}"
        )

    # Remove footer, notes and fully empty rows.
    result = result.loc[result["area_code"].notna()].copy()

    result["area_name"] = clean_description(result["area_name"])

    result["area_code"] = clean_area_code(result["area_code"])

    # Keep rows with plausible published geography codes only.
    #
    # Examples:
    # K02000001 - United Kingdom
    # E12000001 - North East
    # E06000015 - Derby
    geography_pattern = r"^[A-Z][0-9]{8}$"

    result = result.loc[
        result["area_code"]
        .astype("string")
        .str.match(
            geography_pattern,
            na=False,
        )
    ].copy()

    numeric_columns = [
        "number_of_jobs_thousand",
        "median_annual_pay",
        "median_annual_change_percent",
        "mean_annual_pay",
        "mean_annual_change_percent",
    ]

    for column in numeric_columns:
        if column in result.columns:
            result[column] = clean_numeric_series(result[column])

    result["reference_year"] = ONS_ASHE_RELEASE_YEAR

    # Annual earnings represent the tax year ending 5 April in the
    # reference year. Use 5 April as the analytical period end.
    result["reference_period"] = pd.Timestamp(
        year=ONS_ASHE_RELEASE_YEAR,
        month=4,
        day=5,
    )

    result["employment_type"] = "Full-Time"

    result["pay_measure"] = "Annual pay - Gross"

    result["statistic"] = "Median"

    result["unit"] = "GBP/year"

    selected_columns = [
        "reference_year",
        "reference_period",
        "area_code",
        "area_name",
        "employment_type",
        "pay_measure",
        "statistic",
        "median_annual_pay",
        "median_annual_change_percent",
        "number_of_jobs_thousand",
        "mean_annual_pay",
        "mean_annual_change_percent",
        "unit",
    ]

    result = result[[column for column in selected_columns if column in result.columns]]

    result = result.reset_index(drop=True)

    logger.info(
        "ASHE earnings standardised: %s rows x %s columns",
        f"{len(result):,}",
        len(result.columns),
    )

    return result


def get_silver_earnings_path() -> Path:
    """Return the Silver output path for earnings."""

    return settings.silver_path / "ons" / "earnings" / SILVER_FILENAME


def write_silver_earnings(
    dataframe: pd.DataFrame,
) -> Path:
    """Write standardised earnings to Silver Parquet."""

    destination = get_silver_earnings_path()

    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    dataframe.to_parquet(
        destination,
        index=False,
    )

    logger.info(
        "Silver earnings written: %s",
        destination,
    )

    return destination


def build_silver_earnings(
    workbook_path: Path | None = None,
) -> tuple[pd.DataFrame, Path]:
    """Build the complete ASHE Silver earnings dataset."""

    raw = load_raw_earnings(workbook_path)

    silver = standardise_earnings(raw)

    path = write_silver_earnings(silver)

    return silver, path
