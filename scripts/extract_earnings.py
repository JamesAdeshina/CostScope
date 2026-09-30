"""
Run the ONS ASHE earnings Bronze extraction.

Usage
-----

    python -m scripts.extract_earnings
"""

from data_pipeline.extract.ons.earnings import (
    extract_earnings,
)
from data_pipeline.utils.logging_config import get_logger

logger = get_logger(__name__)


def main() -> None:
    """Extract the latest configured ASHE earnings release."""

    workbook_path, metadata_path = extract_earnings()

    logger.info("=" * 70)
    logger.info("ASHE Bronze ingestion complete")
    logger.info(
        "Workbook: %s",
        workbook_path,
    )
    logger.info(
        "Metadata: %s",
        metadata_path,
    )
    logger.info("=" * 70)


if __name__ == "__main__":
    main()
