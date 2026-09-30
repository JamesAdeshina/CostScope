"""
Load CostScope Gold Parquet tables into PostgreSQL.

Loading strategy
----------------
The Gold layer is a reproducible derived dataset, so the MVP PostgreSQL
warehouse uses a transactional full refresh:

    Gold Parquet
        ↓
    TRUNCATE serving warehouse
        ↓
    Load dimensions
        ↓
    Load source dimension
        ↓
    Load facts
        ↓
    Validate row counts / foreign keys / Derby values

This keeps repeated loads deterministic and simple.

Incremental loading can be introduced later when CostScope data volume
requires it.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from sqlalchemy import Connection, Engine, text
from tqdm import tqdm

from backend.app.core.database import get_engine
from data_pipeline.config.settings import settings
from data_pipeline.utils.logging_config import get_logger

logger = get_logger(__name__)


GOLD_DIRECTORY = settings.gold_path / "cost_scope"

SCHEMA_PATH = Path("sql/schema/002_costscope_postgres.sql")

DATABASE_SCHEMA = "costscope"

LOAD_CHUNK_SIZE = 25_000


SOURCE_RECORDS = [
    {
        "source_id": 1,
        "source_code": "ONS_PIPR",
        "publisher": ("Office for National Statistics"),
        "dataset_name": ("Price Index of Private Rents, UK: monthly price statistics"),
        "source_system": "ONS",
        "geography_note": ("Local-area private rent geography as published by ONS."),
        "source_url": ("https://www.ons.gov.uk/"),
    },
    {
        "source_id": 2,
        "source_code": "ONS_ASHE",
        "publisher": ("Office for National Statistics"),
        "dataset_name": (
            "Earnings and hours worked, "
            "place of residence by local authority: "
            "ASHE Table 8"
        ),
        "source_system": "ONS",
        "geography_note": ("Resident geography from ASHE Table 8."),
        "source_url": ("https://www.ons.gov.uk/"),
    },
    {
        "source_id": 3,
        "source_code": "ONS_CPI_MM23",
        "publisher": ("Office for National Statistics"),
        "dataset_name": ("Consumer price inflation time series"),
        "source_system": "ONS",
        "geography_note": ("United Kingdom level CPI."),
        "source_url": ("https://www.ons.gov.uk/"),
    },
    {
        "source_id": 4,
        "source_code": ("NOMIS_UNEMPLOYMENT_MODEL"),
        "publisher": ("Office for National Statistics"),
        "dataset_name": ("Model-based estimates of unemployment"),
        "source_system": "Nomis",
        "geography_note": ("Local-authority model-based unemployment."),
        "source_url": ("https://www.nomisweb.co.uk/"),
    },
]


EXPECTED_FILES = {
    "dim_location": ("dim_location.parquet"),
    "dim_date": ("dim_date.parquet"),
    "dim_metric": ("dim_metric.parquet"),
    "fact_cost_metric": ("fact_cost_metric.parquet"),
}


def load_gold_parquet_tables() -> dict[
    str,
    pd.DataFrame,
]:
    """Load all required CostScope Gold tables."""

    tables: dict[str, pd.DataFrame] = {}

    for (
        table_name,
        filename,
    ) in EXPECTED_FILES.items():
        path = GOLD_DIRECTORY / filename

        if not path.exists():
            raise FileNotFoundError(f"Required Gold table is missing: {path}")

        dataframe = pd.read_parquet(path)

        tables[table_name] = dataframe

        logger.info(
            "Gold source loaded: %-20s %s rows",
            table_name,
            f"{len(dataframe):,}",
        )

    return tables


def prepare_dim_location(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """Prepare Gold location dimension for PostgreSQL."""

    expected = [
        "location_key",
        "location_id",
        "official_area_code",
        "location_name",
        "region_or_country_name",
        "has_official_code",
    ]

    missing = set(expected) - set(dataframe.columns)

    if missing:
        raise ValueError(f"dim_location is missing columns: {sorted(missing)}")

    result = dataframe[expected].copy()

    result["location_key"] = pd.to_numeric(
        result["location_key"],
        errors="raise",
    ).astype("int64")

    result["has_official_code"] = result["has_official_code"].fillna(False).astype(bool)

    return result


def prepare_dim_date(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """Prepare Gold date dimension."""

    expected = [
        "date_key",
        "date",
        "year",
        "quarter",
        "month",
        "month_name",
    ]

    missing = set(expected) - set(dataframe.columns)

    if missing:
        raise ValueError(f"dim_date is missing columns: {sorted(missing)}")

    result = dataframe[expected].copy()

    result["date"] = pd.to_datetime(
        result["date"],
        errors="raise",
    ).dt.date

    for column in (
        "date_key",
        "year",
        "quarter",
        "month",
    ):
        result[column] = pd.to_numeric(
            result[column],
            errors="raise",
        ).astype(int)

    return result


def prepare_dim_metric(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """Prepare Gold metric dimension."""

    result = dataframe.copy()

    required = {
        "metric_key",
        "metric_code",
        "metric_name",
        "unit",
    }

    missing = required - set(result.columns)

    if missing:
        raise ValueError(f"dim_metric is missing columns: {sorted(missing)}")

    if "category" not in result.columns:
        result["category"] = pd.NA

    result = result[
        [
            "metric_key",
            "metric_code",
            "metric_name",
            "unit",
            "category",
        ]
    ]

    result["metric_key"] = pd.to_numeric(
        result["metric_key"],
        errors="raise",
    ).astype(int)

    return result


def prepare_dim_source() -> pd.DataFrame:
    """Create the CostScope source dimension."""

    return pd.DataFrame(SOURCE_RECORDS)


def prepare_fact_cost_metric(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """Prepare CostScope central fact table."""

    expected = [
        "fact_id",
        "date_key",
        "location_key",
        "metric_key",
        "value",
        "is_published",
        "source_id",
        "loaded_at",
    ]

    missing = set(expected) - set(dataframe.columns)

    if missing:
        raise ValueError(f"fact_cost_metric is missing columns: {sorted(missing)}")

    result = dataframe[expected].copy()

    for column in (
        "fact_id",
        "date_key",
        "location_key",
        "metric_key",
        "source_id",
    ):
        result[column] = pd.to_numeric(
            result[column],
            errors="raise",
        ).astype("int64")

    result["value"] = pd.to_numeric(
        result["value"],
        errors="coerce",
    )

    result["is_published"] = result["is_published"].fillna(False).astype(bool)

    result["loaded_at"] = pd.to_datetime(
        result["loaded_at"],
        utc=True,
        errors="raise",
    )

    return result


def execute_schema(
    connection: Connection,
) -> None:
    """Create CostScope PostgreSQL schema and objects."""

    if not SCHEMA_PATH.exists():
        raise FileNotFoundError(f"PostgreSQL schema file not found: {SCHEMA_PATH}")

    sql_text = SCHEMA_PATH.read_text(encoding="utf-8")

    statements = [
        statement.strip() for statement in sql_text.split(";") if statement.strip()
    ]

    logger.info(
        "Applying PostgreSQL schema: %s",
        SCHEMA_PATH,
    )

    for statement in statements:
        connection.exec_driver_sql(statement)


def load_dataframe(
    dataframe: pd.DataFrame,
    *,
    table_name: str,
    connection: Connection,
    chunk_size: int = (LOAD_CHUNK_SIZE),
) -> None:
    """
    Load one DataFrame using bounded chunks.

    The progress bar is particularly useful for the 550k+ row fact table.
    """

    total_rows = len(dataframe)

    if total_rows == 0:
        logger.warning(
            "Skipping empty table: %s",
            table_name,
        )
        return

    logger.info(
        "Loading %-20s %s rows",
        table_name,
        f"{total_rows:,}",
    )

    ranges = range(
        0,
        total_rows,
        chunk_size,
    )

    for start in tqdm(
        ranges,
        desc=table_name,
        unit="chunk",
    ):
        chunk = dataframe.iloc[start : (start + chunk_size)]

        chunk.to_sql(
            name=table_name,
            con=connection,
            schema=DATABASE_SCHEMA,
            if_exists="append",
            index=False,
            method=None,
        )


def truncate_warehouse(
    connection: Connection,
) -> None:
    """Remove previous derived warehouse contents."""

    logger.info("Truncating CostScope PostgreSQL warehouse")

    connection.execute(
        text(
            """
            TRUNCATE TABLE
                costscope.fact_cost_metric,
                costscope.dim_source,
                costscope.dim_metric,
                costscope.dim_date,
                costscope.dim_location
            RESTART IDENTITY
            CASCADE
            """
        )
    )


def validate_database(
    connection: Connection,
    expected: dict[str, int],
) -> None:
    """Validate PostgreSQL warehouse after loading."""

    logger.info("=" * 70)
    logger.info("Validating PostgreSQL warehouse")
    logger.info("=" * 70)

    for (
        table_name,
        expected_rows,
    ) in expected.items():
        actual_rows = connection.execute(
            text(
                f"""
                    SELECT COUNT(*)
                    FROM costscope.{table_name}
                    """
            )
        ).scalar_one()

        if actual_rows != expected_rows:
            raise ValueError(
                f"{table_name} row-count mismatch: "
                f"expected {expected_rows:,}, "
                f"found {actual_rows:,}."
            )

        logger.info(
            "%-22s PASS  %s rows",
            table_name,
            f"{actual_rows:,}",
        )

    invalid_location_fks = connection.execute(
        text(
            """
                SELECT COUNT(*)
                FROM costscope.fact_cost_metric AS f
                LEFT JOIN costscope.dim_location AS l
                    ON l.location_key = f.location_key
                WHERE l.location_key IS NULL
                """
        )
    ).scalar_one()

    invalid_date_fks = connection.execute(
        text(
            """
                SELECT COUNT(*)
                FROM costscope.fact_cost_metric AS f
                LEFT JOIN costscope.dim_date AS d
                    ON d.date_key = f.date_key
                WHERE d.date_key IS NULL
                """
        )
    ).scalar_one()

    invalid_metric_fks = connection.execute(
        text(
            """
                SELECT COUNT(*)
                FROM costscope.fact_cost_metric AS f
                LEFT JOIN costscope.dim_metric AS m
                    ON m.metric_key = f.metric_key
                WHERE m.metric_key IS NULL
                """
        )
    ).scalar_one()

    invalid_source_fks = connection.execute(
        text(
            """
                SELECT COUNT(*)
                FROM costscope.fact_cost_metric AS f
                LEFT JOIN costscope.dim_source AS s
                    ON s.source_id = f.source_id
                WHERE s.source_id IS NULL
                """
        )
    ).scalar_one()

    fk_results = {
        "location_fk": (invalid_location_fks),
        "date_fk": (invalid_date_fks),
        "metric_fk": (invalid_metric_fks),
        "source_fk": (invalid_source_fks),
    }

    for (
        name,
        invalid_count,
    ) in fk_results.items():
        if invalid_count:
            raise ValueError(
                f"{name} validation failed: {invalid_count:,} invalid rows."
            )

        logger.info(
            "%-22s PASS  0 invalid rows",
            name,
        )

    duplicate_grain = connection.execute(
        text(
            """
                SELECT COUNT(*)
                FROM (
                    SELECT
                        date_key,
                        location_key,
                        metric_key,
                        source_id,
                        COUNT(*) AS row_count
                    FROM costscope.fact_cost_metric
                    GROUP BY
                        date_key,
                        location_key,
                        metric_key,
                        source_id
                    HAVING COUNT(*) > 1
                ) AS duplicates
                """
        )
    ).scalar_one()

    if duplicate_grain:
        raise ValueError(
            f"Fact grain validation failed: {duplicate_grain:,} duplicate grains."
        )

    logger.info(
        "%-22s PASS  0 duplicate grains",
        "fact_grain",
    )

    derby = (
        connection.execute(
            text(
                """
                SELECT
                    l.location_id,
                    l.location_name,

                    MAX(
                        CASE
                            WHEN m.metric_code = 'RENT_MONTHLY'
                            THEN f.value
                        END
                    ) FILTER (
                        WHERE d.date = DATE '2026-08-01'
                    ) AS rent_aug_2026,

                    MAX(
                        CASE
                            WHEN m.metric_code = 'EARNINGS_ANNUAL'
                            THEN f.value
                        END
                    ) AS latest_earnings,

                    MAX(
                        CASE
                            WHEN m.metric_code = 'UNEMPLOYMENT_RATE'
                            THEN f.value
                        END
                    ) AS unemployment_rate

                FROM costscope.fact_cost_metric AS f

                INNER JOIN costscope.dim_location AS l
                    ON l.location_key = f.location_key

                INNER JOIN costscope.dim_metric AS m
                    ON m.metric_key = f.metric_key

                INNER JOIN costscope.dim_date AS d
                    ON d.date_key = f.date_key

                WHERE
                    l.location_id = 'E06000015'
                    AND f.is_published = TRUE

                GROUP BY
                    l.location_id,
                    l.location_name
                """
            )
        )
        .mappings()
        .one()
    )

    logger.info(
        "Derby validation: %s | rent £%s | earnings £%s | unemployment %s%%",
        derby["location_name"],
        derby["rent_aug_2026"],
        derby["latest_earnings"],
        derby["unemployment_rate"],
    )

    logger.info("=" * 70)


def load_gold_to_postgres(
    engine: Engine | None = None,
) -> dict[str, int]:
    """Run complete Gold → PostgreSQL warehouse refresh."""

    if engine is None:
        engine = get_engine()

    raw_tables = load_gold_parquet_tables()

    prepared = {
        "dim_location": (prepare_dim_location(raw_tables["dim_location"])),
        "dim_date": (prepare_dim_date(raw_tables["dim_date"])),
        "dim_metric": (prepare_dim_metric(raw_tables["dim_metric"])),
        "dim_source": (prepare_dim_source()),
        "fact_cost_metric": (prepare_fact_cost_metric(raw_tables["fact_cost_metric"])),
    }

    expected_counts = {
        table_name: len(dataframe)
        for (
            table_name,
            dataframe,
        ) in prepared.items()
    }

    logger.info("=" * 70)
    logger.info("Loading CostScope Gold into PostgreSQL")
    logger.info("=" * 70)

    # One transaction:
    # either the warehouse refresh succeeds completely or rolls back.
    with engine.begin() as connection:
        execute_schema(connection)

        truncate_warehouse(connection)

        for table_name in (
            "dim_location",
            "dim_date",
            "dim_metric",
            "dim_source",
            "fact_cost_metric",
        ):
            load_dataframe(
                prepared[table_name],
                table_name=table_name,
                connection=connection,
            )

        validate_database(
            connection,
            expected_counts,
        )

    logger.info("PostgreSQL warehouse refresh committed successfully")

    return expected_counts
