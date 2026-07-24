"""The synchronous Webshare client."""

from __future__ import annotations

import time
from collections.abc import Callable, Mapping
from types import TracebackType
from typing import Any, TypeVar

import httpx

from ._base_client import (
    BaseClient,
    auth_required_error,
    missing_credentials_error,
    resolve_static_api_key,
)
from ._exceptions import APIConnectionError, APITimeoutError
from ._http import (
    DEFAULT_MAX_RETRIES,
    RETRY_STATUS_CODES,
    RequestSpec,
    compute_backoff,
    retry_delay,
)
from ._models import decode
from ._pagination import SyncPage
from .resources import (
    Billing,
    DownloadTokens,
    IDVerificationResource,
    Invoices,
    IPAuthorizations,
    Notifications,
    PaymentMethods,
    PendingPayments,
    Plans,
    ProfileResource,
    Proxies,
    ProxyActivityResource,
    ProxyConfigResource,
    ProxyReplacements,
    Referral,
    ReplacedProxies,
    Stats,
    SubscriptionResource,
    Subusers,
    Transactions,
    Verification,
)

ModelT = TypeVar("ModelT")

CredentialsProvider = Callable[[], str]


class Webshare(BaseClient):
    """Synchronous client for the Webshare proxy API.

    Args:
        api_key: Webshare API key. Falls back to the ``WEBSHARE_API_KEY``
            environment variable when omitted; empty strings are treated as
            absent.
        credentials_provider: Callable returning the token for the
            ``Authorization`` header; called once per attempt, so refreshed
            tokens are picked up between retries. ``api_key`` is shorthand
            for a static provider.
        base_url: API host (default ``https://proxy.webshare.io``). Paths
            carry their full ``/api/vN`` prefix.
        timeout: Request timeout in seconds (default 60). The timeout bounds
            a single HTTP attempt (including reading the response body);
            total call time may exceed it when retries and Retry-After
            waits occur. When ``http_client`` is injected and ``timeout`` is
            not set, the injected client's timeout configuration is used.
        max_retries: Default retry count for retryable failures (default 2).
        http_client: An externally managed ``httpx.Client`` to send requests
            with.
        default_headers: Headers added to every request. Merging is
            case-insensitive; precedence (low to high): SDK defaults <
            ``default_headers`` < auth/subuser/federated < per-request
            headers.
        subuser_id: Sub-user to masquerade as (sent as ``X-Subuser``).
        federated_user_id: User ID for federated access, admin only (sent as
            ``X-Webshare-Federated-Access``).
        retry_non_idempotent: Also retry POST/PATCH requests (off by default;
            only GET/PUT/DELETE retry).
        unauthenticated: Construct a credential-free client for the handful
            of unauthenticated endpoints; calling an authenticated operation
            on such a client raises ``WebshareError``.
        source: Replaces the ``X-Webshare-Source`` caller-identification
            header (default ``WebshareSDK/<version> (Python; <runtime>)``).
    """

    def __init__(
        self,
        *,
        api_key: str | None = None,
        credentials_provider: CredentialsProvider | None = None,
        base_url: str | None = None,
        timeout: float | None = None,
        max_retries: int = DEFAULT_MAX_RETRIES,
        http_client: httpx.Client | None = None,
        default_headers: Mapping[str, str] | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
        retry_non_idempotent: bool = False,
        unauthenticated: bool = False,
        source: str | None = None,
    ) -> None:
        super().__init__(
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            default_headers=default_headers,
            subuser_id=subuser_id,
            federated_user_id=federated_user_id,
            retry_non_idempotent=retry_non_idempotent,
            source=source,
        )
        self._credentials_provider: CredentialsProvider | None
        if unauthenticated:
            self._credentials_provider = None
        elif credentials_provider is not None:
            self._credentials_provider = credentials_provider
        else:
            key = resolve_static_api_key(api_key)
            if key is None:
                raise missing_credentials_error()
            self._credentials_provider = lambda: key
        self._http = http_client if http_client is not None else httpx.Client()
        self._owns_http = http_client is None
        self._defer_timeout_to_http_client = http_client is not None and timeout is None

        self.proxies = Proxies(self)
        self.proxy_config = ProxyConfigResource(self)
        self.proxy_replacements = ProxyReplacements(self)
        self.replaced_proxies = ReplacedProxies(self)
        self.stats = Stats(self)
        self.proxy_activity = ProxyActivityResource(self)
        self.download_tokens = DownloadTokens(self)
        self.ip_authorizations = IPAuthorizations(self)
        self.subusers = Subusers(self)
        self.profile = ProfileResource(self)
        self.notifications = Notifications(self)
        self.id_verification = IDVerificationResource(self)
        self.verification = Verification(self)
        self.billing = Billing(self)
        self.payment_methods = PaymentMethods(self)
        self.pending_payments = PendingPayments(self)
        self.transactions = Transactions(self)
        self.subscription = SubscriptionResource(self)
        self.plans = Plans(self)
        self.invoices = Invoices(self)
        self.referral = Referral(self)

    # -- lifecycle -------------------------------------------------------

    def close(self) -> None:
        """Close the underlying HTTP client (if owned by this client)."""
        if self._owns_http:
            self._http.close()

    def __enter__(self) -> Webshare:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self.close()

    # -- transport -------------------------------------------------------

    @staticmethod
    def _sleep(seconds: float) -> None:
        if seconds > 0:
            time.sleep(seconds)

    def _token_for(self, spec: RequestSpec) -> str | None:
        if spec.auth == "none":
            return None
        if self._credentials_provider is None:
            raise auth_required_error()
        return self._credentials_provider()

    def _send(self, spec: RequestSpec) -> httpx.Response:
        max_retries = self._spec_max_retries(spec)
        retry_allowed = self._retry_allowed(spec)
        attempt = 0
        while True:
            remaining = max_retries - attempt
            # Credentials are fetched per attempt so refreshed tokens are
            # picked up mid-backoff.
            token = self._token_for(spec)
            try:
                response = self._http.request(
                    spec.method,
                    self._request_url(spec),
                    **self._request_kwargs(spec, token),
                )
            except httpx.TimeoutException as exc:
                if retry_allowed and remaining > 0:
                    self._sleep(compute_backoff(attempt))
                    attempt += 1
                    continue
                raise APITimeoutError() from exc
            except httpx.RequestError as exc:
                if retry_allowed and remaining > 0:
                    self._sleep(compute_backoff(attempt))
                    attempt += 1
                    continue
                raise APIConnectionError(str(exc) or "Connection error.") from exc
            if response.status_code in RETRY_STATUS_CODES and retry_allowed and remaining > 0:
                self._sleep(retry_delay(attempt, response.headers.get("Retry-After")))
                attempt += 1
                continue
            self._raise_for_status(response)
            return response

    # -- requester interface ---------------------------------------------

    def request_none(self, spec: RequestSpec) -> None:
        self._send(spec)

    def request_json(self, spec: RequestSpec) -> Any:
        return self._json(self._send(spec))

    def request_model(self, spec: RequestSpec, cls: type[ModelT]) -> ModelT:
        return self._decode_model(self._send(spec), cls)

    def request_model_list(self, spec: RequestSpec, cls: type[ModelT]) -> list[ModelT]:
        return self._decode_model_list(self._send(spec), cls)

    def request_model_dict(self, spec: RequestSpec, cls: type[ModelT]) -> dict[str, ModelT]:
        return self._decode_model_dict(self._send(spec), cls)

    def request_text(self, spec: RequestSpec) -> str:
        return self._send(spec).text

    def request_bytes(self, spec: RequestSpec) -> bytes:
        return self._send(spec).content

    def request_page(self, spec: RequestSpec, item_cls: type[ModelT]) -> SyncPage[ModelT]:
        response = self._send(spec)
        results, count, next_url, previous = self._parse_envelope(response)
        return SyncPage(
            results=[decode(item_cls, item) for item in results],
            count=count,
            next=next_url,
            previous=previous,
            client=self,
            item_cls=item_cls,
            spec=spec,
        )
