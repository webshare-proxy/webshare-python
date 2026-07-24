"""Integration test against the real API.

Runs only when the ``WEBSHARE_API_KEY`` environment variable is set.
"""

from __future__ import annotations

import os

import pytest

from webshare import Webshare

pytestmark = pytest.mark.skipif(
    not os.environ.get("WEBSHARE_API_KEY"),
    reason="WEBSHARE_API_KEY is not set",
)


def test_profile_and_proxy_list() -> None:
    with Webshare() as client:
        profile = client.profile.get()
        assert profile.id > 0
        assert profile.email

        page = client.proxies.list(mode="direct", page_size=1)
        assert page.count is not None
