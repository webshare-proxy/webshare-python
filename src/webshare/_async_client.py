"""The asynchronous Webshare client."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable, Mapping
from types import TracebackType
from typing import Any, TypeVar

import httpx

from webshare._base_client import (
    BaseClient,
    auth_required_error,
    missing_credentials_error,
    resolve_static_api_key,
)
from webshare._exceptions import APIConnectionError, APITimeoutError
from webshare._http import (
    DEFAULT_MAX_RETRIES,
    RETRY_STATUS_CODES,
    RequestSpec,
    compute_backoff,
    retry_delay,
)
from webshare._models import decode
from webshare._pagination import AsyncPage
from webshare.resources import (
    AsyncBilling,
    AsyncDownloadTokens,
    AsyncIDVerificationResource,
    AsyncInvoices,
    AsyncIPAuthorizations,
    AsyncNotifications,
    AsyncPaymentMethods,
    AsyncPendingPayments,
    AsyncPlans,
    AsyncProfileResource,
    AsyncProxies,
    AsyncProxyActivityResource,
    AsyncProxyConfigResource,
    AsyncProxyReplacements,
    AsyncReferral,
    AsyncReplacedProxies,
    AsyncStats,
    AsyncSubscriptionResource,
    AsyncSubusers,
    AsyncTransactions,
    AsyncVerification,
)

ModelT = TypeVar("ModelT")

AsyncCredentialsProvider = Callable[[], str | Awaitable[str]]


class AsyncWebshare(BaseClient):
    """Asynchronous client for the Webshare proxy API.

    Accepts the same options as ``Webshare``; ``credentials_provider`` may be
    a sync or async callable, and ``http_client`` is an ``httpx.AsyncClient``.
    ``timeout`` bounds a single HTTP attempt (total call time may exceed it
    with retries and Retry-After waits); when ``http_client`` is injected and
    ``timeout`` is not set, the injected client's timeout configuration is
    used.
    """

    def __init__(
        self,
        *,
        api_key: str | None = None,
        credentials_provider: AsyncCredentialsProvider | None = None,
        base_url: str | None = None,
        timeout: float | None = None,
        max_retries: int = DEFAULT_MAX_RETRIES,
        http_client: httpx.AsyncClient | None = None,
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
        self._credentials_provider: AsyncCredentialsProvider | None
        if unauthenticated:
            self._credentials_provider = None
        elif credentials_provider is not None:
            self._credentials_provider = credentials_provider
        else:
            key = resolve_static_api_key(api_key)
            if key is None:
                raise missing_credentials_error()
            self._credentials_provider = lambda: key
        self._http = http_client if http_client is not None else httpx.AsyncClient()
        self._owns_http = http_client is None
        self._defer_timeout_to_http_client = http_client is not None and timeout is None

        self.proxies = AsyncProxies(self)
        self.proxy_config = AsyncProxyConfigResource(self)
        self.proxy_replacements = AsyncProxyReplacements(self)
        self.replaced_proxies = AsyncReplacedProxies(self)
        self.stats = AsyncStats(self)
        self.proxy_activity = AsyncProxyActivityResource(self)
        self.download_tokens = AsyncDownloadTokens(self)
        self.ip_authorizations = AsyncIPAuthorizations(self)
        self.subusers = AsyncSubusers(self)
        self.profile = AsyncProfileResource(self)
        self.notifications = AsyncNotifications(self)
        self.id_verification = AsyncIDVerificationResource(self)
        self.verification = AsyncVerification(self)
        self.billing = AsyncBilling(self)
        self.payment_methods = AsyncPaymentMethods(self)
        self.pending_payments = AsyncPendingPayments(self)
        self.transactions = AsyncTransactions(self)
        self.subscription = AsyncSubscriptionResource(self)
        self.plans = AsyncPlans(self)
        self.invoices = AsyncInvoices(self)
        self.referral = AsyncReferral(self)

    # -- lifecycle -------------------------------------------------------

    async def close(self) -> None:
        """Close the underlying HTTP client (if owned by this client)."""
        if self._owns_http:
            await self._http.aclose()

    async def __aenter__(self) -> AsyncWebshare:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        await self.close()

    # -- transport -------------------------------------------------------

    @staticmethod
    async def _sleep(seconds: float) -> None:
        if seconds > 0:
            await asyncio.sleep(seconds)

    async def _token_for(self, spec: RequestSpec) -> str | None:
        if spec.auth == "none":
            return None
        if self._credentials_provider is None:
            raise auth_required_error()
        result = self._credentials_provider()
        if isinstance(result, str):
            return result
        return await result

    async def _send(self, spec: RequestSpec) -> httpx.Response:
        max_retries = self._spec_max_retries(spec)
        retry_allowed = self._retry_allowed(spec)
        attempt = 0
        while True:
            remaining = max_retries - attempt
            # Credentials are fetched per attempt so refreshed tokens are
            # picked up mid-backoff.
            token = await self._token_for(spec)
            try:
                response = await self._http.request(
                    spec.method,
                    self._request_url(spec),
                    **self._request_kwargs(spec, token),
                )
            except httpx.TimeoutException as exc:
                if retry_allowed and remaining > 0:
                    await self._sleep(compute_backoff(attempt))
                    attempt += 1
                    continue
                raise APITimeoutError() from exc
            except httpx.RequestError as exc:
                if retry_allowed and remaining > 0:
                    await self._sleep(compute_backoff(attempt))
                    attempt += 1
                    continue
                raise APIConnectionError(str(exc) or "Connection error.") from exc
            if response.status_code in RETRY_STATUS_CODES and retry_allowed and remaining > 0:
                await self._sleep(retry_delay(attempt, response.headers.get("Retry-After")))
                attempt += 1
                continue
            self._raise_for_status(response)
            return response

    # -- requester interface ---------------------------------------------

    async def request_none(self, spec: RequestSpec) -> None:
        await self._send(spec)

    async def request_json(self, spec: RequestSpec) -> Any:
        return self._json(await self._send(spec))

    async def request_model(self, spec: RequestSpec, cls: type[ModelT]) -> ModelT:
        return self._decode_model(await self._send(spec), cls)

    async def request_model_list(self, spec: RequestSpec, cls: type[ModelT]) -> list[ModelT]:
        return self._decode_model_list(await self._send(spec), cls)

    async def request_model_dict(self, spec: RequestSpec, cls: type[ModelT]) -> dict[str, ModelT]:
        return self._decode_model_dict(await self._send(spec), cls)

    async def request_text(self, spec: RequestSpec) -> str:
        return (await self._send(spec)).text

    async def request_bytes(self, spec: RequestSpec) -> bytes:
        return (await self._send(spec)).content

    async def request_page(self, spec: RequestSpec, item_cls: type[ModelT]) -> AsyncPage[ModelT]:
        response = await self._send(spec)
        results, count, next_url, previous = self._parse_envelope(response)
        return AsyncPage(
            results=[decode(item_cls, item) for item in results],
            count=count,
            next=next_url,
            previous=previous,
            client=self,
            item_cls=item_cls,
            spec=spec,
        )
