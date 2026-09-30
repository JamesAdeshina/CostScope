"""
Compose CostScope overview metrics from domain repositories.
"""

from __future__ import annotations

from backend.app.repositories.inflation_repository import (
    get_latest_inflation_overview,
)
from backend.app.repositories.private_rent_repository import (
    get_location_overview as get_local_location_overview,
)
from backend.app.repositories.unemployment_repository import (
    get_latest_unemployment_overview,
)


def get_location_overview(
    location_code: str,
) -> dict[str, object]:
    """Return the unified CostScope multi-domain overview."""

    overview = get_local_location_overview(location_code)

    inflation = get_latest_inflation_overview()

    unemployment = get_latest_unemployment_overview(location_code)

    overview["inflation"] = inflation

    overview["unemployment"] = unemployment

    sources = overview.setdefault(
        "sources",
        [],
    )

    if inflation is not None and not any(
        source.get("source_code") == "ONS_CPI_MM23" for source in sources
    ):
        sources.append(
            {
                "source_code": ("ONS_CPI_MM23"),
                "publisher": ("Office for National Statistics"),
                "dataset": ("Consumer price inflation time series"),
            }
        )

    if unemployment is not None and not any(
        source.get("source_code") == "NOMIS_UNEMPLOYMENT_MODEL" for source in sources
    ):
        sources.append(
            {
                "source_code": ("NOMIS_UNEMPLOYMENT_MODEL"),
                "publisher": ("Office for National Statistics"),
                "dataset": ("Model-based estimates of unemployment"),
            }
        )

    return overview
