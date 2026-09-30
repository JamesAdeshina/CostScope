"""
CostScope location API routes.
"""

from fastapi import (
    APIRouter,
    HTTPException,
    Query,
    status,
)

from backend.app.repositories.private_rent_repository import (
    GoldDataNotBuiltError,
    LocationNotFoundError,
    get_metric_history,
    search_locations,
)
from backend.app.schemas.location import (
    LocationOverviewResponse,
    LocationSearchResult,
    MetricHistoryResponse,
)
from backend.app.services.location_overview_service import (
    get_location_overview,
)

router = APIRouter(
    prefix="/api/v1",
    tags=["locations"],
)


@router.get(
    "/search",
    response_model=list[LocationSearchResult],
)
def search(
    q: str = Query(
        ...,
        min_length=2,
        max_length=100,
    ),
) -> list[dict[str, object]]:
    """Search CostScope locations."""

    try:
        return search_locations(q)

    except GoldDataNotBuiltError as exc:
        raise HTTPException(
            status_code=(status.HTTP_503_SERVICE_UNAVAILABLE),
            detail=str(exc),
        ) from exc


@router.get(
    "/locations/{location_code}/overview",
    response_model=LocationOverviewResponse,
)
def location_overview(
    location_code: str,
) -> dict[str, object]:
    """Return the unified CostScope overview for one location."""

    try:
        return get_location_overview(location_code)

    except LocationNotFoundError as exc:
        raise HTTPException(
            status_code=(status.HTTP_404_NOT_FOUND),
            detail=str(exc),
        ) from exc

    except GoldDataNotBuiltError as exc:
        raise HTTPException(
            status_code=(status.HTTP_503_SERVICE_UNAVAILABLE),
            detail=str(exc),
        ) from exc


@router.get(
    "/locations/{location_code}/history",
    response_model=MetricHistoryResponse,
)
def location_history(
    location_code: str,
    metric: str = Query(
        default="rent",
        min_length=2,
        max_length=100,
    ),
) -> dict[str, object]:
    """Return an ordered historical metric series."""

    try:
        return get_metric_history(
            location_code,
            metric,
        )

    except LocationNotFoundError as exc:
        raise HTTPException(
            status_code=(status.HTTP_404_NOT_FOUND),
            detail=str(exc),
        ) from exc

    except GoldDataNotBuiltError as exc:
        raise HTTPException(
            status_code=(status.HTTP_503_SERVICE_UNAVAILABLE),
            detail=str(exc),
        ) from exc
