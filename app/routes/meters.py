from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request

from app.core.errors import handle_portal_error
from app.core.security import verify_api_key
from app.integrations.urja.auth import ensure_portal_session
from app.integrations.urja.meters import search_meters
from app.integrations.urja.details import get_meter_energy, get_meter_geo
from app.models.meter import MeterSearchResponse
from app.models.meter_details import MeterEnergyResponse, MeterGeoResponse

router = APIRouter(
    prefix="/meters",
    tags=["Meters"],
    dependencies=[Depends(verify_api_key)],
)


@router.get("/search", response_model=MeterSearchResponse)
async def get_meters(
    request: Request,
    q: str = Query(default="", max_length=100),
    page: int = Query(default=1, ge=1),
):
    client = request.app.state.http_client

    try:
        await ensure_portal_session(client)
        result = await search_meters(client, query=q, page=page)
        return MeterSearchResponse(**result)

    except HTTPException:
        raise

    except Exception as error:
        handle_portal_error(error)


@router.get("/{meter_id}/geo", response_model=MeterGeoResponse)
async def get_meter_location(
    request: Request,
    meter_id: str = Path(
        ...,
        min_length=1,
        max_length=50,
        pattern=r"^[A-Za-z0-9_-]+$",
    ),
):
    client = request.app.state.http_client

    try:
        await ensure_portal_session(client)
        result = await get_meter_geo(client, meter_id)
        return MeterGeoResponse(**result)

    except HTTPException:
        raise

    except Exception as error:
        handle_portal_error(error)


@router.get("/{meter_id}/energy", response_model=MeterEnergyResponse)
async def get_meter_energy_readings(
    request: Request,
    meter_id: str = Path(
        ...,
        min_length=1,
        max_length=50,
        pattern=r"^[A-Za-z0-9_-]+$",
    ),
):
    client = request.app.state.http_client

    try:
        await ensure_portal_session(client)
        result = await get_meter_energy(client, meter_id)
        return MeterEnergyResponse(**result)

    except HTTPException:
        raise

    except Exception as error:
        handle_portal_error(error)
