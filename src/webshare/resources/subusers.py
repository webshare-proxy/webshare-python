"""The sub-user resource (`client.subusers`).

The Sub-User API is only enabled after accepting additional terms at
https://proxy.webshare.io/subuser/ (expect 403s otherwise). To masquerade as a
sub-user on the proxy config/list/stats APIs, pass ``subuser_id`` (sent as the
``X-Subuser`` header) on those calls instead.
"""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime

from .._http import RequestSpec, drop_json_nulls
from .._pagination import AsyncPage, SyncPage
from .._requester import AsyncResource, SyncResource
from ..types.proxy import Subuser


def _list_spec(*, page: int | None, page_size: int | None, plan_id: int | None) -> RequestSpec:
    return RequestSpec(
        method="GET",
        path="/api/v2/subuser/",
        query={"page": page, "page_size": page_size, "plan_id": plan_id},
    )


def _create_spec(
    *,
    label: str | None,
    proxy_limit: float | None,
    max_thread_count: int | None,
    proxy_countries: Mapping[str, int] | None,
    bandwidth_use_start_date: str | datetime | None,
    plan_id: int | None,
) -> RequestSpec:
    return RequestSpec(
        method="POST",
        path="/api/v2/subuser/",
        query={"plan_id": plan_id},
        json_body=drop_json_nulls(
            {
                "label": label,
                "proxy_limit": proxy_limit,
                "max_thread_count": max_thread_count,
                "proxy_countries": dict(proxy_countries) if proxy_countries is not None else None,
                "bandwidth_use_start_date": (
                    bandwidth_use_start_date.isoformat()
                    if isinstance(bandwidth_use_start_date, datetime)
                    else bandwidth_use_start_date
                ),
            }
        ),
    )


def _get_spec(id: int, *, plan_id: int | None) -> RequestSpec:
    return RequestSpec(method="GET", path=f"/api/v2/subuser/{id}/", query={"plan_id": plan_id})


def _update_spec(
    id: int,
    *,
    label: str | None,
    proxy_countries: Mapping[str, int] | None,
    proxy_limit: float | None,
    max_thread_count: int | None,
    bandwidth_use_start_date: str | datetime | None,
    plan_id: int | None,
) -> RequestSpec:
    return RequestSpec(
        method="PATCH",
        path=f"/api/v2/subuser/{id}/",
        query={"plan_id": plan_id},
        json_body=drop_json_nulls(
            {
                "label": label,
                "proxy_countries": dict(proxy_countries) if proxy_countries is not None else None,
                "proxy_limit": proxy_limit,
                "max_thread_count": max_thread_count,
                "bandwidth_use_start_date": (
                    bandwidth_use_start_date.isoformat()
                    if isinstance(bandwidth_use_start_date, datetime)
                    else bandwidth_use_start_date
                ),
            }
        ),
    )


def _delete_spec(id: int, *, plan_id: int | None) -> RequestSpec:
    return RequestSpec(method="DELETE", path=f"/api/v2/subuser/{id}/", query={"plan_id": plan_id})


def _refresh_spec(id: int) -> RequestSpec:
    return RequestSpec(method="POST", path=f"/api/v2/subuser/{id}/refresh/")


