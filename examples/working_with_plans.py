"""List plans and run plan-scoped calls with an explicit plan id.

Most proxy operations accept a plan_id and fall back to an account default
when omitted; passing the id explicitly is the standard pattern. Requires the
WEBSHARE_API_KEY environment variable.
"""

import webshare


def main() -> None:
    with webshare.Webshare() as client:
        # 1. List plans and pick one (here: the first active plan).
        plans = [plan for plan in client.plans.list() if plan.status == "active"]
        if not plans:
            print("No active plans on this account.")
            return
        plan = plans[0]
        print(f"Using plan {plan.id}: {plan.proxy_count} x {plan.proxy_type} proxies")

        # 2. Pass its id to plan-scoped calls.
        page = client.proxies.list(mode="direct", plan_id=plan.id, page_size=5)
        print(f"Plan {plan.id} has {page.count} proxies; first page:")
        for proxy in page.results:
            print(f"  {proxy.proxy_address}:{proxy.port} ({proxy.country_code})")

        config = client.proxy_config.get(plan_id=plan.id)
        print(f"Request timeout: {config.request_timeout}s")

        if config.proxy_list_download_token:
            url = client.proxies.download_url(config.proxy_list_download_token, plan_id=plan.id)
            print(f"Download URL: {url}")


if __name__ == "__main__":
    main()
