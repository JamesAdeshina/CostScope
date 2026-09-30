"""
Run CostScope model-based unemployment Bronze ingestion.
"""

from data_pipeline.extract.nomis.unemployment import (
    extract_unemployment,
)
from data_pipeline.utils.logging_config import get_logger

logger = get_logger(__name__)


def main() -> None:
    """Run unemployment Bronze extraction."""

    csv_path, metadata_path = extract_unemployment()

    logger.info("=" * 70)
    logger.info("Unemployment Bronze ingestion complete")
    logger.info(
        "CSV: %s",
        csv_path,
    )
    logger.info(
        "Metadata: %s",
        metadata_path,
    )
    logger.info("=" * 70)


if __name__ == "__main__":
    main()
