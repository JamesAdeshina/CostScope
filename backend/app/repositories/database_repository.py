"""
PostgreSQL-backed CostScope repository.

PostgreSQL is the preferred serving layer when COSTSCOPE_DATABASE_URL
is configured.

The existing Parquet repository remains available as a development
fallback when no database connection is configured.
"""

from __future__ import annotations

import pandas as pd
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from backend.app.core.database import (
    database_configured,
    get_engine,
)
from backend.app.repositories import private_rent_repository as parquet_repository
from backend.app.repositories.private_rent_repository import (
    GoldDataNotBuiltError,
    LocationNotFoundError,
)

METRIC_ALIASES = {
    "rent": "RENT_MONTHLY",
    "monthly_rent": "RENT_MONTHLY",
    "rent_monthly": "RENT_MONTHLY",
    "rent_monthly_change": "RENT_MONTHLY_CHANGE",
    "rent_annual_change": "RENT_ANNUAL_CHANGE",
}


def _database_error(exc: Exception) -> GoldDataNotBuiltError:
    """Convert database failures into the repository's existing 503 error."""

    return GoldDataNotBuiltError(
        "CostScope PostgreSQL serving warehouse is unavailable. "
        "Verify COSTSCOPE_DATABASE_URL and the database load."
    )


def _location_payload(
    location: pd.Series,
) -> dict[str, object]:
    """Create the existing public location response shape."""

    official_code = location["official_area_code"]

    return {
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
    }


def search_locations(
    query: str,
    *,
    limit: int = 20,
) -> list[dict[str, object]]:
    """Search locations from PostgreSQL or fall back to Gold Parquet."""

    if not database_configured():
        return parquet_repository.search_locations(
            query,
            limit=limit,
        )

    query = query.strip()

    if not query:
        return []

    safe_limit = max(
        1,
        min(
            int(limit),
            100,
        ),
    )

    try:
        with get_engine().connect() as connection:
            rows = (
                connection.execute(
                    text(
                        """
                    SELECT
                        location_id,
                        official_area_code,
                        location_name,
                        region_or_country_name

                    FROM costscope.dim_location

                    WHERE
                        LOWER(location_name) LIKE :pattern
                        OR LOWER(
                            COALESCE(
                                official_area_code,
                                ''
                            )
                        ) LIKE :pattern

                    ORDER BY
                        location_name,
                        location_id

                    LIMIT :limit
                    """
                    ),
                    {
                        "pattern": f"%{query.lower()}%",
                        "limit": safe_limit,
                    },
                )
                .mappings()
                .all()
            )

    except SQLAlchemyError as exc:
        raise _database_error(exc) from exc

    return [
        {
            "location_id": str(row["location_id"]),
            "location_code": (
                str(row["official_area_code"])
                if row["official_area_code"] is not None
                else str(row["location_id"])
            ),
            "name": str(row["location_name"]),
            "region_or_country": (
                None
                if row["region_or_country_name"] is None
                else str(row["region_or_country_name"])
            ),
        }
        for row in rows
    ]


def find_location(
    location_code: str,
) -> pd.Series:
    """Find one location by official code or CostScope location ID."""

    if not database_configured():
        return parquet_repository.find_location(location_code)

    try:
        with get_engine().connect() as connection:
            row = (
                connection.execute(
                    text(
                        """
                    SELECT
                        location_key,
                        location_id,
                        official_area_code,
                        location_name,
                        region_or_country_name,
                        has_official_code

                    FROM costscope.dim_location

                    WHERE
                        location_id = :location_code
                        OR official_area_code = :location_code

                    ORDER BY
                        CASE
                            WHEN location_id = :location_code
                            THEN 0
                            ELSE 1
                        END

                    LIMIT 1
                    """
                    ),
                    {
                        "location_code": location_code,
                    },
                )
                .mappings()
                .first()
            )

    except SQLAlchemyError as exc:
        raise _database_error(exc) from exc

    if row is None:
        raise LocationNotFoundError(f"Location not found: {location_code}")

    return pd.Series(dict(row))


def get_latest_rent_overview(
    location_code: str,
) -> dict[str, object]:
    """Return latest private-rent overview."""

    if not database_configured():
        return parquet_repository.get_latest_rent_overview(location_code)

    location = find_location(location_code)

    location_key = int(location["location_key"])

    try:
        with get_engine().connect() as connection:
            latest = (
                connection.execute(
                    text(
                        """
                    SELECT
                        reference_period,
                        value,
                        unit,
                        source_code,
                        publisher,
                        dataset_name

                    FROM costscope.vw_cost_metrics

                    WHERE
                        location_key = :location_key
                        AND metric_code = 'RENT_MONTHLY'
                        AND is_published = TRUE

                    ORDER BY reference_period DESC

                    LIMIT 1
                    """
                    ),
                    {
                        "location_key": location_key,
                    },
                )
                .mappings()
                .first()
            )

            if latest is None:
                raise LocationNotFoundError(
                    f"No published rent observation for {location_code}."
                )

            change_rows = (
                connection.execute(
                    text(
                        """
                    SELECT
                        metric_code,
                        value

                    FROM costscope.vw_cost_metrics

                    WHERE
                        location_key = :location_key
                        AND reference_period = :reference_period
                        AND is_published = TRUE
                        AND metric_code IN (
                            'RENT_MONTHLY_CHANGE',
                            'RENT_ANNUAL_CHANGE'
                        )
                    """
                    ),
                    {
                        "location_key": location_key,
                        "reference_period": latest["reference_period"],
                    },
                )
                .mappings()
                .all()
            )

    except LocationNotFoundError:
        raise

    except SQLAlchemyError as exc:
        raise _database_error(exc) from exc

    change_lookup = {
        str(row["metric_code"]): float(row["value"])
        for row in change_rows
        if row["value"] is not None
    }

    return {
        "location": _location_payload(location),
        "rent": {
            "monthly_rent": float(latest["value"]),
            "unit": str(latest["unit"]),
            "reference_period": latest["reference_period"],
            "monthly_change_percent": (change_lookup.get("RENT_MONTHLY_CHANGE")),
            "annual_change_percent": (change_lookup.get("RENT_ANNUAL_CHANGE")),
        },
        "source": {
            "source_code": str(latest["source_code"]),
            "publisher": str(latest["publisher"]),
            "dataset": str(latest["dataset_name"]),
        },
    }


