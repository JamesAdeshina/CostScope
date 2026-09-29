"""
CostScope FastAPI application.

This module creates the API application and registers application routes.
"""

from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI

from backend.app.api.routes.health import router as health_router
from backend.app.api.routes.locations import router as locations_router
from backend.app.core.config import api_settings
from backend.app.core.logging_config import get_api_logger


logger = get_api_logger(__name__)


@asynccontextmanager
async def lifespan(
    app: FastAPI,
) -> AsyncIterator[None]:
    """
    Manage FastAPI startup and shutdown events.

    Parameters
    ----------
    app:
        FastAPI application instance.
    """

    logger.info(
        "Starting %s API",
        api_settings.app_name,
    )

    yield

    logger.info(
        "Stopping %s API",
        api_settings.app_name,
    )


app = FastAPI(
    title="CostScope API",
    description=(
        "API powering CostScope, a UK cost-of-living "
        "data engineering and analytics platform."
    ),
    version="0.2.0",
    debug=api_settings.debug,
    lifespan=lifespan,
)


app.include_router(
    health_router
)

app.include_router(
    locations_router
)


@app.get("/")
def root() -> dict[str, str]:
    """Return basic API metadata."""

    return {
        "service": "CostScope API",
        "version": "0.2.0",
        "documentation": "/docs",
    }