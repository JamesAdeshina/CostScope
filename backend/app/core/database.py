"""
PostgreSQL database configuration for CostScope.

Environment variables
---------------------

Preferred:
    COSTSCOPE_DATABASE_URL

Fallback:
    DATABASE_URL

Example:
    postgresql://postgres:password@localhost:5432/costscope

Supabase PostgreSQL URLs are supported as well.

The URL is normalised to SQLAlchemy's psycopg driver.
"""

from __future__ import annotations

import os
from functools import lru_cache

from dotenv import load_dotenv
from sqlalchemy import Engine, create_engine

load_dotenv()


def get_database_url() -> str:
    """
    Return the configured PostgreSQL connection URL.

    Raises
    ------
    RuntimeError
        When no database connection has been configured.
    """

    database_url = os.getenv("COSTSCOPE_DATABASE_URL") or os.getenv("DATABASE_URL")

    if not database_url:
        raise RuntimeError(
            "PostgreSQL is not configured. "
            "Set COSTSCOPE_DATABASE_URL in your environment or .env file."
        )

    database_url = database_url.strip()

    if database_url.startswith("postgres://"):
        database_url = database_url.replace(
            "postgres://",
            "postgresql+psycopg://",
            1,
        )

    elif database_url.startswith("postgresql://"):
        database_url = database_url.replace(
            "postgresql://",
            "postgresql+psycopg://",
            1,
        )

    return database_url


def database_configured() -> bool:
    """Return whether a PostgreSQL URL is available."""

    return bool(os.getenv("COSTSCOPE_DATABASE_URL") or os.getenv("DATABASE_URL"))


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    """Create and cache the CostScope SQLAlchemy engine."""

    return create_engine(
        get_database_url(),
        pool_pre_ping=True,
        pool_recycle=300,
        future=True,
    )
