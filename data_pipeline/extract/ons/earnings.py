"""
ONS ASHE earnings extractor.

Downloads the official ONS ASHE Table 8 ZIP archive, validates it,
preserves the raw archive in Bronze storage and extracts the workbook
containing Table 8.7a Annual Pay - Gross.

The Bronze layer preserves source material without altering published
statistical values.
"""

from __future__ import annotations

import hashlib
import json
import zipfile
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

import requests
from requests import Response
from tenacity import retry, stop_after_attempt, wait_exponential
from tqdm import tqdm

from data_pipeline.config.settings import settings
from data_pipeline.config.sources import (
    ONS_ASHE_DATASET_NAME,
    ONS_ASHE_PUBLISHER,
    ONS_ASHE_RELEASE,
    ONS_ASHE_TABLE8_2025_URL,
    ONS_ASHE_TARGET_MEASURE,
    ONS_ASHE_TARGET_PAY_TYPE,
    ONS_ASHE_TARGET_TABLE,
)
from data_pipeline.utils.logging_config import get_logger

logger = get_logger(__name__)


DATASET_CODE = "ons_ashe_table8"
ARCHIVE_FILENAME = "ashe_table8_2025_provisional.zip"


@dataclass
class EarningsExtractionMetadata:
    """Metadata describing one ASHE Bronze ingestion."""

    run_id: str
    dataset_code: str
    dataset_name: str
    publisher: str
    release: str
    source_url: str
    started_at: str
    completed_at: str
    status: str
    archive_filename: str
    workbook_filename: str
    archive_size_bytes: int
    archive_sha256: str
    workbook_sha256: str


def generate_run_id() -> str:
    """Create a UTC-based extraction run identifier."""

    return datetime.now(UTC).strftime("run_%Y%m%d_%H%M%S")


def calculate_sha256(
    file_path: Path,
) -> str:
    """Calculate the SHA-256 checksum of a file."""

    digest = hashlib.sha256()

    with file_path.open("rb") as file_handle:
        for chunk in iter(
            lambda: file_handle.read(1024 * 1024),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(
        multiplier=2,
        min=2,
        max=10,
    ),
    reraise=True,
)
def request_archive(
    url: str,
) -> Response:
    """Request the ONS archive with retry behaviour."""

    logger.info("Requesting ONS ASHE Table 8 archive")

    response = requests.get(
        url,
        stream=True,
        timeout=90,
        headers={
            "User-Agent": "CostScope/0.2",
        },
    )

    response.raise_for_status()

    return response


def download_archive(
    destination: Path,
) -> int:
    """
    Download the source ZIP using an atomic temporary file.

    Returns
    -------
    int
        Number of bytes downloaded.
    """

    response = request_archive(ONS_ASHE_TABLE8_2025_URL)

    total_size = int(
        response.headers.get(
            "content-length",
            0,
        )
    )

    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporary_path = destination.with_suffix(".zip.part")

    bytes_written = 0

    logger.info(
        "Downloading ASHE archive to %s",
        destination,
    )

    try:
        with temporary_path.open("wb") as file_handle:
            with tqdm(
                total=total_size or None,
                unit="B",
                unit_scale=True,
                unit_divisor=1024,
                desc="Downloading ONS earnings",
                dynamic_ncols=True,
            ) as progress:
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    if not chunk:
                        continue

                    file_handle.write(chunk)

                    size = len(chunk)

                    bytes_written += size

                    progress.update(size)

        if bytes_written == 0:
            raise ValueError("ONS ASHE download returned an empty archive.")

        temporary_path.replace(destination)

    finally:
        response.close()

        if temporary_path.exists():
            temporary_path.unlink()

    return bytes_written


def validate_zip_archive(
    archive_path: Path,
) -> list[str]:
    """
    Validate the downloaded ZIP and return archive members.

    Raises
    ------
    ValueError
        If the ZIP is corrupt or contains no files.
    """

    if not zipfile.is_zipfile(archive_path):
        raise ValueError("Downloaded ASHE source is not a valid ZIP archive.")

    with zipfile.ZipFile(archive_path) as archive:
        members = [member for member in archive.namelist() if not member.endswith("/")]

        if not members:
            raise ValueError("ASHE ZIP archive contains no files.")

        corrupt_member = archive.testzip()

        if corrupt_member is not None:
            raise ValueError(f"Corrupt file detected in ASHE ZIP: {corrupt_member}")

    logger.info(
        "ASHE archive validated: %s files",
        len(members),
    )

    return members


