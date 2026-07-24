"""Retry behavior: 429 with Retry-After, 5xx backoff, POST opt-in."""

from __future__ import annotations

import pytest

import webshare
from webshare import AsyncWebshare, Webshare
from webshare._http import compute_backoff, parse_retry_after

from .conftest import MockServer

PROFILE = {"id": 1, "email": "user@webshare.io"}


def test_retry_on_429_honors_retry_after(server: MockServer, no_sleep: list[float]) -> None:
    server.enqueue(status=429, json_body={"detail": "throttled"}, headers={"Retry-After": "3"})
    server.enqueue(json_body=PROFILE)
    client = Webshare(base_url=server.base_url, api_key="k")
    profile = client.profile.get()
    assert profile.id == 1
    assert len(server.requests) == 2
    assert no_sleep == [3.0]


def test_retry_on_5xx(server: MockServer, no_sleep: list[float]) -> None:
    server.enqueue(status=500, text="oops")
    server.enqueue(status=503, text="oops")
    server.enqueue(json_body=PROFILE)
    client = Webshare(base_url=server.base_url, api_key="k")
    assert client.profile.get().id == 1
    assert len(server.requests) == 3
    assert len(no_sleep) == 2


def test_retries_exhausted(server: MockServer, no_sleep: list[float]) -> None:
    for _ in range(3):
        server.enqueue(status=429, json_body={"detail": "throttled"})
    client = Webshare(base_url=server.base_url, api_key="k", max_retries=2)
    with pytest.raises(webshare.RateLimitError):
        client.profile.get()
    assert len(server.requests) == 3


def test_no_retry_on_post(server: MockServer, no_sleep: list[float]) -> None:
    server.enqueue(status=500, text="oops")
    client = Webshare(base_url=server.base_url, api_key="k")
    with pytest.raises(webshare.InternalServerError):
        client.proxies.refresh()
    assert len(server.requests) == 1


def test_post_retry_opt_in(server: MockServer, no_sleep: list[float]) -> None:
    server.enqueue(status=503, text="oops")
    server.enqueue(status=204)
    client = Webshare(base_url=server.base_url, api_key="k", retry_non_idempotent=True)
    client.proxies.refresh()
    assert len(server.requests) == 2


def test_per_request_max_retries_override(server: MockServer, no_sleep: list[float]) -> None:
    server.enqueue(status=500, text="oops")
    client = Webshare(base_url=server.base_url, api_key="k", max_retries=2)
    with pytest.raises(webshare.InternalServerError):
        client.profile.get(max_retries=0)
    assert len(server.requests) == 1


async def test_async_retry_on_429(server: MockServer, no_sleep: list[float]) -> None:
    server.enqueue(status=429, json_body={"detail": "throttled"}, headers={"Retry-After": "0"})
    server.enqueue(json_body=PROFILE)
    async with AsyncWebshare(base_url=server.base_url, api_key="k") as client:
        profile = await client.profile.get()
    assert profile.id == 1
    assert len(server.requests) == 2


def test_parse_retry_after() -> None:
    assert parse_retry_after("5") == 5.0
    assert parse_retry_after("0") == 0.0
    assert parse_retry_after(None) is None
    assert parse_retry_after("not-a-value") is None
    # Values are capped at 60 seconds.
    assert parse_retry_after("3600") == 60.0
    # HTTP-date form parses to a non-negative delay (date in the past -> 0).
    assert parse_retry_after("Wed, 21 Oct 2015 07:28:00 GMT") == 0.0


def test_compute_backoff_bounds() -> None:
    for attempt in range(6):
        for _ in range(50):
            delay = compute_backoff(attempt)
            assert 0 <= delay <= min(8.0, 0.5 * (2**attempt))
