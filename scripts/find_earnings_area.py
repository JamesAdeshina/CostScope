"""
Search the CostScope Silver earnings dataset by geography name or code.

Examples
--------

    python -m scripts.find_earnings_area derby
    python -m scripts.find_earnings_area E06000015
"""

from __future__ import annotations

import sys

import pandas as pd

from data_pipeline.transform.ons.earnings import (
    get_silver_earnings_path,
)


def main() -> None:
    """Search Silver earnings data."""

    if len(sys.argv) < 2:
        raise SystemExit("Usage: python -m scripts.find_earnings_area <query>")

    query = " ".join(sys.argv[1:]).strip()

    path = get_silver_earnings_path()

    if not path.exists():
        raise SystemExit(
            "Silver earnings dataset does not exist. "
            "Run `python -m scripts.build_earnings_silver` first."
        )

    dataframe = pd.read_parquet(path)

    mask = dataframe["area_name"].astype("string").str.contains(
        query,
        case=False,
        regex=False,
        na=False,
    ) | dataframe["area_code"].astype("string").str.contains(
        query,
        case=False,
        regex=False,
        na=False,
    )

    results = dataframe.loc[mask].copy()

    if results.empty:
        print(f"No earnings geographies found for: {query}")

        return

    columns = [
        "area_code",
        "area_name",
        "reference_year",
        "median_annual_pay",
        "median_annual_change_percent",
        "number_of_jobs_thousand",
    ]

    print(results[columns].to_string(index=False))


if __name__ == "__main__":
    main()
