"""Integration test against the real API.

Runs only when the ``WEBSHARE_INTEGRATION_TEST`` environment variable is set
to a truthy value — a dedicated opt-in, separate from ``WEBSHARE_API_KEY``
(which anyone using the SDK normally has set, and which would otherwise cause
a plain ``pytest`` run to silently hit production). ``WEBSHARE_API_KEY`` is
still required to authenticate; the optional ``WEBSHARE_BASE_URL`` environment
variable targets a non-production host (default: production).
"""

from __future__ import annotations

import os

import pytest

from webshare import Webshare

pytestmark = pytest.mark.skipif(
    os.environ.get("WEBSHARE_INTEGRATION_TEST", "").lower() not in ("1", "true", "yes"),
    reason="WEBSHARE_INTEGRATION_TEST is not set",
)


def test_profile_and_proxy_list() -> None:
    with Webshare(base_url=os.environ.get("WEBSHARE_BASE_URL")) as client:
        profile = client.profile.get()
        assert profile.id > 0
        assert profile.email

        page = client.proxies.list(mode="direct", page_size=1)
        assert page.count is not None
