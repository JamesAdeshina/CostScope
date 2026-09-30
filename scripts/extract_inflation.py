"""
Run CostScope ONS CPI Bronze ingestion.

Usage
-----

    python -m scripts.extract_inflation
"""

from data_pipeline.extract.ons.inflation import (
    extract_inflation,
)
from data_pipeline.utils.logging_config import get_logger

logger = get_logger(__name__)


def main() -> None:
    """Extract configured ONS CPI series."""

    run_directory, metadata_path = extract_inflation()

    logger.info("=" * 70)
    logger.info("CPI Bronze ingestion complete")
    logger.info(
        "Run directory: %s",
        run_directory,
    )
    logger.info(
        "Metadata: %s",
        metadata_path,
    )
    logger.info("=" * 70)


if __name__ == "__main__":
    main()
