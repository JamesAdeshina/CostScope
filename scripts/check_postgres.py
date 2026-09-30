"""
Inspect the CostScope PostgreSQL warehouse.

Usage
-----

    python -m scripts.check_postgres
"""

from sqlalchemy import text

from backend.app.core.database import (
    get_engine,
)


def main() -> None:
    """Print database health and Derby serving metrics."""

    engine = get_engine()

    with engine.connect() as connection:
        result = (
            connection.execute(
                text(
                    """
                SELECT
                    current_database() AS database_name,
                    current_user AS database_user,
                    version() AS postgres_version
                """
                )
            )
            .mappings()
            .one()
        )

        print()
        print("=" * 80)
        print("DATABASE")
        print("=" * 80)
        print(f"Database: {result['database_name']}")
        print(f"User:     {result['database_user']}")
        print(f"Version:  {result['postgres_version']}")

        print()
        print("=" * 80)
        print("TABLE COUNTS")
        print("=" * 80)

        tables = [
            "dim_location",
            "dim_date",
            "dim_metric",
            "dim_source",
            "fact_cost_metric",
        ]

        for table_name in tables:
            row_count = connection.execute(
                text(
                    f"""
                    SELECT COUNT(*)
                    FROM costscope.{table_name}
                    """
                )
            ).scalar_one()

            print(f"{table_name:<22} {row_count:>12,}")

        print()
        print("=" * 80)
        print("DERBY LATEST METRICS")
        print("=" * 80)

        rows = (
            connection.execute(
                text(
                    """
                SELECT
                    metric_code,
                    metric_name,
                    value,
                    unit,
                    reference_period,
                    source_code

                FROM costscope.vw_cost_metrics

                WHERE
                    location_id = 'E06000015'
                    AND is_published = TRUE
                    AND metric_code IN (
                        'RENT_MONTHLY',
                        'EARNINGS_ANNUAL',
                        'UNEMPLOYMENT_RATE'
                    )

                ORDER BY
                    metric_code,
                    reference_period DESC
                """
                )
            )
            .mappings()
            .all()
        )

        latest_seen: set[str] = set()

        for row in rows:
            metric_code = str(row["metric_code"])

            if metric_code in latest_seen:
                continue

            latest_seen.add(metric_code)

            print(
                f"{metric_code:<24}"
                f"{row['value']:>12,.2f} "
                f"{row['unit']:<12} "
                f"{row['reference_period']} "
                f"{row['source_code']}"
            )

        print()
        print("=" * 80)
        print("UK CPI")
        print("=" * 80)

        cpi = (
            connection.execute(
                text(
                    """
                SELECT
                    value,
                    unit,
                    reference_period,
                    source_code

                FROM costscope.vw_cost_metrics

                WHERE
                    location_id = 'K02000001'
                    AND metric_code = 'CPI_ANNUAL_RATE'
                    AND is_published = TRUE

                ORDER BY reference_period DESC

                LIMIT 1
                """
                )
            )
            .mappings()
            .one()
        )

        print(
            f"CPI annual rate: "
            f"{cpi['value']}% | "
            f"{cpi['reference_period']} | "
            f"{cpi['source_code']}"
        )


if __name__ == "__main__":
    main()
