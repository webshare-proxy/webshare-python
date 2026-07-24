"""Use the asynchronous client.

Requires the WEBSHARE_API_KEY environment variable.
"""

import asyncio

import webshare


async def main() -> None:
    async with webshare.AsyncWebshare() as client:
        profile = await client.profile.get()
        print(f"Signed in as {profile.email}")

        page = await client.proxies.list(mode="direct", page_size=25)
        async for proxy in page:
            print(f"{proxy.proxy_address}:{proxy.port}")


if __name__ == "__main__":
    asyncio.run(main())
