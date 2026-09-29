"""
Development utility for inspecting the latest ONS Private Rent workbook.

Run from the repository root with:

    python -m scripts.inspect_ons_rent

The script prints:

1. Workbook worksheet structure.
2. The first raw rows from the statistical data worksheet.

This helps identify the real header row before Silver transformation.
"""

from pathlib import Path

import pandas as pd

from data_pipeline.config.settings import settings
from data_pipeline.quality.ons.inspect_private_rent import (
    inspect_raw_table_rows,
    inspect_workbook,
)
from data_pipeline.utils.logging_config import get_logger

logger = get_logger(__name__)


def find_latest_workbook() -> Path:
    """
    Find the latest downloaded ONS Private Rent workbook.

    Returns
    -------
    Path
        Most recently modified Bronze workbook.

    Raises
    ------
    FileNotFoundError
        If the Bronze layer does not yet contain a workbook.
    """

    bronze_root = settings.bronze_path / "ons" / "private_rent"

    logger.info(
        "Searching for ONS Private Rent workbooks under %s",
        bronze_root,
    )

    workbooks = list(bronze_root.rglob("price_index_private_rents.xlsx"))

    if not workbooks:
        raise FileNotFoundError(
            "No ONS Private Rent workbook found. "
            "Run `python -m data_pipeline.main` first."
        )

    latest_workbook = max(
        workbooks,
        key=lambda path: path.stat().st_mtime,
    )

    logger.info(
        "Latest workbook found: %s",
        latest_workbook,
    )

    return latest_workbook


def display_workbook_structure(
    structure: dict[str, list[str]],
) -> None:
    """Print worksheet names and preliminary columns."""

    print()
    print("=" * 90)
    print("ONS PRIVATE RENT WORKBOOK STRUCTURE")
    print("=" * 90)

    for sheet_name, columns in structure.items():
        print()
        print(f"Worksheet: {sheet_name}")
        print("-" * 90)

        for position, column in enumerate(
            columns,
            start=1,
        ):
            print(f"{position:>3}. {column}")


def display_raw_rows(
    dataframe: pd.DataFrame,
) -> None:
    """
    Print raw worksheet rows without truncating important values.

    Parameters
    ----------
    dataframe:
        Raw worksheet preview.
    """

    print()
    print("=" * 90)
    print("RAW TABLE 1 PREVIEW")
    print("=" * 90)

    # Keep the console readable while still exposing all columns.
    with pd.option_context(
        "display.max_columns",
        None,
        "display.max_rows",
        None,
        "display.width",
        300,
        "display.max_colwidth",
        60,
    ):
        print(
            dataframe.to_string(
                index=True,
                header=True,
            )
        )

    print()
    print("=" * 90)
    print(
        f"Preview dimensions: {len(dataframe)} rows x {len(dataframe.columns)} columns"
    )
    print("=" * 90)


def main() -> None:
    """Run detailed workbook inspection."""

    workbook_path = find_latest_workbook()

    structure = inspect_workbook(
        workbook_path,
    )

    display_workbook_structure(
        structure,
    )

    raw_preview = inspect_raw_table_rows(
        workbook_path,
        sheet_name="Table 1",
        row_count=25,
    )

    display_raw_rows(
        raw_preview,
    )


if __name__ == "__main__":
    main()
