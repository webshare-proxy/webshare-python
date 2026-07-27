"""Retry behavior: 429 with Retry-After, 5xx backoff, POST opt-in."""

from __future__ import annotations

from pathlib import Path

import httpx
import pytest

import webshare
from tests.conftest import MockServer
from webshare import AsyncWebshare, Webshare
from webshare._http import compute_backoff, parse_retry_after

PROFILE = {"id": 1, "email": "user@webshare.io"}


def test_retry_on_429_honors_retry_after(server: MockServer, no_sleep: list[float]) -> None:
    server.enqueue(status=429, json_body={"detail": "throttled"}, headers={"Retry-After": "3"})
    server.enqueue(json_body=PROFILE)
    with Webshare(base_url=server.base_url, api_key="k") as client:
        profile = client.profile.get()
    assert profile.id == 1
    assert len(server.requests) == 2
    assert no_sleep == [3.0]


def test_retry_on_5xx(server: MockServer, no_sleep: list[float]) -> None:
    server.enqueue(status=500, text="oops")
    server.enqueue(status=503, text="oops")
    server.enqueue(json_body=PROFILE)
    with Webshare(base_url=server.base_url, api_key="k") as client:
        assert client.profile.get().id == 1
    assert len(server.requests) == 3
    assert len(no_sleep) == 2


def test_retries_exhausted(server: MockServer, no_sleep: list[float]) -> None:
    for _ in range(3):
        server.enqueue(status=429, json_body={"detail": "throttled"})
    with Webshare(base_url=server.base_url, api_key="k", max_retries=2) as client:
        with pytest.raises(webshare.RateLimitError):
            client.profile.get()
    assert len(server.requests) == 3


def test_no_retry_on_post(server: MockServer, no_sleep: list[float]) -> None:
    server.enqueue(status=500, text="oops")
    with Webshare(base_url=server.base_url, api_key="k") as client:
        with pytest.raises(webshare.InternalServerError):
            client.proxies.refresh()
    assert len(server.requests) == 1


def test_post_retry_opt_in(server: MockServer, no_sleep: list[float]) -> None:
    server.enqueue(status=503, text="oops")
    server.enqueue(status=204)
    with Webshare(base_url=server.base_url, api_key="k", retry_non_idempotent=True) as client:
        client.proxies.refresh()
    assert len(server.requests) == 2


def test_per_request_max_retries_override(server: MockServer, no_sleep: list[float]) -> None:
    server.enqueue(status=500, text="oops")
    with Webshare(base_url=server.base_url, api_key="k", max_retries=2) as client:
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


def test_multipart_retry_replays_file_bytes(
    server: MockServer, no_sleep: list[float], tmp_path: Path
) -> None:
    evidence = tmp_path / "evidence.bin"
    evidence.write_bytes(b"replayable-bytes")
    server.enqueue(status=503, text="oops")
    server.enqueue(json_body={"id": 1, "type": "abuse_report", "state": "inflow"})
    with Webshare(base_url=server.base_url, api_key="k", retry_non_idempotent=True) as client:
        with evidence.open("rb") as handle:
            flow = client.verification.flows.submit_evidence(1, explanation="x", files=[handle])
    assert flow.id == 1
    assert len(server.requests) == 2
    # The file object was buffered at request-build time, so the retried
    # attempt carries the full bytes even though the stream is at EOF.
    assert b"replayable-bytes" in server.requests[0].body
    assert b"replayable-bytes" in server.requests[1].body


def test_retry_after_exposed_on_non_retried_error(
    server: MockServer, no_sleep: list[float]
) -> None:
    # POST is not retried by default; the parsed Retry-After is surfaced so
    # the caller can self-throttle.
    server.enqueue(status=429, json_body={"detail": "throttled"}, headers={"Retry-After": "7"})
    with Webshare(base_url=server.base_url, api_key="k") as client:
        with pytest.raises(webshare.RateLimitError) as excinfo:
            client.proxies.refresh()
    assert excinfo.value.retry_after == 7.0
    assert len(server.requests) == 1


def test_parse_retry_after() -> None:
    assert parse_retry_after("5") == 5.0
    assert parse_retry_after("0") == 0.0
    assert parse_retry_after(" 5 ") == 5.0
    assert parse_retry_after(None) is None
    assert parse_retry_after("not-a-value") is None
    # Values are capped at 60 seconds.
    assert parse_retry_after("3600") == 60.0
    # Invalid values are treated as an absent header.
    assert parse_retry_after("") is None
    assert parse_retry_after("   ") is None
    assert parse_retry_after("nan") is None
    assert parse_retry_after("inf") is None
    assert parse_retry_after("-5") is None
    # HTTP-dates in the past yield a negative delay -> treated as absent.
    assert parse_retry_after("Wed, 21 Oct 2015 07:28:00 GMT") is None


def test_parse_retry_after_http_dates() -> None:
    from datetime import datetime, timedelta, timezone
    from email.utils import format_datetime

    future = datetime.now(timezone.utc) + timedelta(seconds=30)
    delay = parse_retry_after(format_datetime(future, usegmt=True))
    assert delay is not None
    assert 0 < delay <= 31
    # Naive HTTP-dates ("-0000" zone) are interpreted as UTC.
    naive = format_datetime(future.replace(tzinfo=None))
    delay = parse_retry_after(naive)
    assert delay is not None
    assert 0 < delay <= 31


def test_compute_backoff_bounds() -> None:
    for attempt in range(6):
        for _ in range(50):
            delay = compute_backoff(attempt)
            assert 0 <= delay <= min(8.0, 0.5 * (2**attempt))


def test_connection_error_mapped_and_retried(no_sleep: list[float]) -> None:
    calls = {"n": 0}

    def fake_request(method: str, url: str, **kwargs: object) -> httpx.Response:
        calls["n"] += 1
        raise httpx.ConnectError("boom")

    with Webshare(base_url="http://example.invalid", api_key="k") as client:
        client._http.request = fake_request  # type: ignore[assignment]
        with pytest.raises(webshare.APIConnectionError):
            client.profile.get()
    # max_retries defaults to 2 -> 3 attempts total.
    assert calls["n"] == 3
    assert len(no_sleep) == 2


async def test_async_connection_error_mapped_and_retried(no_sleep: list[float]) -> None:
    calls = {"n": 0}

    async def fake_request(method: str, url: str, **kwargs: object) -> httpx.Response:
        calls["n"] += 1
        raise httpx.ConnectError("boom")

    async with AsyncWebshare(base_url="http://example.invalid", api_key="k") as client:
        client._http.request = fake_request  # type: ignore[assignment]
        with pytest.raises(webshare.APIConnectionError):
            await client.profile.get()
    assert calls["n"] == 3
    assert len(no_sleep) == 2
