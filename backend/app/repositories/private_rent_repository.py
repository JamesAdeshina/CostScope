"""
Repository for querying CostScope Gold Private Rent data.

For the current local-review milestone the API queries Gold Parquet
files directly.

The repository boundary allows PostgreSQL to replace this implementation
without changing route or service behaviour.
"""

from __future__ import annotations

from functools import lru_cache

import pandas as pd

from backend.app.core.config import settings


class GoldDataNotBuiltError(RuntimeError):
    """Raised when required Gold artifacts do not exist."""


class LocationNotFoundError(LookupError):
    """Raised when a requested location cannot be found."""


@lru_cache(maxsize=1)
def load_gold_tables() -> dict[str, pd.DataFrame]:
    """Load CostScope Gold tables once per API process."""

    root = settings.gold_path / "cost_scope"

    table_names = [
        "dim_location",
        "dim_date",
        "dim_metric",
        "fact_cost_metric",
    ]

    tables: dict[str, pd.DataFrame] = {}

    for table_name in table_names:
        path = root / f"{table_name}.parquet"

        if not path.exists():
            raise GoldDataNotBuiltError(
                f"Gold table not found: {path}. "
                "Run `python -m scripts.build_private_rent_gold` first."
            )

        tables[table_name] = pd.read_parquet(
            path,
            engine="pyarrow",
        )

    return tables


def search_locations(
    query: str,
    *,
    limit: int = 20,
) -> list[dict[str, object]]:
    """Search Gold locations by name or official geography code."""

    locations = load_gold_tables()["dim_location"]

    query = query.strip()

    if not query:
        return []

    name_match = (
        locations["location_name"]
        .astype("string")
        .str.contains(
            query,
            case=False,
            na=False,
            regex=False,
        )
    )

    code_match = (
        locations["official_area_code"]
        .astype("string")
        .str.contains(
            query,
            case=False,
            na=False,
            regex=False,
        )
    )

    matches = (
        locations.loc[name_match | code_match]
        .sort_values(
            [
                "location_name",
                "location_id",
            ]
        )
        .head(limit)
    )

    results: list[dict[str, object]] = []

    for _, row in matches.iterrows():
        official_code = row["official_area_code"]

        location_code = (
            str(official_code) if pd.notna(official_code) else str(row["location_id"])
        )

        results.append(
            {
                "location_id": str(row["location_id"]),
                "location_code": location_code,
                "name": str(row["location_name"]),
                "region_or_country": (
                    None
                    if pd.isna(row["region_or_country_name"])
                    else str(row["region_or_country_name"])
                ),
            }
        )

    return results


def find_location(
    location_code: str,
) -> pd.Series:
    """Find one location by official code or internal location ID."""

    locations = load_gold_tables()["dim_location"]

    matches = locations.loc[
        (locations["location_id"].astype(str) == location_code)
        | (locations["official_area_code"].astype(str) == location_code)
    ]

    if matches.empty:
        raise LocationNotFoundError(f"Location not found: {location_code}")

    return matches.iloc[0]


