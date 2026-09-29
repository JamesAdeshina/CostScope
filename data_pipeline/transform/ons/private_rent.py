"""
Silver transformation for the ONS Private Rent dataset.

The ONS workbook contains descriptive rows before the statistical table.
The real header is located on Excel row 3, corresponding to ``header=2``
when read with pandas.

The Silver layer:

1. Reads the Bronze workbook.
2. Standardises column names.
3. Normalises ONS disclosure / not-applicable markers.
4. Parses reporting periods.
5. Converts statistical measures to numeric values.
6. Creates a stable CostScope geography identifier.
7. Writes analytics-friendly Parquet.

No statistical values or geography codes are fabricated.
"""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

from data_pipeline.config.settings import settings
from data_pipeline.utils.logging_config import get_logger

logger = get_logger(__name__)


SOURCE_SHEET = "Table 1"
HEADER_ROW = 2


# ONS markers encountered in the workbook.
#
# These are metadata markers, not actual values.
ONS_MISSING_MARKERS = {
    "[x]",
    "[z]",
}


TEXT_COLUMNS = {
    "area_code",
    "area_name",
    "region_or_country_name",
}


def normalise_column_name(column: str) -> str:
    """
    Convert a source heading to snake_case.

    Example
    -------
    ``Rental price one bed`` becomes ``rental_price_one_bed``.
    """

    cleaned = column.strip().lower()

    cleaned = re.sub(
        r"[^a-z0-9]+",
        "_",
        cleaned,
    )

    return cleaned.strip("_")


def load_raw_table(
    workbook_path: Path,
) -> pd.DataFrame:
    """Read the statistical table using the correct ONS header row."""

    logger.info(
        "Reading ONS Private Rent table from %s",
        workbook_path,
    )

    dataframe = pd.read_excel(
        workbook_path,
        sheet_name=SOURCE_SHEET,
        header=HEADER_ROW,
        engine="openpyxl",
    )

    logger.info(
        "Raw table loaded: %s rows x %s columns",
        f"{len(dataframe):,}",
        len(dataframe.columns),
    )

    return dataframe


def standardise_columns(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """Convert all source headings to CostScope snake_case names."""

    result = dataframe.copy()

    result.columns = [normalise_column_name(str(column)) for column in result.columns]

    logger.info(
        "Standardised %s column names",
        len(result.columns),
    )

    return result


def remove_empty_rows(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """Remove completely empty workbook rows."""

    before = len(dataframe)

    result = dataframe.dropna(
        how="all",
    ).copy()

    removed = before - len(result)

    logger.info(
        "Removed %s completely empty rows",
        f"{removed:,}",
    )

    return result


def standardise_text_columns(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Clean textual geography fields.

    ONS markers such as ``[z]`` are converted to missing values rather
    than being treated as genuine geography codes or names.
    """

    result = dataframe.copy()

    for column in TEXT_COLUMNS:
        if column not in result.columns:
            continue

        result[column] = result[column].astype("string").str.strip()

        result[column] = result[column].replace(
            list(ONS_MISSING_MARKERS),
            pd.NA,
        )

    return result


def parse_dates(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """Parse the ONS reporting-period column."""

    result = dataframe.copy()

    result["time_period"] = pd.to_datetime(
        result["time_period"],
        errors="coerce",
    )

    return result


def identify_numeric_columns(
    dataframe: pd.DataFrame,
) -> list[str]:
    """Return statistical measure columns."""

    non_numeric_columns = {
        "time_period",
        "area_code",
        "area_name",
        "region_or_country_name",
        "location_id",
    }

    return [column for column in dataframe.columns if column not in non_numeric_columns]


def convert_numeric_columns(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Convert statistical columns to numeric values.

    ONS markers such as [x] and [z] therefore become NaN rather than 0.
    """

    result = dataframe.copy()

    numeric_columns = identify_numeric_columns(result)

    for column in numeric_columns:
        result[column] = pd.to_numeric(
            result[column],
            errors="coerce",
        )

    logger.info(
        "Converted %s statistical columns to numeric values",
        len(numeric_columns),
    )

    return result


def create_location_id(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Create CostScope's stable source-geography identifier.

    Where ONS supplies an official area code, that code is used.

    Some Northern Ireland Broad Rental Market Areas do not have a code
    in this source. For those observations, CostScope uses a clearly
    namespaced fallback based on area name and parent geography.

    The fallback identifier is internal to CostScope and must never be
    presented as an official ONS geography code.
    """

    result = dataframe.copy()

    has_official_code = result["area_code"].notna() & result["area_code"].ne("")

    fallback_region = (
        result["region_or_country_name"].fillna("unknown").astype("string")
    )

    fallback_name = result["area_name"].fillna("unknown").astype("string")

    fallback_identifier = "name:" + fallback_region + ":" + fallback_name

    result["location_id"] = (
        result["area_code"]
        .where(
            has_official_code,
            fallback_identifier,
        )
        .astype("string")
    )

    logger.info(
        "Created geography identifiers: %s official-code rows, %s fallback rows",
        f"{int(has_official_code.sum()):,}",
        f"{int((~has_official_code).sum()):,}",
    )

    return result


def transform_private_rent(
    workbook_path: Path,
) -> pd.DataFrame:
    """Transform an ONS Bronze workbook into Silver form."""

    logger.info("=" * 70)
    logger.info("ONS Private Rent Silver transformation started")
    logger.info("=" * 70)

    dataframe = load_raw_table(
        workbook_path,
    )

    dataframe = standardise_columns(
        dataframe,
    )

    dataframe = remove_empty_rows(
        dataframe,
    )

    dataframe = standardise_text_columns(
        dataframe,
    )

    dataframe = parse_dates(
        dataframe,
    )

    dataframe = convert_numeric_columns(
        dataframe,
    )

    dataframe = create_location_id(
        dataframe,
    )

    logger.info(
        "Silver transformation completed: %s rows x %s columns",
        f"{len(dataframe):,}",
        len(dataframe.columns),
    )

    return dataframe


def write_silver_dataset(
    dataframe: pd.DataFrame,
) -> Path:
    """Write the validated Silver dataset as Parquet."""

    output_directory = settings.silver_path / "ons" / "private_rent"

    output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = output_directory / "private_rent.parquet"

    dataframe.to_parquet(
        output_path,
        index=False,
        engine="pyarrow",
    )

    logger.info(
        "Silver dataset written to %s",
        output_path,
    )

    return output_path
