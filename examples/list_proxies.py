"""List proxies and iterate across all pages.

Requires the WEBSHARE_API_KEY environment variable.
"""

import webshare


def main() -> None:
    with webshare.Webshare() as client:
        page = client.proxies.list(mode="direct", page_size=25)
        print(f"Total proxies: {page.count}")

        # Iterating the page object automatically follows the `next` URL
        # across every page.
        for proxy in page:
            print(f"{proxy.proxy_address}:{proxy.port} ({proxy.country_code})")


if __name__ == "__main__":
    main()
