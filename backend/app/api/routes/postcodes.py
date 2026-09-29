"""
CostScope postcode resolution routes.
"""

from fastapi import (
    APIRouter,
    HTTPException,
    status,
)

from backend.app.repositories.private_rent_repository import (
    GoldDataNotBuiltError,
    LocationNotFoundError,
    get_latest_rent_overview,
)
from backend.app.schemas.postcode import (
    PostcodeOverviewResponse,
)
from backend.app.services.postcode_service import (
    InvalidPostcodeError,
    PostcodeServiceError,
    lookup_postcode,
)

router = APIRouter(
    prefix="/api/v1",
    tags=["postcodes"],
)


@router.get(
    "/postcode/{postcode}",
    response_model=PostcodeOverviewResponse,
)
def postcode_overview(
    postcode: str,
) -> dict[str, object]:
    """
    Resolve a UK postcode and return CostScope metrics.

    The postcode service provides geography only. Cost-of-living
    statistics continue to come from CostScope's Gold analytical model.
    """

    try:
        geography = lookup_postcode(postcode)

        overview = get_latest_rent_overview(str(geography["admin_district_code"]))

        return {
            "postcode": geography,
            "overview": overview,
        }

    except InvalidPostcodeError as exc:
        raise HTTPException(
            status_code=(status.HTTP_404_NOT_FOUND),
            detail=str(exc),
        ) from exc

    except LocationNotFoundError as exc:
        raise HTTPException(
            status_code=(status.HTTP_404_NOT_FOUND),
            detail=(
                "The postcode was resolved, but CostScope "
                f"does not currently contain matching data: {exc}"
            ),
        ) from exc

    except PostcodeServiceError as exc:
        raise HTTPException(
            status_code=(status.HTTP_502_BAD_GATEWAY),
            detail=str(exc),
        ) from exc

    except GoldDataNotBuiltError as exc:
        raise HTTPException(
            status_code=(status.HTTP_503_SERVICE_UNAVAILABLE),
            detail=str(exc),
        ) from exc
