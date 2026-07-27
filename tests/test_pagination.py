"""Multi-page iteration for both clients, following `next` URLs verbatim."""

from __future__ import annotations

import pytest

from tests.conftest import MockServer
from webshare import AsyncWebshare, Webshare, WebshareError
from webshare._http import RequestSpec


def _proxy(id: str) -> dict[str, object]:
    return {"id": id, "proxy_address": "1.2.3.4", "port": 8168, "valid": True}


def _page(server: MockServer, ids: list[str], next_path: str | None) -> dict[str, object]:
    return {
        "count": 3,
        "next": server.base_url + next_path if next_path else None,
        "previous": None,
        "results": [_proxy(id) for id in ids],
    }


def test_sync_iteration_across_pages(server: MockServer) -> None:
    next_path = "/api/v2/proxy/list/?mode=direct&page=2"
    server.enqueue(json_body=_page(server, ["d-1", "d-2"], next_path))
    server.enqueue(json_body=_page(server, ["d-3"], None))
    with Webshare(base_url=server.base_url, api_key="k") as client:
        page = client.proxies.list(mode="direct")
        assert page.count == 3
        assert [p.id for p in page.results] == ["d-1", "d-2"]

        ids = [proxy.id for proxy in page]
    assert ids == ["d-1", "d-2", "d-3"]
    assert len(server.requests) == 2
    # The next URL is followed verbatim.
    assert server.requests[1].path == "/api/v2/proxy/list/"
    assert server.requests[1].query == {"mode": ["direct"], "page": ["2"]}
    assert server.requests[1].headers["Authorization"] == "Token k"


def test_sync_next_page(server: MockServer) -> None:
    server.enqueue(json_body=_page(server, ["d-1"], "/api/v2/proxy/list/?page=2"))
    server.enqueue(json_body=_page(server, ["d-2"], None))
    with Webshare(base_url=server.base_url, api_key="k") as client:
        page = client.proxies.list(mode="direct")
        second = page.next_page()
        assert second is not None
        assert [p.id for p in second.results] == ["d-2"]
        assert second.next_page() is None


async def test_async_iteration_across_pages(server: MockServer) -> None:
    server.enqueue(json_body=_page(server, ["d-1", "d-2"], "/api/v2/proxy/list/?page=2"))
    server.enqueue(json_body=_page(server, ["d-3"], None))
    async with AsyncWebshare(base_url=server.base_url, api_key="k") as client:
        page = await client.proxies.list(mode="direct")
        ids = [proxy.id async for proxy in page]
    assert ids == ["d-1", "d-2", "d-3"]
    assert len(server.requests) == 2


def test_cross_origin_next_url_is_refused(server: MockServer) -> None:
    page_body = {
        "count": 2,
        "next": "https://attacker.invalid/api/v2/proxy/list/?page=2",
        "previous": None,
        "results": [_proxy("d-1")],
    }
    server.enqueue(json_body=page_body)
    with Webshare(base_url=server.base_url, api_key="k") as client:
        page = client.proxies.list(mode="direct")
        with pytest.raises(WebshareError, match="cross-origin"):
            list(page)
    # The token was never sent to the foreign origin.
    assert len(server.requests) == 1


def test_for_url_clears_body_and_multipart() -> None:
    spec = RequestSpec(
        method="POST",
        path="/api/v2/verification/flow/1/submit_evidence/",
        json_body={"a": 1},
        multipart_data={"explanation": "x"},
        multipart_files=[("f.txt", b"1")],
    )
    follow = spec.for_url("https://proxy.webshare.io/api/v2/x/?page=2")
    assert follow.method == "GET"
    assert follow.query is None
    assert follow.json_body is None
    assert follow.multipart_data is None
    assert follow.multipart_files is None
    assert follow.absolute_url == "https://proxy.webshare.io/api/v2/x/?page=2"


def test_starting_after_pagination(server: MockServer) -> None:
    activity = {"timestamp": "2024-01-01T00:00:00+00:00", "protocol": "http", "bytes": 10}
    server.enqueue(
        json_body={
            "count": 2,
            "next": server.base_url + "/api/v2/proxy/activity/?starting_after=x",
            "previous": None,
            "results": [activity],
        }
    )
    server.enqueue(json_body={"count": 2, "next": None, "previous": None, "results": [activity]})
    with Webshare(base_url=server.base_url, api_key="k") as client:
        page = client.proxy_activity.list(page_size=1)
        items = list(page)
    assert len(items) == 2
    assert items[0].protocol == "http"
    assert server.requests[0].query == {"page_size": ["1"]}
    assert server.requests[1].query == {"starting_after": ["x"]}
