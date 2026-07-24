"""Unit tests for the pure proxy URL helpers."""

from __future__ import annotations

import pytest

from webshare import build_proxy_list_download_url, build_proxy_url


def test_backbone_basic() -> None:
    url = build_proxy_url(username="user", password="pass")
    assert url == "http://user:pass@p.webshare.io:80"


def test_backbone_country_codes_lowercased() -> None:
    url = build_proxy_url(username="user", password="pass", country_codes=["US", "FR"])
    assert url == "http://user-us-fr:pass@p.webshare.io:80"


def test_backbone_sticky_session() -> None:
    url = build_proxy_url(username="user", password="pass", country_codes=["us"], session_id=1234)
    assert url == "http://user-us-1234:pass@p.webshare.io:80"


def test_backbone_rotate() -> None:
    url = build_proxy_url(username="user", password="pass", country_codes=["us"], rotate=True)
    assert url == "http://user-us-rotate:pass@p.webshare.io:80"


def test_backbone_city_ordering() -> None:
    # Documented order: country codes, then city, then session/rotate last.
    url = build_proxy_url(
        username="user",
        password="pass",
        country_codes=["de"],
        city="Munich",
        session_id="1234",
    )
    assert url == "http://user-de-city_munich-1234:pass@p.webshare.io:80"


def test_backbone_custom_port_and_scheme() -> None:
    url = build_proxy_url(username="user", password="pass", scheme="socks5", port=1080)
    assert url == "socks5://user:pass@p.webshare.io:1080"


def test_backbone_ip_authorization() -> None:
    assert build_proxy_url(port=9999) == "http://p.webshare.io:9999"
    assert build_proxy_url() == "http://p.webshare.io:80"


def test_direct_mode() -> None:
    url = build_proxy_url(
        mode="direct", username="user", password="pass", proxy_address="1.2.3.4", port=8168
    )
    assert url == "http://user:pass@1.2.3.4:8168"


def test_direct_ip_authorization() -> None:
    url = build_proxy_url(mode="direct", proxy_address="1.2.3.4", port=8168)
    assert url == "http://1.2.3.4:8168"


def test_credentials_are_url_quoted() -> None:
    url = build_proxy_url(username="user", password="p@ss:word/1")
    assert url == "http://user:p%40ss%3Aword%2F1@p.webshare.io:80"


def test_session_and_rotate_are_mutually_exclusive() -> None:
    with pytest.raises(ValueError, match="mutually exclusive"):
        build_proxy_url(username="u", password="p", session_id=1, rotate=True)


def test_invalid_country_code() -> None:
    with pytest.raises(ValueError, match="country code"):
        build_proxy_url(username="u", password="p", country_codes=["USA"])


def test_invalid_city() -> None:
    with pytest.raises(ValueError, match="city"):
        build_proxy_url(username="u", password="p", city="Los Angeles")


def test_invalid_session_id() -> None:
    with pytest.raises(ValueError, match="session_id"):
        build_proxy_url(username="u", password="p", session_id="abc")


def test_username_without_password() -> None:
    with pytest.raises(ValueError, match="together"):
        build_proxy_url(username="u")


def test_direct_mode_rejects_username_params() -> None:
    with pytest.raises(ValueError, match="backbone"):
        build_proxy_url(
            mode="direct",
            username="u",
            password="p",
            proxy_address="1.2.3.4",
            port=80,
            country_codes=["us"],
        )


def test_direct_mode_requires_address_and_port() -> None:
    with pytest.raises(ValueError, match="proxy_address"):
        build_proxy_url(mode="direct", username="u", password="p")


def test_ip_auth_rejects_username_params() -> None:
    with pytest.raises(ValueError, match="username/password"):
        build_proxy_url(country_codes=["us"])


def test_download_url_defaults() -> None:
    url = build_proxy_list_download_url("tok123")
    assert url == (
        "https://proxy.webshare.io/api/v2/proxy/list/download/tok123/-/any/username/direct/-/"
    )


def test_download_url_full() -> None:
    url = build_proxy_list_download_url(
        "tok123",
        country_codes=["us", "FR"],
        authentication_method="sourceip",
        endpoint_mode="backbone",
        search="fast proxy",
        plan_id=42,
    )
    assert url == (
        "https://proxy.webshare.io/api/v2/proxy/list/download/tok123/US-FR/any/"
        "sourceip/backbone/fast%20proxy/?plan_id=42"
    )
