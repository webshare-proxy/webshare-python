"""Official Python SDK for the Webshare proxy API.

Quickstart::

    import webshare

    with webshare.Webshare() as client:  # reads WEBSHARE_API_KEY
        for proxy in client.proxies.list(mode="direct"):
            print(proxy.proxy_address, proxy.port)
"""

from webshare import types
from webshare._async_client import AsyncWebshare
from webshare._client import Webshare
from webshare._exceptions import (
    APIConnectionError,
    APIError,
    APITimeoutError,
    AuthenticationError,
    BadRequestError,
    InternalServerError,
    NotFoundError,
    PermissionDeniedError,
    RateLimitError,
    ResponseDecodeError,
    WebshareError,
)
from webshare._pagination import AsyncPage, SyncPage
from webshare._proxy_url import build_proxy_list_download_url, build_proxy_url
from webshare._version import __version__

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
    "ResponseDecodeError",
    "SyncPage",
    "Webshare",
    "WebshareError",
    "__version__",
    "build_proxy_list_download_url",
    "build_proxy_url",
    "types",
]
