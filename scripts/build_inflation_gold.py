"""
Build ONS CPI metrics into CostScope Gold.

Usage
-----

    python -m scripts.build_inflation_gold
"""

from data_pipeline.model.inflation_gold import (
    build_inflation_gold,
    write_inflation_gold,
)
from data_pipeline.quality.gold.inflation_quality import (
    validate_inflation_gold,
)
from data_pipeline.utils.logging_config import get_logger

logger = get_logger(__name__)


def main() -> None:
    """Build, validate and write CPI Gold data."""

    logger.info("=" * 70)
    logger.info("Building CostScope Gold inflation")
    logger.info("=" * 70)

    tables = build_inflation_gold()

    validate_inflation_gold(tables)

    paths = write_inflation_gold(tables)

    logger.info("=" * 70)
    logger.info("CostScope Gold inflation completed")

    for (
        table_name,
        path,
    ) in paths.items():
        logger.info(
            "%s -> %s",
            table_name,
            path,
        )

    logger.info("=" * 70)


if __name__ == "__main__":
    main()
