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
    get_location_overview,
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
    Resolve a postcode and return the CostScope location overview.

    Postcodes.io provides geography resolution only. Cost-of-living
    metrics come from CostScope's analytical Gold layer.
    """

    try:
        geography = lookup_postcode(postcode)

        overview = get_location_overview(str(geography["admin_district_code"]))

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
                "does not currently contain matching data: "
                f"{exc}"
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
