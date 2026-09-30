"""
Build model-based unemployment into CostScope Gold.
"""

from data_pipeline.model.unemployment_gold import (
    build_unemployment_gold,
    write_unemployment_gold,
)
from data_pipeline.quality.gold.unemployment_quality import (
    validate_unemployment_gold,
)
from data_pipeline.utils.logging_config import get_logger

logger = get_logger(__name__)


def main() -> None:
    """Build and validate unemployment Gold."""

    logger.info("=" * 70)
    logger.info("Building CostScope Gold unemployment")
    logger.info("=" * 70)

    tables = build_unemployment_gold()

    validate_unemployment_gold(tables)

    paths = write_unemployment_gold(tables)

    logger.info("=" * 70)
    logger.info("CostScope Gold unemployment completed")

    for (
        name,
        path,
    ) in paths.items():
        logger.info(
            "%s -> %s",
            name,
            path,
        )

    logger.info("=" * 70)


if __name__ == "__main__":
    main()
