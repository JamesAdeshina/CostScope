"""
Inspection utilities for the ONS Private Rent workbook.

The ONS workbook contains descriptive title rows and notes before the
actual tabular header. These utilities inspect the source without making
assumptions about where the real header begins.

No transformation is performed here.
"""

from pathlib import Path

import pandas as pd

from data_pipeline.utils.logging_config import get_logger

logger = get_logger(__name__)


def inspect_workbook(
    workbook_path: Path,
) -> dict[str, list[str]]:
    """
    Inspect workbook worksheet names and preliminary columns.

    Parameters
    ----------
    workbook_path:
        Path to the downloaded ONS XLSX workbook.

    Returns
    -------
    dict[str, list[str]]
        Mapping of worksheet names to preliminary column names.
    """

    logger.info(
        "Inspecting workbook: %s",
        workbook_path,
    )

    excel_file = pd.ExcelFile(
        workbook_path,
        engine="openpyxl",
    )

    logger.info(
        "Workbook contains %s worksheets",
        len(excel_file.sheet_names),
    )

    structure: dict[str, list[str]] = {}

    for sheet_name in excel_file.sheet_names:
        logger.info(
            "Inspecting sheet: %s",
            sheet_name,
        )

        preview = pd.read_excel(
            workbook_path,
            sheet_name=sheet_name,
            nrows=10,
            engine="openpyxl",
        )

        structure[sheet_name] = [str(column) for column in preview.columns]

        logger.info(
            "Sheet '%s': %s rows previewed, %s columns detected",
            sheet_name,
            len(preview),
            len(preview.columns),
        )

    return structure


def inspect_raw_table_rows(
    workbook_path: Path,
    *,
    sheet_name: str = "Table 1",
    row_count: int = 25,
) -> pd.DataFrame:
    """
    Read raw worksheet rows without treating any row as a header.

    This allows us to identify the exact row containing the true column
    names before writing transformation logic.

    Parameters
    ----------
    workbook_path:
        Path to the ONS workbook.

    sheet_name:
        Worksheet containing the statistical table.

    row_count:
        Number of rows to inspect.

    Returns
    -------
    pandas.DataFrame
        Raw worksheet preview with integer column positions.
    """

    logger.info(
        "Reading first %s raw rows from worksheet '%s'",
        row_count,
        sheet_name,
    )

    raw_preview = pd.read_excel(
        workbook_path,
        sheet_name=sheet_name,
        header=None,
        nrows=row_count,
        engine="openpyxl",
    )

    logger.info(
        "Raw preview loaded: %s rows x %s columns",
        len(raw_preview),
        len(raw_preview.columns),
    )

    return raw_preview
