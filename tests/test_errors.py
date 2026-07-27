"""Error mapping: status to class, field errors, codes, request IDs."""

from __future__ import annotations

from collections.abc import Iterator

import pytest

import webshare
from tests.conftest import MockServer
from webshare import Webshare


@pytest.fixture
def client(server: MockServer) -> Iterator[Webshare]:
    with Webshare(base_url=server.base_url, api_key="k", max_retries=0) as c:
        yield c


def test_400_field_errors(server: MockServer, client: Webshare) -> None:
    server.enqueue(status=400, json_body={"mode": ["This field is required."]})
    with pytest.raises(webshare.BadRequestError) as excinfo:
        client.proxies.list(mode="direct")
    error = excinfo.value
    assert error.status_code == 400
    assert error.field_errors == {"mode": ["This field is required."]}


def test_400_field_errors_object_form(server: MockServer, client: Webshare) -> None:
    # The live API returns lists of objects, not the documented list of
    # strings; this is the real shape verbatim.
    server.enqueue(
        status=400,
        json_body={"mode": [{"message": "This field is required.", "code": "required"}]},
    )
    with pytest.raises(webshare.BadRequestError) as excinfo:
        client.proxies.list(mode="direct")
    error = excinfo.value
    assert error.status_code == 400
    assert error.field_errors == {"mode": ["This field is required."]}


def test_400_field_errors_bare_string_value(server: MockServer, client: Webshare) -> None:
    server.enqueue(status=400, json_body={"mode": "This field is required."})
    with pytest.raises(webshare.BadRequestError) as excinfo:
        client.proxies.list(mode="direct")
    assert excinfo.value.field_errors == {"mode": ["This field is required."]}


def test_401_authentication_error(server: MockServer, client: Webshare) -> None:
    server.enqueue(status=401, json_body={"detail": "Invalid token."})
    with pytest.raises(webshare.AuthenticationError) as excinfo:
        client.profile.get()
    assert excinfo.value.detail == "Invalid token."
    # The live API does not send X-Request-ID; absence yields None.
    assert excinfo.value.request_id is None


def test_403_surfaces_code(server: MockServer, client: Webshare) -> None:
    server.enqueue(
        status=403,
        json_body={"detail": "Two factor authentication is needed.", "code": "2fa_needed"},
        headers={"X-Request-ID": "req-123"},
    )
    with pytest.raises(webshare.PermissionDeniedError) as excinfo:
        client.profile.get()
    error = excinfo.value
    assert error.code == "2fa_needed"
    assert error.request_id == "req-123"
    assert error.detail == "Two factor authentication is needed."


def test_404_not_found(server: MockServer, client: Webshare) -> None:
    server.enqueue(status=404, json_body={"detail": "Not found."})
    with pytest.raises(webshare.NotFoundError):
        client.subusers.get(42)


def test_429_rate_limit(server: MockServer, client: Webshare) -> None:
    server.enqueue(status=429, json_body={"detail": "Request was throttled."})
    with pytest.raises(webshare.RateLimitError) as excinfo:
        client.profile.get()
    assert excinfo.value.status_code == 429


def test_5xx_internal_server_error(server: MockServer, client: Webshare) -> None:
    server.enqueue(status=502, text="Bad Gateway")
    with pytest.raises(webshare.InternalServerError) as excinfo:
        client.profile.get()
    error = excinfo.value
    assert error.status_code == 502
    # Non-JSON bodies are kept as the detail text.
    assert error.detail == "Bad Gateway"


def test_bare_json_string_body(server: MockServer, client: Webshare) -> None:
    server.enqueue(status=400, json_body="something went wrong")
    with pytest.raises(webshare.BadRequestError) as excinfo:
        client.profile.get()
    assert excinfo.value.detail == "something went wrong"


def test_errors_are_webshare_errors(server: MockServer, client: Webshare) -> None:
    server.enqueue(status=400, json_body={"detail": "bad"})
    with pytest.raises(webshare.WebshareError):
        client.profile.get()


def test_2xx_non_json_raises_response_decode_error(server: MockServer, client: Webshare) -> None:
    server.enqueue(status=200, text="<html>maintenance</html>", content_type="text/html")
    with pytest.raises(webshare.ResponseDecodeError) as excinfo:
        client.profile.get()
    error = excinfo.value
    assert isinstance(error, webshare.WebshareError)
    assert error.status_code == 200
    assert "<html>maintenance</html>" in error.body


def test_malformed_envelope_raises_response_decode_error(
    server: MockServer, client: Webshare
) -> None:
    server.enqueue(status=200, json_body={"count": 1, "next": None, "results": None})
    with pytest.raises(webshare.ResponseDecodeError) as excinfo:
        client.proxies.list(mode="direct")
    assert excinfo.value.status_code == 200
    assert "results" in str(excinfo.value)


def test_error_body_capped_and_detail_truncated(server: MockServer, client: Webshare) -> None:
    huge = "x" * (1024 * 1024 + 4096)
    server.enqueue(status=500, text=huge)
    with pytest.raises(webshare.InternalServerError) as excinfo:
        client.profile.get()
    error = excinfo.value
    # Raw capture is capped at 1 MiB; the human-facing detail at ~2 KB.
    assert isinstance(error.body, str)
    assert len(error.body) == 1024 * 1024
    assert error.detail is not None
    assert len(error.detail) < 2200
    assert len(str(error)) < 2200