class Subusers(SyncResource):
    def list(
        self,
        *,
        page: int | None = None,
        page_size: int | None = None,
        plan_id: int | None = None,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> SyncPage[Subuser]:
        """List sub-users."""
        return self._client.request_page(
            _list_spec(page=page, page_size=page_size, plan_id=plan_id).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            Subuser,
        )

    def create(
        self,
        *,
        label: str | None = None,
        proxy_limit: float | None = None,
        max_thread_count: int | None = None,
        proxy_countries: Mapping[str, int] | None = None,
        bandwidth_use_start_date: str | datetime | None = None,
        plan_id: int | None = None,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> Subuser:
        """Create a sub-user. ``proxy_limit`` is in GBs (0 means unlimited)."""
        return self._client.request_model(
            _create_spec(
                label=label,
                proxy_limit=proxy_limit,
                max_thread_count=max_thread_count,
                proxy_countries=proxy_countries,
                bandwidth_use_start_date=bandwidth_use_start_date,
                plan_id=plan_id,
            ).with_options(timeout, headers, max_retries, subuser_id, federated_user_id),
            Subuser,
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
    ) -> Subuser:
        """Get a sub-user."""
        return self._client.request_model(
            _get_spec(id, plan_id=plan_id).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            Subuser,
        )

    def update(
        self,
        id: int,
        *,
        label: str | None = None,
        proxy_countries: Mapping[str, int] | None = None,
        proxy_limit: float | None = None,
        max_thread_count: int | None = None,
        bandwidth_use_start_date: str | datetime | None = None,
        plan_id: int | None = None,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> Subuser:
        """Partially update a sub-user."""
        return self._client.request_model(
            _update_spec(
                id,
                label=label,
                proxy_countries=proxy_countries,
                proxy_limit=proxy_limit,
                max_thread_count=max_thread_count,
                bandwidth_use_start_date=bandwidth_use_start_date,
                plan_id=plan_id,
            ).with_options(timeout, headers, max_retries, subuser_id, federated_user_id),
            Subuser,
        )

    def delete(
        self,
        id: int,
        *,
        plan_id: int | None = None,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> None:
        """Delete a sub-user."""
        return self._client.request_none(
            _delete_spec(id, plan_id=plan_id).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            )
        )

    def refresh_proxy_list(
        self,
        id: int,
        *,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> Subuser:
        """Refresh the proxy list of a sub-user (requires a custom proxy list)."""
        return self._client.request_model(
            _refresh_spec(id).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            Subuser,
        )


class AsyncSubusers(AsyncResource):
    async def list(
        self,
        *,
        page: int | None = None,
        page_size: int | None = None,
        plan_id: int | None = None,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> AsyncPage[Subuser]:
        """List sub-users."""
        return await self._client.request_page(
            _list_spec(page=page, page_size=page_size, plan_id=plan_id).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            Subuser,
        )

    async def create(
        self,
        *,
        label: str | None = None,
        proxy_limit: float | None = None,
        max_thread_count: int | None = None,
        proxy_countries: Mapping[str, int] | None = None,
        bandwidth_use_start_date: str | datetime | None = None,
        plan_id: int | None = None,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> Subuser:
        """Create a sub-user. ``proxy_limit`` is in GBs (0 means unlimited)."""
        return await self._client.request_model(
            _create_spec(
                label=label,
                proxy_limit=proxy_limit,
                max_thread_count=max_thread_count,
                proxy_countries=proxy_countries,
                bandwidth_use_start_date=bandwidth_use_start_date,
                plan_id=plan_id,
            ).with_options(timeout, headers, max_retries, subuser_id, federated_user_id),
            Subuser,
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
    ) -> Subuser:
        """Get a sub-user."""
        return await self._client.request_model(
            _get_spec(id, plan_id=plan_id).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            Subuser,
        )

    async def update(
        self,
        id: int,
        *,
        label: str | None = None,
        proxy_countries: Mapping[str, int] | None = None,
        proxy_limit: float | None = None,
        max_thread_count: int | None = None,
        bandwidth_use_start_date: str | datetime | None = None,
        plan_id: int | None = None,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> Subuser:
        """Partially update a sub-user."""
        return await self._client.request_model(
            _update_spec(
                id,
                label=label,
                proxy_countries=proxy_countries,
                proxy_limit=proxy_limit,
                max_thread_count=max_thread_count,
                bandwidth_use_start_date=bandwidth_use_start_date,
                plan_id=plan_id,
            ).with_options(timeout, headers, max_retries, subuser_id, federated_user_id),
            Subuser,
        )

    async def delete(
        self,
        id: int,
        *,
        plan_id: int | None = None,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> None:
        """Delete a sub-user."""
        return await self._client.request_none(
            _delete_spec(id, plan_id=plan_id).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            )
        )

    async def refresh_proxy_list(
        self,
        id: int,
        *,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> Subuser:
        """Refresh the proxy list of a sub-user (requires a custom proxy list)."""
        return await self._client.request_model(
            _refresh_spec(id).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            Subuser,
        )
