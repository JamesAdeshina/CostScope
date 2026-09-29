"""
ONS Private Rent extractor.

This module downloads the official Office for National Statistics
Price Index of Private Rents monthly workbook and stores the original
file in the CostScope Bronze layer.

The Bronze layer preserves source data with minimal modification.

Responsibilities
----------------
1. Download the source workbook.
2. Validate the HTTP response.
3. Calculate a SHA-256 checksum.
4. Store the source file using an ingestion timestamp.
5. Store ingestion metadata.
6. Avoid silently overwriting source data.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

import requests
from requests import Response
from tenacity import retry, stop_after_attempt, wait_exponential
from tqdm import tqdm

from data_pipeline.config.settings import settings
from data_pipeline.utils.logging_config import get_logger

logger = get_logger(__name__)


DATASET_NAME = "ons_private_rent"
SOURCE_NAME = "Office for National Statistics"
SOURCE_FORMAT = "xlsx"


@dataclass
class ExtractionMetadata:
    """Metadata captured for each extraction run."""

    run_id: str
    dataset: str
    source: str
    source_url: str
    started_at: str
    completed_at: str
    status: str
    filename: str
    file_size_bytes: int
    sha256: str


def generate_run_id() -> str:
    """Generate a unique pipeline run identifier."""

    now = datetime.now(UTC)

    return now.strftime("run_%Y%m%d_%H%M%S")


def calculate_sha256(file_path: Path) -> str:
    """
    Calculate SHA-256 checksum for a file.

    Parameters
    ----------
    file_path:
        File whose checksum should be calculated.

    Returns
    -------
    str
        SHA-256 hexadecimal digest.
    """

    sha256 = hashlib.sha256()

    with file_path.open("rb") as file_handle:
        for chunk in iter(lambda: file_handle.read(1024 * 1024), b""):
            sha256.update(chunk)

    return sha256.hexdigest()


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(
        multiplier=2,
        min=2,
        max=10,
    ),
    reraise=True,
)
def request_dataset(url: str) -> Response:
    """
    Download the ONS dataset with retry behaviour.

    Parameters
    ----------
    url:
        ONS dataset URL.

    Returns
    -------
    requests.Response
        HTTP response containing the workbook.
    """

    logger.info("Requesting ONS private rent dataset")

    response = requests.get(
        url,
        stream=True,
        timeout=60,
        headers={
            "User-Agent": "CostScope/0.1",
        },
    )

    response.raise_for_status()

    return response


def download_dataset(
    destination: Path,
) -> int:
    """
    Download the ONS workbook to the Bronze layer.

    Parameters
    ----------
    destination:
        Path where the downloaded workbook should be stored.

    Returns
    -------
    int
        Number of bytes written.
    """

    response = request_dataset(settings.ons_private_rent_dataset_url)

    total_size = int(
        response.headers.get(
            "content-length",
            0,
        )
    )

    bytes_written = 0

    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    logger.info(
        "Downloading dataset to %s",
        destination,
    )

    with destination.open("wb") as file_handle:
        with tqdm(
            total=total_size,
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
            desc="Downloading ONS rent data",
            dynamic_ncols=True,
        ) as progress:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if not chunk:
                    continue

                file_handle.write(chunk)

                chunk_size = len(chunk)

                bytes_written += chunk_size
                progress.update(chunk_size)

    return bytes_written


def write_metadata(
    metadata: ExtractionMetadata,
    destination: Path,
) -> None:
    """
    Write extraction metadata as JSON.

    Parameters
    ----------
    metadata:
        Extraction metadata object.

    destination:
        Output JSON path.
    """

    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with destination.open(
        "w",
        encoding="utf-8",
    ) as file_handle:
        json.dump(
            asdict(metadata),
            file_handle,
            indent=2,
        )


def extract_private_rent() -> tuple[Path, Path]:
    """
    Run ONS private rent extraction.

    Returns
    -------
    tuple[Path, Path]
        Workbook path and metadata path.
    """

    started_at = datetime.now(UTC)
    run_id = generate_run_id()

    ingestion_date = started_at.strftime("%Y-%m-%d")

    bronze_directory = (
        settings.bronze_path
        / "ons"
        / "private_rent"
        / f"ingestion_date={ingestion_date}"
        / run_id
    )

    workbook_path = bronze_directory / "price_index_private_rents.xlsx"

    metadata_path = bronze_directory / "metadata.json"

    logger.info("=" * 70)
    logger.info("ONS private rent extraction started")
    logger.info("Run ID: %s", run_id)
    logger.info("=" * 70)

    try:
        file_size = download_dataset(workbook_path)

        logger.info(
            "Download completed: %s bytes",
            f"{file_size:,}",
        )

        checksum = calculate_sha256(workbook_path)

        logger.info(
            "SHA-256: %s",
            checksum,
        )

        completed_at = datetime.now(UTC)

        metadata = ExtractionMetadata(
            run_id=run_id,
            dataset=DATASET_NAME,
            source=SOURCE_NAME,
            source_url=settings.ons_private_rent_dataset_url,
            started_at=started_at.isoformat(),
            completed_at=completed_at.isoformat(),
            status="SUCCESS",
            filename=workbook_path.name,
            file_size_bytes=file_size,
            sha256=checksum,
        )

        write_metadata(
            metadata,
            metadata_path,
        )

        logger.info(
            "Metadata written to %s",
            metadata_path,
        )

        logger.info("ONS private rent extraction completed successfully")

        return workbook_path, metadata_path

    except Exception:
        logger.exception("ONS private rent extraction failed")

        if workbook_path.exists():
            workbook_path.unlink()

        raise
