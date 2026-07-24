"""Error mapping: status to class, field errors, codes, request IDs."""

from __future__ import annotations

import pytest

import webshare
from webshare import Webshare

from .conftest import MockServer


def make_client(server: MockServer) -> Webshare:
    return Webshare(base_url=server.base_url, api_key="k", max_retries=0)


def test_400_field_errors(server: MockServer) -> None:
    server.enqueue(status=400, json_body={"mode": ["This field is required."]})
    with pytest.raises(webshare.BadRequestError) as excinfo:
        make_client(server).proxies.list(mode="direct")
    error = excinfo.value
    assert error.status_code == 400
    assert error.field_errors == {"mode": ["This field is required."]}


def test_401_authentication_error(server: MockServer) -> None:
    server.enqueue(status=401, json_body={"detail": "Invalid token."})
    with pytest.raises(webshare.AuthenticationError) as excinfo:
        make_client(server).profile.get()
    assert excinfo.value.detail == "Invalid token."


def test_403_surfaces_code(server: MockServer) -> None:
    server.enqueue(
        status=403,
        json_body={"detail": "Two factor authentication is needed.", "code": "2fa_needed"},
        headers={"X-Request-ID": "req-123"},
    )
    with pytest.raises(webshare.PermissionDeniedError) as excinfo:
        make_client(server).profile.get()
    error = excinfo.value
    assert error.code == "2fa_needed"
    assert error.request_id == "req-123"
    assert error.detail == "Two factor authentication is needed."


def test_404_not_found(server: MockServer) -> None:
    server.enqueue(status=404, json_body={"detail": "Not found."})
    with pytest.raises(webshare.NotFoundError):
        make_client(server).subusers.get(42)


def test_429_rate_limit(server: MockServer) -> None:
    server.enqueue(status=429, json_body={"detail": "Request was throttled."})
    with pytest.raises(webshare.RateLimitError) as excinfo:
        make_client(server).profile.get()
    assert excinfo.value.status_code == 429


def test_5xx_internal_server_error(server: MockServer) -> None:
    server.enqueue(status=502, text="Bad Gateway")
    with pytest.raises(webshare.InternalServerError) as excinfo:
        make_client(server).profile.get()
    error = excinfo.value
    assert error.status_code == 502
    # Non-JSON bodies are kept as the detail text.
    assert error.detail == "Bad Gateway"


def test_bare_json_string_body(server: MockServer) -> None:
    server.enqueue(status=400, json_body="something went wrong")
    with pytest.raises(webshare.BadRequestError) as excinfo:
        make_client(server).profile.get()
    assert excinfo.value.detail == "something went wrong"


def test_errors_are_webshare_errors(server: MockServer) -> None:
    server.enqueue(status=400, json_body={"detail": "bad"})
    with pytest.raises(webshare.WebshareError):
        make_client(server).profile.get()
