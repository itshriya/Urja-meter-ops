import httpx
from fastapi import HTTPException


def handle_portal_error(error: Exception) -> None:
    if isinstance(error, httpx.TimeoutException):
        raise HTTPException(
            status_code=504,
            detail="The meter portal timed out.",
        )

    if isinstance(error, httpx.HTTPStatusError):
        status_code = error.response.status_code

        if status_code in (401, 403):
            raise HTTPException(
                status_code=502,
                detail="The meter portal rejected the request.",
            )

        return_status = 502
        raise HTTPException(
            status_code=return_status,
            detail="The meter portal returned an error.",
        )

    if isinstance(error, httpx.RequestError):
        raise HTTPException(
            status_code=502,
            detail="Unable to connect to the meter portal.",
        )

    raise HTTPException(
        status_code=500,
        detail="An unexpected error occurred.",
    )
