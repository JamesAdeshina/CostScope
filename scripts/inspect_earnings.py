"""
Inspect the latest ONS ASHE Table 8.7a workbook.

The output identifies:

- available worksheet names
- the opening rows of the Full-Time worksheet
- rows containing "Median"
- rows containing "Derby"

Run with:

    python -m scripts.inspect_earnings
"""

from __future__ import annotations

import pandas as pd

from data_pipeline.quality.ons.inspect_earnings import (
    detect_median_header_rows,
    find_rows_containing,
    get_sheet_names,
    read_raw_full_time_sheet,
)
from data_pipeline.utils.earnings import (
    find_latest_earnings_workbook,
)
from data_pipeline.utils.logging_config import get_logger

logger = get_logger(__name__)


def print_dataframe(
    dataframe: pd.DataFrame,
) -> None:
    """Print a dataframe without hiding columns."""

    with pd.option_context(
        "display.max_columns",
        None,
        "display.max_rows",
        100,
        "display.width",
        300,
        "display.max_colwidth",
        80,
    ):
        print(
            dataframe.to_string(
                index=True,
                header=True,
            )
        )


def main() -> None:
    """Inspect the latest ASHE earnings workbook."""

    workbook_path = find_latest_earnings_workbook()

    logger.info(
        "Inspecting ASHE workbook: %s",
        workbook_path,
    )

    sheet_names = get_sheet_names(workbook_path)

    print()
    print("=" * 100)
    print("ASHE WORKBOOK SHEETS")
    print("=" * 100)

    for sheet_name in sheet_names:
        print(f"  - {sheet_name}")

    dataframe = read_raw_full_time_sheet(workbook_path)

    print()
    print("=" * 100)
    print("FULL-TIME SHEET - FIRST 30 RAW ROWS")
    print("=" * 100)

    print_dataframe(dataframe.head(30))

    median_rows = detect_median_header_rows(dataframe)

    print()
    print("=" * 100)
    print("ROWS CONTAINING 'MEDIAN'")
    print("=" * 100)
    print(median_rows)

    if median_rows:
        start = max(
            median_rows[0] - 3,
            0,
        )

        end = min(
            median_rows[0] + 8,
            len(dataframe),
        )

        print_dataframe(dataframe.iloc[start:end])

    derby_rows = find_rows_containing(
        dataframe,
        "Derby",
    )

    print()
    print("=" * 100)
    print("ROWS CONTAINING 'DERBY'")
    print("=" * 100)

    if derby_rows.empty:
        print("No Derby rows detected.")

    else:
        print_dataframe(derby_rows)

    print()
    print("=" * 100)
    print(
        f"Workbook dimensions: "
        f"{len(dataframe):,} rows x "
        f"{len(dataframe.columns)} columns"
    )
    print("=" * 100)


if __name__ == "__main__":
    main()
