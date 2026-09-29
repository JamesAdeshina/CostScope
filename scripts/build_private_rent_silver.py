"""
Build the CostScope ONS Private Rent Silver dataset.

Run with:

    python -m scripts.build_private_rent_silver
"""

from data_pipeline.quality.ons.private_rent_quality import (
    assert_no_critical_failures,
    run_private_rent_quality_checks,
)
from data_pipeline.transform.ons.private_rent import (
    transform_private_rent,
    write_silver_dataset,
)
from data_pipeline.utils.bronze import (
    find_latest_private_rent_workbook,
)
from data_pipeline.utils.logging_config import get_logger

logger = get_logger(__name__)


def main() -> None:
    """Build and validate the Silver dataset."""

    logger.info("=" * 70)
    logger.info("Building ONS Private Rent Silver dataset")
    logger.info("=" * 70)

    workbook_path = find_latest_private_rent_workbook()

    logger.info(
        "Using Bronze source: %s",
        workbook_path,
    )

    dataframe = transform_private_rent(
        workbook_path,
    )

    quality_results = run_private_rent_quality_checks(dataframe)

    assert_no_critical_failures(quality_results)

    output_path = write_silver_dataset(dataframe)

    logger.info(
        "Silver build complete: %s",
        output_path,
    )

    logger.info(
        "Rows: %s",
        f"{len(dataframe):,}",
    )


if __name__ == "__main__":
    main()
