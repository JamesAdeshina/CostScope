"""
Diagnose duplicate observations in the ONS Private Rent dataset.

The Silver quality gate currently assumes that one geography should have
one observation per reporting period:

    time_period + area_code

This script determines whether duplicate keys are:

1. exact duplicate source rows, or
2. conflicting observations that require a richer business key.

Run with:

    python -m scripts.diagnose_private_rent_duplicates
"""

from __future__ import annotations

import pandas as pd

from data_pipeline.transform.ons.private_rent import transform_private_rent
from data_pipeline.utils.bronze import find_latest_private_rent_workbook
from data_pipeline.utils.logging_config import get_logger

logger = get_logger(__name__)


KEY_COLUMNS = [
    "time_period",
    "area_code",
]


def find_duplicate_rows(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """Return every row belonging to a duplicated observation key."""

    duplicate_mask = dataframe.duplicated(
        subset=KEY_COLUMNS,
        keep=False,
    )

    return (
        dataframe.loc[duplicate_mask]
        .sort_values(
            KEY_COLUMNS
            + [
                "area_name",
                "region_or_country_name",
            ]
        )
        .copy()
    )


def classify_duplicate_groups(
    duplicates: pd.DataFrame,
) -> tuple[int, int]:
    """
    Count exact and conflicting duplicate groups.

    Returns
    -------
    tuple[int, int]
        Number of exact-duplicate groups and conflicting groups.
    """

    exact_groups = 0
    conflicting_groups = 0

    for _, group in duplicates.groupby(
        KEY_COLUMNS,
        dropna=False,
    ):
        unique_rows = group.drop_duplicates()

        if len(unique_rows) == 1:
            exact_groups += 1
        else:
            conflicting_groups += 1

    return exact_groups, conflicting_groups


def build_duplicate_summary(
    duplicates: pd.DataFrame,
) -> pd.DataFrame:
    """Summarise duplicated geography-period combinations."""

    summary = (
        duplicates.groupby(
            [
                "area_code",
                "area_name",
                "region_or_country_name",
            ],
            dropna=False,
        )
        .agg(
            duplicate_rows=("time_period", "size"),
            periods=("time_period", "nunique"),
            first_period=("time_period", "min"),
            last_period=("time_period", "max"),
        )
        .reset_index()
        .sort_values(
            [
                "duplicate_rows",
                "area_name",
            ],
            ascending=[
                False,
                True,
            ],
        )
    )

    return summary


def display_example_groups(
    duplicates: pd.DataFrame,
    *,
    max_groups: int = 10,
) -> None:
    """Print a sample of duplicate groups for manual inspection."""

    print()
    print("=" * 100)
    print("SAMPLE DUPLICATE GROUPS")
    print("=" * 100)

    grouped = duplicates.groupby(
        KEY_COLUMNS,
        dropna=False,
        sort=True,
    )

    for position, (key, group) in enumerate(
        grouped,
        start=1,
    ):
        if position > max_groups:
            break

        time_period, area_code = key

        print()
        print("-" * 100)
        print(f"Group {position}: time_period={time_period}, area_code={area_code}")
        print("-" * 100)

        display_columns = [
            "time_period",
            "area_code",
            "area_name",
            "region_or_country_name",
            "index",
            "monthly_change",
            "annual_change",
            "rental_price",
        ]

        print(
            group[display_columns].to_string(
                index=False,
            )
        )


def main() -> None:
    """Run duplicate analysis."""

    logger.info("=" * 70)
    logger.info("Diagnosing ONS Private Rent duplicate observations")
    logger.info("=" * 70)

    workbook_path = find_latest_private_rent_workbook()

    dataframe = transform_private_rent(
        workbook_path,
    )

    duplicates = find_duplicate_rows(
        dataframe,
    )

    duplicate_groups = duplicates.groupby(
        KEY_COLUMNS,
        dropna=False,
    ).ngroups

    exact_groups, conflicting_groups = classify_duplicate_groups(duplicates)

    print()
    print("=" * 100)
    print("PRIVATE RENT DUPLICATE DIAGNOSTIC")
    print("=" * 100)

    print(f"Total Silver candidate rows : {len(dataframe):,}")
    print(f"Rows in duplicate groups   : {len(duplicates):,}")
    print(f"Duplicate key groups       : {duplicate_groups:,}")
    print(f"Exact duplicate groups     : {exact_groups:,}")
    print(f"Conflicting groups         : {conflicting_groups:,}")

    summary = build_duplicate_summary(duplicates)

    print()
    print("=" * 100)
    print("DUPLICATE GEOGRAPHY SUMMARY")
    print("=" * 100)

    print(
        summary.head(30).to_string(
            index=False,
        )
    )

    display_example_groups(
        duplicates,
        max_groups=10,
    )


if __name__ == "__main__":
    main()
