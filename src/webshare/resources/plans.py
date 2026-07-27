"""The plan resource (`client.plans`)."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime

from webshare._http import RequestSpec, drop_json_nulls
from webshare._pagination import AsyncPage, SyncPage
from webshare._requester import AsyncResource, SyncResource
from webshare.types.commerce import Plan, PlanCancelResponse


def _list_spec(*, page: int | None, page_size: int | None) -> RequestSpec:
    return RequestSpec(
        method="GET",
        path="/api/v2/subscription/plan/",
        query={"page": page, "page_size": page_size},
    )


def _get_spec(id: int) -> RequestSpec:
    return RequestSpec(method="GET", path=f"/api/v2/subscription/plan/{id}/")


def _update_spec(id: int, *, automatic_refresh_next_at: str | datetime | None) -> RequestSpec:
    value = (
        automatic_refresh_next_at.isoformat()
        if isinstance(automatic_refresh_next_at, datetime)
        else automatic_refresh_next_at
    )
    return RequestSpec(
        method="PATCH",
        path=f"/api/v2/subscription/plan/{id}/",
        json_body=drop_json_nulls({"automatic_refresh_next_at": value}),
    )


def _cancel_spec(id: int) -> RequestSpec:
    return RequestSpec(method="POST", path=f"/api/v2/subscription/plan/{id}/cancel/")


class Plans(SyncResource):
    def list(
        self,
        *,
        page: int | None = None,
        page_size: int | None = None,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> SyncPage[Plan]:
        """List all plans created by the user (including non-active ones)."""
        return self._client.request_page(
            _list_spec(page=page, page_size=page_size).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            Plan,
        )

    def get(
        self,
        id: int,
        *,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> Plan:
        """Get a plan (the active plan ID is on the subscription object)."""
        return self._client.request_model(
            _get_spec(id).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            Plan,
        )

    def update(
        self,
        id: int,
        *,
        automatic_refresh_next_at: str | datetime | None = None,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> Plan:
        """Update a plan; only ``automatic_refresh_next_at`` is editable."""
        return self._client.request_model(
            _update_spec(id, automatic_refresh_next_at=automatic_refresh_next_at).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            Plan,
        )

    def cancel(
        self,
        id: int,
        *,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> PlanCancelResponse:
        """Cancel a plan; the subscription is credited for the remainder."""
        return self._client.request_model(
            _cancel_spec(id).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            PlanCancelResponse,
        )


class AsyncPlans(AsyncResource):
    async def list(
        self,
        *,
        page: int | None = None,
        page_size: int | None = None,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> AsyncPage[Plan]:
        """List all plans created by the user (including non-active ones)."""
        return await self._client.request_page(
            _list_spec(page=page, page_size=page_size).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            Plan,
        )

    async def get(
        self,
        id: int,
        *,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> Plan:
        """Get a plan (the active plan ID is on the subscription object)."""
        return await self._client.request_model(
            _get_spec(id).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            Plan,
        )

    async def update(
        self,
        id: int,
        *,
        automatic_refresh_next_at: str | datetime | None = None,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> Plan:
        """Update a plan; only ``automatic_refresh_next_at`` is editable."""
        return await self._client.request_model(
            _update_spec(id, automatic_refresh_next_at=automatic_refresh_next_at).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            Plan,
        )

    async def cancel(
        self,
        id: int,
        *,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> PlanCancelResponse:
        """Cancel a plan; the subscription is credited for the remainder."""
        return await self._client.request_model(
            _cancel_spec(id).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            PlanCancelResponse,
        )
