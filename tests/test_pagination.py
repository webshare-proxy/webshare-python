"""Multi-page iteration for both clients, following `next` URLs verbatim."""

from __future__ import annotations

from webshare import AsyncWebshare, Webshare

from .conftest import MockServer


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
    client = Webshare(base_url=server.base_url, api_key="k")

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
    client = Webshare(base_url=server.base_url, api_key="k")

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
    client = Webshare(base_url=server.base_url, api_key="k")

    page = client.proxy_activity.list(page_size=1)
    items = list(page)
    assert len(items) == 2
    assert items[0].protocol == "http"
    assert server.requests[0].query == {"page_size": ["1"]}
    assert server.requests[1].query == {"starting_after": ["x"]}
