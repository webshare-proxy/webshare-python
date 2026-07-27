"""The proxy replacement resource (`client.proxy_replacements`), on v3."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, Literal

from webshare._http import RequestSpec, drop_json_nulls
from webshare._pagination import AsyncPage, SyncPage
from webshare._requester import AsyncResource, SyncResource
from webshare.types.proxy import ProxyReplacement

ReplacementState = Literal["validating", "validated", "processing", "completed", "failed"]


def _list_spec(
    *,
    plan_id: int | None,
    ordering: str | None,
    dry_run: bool | None,
    state: ReplacementState | None,
    page: int | None,
    page_size: int | None,
) -> RequestSpec:
    return RequestSpec(
        method="GET",
        path="/api/v3/proxy/replace/",
        query={
            "plan_id": plan_id,
            "ordering": ordering,
            "dry_run": dry_run,
            "state": state,
            "page": page,
            "page_size": page_size,
        },
    )


def _create_spec(
    *,
    to_replace: Mapping[str, Any],
    replace_with: Sequence[Mapping[str, Any]],
    dry_run: bool | None,
    plan_id: int | None,
) -> RequestSpec:
    return RequestSpec(
        method="POST",
        path="/api/v3/proxy/replace/",
        query={"plan_id": plan_id},
        json_body=drop_json_nulls(
            {
                "to_replace": dict(to_replace),
                "replace_with": [dict(item) for item in replace_with],
                "dry_run": dry_run,
            }
        ),
    )


def _get_spec(id: int, *, plan_id: int | None) -> RequestSpec:
    return RequestSpec(
        method="GET",
        path=f"/api/v3/proxy/replace/{id}/",
        query={"plan_id": plan_id},
    )


class ProxyReplacements(SyncResource):
    def list(
        self,
        *,
        plan_id: int | None = None,
        ordering: str | None = None,
        dry_run: bool | None = None,
        state: ReplacementState | None = None,
        page: int | None = None,
        page_size: int | None = None,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> SyncPage[ProxyReplacement]:
        """List proxy replacements."""
        return self._client.request_page(
            _list_spec(
                plan_id=plan_id,
                ordering=ordering,
                dry_run=dry_run,
                state=state,
                page=page,
                page_size=page_size,
            ).with_options(timeout, headers, max_retries, subuser_id, federated_user_id),
            ProxyReplacement,
        )

    def create(
        self,
        *,
        to_replace: Mapping[str, Any],
        replace_with: Sequence[Mapping[str, Any]],
        dry_run: bool | None = None,
        plan_id: int | None = None,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> ProxyReplacement:
        """Create a proxy replacement (asynchronous API).

        The replacement is returned in ``validating`` state; poll ``get`` until
        it is ``completed`` or ``failed``. Use ``dry_run=True`` to learn
        ``proxies_removed``/``proxies_added`` without modifying the list.
        ``to_replace`` supports types ``ip_range``, ``ip_address``, ``asn``,
        ``country``; ``replace_with`` supports ``ip_range``, ``asn``,
        ``country``, ``any`` (not ``ip_address``). Unavailable when
        ``plan.pool_filter`` is ``residential``.
        """
        return self._client.request_model(
            _create_spec(
                to_replace=to_replace,
                replace_with=replace_with,
                dry_run=dry_run,
                plan_id=plan_id,
            ).with_options(timeout, headers, max_retries, subuser_id, federated_user_id),
            ProxyReplacement,
        )

    def get(
        self,
        id: int,
        *,
        plan_id: int | None = None,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> ProxyReplacement:
        """Get a proxy replacement (poll after ``create``)."""
        return self._client.request_model(
            _get_spec(id, plan_id=plan_id).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            ProxyReplacement,
        )


class AsyncProxyReplacements(AsyncResource):
    async def list(
        self,
        *,
        plan_id: int | None = None,
        ordering: str | None = None,
        dry_run: bool | None = None,
        state: ReplacementState | None = None,
        page: int | None = None,
        page_size: int | None = None,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> AsyncPage[ProxyReplacement]:
        """List proxy replacements."""
        return await self._client.request_page(
            _list_spec(
                plan_id=plan_id,
                ordering=ordering,
                dry_run=dry_run,
                state=state,
                page=page,
                page_size=page_size,
            ).with_options(timeout, headers, max_retries, subuser_id, federated_user_id),
            ProxyReplacement,
        )

    async def create(
        self,
        *,
        to_replace: Mapping[str, Any],
        replace_with: Sequence[Mapping[str, Any]],
        dry_run: bool | None = None,
        plan_id: int | None = None,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> ProxyReplacement:
        """Create a proxy replacement (asynchronous API); see the sync client
        docstring for the polling workflow."""
        return await self._client.request_model(
            _create_spec(
                to_replace=to_replace,
                replace_with=replace_with,
                dry_run=dry_run,
                plan_id=plan_id,
            ).with_options(timeout, headers, max_retries, subuser_id, federated_user_id),
            ProxyReplacement,
        )

    async def get(
        self,
        id: int,
        *,
        plan_id: int | None = None,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> ProxyReplacement:
        """Get a proxy replacement (poll after ``create``)."""
        return await self._client.request_model(
            _get_spec(id, plan_id=plan_id).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            ProxyReplacement,
        )
