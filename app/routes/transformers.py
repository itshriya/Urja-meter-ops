from fastapi import APIRouter, Depends, HTTPException, Query, Request

from app.core.security import verify_api_key
from app.core.errors import handle_portal_error
from app.integrations.urja.auth import ensure_portal_session
from app.integrations.urja.transformers import get_transformers
from app.models.transformer import TransformerSearchResponse

router = APIRouter(
    prefix="/transformers",
    tags=["Transformers"],
    dependencies=[Depends(verify_api_key)],
)


@router.get("", response_model=TransformerSearchResponse)
async def list_transformers(
    request: Request,
    page: int = Query(default=1, ge=1),
):
    client = request.app.state.http_client

    try:
        await ensure_portal_session(client)

        result = await get_transformers(
            client,
            page=page,
        )

        return TransformerSearchResponse(**result)

    except HTTPException:
        raise

    except Exception as error:
        handle_portal_error(error)
