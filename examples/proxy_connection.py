"""Build proxy connection URLs with the pure helper.

The backbone username grammar supports country targeting, city targeting
(residential plans), sticky sessions and per-request rotation.
"""

from webshare import build_proxy_url


def main() -> None:
    # Backbone mode: connect to p.webshare.io with a sticky session in the US.
    sticky = build_proxy_url(
        username="myuser",
        password="mypassword",
        country_codes=["US"],
        session_id=1234,
    )
    print(sticky)  # http://myuser-us-1234:mypassword@p.webshare.io:80

    # Rotate to a new IP on every request, targeting a city.
    rotating = build_proxy_url(
        username="myuser",
        password="mypassword",
        country_codes=["us"],
        city="los_angeles",
        rotate=True,
    )
    print(rotating)  # http://myuser-us-city_los_angeles-rotate:mypassword@p.webshare.io:80

    # Direct mode: connect straight to a proxy from client.proxies.list().
    direct = build_proxy_url(
        mode="direct",
        username="myuser",
        password="mypassword",
        proxy_address="1.2.3.4",
        port=8168,
    )
    print(direct)  # http://myuser:mypassword@1.2.3.4:8168

    # IP authorization mode: no credentials in the URL at all.
    ip_auth = build_proxy_url(mode="direct", proxy_address="1.2.3.4", port=8168)
    print(ip_auth)  # http://1.2.3.4:8168


if __name__ == "__main__":
    main()
