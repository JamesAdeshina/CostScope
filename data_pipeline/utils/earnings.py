"""
Utilities for locating ONS ASHE earnings Bronze files.
"""

from pathlib import Path

from data_pipeline.config.settings import settings


def find_latest_earnings_workbook() -> Path:
    """Return the latest extracted ASHE Table 8.7a workbook."""

    root = settings.bronze_path / "ons" / "earnings"

    workbooks = list(root.rglob("ashe_table8_7a_annual_pay_gross_2025.xlsx"))

    if not workbooks:
        raise FileNotFoundError(
            "No ASHE earnings workbook found. "
            "Run `python -m scripts.extract_earnings` first."
        )

    return max(
        workbooks,
        key=lambda path: path.stat().st_mtime,
    )