def get_latest_earnings_overview(
    location_code: str,
) -> dict[str, object] | None:
    """Return latest published ASHE earnings."""

    if not database_configured():
        return parquet_repository.get_latest_earnings_overview(location_code)

    location = find_location(location_code)

    location_key = int(location["location_key"])

    try:
        with get_engine().connect() as connection:
            latest = (
                connection.execute(
                    text(
                        """
                    SELECT
                        reference_period,
                        value

                    FROM costscope.vw_cost_metrics

                    WHERE
                        location_key = :location_key
                        AND metric_code = 'EARNINGS_ANNUAL'
                        AND is_published = TRUE

                    ORDER BY reference_period DESC

                    LIMIT 1
                    """
                    ),
                    {
                        "location_key": location_key,
                    },
                )
                .mappings()
                .first()
            )

            if latest is None:
                return None

            change = connection.execute(
                text(
                    """
                    SELECT value

                    FROM costscope.vw_cost_metrics

                    WHERE
                        location_key = :location_key
                        AND metric_code = 'EARNINGS_ANNUAL_CHANGE'
                        AND reference_period = :reference_period
                        AND is_published = TRUE

                    LIMIT 1
                    """
                ),
                {
                    "location_key": location_key,
                    "reference_period": latest["reference_period"],
                },
            ).scalar_one_or_none()

    except SQLAlchemyError as exc:
        raise _database_error(exc) from exc

    return {
        "median_annual_pay": float(latest["value"]),
        "unit": "GBP/year",
        "reference_period": latest["reference_period"],
        "annual_change_percent": (None if change is None else float(change)),
    }


def get_metric_history(
    location_code: str,
    metric: str,
) -> dict[str, object]:
    """Return historical metric observations."""

    if not database_configured():
        return parquet_repository.get_metric_history(
            location_code,
            metric,
        )

    location = find_location(location_code)

    requested_metric = metric.strip().lower()

    canonical_code = METRIC_ALIASES.get(
        requested_metric,
        metric.strip().upper(),
    )

    try:
        with get_engine().connect() as connection:
            metric_row = (
                connection.execute(
                    text(
                        """
                    SELECT
                        metric_key,
                        metric_code,
                        metric_name,
                        unit

                    FROM costscope.dim_metric

                    WHERE metric_code = :metric_code

                    LIMIT 1
                    """
                    ),
                    {
                        "metric_code": canonical_code,
                    },
                )
                .mappings()
                .first()
            )

            if metric_row is None:
                raise LocationNotFoundError(f"Metric not found: {metric}")

            observations = (
                connection.execute(
                    text(
                        """
                    SELECT
                        reference_period,
                        value,
                        source_code,
                        publisher,
                        dataset_name

                    FROM costscope.vw_cost_metrics

                    WHERE
                        location_key = :location_key
                        AND metric_code = :metric_code
                        AND is_published = TRUE

                    ORDER BY reference_period
                    """
                    ),
                    {
                        "location_key": int(location["location_key"]),
                        "metric_code": canonical_code,
                    },
                )
                .mappings()
                .all()
            )

    except LocationNotFoundError:
        raise

    except SQLAlchemyError as exc:
        raise _database_error(exc) from exc

    source = {
        "source_code": "ONS_PIPR",
        "publisher": ("Office for National Statistics"),
        "dataset": ("Price Index of Private Rents, UK: monthly price statistics"),
    }

    if observations:
        first = observations[0]

        source = {
            "source_code": str(first["source_code"]),
            "publisher": str(first["publisher"]),
            "dataset": str(first["dataset_name"]),
        }

    return {
        "location": _location_payload(location),
        "metric_code": str(metric_row["metric_code"]),
        "metric_name": str(metric_row["metric_name"]),
        "unit": str(metric_row["unit"]),
        "observations": [
            {
                "reference_period": row["reference_period"],
                "value": float(row["value"]),
            }
            for row in observations
        ],
        "source": source,
    }


def get_location_overview(
    location_code: str,
) -> dict[str, object]:
    """Return local CostScope overview from PostgreSQL."""

    if not database_configured():
        return parquet_repository.get_location_overview(location_code)

    location = find_location(location_code)

    rent_payload = None

    try:
        rent_payload = get_latest_rent_overview(location_code).get("rent")

    except LocationNotFoundError:
        rent_payload = None

    earnings_payload = get_latest_earnings_overview(location_code)

    sources: list[dict[str, str]] = []

    if rent_payload is not None:
        sources.append(
            {
                "source_code": "ONS_PIPR",
                "publisher": ("Office for National Statistics"),
                "dataset": (
                    "Price Index of Private Rents, UK: monthly price statistics"
                ),
            }
        )

    if earnings_payload is not None:
        sources.append(
            {
                "source_code": "ONS_ASHE",
                "publisher": ("Office for National Statistics"),
                "dataset": (
                    "Earnings and hours worked, "
                    "place of residence by local authority: "
                    "ASHE Table 8"
                ),
            }
        )

    return {
        "location": _location_payload(location),
        "rent": rent_payload,
        "earnings": earnings_payload,
        "sources": sources,
    }
