"""Official Python SDK for the Webshare proxy API.

Quickstart::

    import webshare

    client = webshare.Webshare()  # reads WEBSHARE_API_KEY
    for proxy in client.proxies.list(mode="direct"):
        print(proxy.proxy_address, proxy.port)
"""

from . import types
from ._async_client import AsyncWebshare
from ._client import Webshare
from ._exceptions import (
    APIConnectionError,
    APIError,
    APITimeoutError,
    AuthenticationError,
    BadRequestError,
    InternalServerError,
    NotFoundError,
    PermissionDeniedError,
    RateLimitError,
    WebshareError,
)
from ._pagination import AsyncPage, SyncPage
from ._proxy_url import build_proxy_list_download_url, build_proxy_url
from ._version import __version__

__all__ = [
    "APIConnectionError",
    "APIError",
    "APITimeoutError",
    "AsyncPage",
    "AsyncWebshare",
    "AuthenticationError",
    "BadRequestError",
    "InternalServerError",
    "NotFoundError",
    "PermissionDeniedError",
    "RateLimitError",
    "SyncPage",
    "Webshare",
    "WebshareError",
    "__version__",
    "build_proxy_list_download_url",
    "build_proxy_url",
    "types",
]
