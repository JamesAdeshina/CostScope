"""
Build CostScope Gold tables from validated Private Rent Silver data.

Run with:

    python -m scripts.build_private_rent_gold
"""

from data_pipeline.model.private_rent_gold import (
    build_gold_tables,
    write_gold_tables,
)
from data_pipeline.quality.gold.private_rent_quality import (
    validate_gold_tables,
)
from data_pipeline.utils.logging_config import get_logger

logger = get_logger(__name__)


def main() -> None:
    """Build, validate and persist Gold analytical tables."""

    tables = build_gold_tables()

    logger.info("=" * 70)
    logger.info("Running Gold quality checks")
    logger.info("=" * 70)

    validate_gold_tables(tables)

    output_paths = write_gold_tables(tables)

    logger.info("=" * 70)
    logger.info("Gold build completed successfully")
    logger.info("=" * 70)

    for table_name, path in output_paths.items():
        logger.info(
            "%s -> %s",
            table_name,
            path,
        )


if __name__ == "__main__":
    main()