def find_target_workbook(
    members: list[str],
) -> str:
    """
    Find the ASHE Table 8.7a annual gross-pay workbook.

    ONS filenames occasionally contain inconsistent whitespace. Matching
    therefore uses normalised semantic tokens instead of an exact
    filename.

    The coefficient-of-variation workbook (Table 8.7b / CV) is excluded.

    Parameters
    ----------
    members:
        File paths contained in the downloaded ZIP archive.

    Returns
    -------
    str
        Archive member path for the required workbook.

    Raises
    ------
    ValueError
        If exactly one valid workbook cannot be identified.
    """

    matches: list[str] = []

    for member in members:
        filename = Path(member).name

        normalised = " ".join(filename.lower().split())

        is_excel = normalised.endswith(".xlsx") or normalised.endswith(".xls")

        is_target_table = ONS_ASHE_TARGET_TABLE.lower() in normalised

        is_target_measure = ONS_ASHE_TARGET_MEASURE.lower() in normalised

        is_target_pay_type = ONS_ASHE_TARGET_PAY_TYPE.lower() in normalised

        is_cv_workbook = (
            " cv." in normalised
            or normalised.endswith(" cv.xlsx")
            or normalised.endswith(" cv.xls")
        )

        if (
            is_excel
            and is_target_table
            and is_target_measure
            and is_target_pay_type
            and not is_cv_workbook
        ):
            matches.append(member)

    if len(matches) != 1:
        raise ValueError(
            "Expected exactly one ASHE Table 8.7a "
            "Annual Pay - Gross workbook, "
            f"but found {len(matches)}. "
            f"Matches: {matches}"
        )

    logger.info(
        "Matched ASHE workbook: %s",
        matches[0],
    )

    return matches[0]


def extract_target_workbook(
    archive_path: Path,
    archive_member: str,
    destination: Path,
) -> None:
    """
    Extract only the required ASHE workbook.

    The remaining archive files remain preserved inside the original
    Bronze ZIP.
    """

    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporary_path = destination.with_suffix(".xlsx.part")

    with zipfile.ZipFile(archive_path) as archive:
        with archive.open(archive_member) as source:
            with temporary_path.open("wb") as target:
                while True:
                    chunk = source.read(1024 * 1024)

                    if not chunk:
                        break

                    target.write(chunk)

    if temporary_path.stat().st_size == 0:
        temporary_path.unlink(missing_ok=True)

        raise ValueError("Extracted ASHE workbook is empty.")

    temporary_path.replace(destination)


def write_metadata(
    metadata: EarningsExtractionMetadata,
    destination: Path,
) -> None:
    """Write extraction metadata as formatted JSON."""

    with destination.open(
        "w",
        encoding="utf-8",
    ) as file_handle:
        json.dump(
            asdict(metadata),
            file_handle,
            indent=2,
        )


def extract_earnings() -> tuple[Path, Path]:
    """
    Run the ONS ASHE earnings Bronze extraction.

    Returns
    -------
    tuple[Path, Path]
        Extracted workbook path and metadata path.
    """

    started_at = datetime.now(UTC)

    run_id = generate_run_id()

    ingestion_date = started_at.strftime("%Y-%m-%d")

    bronze_directory = (
        settings.bronze_path
        / "ons"
        / "earnings"
        / f"ingestion_date={ingestion_date}"
        / run_id
    )

    archive_path = bronze_directory / ARCHIVE_FILENAME

    workbook_path = bronze_directory / "ashe_table8_7a_annual_pay_gross_2025.xlsx"

    metadata_path = bronze_directory / "metadata.json"

    logger.info("=" * 70)
    logger.info("ONS ASHE earnings extraction started")
    logger.info(
        "Run ID: %s",
        run_id,
    )
    logger.info("=" * 70)

    try:
        archive_size = download_archive(archive_path)

        logger.info(
            "Archive downloaded: %s bytes",
            f"{archive_size:,}",
        )

        members = validate_zip_archive(archive_path)

        workbook_member = find_target_workbook(members)

        logger.info(
            "Target workbook found: %s",
            workbook_member,
        )

        extract_target_workbook(
            archive_path,
            workbook_member,
            workbook_path,
        )

        archive_sha256 = calculate_sha256(archive_path)

        workbook_sha256 = calculate_sha256(workbook_path)

        logger.info(
            "Archive SHA-256: %s",
            archive_sha256,
        )

        logger.info(
            "Workbook SHA-256: %s",
            workbook_sha256,
        )

        completed_at = datetime.now(UTC)

        metadata = EarningsExtractionMetadata(
            run_id=run_id,
            dataset_code=DATASET_CODE,
            dataset_name=ONS_ASHE_DATASET_NAME,
            publisher=ONS_ASHE_PUBLISHER,
            release=ONS_ASHE_RELEASE,
            source_url=ONS_ASHE_TABLE8_2025_URL,
            started_at=started_at.isoformat(),
            completed_at=completed_at.isoformat(),
            status="SUCCESS",
            archive_filename=archive_path.name,
            workbook_filename=workbook_path.name,
            archive_size_bytes=archive_size,
            archive_sha256=archive_sha256,
            workbook_sha256=workbook_sha256,
        )

        write_metadata(
            metadata,
            metadata_path,
        )

        logger.info(
            "Metadata written: %s",
            metadata_path,
        )

        logger.info("ONS ASHE earnings extraction completed successfully")

        return (
            workbook_path,
            metadata_path,
        )

    except Exception:
        logger.exception("ONS ASHE earnings extraction failed")

        # Never leave partially extracted workbooks behind.
        if workbook_path.exists():
            workbook_path.unlink()

        raise
