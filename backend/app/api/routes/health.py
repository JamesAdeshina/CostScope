"""
Health-check endpoints.

Health endpoints allow developers, deployment platforms and monitoring
tools to verify that the CostScope API is running.
"""

from datetime import UTC, datetime

from fastapi import APIRouter

router = APIRouter(
    prefix="/health",
    tags=["Health"],
)


@router.get("")
def health_check() -> dict[str, str]:
    """
    Return basic API health information.

    Returns
    -------
    dict[str, str]
        Health status and current UTC timestamp.
    """

    return {
        "status": "ok",
        "service": "CostScope API",
        "timestamp": datetime.now(UTC).isoformat(),
    }
