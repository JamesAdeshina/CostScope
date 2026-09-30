"""
Load the complete CostScope Gold warehouse into PostgreSQL.

Usage
-----

    python -m scripts.load_gold_to_postgres
"""

from data_pipeline.load.postgres import (
    load_gold_to_postgres,
)
from data_pipeline.utils.logging_config import get_logger

logger = get_logger(__name__)


def main() -> None:
    """Run PostgreSQL warehouse refresh."""

    counts = load_gold_to_postgres()

    logger.info("=" * 70)
    logger.info("CostScope PostgreSQL load completed")

    for (
        table_name,
        row_count,
    ) in counts.items():
        logger.info(
            "%-22s %s rows",
            table_name,
            f"{row_count:,}",
        )

    logger.info("=" * 70)


if __name__ == "__main__":
    main()
