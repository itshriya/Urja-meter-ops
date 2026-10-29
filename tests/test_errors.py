import httpx
import pytest
from fastapi import HTTPException

from app.core.errors import handle_portal_error


def test_portal_timeout_returns_504():
    with pytest.raises(HTTPException) as exc_info:
        handle_portal_error(httpx.TimeoutException("internal timeout"))

    assert exc_info.value.status_code == 504
    assert exc_info.value.detail == "The meter portal timed out."


def test_portal_connection_error_returns_502():
    request = httpx.Request("GET", "https://example.com")

    with pytest.raises(HTTPException) as exc_info:
        handle_portal_error(
            httpx.ConnectError("connection failed", request=request)
        )

    assert exc_info.value.status_code == 502
    assert exc_info.value.detail == "Unable to connect to the meter portal."


def test_portal_401_error_returns_502():
    request = httpx.Request("GET", "https://example.com")
    response = httpx.Response(401, request=request)
    error = httpx.HTTPStatusError(
        "unauthorized",
        request=request,
        response=response,
    )

    with pytest.raises(HTTPException) as exc_info:
        handle_portal_error(error)

    assert exc_info.value.status_code == 502
    assert exc_info.value.detail == "The meter portal rejected the request."


def test_unexpected_error_returns_500():
    with pytest.raises(HTTPException) as exc_info:
        handle_portal_error(ValueError("sensitive internal detail"))

    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "An unexpected error occurred."
