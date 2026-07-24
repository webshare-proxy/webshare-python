"""The proxy activity resource (`client.proxy_activity`)."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime

from .._http import RequestSpec
from .._pagination import AsyncPage, SyncPage
from .._requester import AsyncResource, SyncResource
from ..types.proxy import ProxyActivity


def _list_spec(
    *,
    timestamp__lte: str | datetime | None,
    timestamp__gte: str | datetime | None,
    search: str | None,
    error_reason: str | None,
    starting_after: str | datetime | None,
    page_size: int | None,
    bytes__gte: str | int | None,
    bytes__lte: str | int | None,
    verification_category: str | None,
    plan_id: int | None,
) -> RequestSpec:
    return RequestSpec(
        method="GET",
        path="/api/v2/proxy/activity/",
        query={
            "timestamp__lte": timestamp__lte,
            "timestamp__gte": timestamp__gte,
            "search": search,
            "error_reason": error_reason,
            "starting_after": starting_after,
            "page_size": page_size,
            "bytes__gte": bytes__gte,
            "bytes__lte": bytes__lte,
            "verification_category": verification_category,
            "plan_id": plan_id,
        },
    )


def _download_spec(
    *,
    download_token: str,
    timestamp__lte: str | datetime | None,
    timestamp__gte: str | datetime | None,
    search: str | None,
    error_reason: str | None,
    starting_after: str | datetime | None,
    bytes__gte: str | int | None,
    bytes__lte: str | int | None,
    plan_id: int | None,
) -> RequestSpec:
    return RequestSpec(
        method="GET",
        path="/api/v2/proxy/activity/download/",
        query={
            "download_token": download_token,
            "timestamp__lte": timestamp__lte,
            "timestamp__gte": timestamp__gte,
            "search": search,
            "error_reason": error_reason,
            "starting_after": starting_after,
            "bytes__gte": bytes__gte,
            "bytes__lte": bytes__lte,
            "plan_id": plan_id,
        },
        authenticated=False,
    )


class ProxyActivityResource(SyncResource):
    def list(
        self,
        *,
        timestamp__lte: str | datetime | None = None,
        timestamp__gte: str | datetime | None = None,
        search: str | None = None,
        error_reason: str | None = None,
        starting_after: str | datetime | None = None,
        page_size: int | None = None,
        bytes__gte: str | int | None = None,
        bytes__lte: str | int | None = None,
        verification_category: str | None = None,
        plan_id: int | None = None,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> SyncPage[ProxyActivity]:
        """List proxy activity.

        Paginates via ``starting_after``/``page_size`` (pass the ``timestamp``
        of the last activity as ``starting_after``); iterating the returned
        page follows the envelope ``next`` URL automatically.
        """
        return self._client.request_page(
            _list_spec(
                timestamp__lte=timestamp__lte,
                timestamp__gte=timestamp__gte,
                search=search,
                error_reason=error_reason,
                starting_after=starting_after,
                page_size=page_size,
                bytes__gte=bytes__gte,
                bytes__lte=bytes__lte,
                verification_category=verification_category,
                plan_id=plan_id,
            ).with_options(timeout, headers, max_retries, subuser_id, federated_user_id),
            ProxyActivity,
        )

    def download(
        self,
        *,
        download_token: str,
        timestamp__lte: str | datetime | None = None,
        timestamp__gte: str | datetime | None = None,
        search: str | None = None,
        error_reason: str | None = None,
        starting_after: str | datetime | None = None,
        bytes__gte: str | int | None = None,
        bytes__lte: str | int | None = None,
        plan_id: int | None = None,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> str:
        """Download proxy activities as CSV text.

        ``download_token`` comes from ``client.download_tokens.get`` with scope
        ``activity``; the endpoint itself is unauthenticated.
        """
        return self._client.request_text(
            _download_spec(
                download_token=download_token,
                timestamp__lte=timestamp__lte,
                timestamp__gte=timestamp__gte,
                search=search,
                error_reason=error_reason,
                starting_after=starting_after,
                bytes__gte=bytes__gte,
                bytes__lte=bytes__lte,
                plan_id=plan_id,
            ).with_options(timeout, headers, max_retries, subuser_id, federated_user_id)
        )


class AsyncProxyActivityResource(AsyncResource):
    async def list(
        self,
        *,
        timestamp__lte: str | datetime | None = None,
        timestamp__gte: str | datetime | None = None,
        search: str | None = None,
        error_reason: str | None = None,
        starting_after: str | datetime | None = None,
        page_size: int | None = None,
        bytes__gte: str | int | None = None,
        bytes__lte: str | int | None = None,
        verification_category: str | None = None,
        plan_id: int | None = None,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> AsyncPage[ProxyActivity]:
        """List proxy activity (``starting_after`` pagination)."""
        return await self._client.request_page(
            _list_spec(
                timestamp__lte=timestamp__lte,
                timestamp__gte=timestamp__gte,
                search=search,
                error_reason=error_reason,
                starting_after=starting_after,
                page_size=page_size,
                bytes__gte=bytes__gte,
                bytes__lte=bytes__lte,
                verification_category=verification_category,
                plan_id=plan_id,
            ).with_options(timeout, headers, max_retries, subuser_id, federated_user_id),
            ProxyActivity,
        )

    async def download(
        self,
        *,
        download_token: str,
        timestamp__lte: str | datetime | None = None,
        timestamp__gte: str | datetime | None = None,
        search: str | None = None,
        error_reason: str | None = None,
        starting_after: str | datetime | None = None,
        bytes__gte: str | int | None = None,
        bytes__lte: str | int | None = None,
        plan_id: int | None = None,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> str:
        """Download proxy activities as CSV text (token scope ``activity``)."""
        return await self._client.request_text(
            _download_spec(
                download_token=download_token,
                timestamp__lte=timestamp__lte,
                timestamp__gte=timestamp__gte,
                search=search,
                error_reason=error_reason,
                starting_after=starting_after,
                bytes__gte=bytes__gte,
                bytes__lte=bytes__lte,
                plan_id=plan_id,
            ).with_options(timeout, headers, max_retries, subuser_id, federated_user_id)
        )
