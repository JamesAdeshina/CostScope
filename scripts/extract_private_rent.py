"""
Run CostScope private-rent Bronze extraction.

Usage
-----
    python -m scripts.extract_private_rent
"""

from data_pipeline.extract.ons.private_rent import (
    extract_private_rent,
)
from data_pipeline.utils.logging_config import (
    get_logger,
)

logger = get_logger(__name__)


def main() -> None:
    """Extract ONS private-rent source data."""

    logger.info("=" * 70)
    logger.info("Starting CostScope private-rent extraction")
    logger.info("=" * 70)

    result = extract_private_rent()

    logger.info("Private-rent extraction completed")

    if result is not None:
        logger.info(
            "Result: %s",
            result,
        )

    logger.info("=" * 70)


if __name__ == "__main__":
    main()
