"""Proxy connection helpers.

``build_proxy_url`` builds proxy connection URLs for both connection modes:

* **Backbone** mode connects to ``p.webshare.io`` and encodes geo targeting,
  sticky sessions and rotation into the proxy username using the grammar
  ``{username}[-{cc}...][-city_{name}][-{session}|-rotate]``.
* **Direct** mode connects to the ``proxy_address``/``port`` returned by the
  proxy list API.

``build_proxy_list_download_url`` builds the path-style, unauthenticated proxy
list download URL (token from the proxy config's ``proxy_list_download_token``).

Both are pure functions.
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from typing import Literal
from urllib.parse import quote

from webshare._http import DEFAULT_BASE_URL

__all__ = ["BACKBONE_HOST", "build_proxy_list_download_url", "build_proxy_url"]

BACKBONE_HOST = "p.webshare.io"
_DEFAULT_BACKBONE_PORT = 80

_COUNTRY_CODE_RE = re.compile(r"^[A-Za-z]{2}$")
_CITY_RE = re.compile(r"^[A-Za-z_]+$")


def _build_backbone_username(
    username: str,
    *,
    country_codes: Sequence[str] | None,
    city: str | None,
    session_id: int | str | None,
    rotate: bool,
) -> str:
    """Apply the backbone username parameter grammar, in documented order:
    country codes first, then city, then session/rotate last."""
    parts = [username]
    for code in country_codes or ():
        if not _COUNTRY_CODE_RE.fullmatch(code):
            raise ValueError(
                f"Invalid country code {code!r}: must be a 2-letter ISO 3166-1 alpha-2 code."
            )
        parts.append(code.lower())
    if city is not None:
        if not _CITY_RE.fullmatch(city):
            raise ValueError(
                f"Invalid city {city!r}: city names may contain only letters and underscores."
            )
        parts.append(f"city_{city.lower()}")
    if session_id is not None and rotate:
        raise ValueError("session_id and rotate are mutually exclusive.")
    if session_id is not None:
        session = str(session_id)
        # `str.isdigit()` alone also accepts non-ASCII digit characters
        # (e.g. superscripts, Arabic-indic digits); require plain ASCII 0-9.
        if not (session.isascii() and session.isdigit()):
            raise ValueError(f"Invalid session_id {session_id!r}: must be numeric.")
        parts.append(session)
    elif rotate:
        parts.append("rotate")
    return "-".join(parts)


def build_proxy_url(
    *,
    mode: Literal["backbone", "direct"] = "backbone",
    scheme: str = "http",
    username: str | None = None,
    password: str | None = None,
    proxy_address: str | None = None,
    port: int | None = None,
    country_codes: Sequence[str] | None = None,
    city: str | None = None,
    session_id: int | str | None = None,
    rotate: bool = False,
) -> str:
    """Build a proxy connection URL.

    Args:
        mode: ``backbone`` (connect to ``p.webshare.io``; required for
            residential plans) or ``direct`` (connect to the proxy's own
            address).
        scheme: URL scheme, e.g. ``http`` or ``socks5``.
        username: Proxy username. Omit together with ``password`` for
            IP-authorization mode (the source IP must be authorized).
        password: Proxy password.
        proxy_address: Proxy IP address; required in ``direct`` mode.
        port: Port to connect to. Defaults to 80 in ``backbone`` mode;
            required in ``direct`` mode.
        country_codes: Backbone geo targeting: ISO 3166-1 alpha-2 country
            codes appended to the username (lowercased).
        city: Backbone city targeting (residential plans only). Letters and
            underscores only.
        session_id: Numeric sticky-session ID; the same session ID routes to
            the same exit IP. Mutually exclusive with ``rotate``.
        rotate: Rotate to a new IP on every request.

    Returns:
        The proxy URL, e.g. ``http://user-us-1234:pass@p.webshare.io:80``.

    Raises:
        ValueError: On invalid or conflicting parameter combinations.
    """
    if (username is None) != (password is None):
        raise ValueError("username and password must be provided together.")
    has_username_params = (
        bool(country_codes) or city is not None or session_id is not None or rotate
    )

    if mode == "direct":
        if has_username_params:
            raise ValueError(
                "country_codes, city, session_id and rotate only apply to backbone mode "
                "(they are encoded into the backbone username)."
            )
        if proxy_address is None or port is None:
            raise ValueError(
                "direct mode requires proxy_address and port (from the proxy list API)."
            )
        host = proxy_address
    elif mode == "backbone":
        if proxy_address is not None:
            raise ValueError("proxy_address does not apply to backbone mode; use direct mode.")
        host = BACKBONE_HOST
        if port is None:
            port = _DEFAULT_BACKBONE_PORT
    else:
        raise ValueError(f"Invalid mode {mode!r}: expected 'backbone' or 'direct'.")

    if username is None or password is None:
        # IP authorization mode: no credentials in the URL.
        if has_username_params:
            raise ValueError(
                "country_codes, city, session_id and rotate require username/password "
                "authentication; with IP authorization, geo selection is configured via "
                "the proxy config API."
            )
        return f"{scheme}://{host}:{port}"

    if mode == "backbone":
        username = _build_backbone_username(
            username,
            country_codes=country_codes,
            city=city,
            session_id=session_id,
            rotate=rotate,
        )
    return f"{scheme}://{quote(username, safe='')}:{quote(password, safe='')}@{host}:{port}"


def proxy_list_download_path(
    token: str,
    *,
    country_codes: Sequence[str] | None = None,
    proxy_protocol: str = "any",
    authentication_method: Literal["username", "sourceip"] = "username",
    endpoint_mode: Literal["direct", "backbone"] = "direct",
    search: str | None = None,
) -> str:
    """Build the path portion of the proxy list download URL."""
    country_segment = (
        "-".join(quote(code.upper(), safe="") for code in country_codes) if country_codes else "-"
    )
    search_segment = quote(search, safe="") if search else "-"
    return (
        f"/api/v2/proxy/list/download/{quote(token, safe='')}/{country_segment}/"
        f"{quote(proxy_protocol, safe='')}/{quote(authentication_method, safe='')}/"
        f"{quote(endpoint_mode, safe='')}/{search_segment}/"
    )


def build_proxy_list_download_url(
    token: str,
    *,
    country_codes: Sequence[str] | None = None,
    proxy_protocol: str = "any",
    authentication_method: Literal["username", "sourceip"] = "username",
    endpoint_mode: Literal["direct", "backbone"] = "direct",
    search: str | None = None,
    plan_id: int | None = None,
    base_url: str = DEFAULT_BASE_URL,
) -> str:
    """Build the full, unauthenticated proxy list download URL.

    Args:
        token: The ``proxy_list_download_token`` from the proxy config API.
        country_codes: Country codes to filter by (hyphen-joined in the URL);
            omit for all countries.
        proxy_protocol: The literal protocol slot in the URL; default ``any``.
        authentication_method: ``username`` or ``sourceip``.
        endpoint_mode: ``direct`` or ``backbone`` (must be ``backbone`` for
            residential plans).
        search: Optional search terms (URL-encoded into the path).
        plan_id: Target a specific plan; otherwise the default plan is used.
        base_url: API host; defaults to ``https://proxy.webshare.io``.

    Returns:
        A URL serving one ``address:port:username:password`` record per line.
    """
    path = proxy_list_download_path(
        token,
        country_codes=country_codes,
        proxy_protocol=proxy_protocol,
        authentication_method=authentication_method,
        endpoint_mode=endpoint_mode,
        search=search,
    )
    url = base_url.rstrip("/") + path
    if plan_id is not None:
        url += f"?plan_id={plan_id}"
    return url
