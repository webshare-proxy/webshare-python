"""A small consumer program used to verify the SDK's public typing surface.

Checked with ``mypy --strict`` in CI; not meant to be executed against the
real API.
"""

from __future__ import annotations

import asyncio

import webshare
from webshare.types import Proxy, Subscription


def sync_usage() -> list[str]:
    client = webshare.Webshare(api_key="example", timeout=30.0, max_retries=1)
    addresses: list[str] = []
    try:
        page: webshare.SyncPage[Proxy] = client.proxies.list(mode="direct", page_size=50)
        for proxy in page:
            if proxy.proxy_address is not None and proxy.port is not None:
                addresses.append(f"{proxy.proxy_address}:{proxy.port}")

        subscription: Subscription = client.subscription.get()
        if subscription.plan is not None:
            plan = client.plans.get(subscription.plan)
            _ = plan.proxy_count

        url: str = webshare.build_proxy_url(
            username="user",
            password="pass",
            country_codes=["us"],
            session_id=1234,
        )
        _ = url
    except webshare.RateLimitError as err:
        _ = err.status_code
    except webshare.APIError as err:
        _ = (err.code, err.request_id, err.field_errors)
    except webshare.APIConnectionError:
        pass
    finally:
        client.close()
    return addresses


async def async_usage() -> int:
    async with webshare.AsyncWebshare(api_key="example") as client:
        profile = await client.profile.get()
        _ = profile.email
        page = await client.proxies.list(mode="direct")
        total = 0
        async for _proxy in page:
            total += 1
        return total


if __name__ == "__main__":
    sync_usage()
    asyncio.run(async_usage())
