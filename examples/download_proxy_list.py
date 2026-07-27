"""Download the proxy list as plain text.

Requires the WEBSHARE_API_KEY environment variable. The download endpoint
itself is unauthenticated: it uses the `proxy_list_download_token` from the
proxy config API.
"""

import webshare


def main() -> None:
    with webshare.Webshare() as client:
        # Plan-scoped calls take the plan id from client.plans.list().
        plan = next((p for p in client.plans.list() if p.status == "active"), None)
        if plan is None:
            raise SystemExit("No active plan found on this account.")
        config = client.proxy_config.get(plan_id=plan.id)
        token = config.proxy_list_download_token
        assert token is not None

        # A shareable download URL (also available without a client via
        # webshare.build_proxy_list_download_url).
        url = client.proxies.download_url(token, country_codes=["US"], plan_id=plan.id)
        print(f"Download URL: {url}")

        # Or fetch the list directly; one address:port:username:password
        # record per line.
        text = client.proxies.download(token, country_codes=["US"], plan_id=plan.id)
        for line in text.splitlines()[:5]:
            print(line)


if __name__ == "__main__":
    main()
