"""
Build and validate CostScope Silver inflation data.

Usage
-----

    python -m scripts.build_inflation_silver
"""

from data_pipeline.quality.ons.inflation_quality import (
    validate_inflation_silver,
)
from data_pipeline.transform.ons.inflation import (
    build_silver_inflation,
    write_silver_inflation,
)
from data_pipeline.utils.logging_config import get_logger

logger = get_logger(__name__)


def main() -> None:
    """Build, validate and write the CPI Silver dataset."""

    logger.info("=" * 70)
    logger.info("Building CostScope Silver inflation")
    logger.info("=" * 70)

    dataframe = build_silver_inflation()

    validate_inflation_silver(dataframe)

    output_path = write_silver_inflation(dataframe)

    latest = dataframe.sort_values("reference_period").iloc[-1]

    logger.info("=" * 70)
    logger.info("Silver inflation completed")
    logger.info(
        "Rows: %s",
        f"{len(dataframe):,}",
    )
    logger.info(
        "Output: %s",
        output_path,
    )
    logger.info(
        "Latest period: %s",
        latest["reference_period"].date(),
    )
    logger.info(
        "CPI annual rate: %s%%",
        latest["cpi_annual_rate"],
    )
    logger.info(
        "CPI monthly rate: %s%%",
        latest["cpi_monthly_rate"],
    )
    logger.info(
        "CPI index: %s",
        latest["cpi_index"],
    )
    logger.info("=" * 70)


if __name__ == "__main__":
    main()
