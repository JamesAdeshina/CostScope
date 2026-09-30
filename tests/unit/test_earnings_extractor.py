"""
Unit tests for the ONS ASHE earnings extractor.
"""

from pathlib import Path

import pytest

from data_pipeline.extract.ons.earnings import (
    calculate_sha256,
    find_target_workbook,
)


def test_find_target_workbook_with_ons_spacing() -> None:
    """
    Matcher should handle the multiple spaces used by the real ONS ZIP.
    """

    members = [
        "PROV - Home Geography Table 8.1a   Weekly pay - Gross 2025.xlsx",
        ("PROV - Home Geography Table 8.7a   Annual pay - Gross 2025.xlsx"),
        ("PROV - Home Geography Table 8.7b   Annual pay - Gross 2025 CV.xlsx"),
    ]

    result = find_target_workbook(members)

    assert result == ("PROV - Home Geography Table 8.7a   Annual pay - Gross 2025.xlsx")


def test_find_target_workbook_is_case_insensitive() -> None:
    """Filename capitalisation should not affect detection."""

    members = [
        ("PROV - HOME GEOGRAPHY TABLE 8.7A   ANNUAL PAY - GROSS 2025.XLSX"),
    ]

    result = find_target_workbook(members)

    assert result == members[0]


def test_find_target_workbook_rejects_cv_file() -> None:
    """The coefficient-of-variation workbook is not our metric source."""

    members = [
        ("PROV - Home Geography Table 8.7b   Annual pay - Gross 2025 CV.xlsx"),
    ]

    with pytest.raises(
        ValueError,
        match="found 0",
    ):
        find_target_workbook(members)


def test_calculate_earnings_sha256(
    tmp_path: Path,
) -> None:
    """ASHE files should produce deterministic SHA-256 hashes."""

    test_file = tmp_path / "sample.txt"

    test_file.write_text(
        "CostScope earnings",
        encoding="utf-8",
    )

    first = calculate_sha256(test_file)

    second = calculate_sha256(test_file)

    assert first == second
    assert len(first) == 64
