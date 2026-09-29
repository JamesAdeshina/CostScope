"""
Utilities for locating Bronze-layer source files.
"""

from pathlib import Path

from data_pipeline.config.settings import settings


def find_latest_private_rent_workbook() -> Path:
    """
    Locate the latest ONS Private Rent Bronze workbook.

    Returns
    -------
    Path
        Latest workbook according to file modification time.

    Raises
    ------
    FileNotFoundError
        If no source workbook has been ingested.
    """

    bronze_root = settings.bronze_path / "ons" / "private_rent"

    workbooks = list(bronze_root.rglob("price_index_private_rents.xlsx"))

    if not workbooks:
        raise FileNotFoundError("No ONS Private Rent Bronze workbook found.")

    return max(
        workbooks,
        key=lambda path: path.stat().st_mtime,
    )
