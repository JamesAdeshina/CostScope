"""
Inspection utilities for the ONS ASHE earnings workbook.

ASHE spreadsheets contain titles, notes and multi-row headings.
Before transformation, CostScope inspects the published structure rather
than assuming fixed row positions.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from data_pipeline.config.sources import (
    ONS_ASHE_TARGET_SHEET,
)
from data_pipeline.utils.logging_config import get_logger

logger = get_logger(__name__)


def get_sheet_names(
    workbook_path: Path,
) -> list[str]:
    """Return workbook worksheet names."""

    excel_file = pd.ExcelFile(
        workbook_path,
        engine="openpyxl",
    )

    return excel_file.sheet_names


def read_raw_full_time_sheet(
    workbook_path: Path,
    *,
    rows: int | None = None,
) -> pd.DataFrame:
    """
    Read the Full-Time worksheet without interpreting a header row.

    This preserves the exact worksheet structure for inspection.
    """

    logger.info(
        "Reading ASHE worksheet '%s'",
        ONS_ASHE_TARGET_SHEET,
    )

    dataframe = pd.read_excel(
        workbook_path,
        sheet_name=ONS_ASHE_TARGET_SHEET,
        header=None,
        nrows=rows,
        engine="openpyxl",
    )

    logger.info(
        "ASHE raw sheet loaded: %s rows x %s columns",
        f"{len(dataframe):,}",
        len(dataframe.columns),
    )

    return dataframe


def find_rows_containing(
    dataframe: pd.DataFrame,
    search_term: str,
) -> pd.DataFrame:
    """Return worksheet rows containing a case-insensitive term."""

    search_term = search_term.strip().lower()

    mask = dataframe.apply(
        lambda row: (
            row.astype("string")
            .str.lower()
            .str.contains(
                search_term,
                regex=False,
                na=False,
            )
            .any()
        ),
        axis=1,
    )

    return dataframe.loc[mask].copy()


def detect_median_header_rows(
    dataframe: pd.DataFrame,
) -> list[int]:
    """Return row indexes containing the word 'Median'."""

    matches = find_rows_containing(
        dataframe,
        "Median",
    )

    return [int(index) for index in matches.index]