def get_latest_rent_overview(
    location_code: str,
) -> dict[str, object]:
    """Return the latest headline rent observation for a location."""

    tables = load_gold_tables()

    location = find_location(location_code)

    facts = tables["fact_cost_metric"]

    metrics = tables["dim_metric"]

    dates = tables["dim_date"]

    metric_lookup = metrics.set_index("metric_code")["metric_key"].to_dict()

    rent_metric_key = metric_lookup["RENT_MONTHLY"]

    location_key = int(location["location_key"])

    rent_rows = facts.loc[
        (facts["location_key"] == location_key)
        & (facts["metric_key"] == rent_metric_key)
        & (facts["is_published"])
    ]

    if rent_rows.empty:
        raise LocationNotFoundError(
            f"No published rent observation for {location_code}."
        )

    latest_rent = rent_rows.sort_values("date_key").iloc[-1]

    latest_date_key = int(latest_rent["date_key"])

    period_facts = facts.loc[
        (facts["location_key"] == location_key) & (facts["date_key"] == latest_date_key)
    ]

    def metric_value(
        metric_code: str,
    ) -> float | None:
        metric_key = metric_lookup[metric_code]

        rows = period_facts.loc[
            (period_facts["metric_key"] == metric_key) & (period_facts["is_published"])
        ]

        if rows.empty:
            return None

        return float(rows.iloc[0]["value"])

    date_row = dates.loc[dates["date_key"] == latest_date_key].iloc[0]

    metric_row = metrics.loc[metrics["metric_key"] == rent_metric_key].iloc[0]

    official_code = location["official_area_code"]

    return {
        "location": {
            "location_id": str(location["location_id"]),
            "location_code": (
                str(official_code)
                if pd.notna(official_code)
                else str(location["location_id"])
            ),
            "name": str(location["location_name"]),
            "region_or_country": (
                None
                if pd.isna(location["region_or_country_name"])
                else str(location["region_or_country_name"])
            ),
        },
        "rent": {
            "monthly_rent": float(latest_rent["value"]),
            "unit": str(metric_row["unit"]),
            "reference_period": (pd.Timestamp(date_row["date"]).date()),
            "monthly_change_percent": (metric_value("RENT_MONTHLY_CHANGE")),
            "annual_change_percent": (metric_value("RENT_ANNUAL_CHANGE")),
        },
        "source": {
            "source_code": "ONS_PIPR",
            "publisher": ("Office for National Statistics"),
            "dataset": ("Price Index of Private Rents, UK: monthly price statistics"),
        },
    }


def get_metric_history(
    location_code: str,
    metric: str,
) -> dict[str, object]:
    """
    Return historical observations for one location and metric.

    Parameters
    ----------
    location_code:
        Official geography code or internal CostScope location ID.

    metric:
        Public metric alias or canonical metric code.

    Returns
    -------
    dict
        Location metadata, metric metadata and ordered observations.
    """

    tables = load_gold_tables()

    location = find_location(location_code)

    facts = tables["fact_cost_metric"]

    metrics = tables["dim_metric"]

    dates = tables["dim_date"]

    metric_aliases = {
        "rent": "RENT_MONTHLY",
        "monthly_rent": "RENT_MONTHLY",
        "rent_monthly": "RENT_MONTHLY",
        "rent_monthly_change": "RENT_MONTHLY_CHANGE",
        "rent_annual_change": "RENT_ANNUAL_CHANGE",
    }

    requested_metric = metric.strip().lower()

    canonical_code = metric_aliases.get(
        requested_metric,
        metric.strip().upper(),
    )

    metric_rows = metrics.loc[metrics["metric_code"] == canonical_code]

    if metric_rows.empty:
        raise LocationNotFoundError(f"Metric not found: {metric}")

    metric_row = metric_rows.iloc[0]

    location_key = int(location["location_key"])

    metric_key = int(metric_row["metric_key"])

    history = facts.loc[
        (facts["location_key"] == location_key)
        & (facts["metric_key"] == metric_key)
        & (facts["is_published"])
    ].copy()

    history = history.merge(
        dates[
            [
                "date_key",
                "date",
            ]
        ],
        on="date_key",
        how="left",
        validate="many_to_one",
    )

    history = history.sort_values("date")

    official_code = location["official_area_code"]

    observations = [
        {
            "reference_period": (pd.Timestamp(row["date"]).date()),
            "value": float(row["value"]),
        }
        for _, row in history.iterrows()
    ]

    return {
        "location": {
            "location_id": str(location["location_id"]),
            "location_code": (
                str(official_code)
                if pd.notna(official_code)
                else str(location["location_id"])
            ),
            "name": str(location["location_name"]),
            "region_or_country": (
                None
                if pd.isna(location["region_or_country_name"])
                else str(location["region_or_country_name"])
            ),
        },
        "metric_code": str(metric_row["metric_code"]),
        "metric_name": str(metric_row["metric_name"]),
        "unit": str(metric_row["unit"]),
        "observations": observations,
        "source": {
            "source_code": "ONS_PIPR",
            "publisher": ("Office for National Statistics"),
            "dataset": ("Price Index of Private Rents, UK: monthly price statistics"),
        },
    }
