"""
Search the ONS Private Rent Silver dataset by geography.

Examples
--------
python -m scripts.find_private_rent_area Derby
python -m scripts.find_private_rent_area Nottingham
python -m scripts.find_private_rent_area London
"""

from __future__ import annotations

import argparse

import pandas as pd

from data_pipeline.config.settings import settings


def load_silver_dataset() -> pd.DataFrame:
    """Load the Silver Private Rent Parquet dataset."""

    path = settings.silver_path / "ons" / "private_rent" / "private_rent.parquet"

    if not path.exists():
        raise FileNotFoundError(
            "Silver Private Rent dataset not found. "
            "Run `python -m scripts.build_private_rent_silver` first."
        )

    return pd.read_parquet(
        path,
        engine="pyarrow",
    )


def search_area(
    dataframe: pd.DataFrame,
    query: str,
) -> pd.DataFrame:
    """
    Search area names using case-insensitive partial matching.

    Parameters
    ----------
    dataframe:
        Silver rent dataset.

    query:
        Location text supplied by the user.

    Returns
    -------
    pandas.DataFrame
        Matching geography-period observations.
    """

    mask = (
        dataframe["area_name"]
        .astype("string")
        .str.contains(
            query,
            case=False,
            na=False,
            regex=False,
        )
    )

    return dataframe.loc[mask].copy()


def main() -> None:
    """Run CLI geography search."""

    parser = argparse.ArgumentParser(
        description=("Search CostScope ONS Private Rent data by geography.")
    )

    parser.add_argument(
        "query",
        help="Location name, for example Derby",
    )

    args = parser.parse_args()

    dataframe = load_silver_dataset()

    matches = search_area(
        dataframe,
        args.query,
    )

    if matches.empty:
        print(f"No geography matching '{args.query}' was found.")
        return

    geography_summary = (
        matches[
            [
                "area_code",
                "area_name",
                "region_or_country_name",
            ]
        ]
        .drop_duplicates()
        .sort_values(
            [
                "area_name",
                "area_code",
            ]
        )
    )

    print()
    print("=" * 80)
    print(f"GEOGRAPHIES MATCHING: {args.query}")
    print("=" * 80)

    print(geography_summary.to_string(index=False))

    print()
    print("=" * 80)
    print("LATEST RENT OBSERVATIONS")
    print("=" * 80)

    latest = (
        matches.sort_values("time_period")
        .groupby(
            [
                "area_code",
                "area_name",
            ],
            as_index=False,
        )
        .tail(1)
    )

    display_columns = [
        "time_period",
        "area_code",
        "area_name",
        "region_or_country_name",
        "rental_price",
        "monthly_change",
        "annual_change",
    ]

    print(latest[display_columns].to_string(index=False))


if __name__ == "__main__":
    main()
