"""List proxies and iterate across all pages.

Requires the WEBSHARE_API_KEY environment variable.
"""

import webshare


def main() -> None:
    with webshare.Webshare() as client:
        # Plan-scoped calls take the plan id from client.plans.list().
        plan = next(p for p in client.plans.list() if p.status == "active")

        page = client.proxies.list(mode="direct", plan_id=plan.id, page_size=25)
        print(f"Plan {plan.id}: {page.count} proxies")

        # Iterating the page object automatically follows the `next` URL
        # across every page.
        for proxy in page:
            print(f"{proxy.proxy_address}:{proxy.port} ({proxy.country_code})")


if __name__ == "__main__":
    main()
