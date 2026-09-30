"""
Extend CostScope Gold with ONS ASHE earnings.

Usage
-----

    python -m scripts.build_earnings_gold
"""

from data_pipeline.model.earnings_gold import (
    build_earnings_gold,
    write_earnings_gold,
)
from data_pipeline.quality.gold.earnings_quality import (
    validate_earnings_gold,
)
from data_pipeline.utils.logging_config import get_logger

logger = get_logger(__name__)


def main() -> None:
    """Build, validate and write earnings into Gold."""

    logger.info("=" * 70)
    logger.info("Building CostScope Gold earnings")
    logger.info("=" * 70)

    tables = build_earnings_gold()

    validate_earnings_gold(tables)

    paths = write_earnings_gold(tables)

    logger.info("=" * 70)
    logger.info("CostScope Gold earnings completed")

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
