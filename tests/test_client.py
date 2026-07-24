"""Client construction, auth, headers and timeout behavior."""

from __future__ import annotations

import pytest

import webshare
from webshare import AsyncWebshare, Webshare

from .conftest import MockServer

PROFILE = {"id": 1, "email": "user@webshare.io"}


def make_client(server: MockServer, **kwargs: object) -> Webshare:
    kwargs.setdefault("api_key", "test-key")
    return Webshare(base_url=server.base_url, **kwargs)  # type: ignore[arg-type]


def test_auth_header_and_defaults(server: MockServer) -> None:
    server.enqueue(json_body=PROFILE)
    client = make_client(server)
    profile = client.profile.get()
    assert profile.id == 1
    assert profile.email == "user@webshare.io"
    request = server.requests[0]
    assert request.method == "GET"
    assert request.path == "/api/v2/profile/"
    assert request.headers["Authorization"] == "Token test-key"
    assert request.headers["Accept"] == "application/json"
    assert request.headers["User-Agent"] == f"webshare-python/{webshare.__version__}"


def test_api_key_from_environment(server: MockServer, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("WEBSHARE_API_KEY", "env-key")
    server.enqueue(json_body=PROFILE)
    client = Webshare(base_url=server.base_url)
    client.profile.get()
    assert server.requests[0].headers["Authorization"] == "Token env-key"


def test_missing_credentials_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("WEBSHARE_API_KEY", raising=False)
    with pytest.raises(webshare.WebshareError, match="WEBSHARE_API_KEY"):
        Webshare()
    with pytest.raises(webshare.WebshareError, match="WEBSHARE_API_KEY"):
        AsyncWebshare()


def test_credentials_provider_called_per_request(server: MockServer) -> None:
    tokens = iter(["token-1", "token-2"])
    client = Webshare(base_url=server.base_url, credentials_provider=lambda: next(tokens))
    server.enqueue(json_body=PROFILE)
    server.enqueue(json_body=PROFILE)
    client.profile.get()
    client.profile.get()
    assert server.requests[0].headers["Authorization"] == "Token token-1"
    assert server.requests[1].headers["Authorization"] == "Token token-2"


async def test_async_credentials_provider(server: MockServer) -> None:
    async def provider() -> str:
        return "async-token"

    client = AsyncWebshare(base_url=server.base_url, credentials_provider=provider)
    server.enqueue(json_body=PROFILE)
    profile = await client.profile.get()
    assert profile.email == "user@webshare.io"
    assert server.requests[0].headers["Authorization"] == "Token async-token"
    await client.close()


def test_default_and_per_request_headers(server: MockServer) -> None:
    client = make_client(server, default_headers={"X-Team": "infra"})
    server.enqueue(json_body=PROFILE)
    client.profile.get(headers={"X-Trace": "abc"})
    request = server.requests[0]
    assert request.headers["X-Team"] == "infra"
    assert request.headers["X-Trace"] == "abc"


def test_subuser_and_federated_headers(server: MockServer) -> None:
    client = make_client(server, subuser_id=7, federated_user_id=99)
    server.enqueue(json_body={"count": 0, "next": None, "previous": None, "results": []})
    server.enqueue(json_body={"count": 0, "next": None, "previous": None, "results": []})
    client.proxies.list(mode="direct")
    assert server.requests[0].headers["X-Subuser"] == "7"
    assert server.requests[0].headers["X-Webshare-Federated-Access"] == "99"
    # Per-request values override client-level values.
    client.proxies.list(mode="direct", subuser_id=8, federated_user_id=100)
    assert server.requests[1].headers["X-Subuser"] == "8"
    assert server.requests[1].headers["X-Webshare-Federated-Access"] == "100"


def test_timeout_raises_api_timeout_error(server: MockServer) -> None:
    server.enqueue(json_body=PROFILE, delay=1.0)
    client = make_client(server, timeout=0.1, max_retries=0)
    with pytest.raises(webshare.APITimeoutError):
        client.profile.get()


async def test_async_timeout(server: MockServer) -> None:
    server.enqueue(json_body=PROFILE, delay=1.0)
    async with AsyncWebshare(base_url=server.base_url, api_key="k", timeout=0.1) as client:
        with pytest.raises(webshare.APITimeoutError):
            await client.profile.get(max_retries=0)


def test_context_manager_and_base_url_join(server: MockServer) -> None:
    server.enqueue(json_body=PROFILE)
    with Webshare(base_url=server.base_url + "/", api_key="k") as client:
        client.profile.get()
    assert server.requests[0].path == "/api/v2/profile/"
