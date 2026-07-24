"""The plan resource (`client.plans`)."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import datetime

from .._http import RequestSpec
from .._pagination import AsyncPage, SyncPage
from .._requester import AsyncResource, SyncResource
from ..types.commerce import CheckoutResponse, Plan, PlanCancelResponse
from .subscription import ProxySubtype, ProxyType, Term, _checkout_body


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
        json_body={"automatic_refresh_next_at": value},
    )


def _upgrade_spec(
    id: int, *, payment_method: int | str | None, body: dict[str, object]
) -> RequestSpec:
    json_body = dict(body)
    json_body["payment_method"] = payment_method
    return RequestSpec(
        method="POST", path=f"/api/v2/subscription/plan/{id}/upgrade/", json_body=json_body
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

    def upgrade(
        self,
        id: int,
        *,
        proxy_type: ProxyType | None = None,
        proxy_subtype: ProxySubtype | None = None,
        proxy_countries: Mapping[str, int] | None = None,
        bandwidth_limit: float | None = None,
        on_demand_refreshes_total: int | None = None,
        automatic_refresh_frequency: int | None = None,
        proxy_replacements_total: int | None = None,
        subusers_total: int | None = None,
        is_unlimited_ip_authorizations: bool | None = None,
        is_high_concurrency: bool | None = None,
        is_2x_concurrency: bool | None = None,
        is_high_priority_network: bool | None = None,
        high_quality_ips_only: bool | None = None,
        required_site_checks: Sequence[str] | None = None,
        term: Term | None = None,
        payment_method: int | str | None = None,
        recaptcha: str | None = None,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> CheckoutResponse:
        """Upgrade a plan (checkout-shaped response; recaptcha only when a
        payment is required)."""
        return self._client.request_model(
            _upgrade_spec(
                id,
                payment_method=payment_method,
                body=_checkout_body(
                    proxy_type=proxy_type,
                    proxy_subtype=proxy_subtype,
                    proxy_countries=proxy_countries,
                    bandwidth_limit=bandwidth_limit,
                    on_demand_refreshes_total=on_demand_refreshes_total,
                    automatic_refresh_frequency=automatic_refresh_frequency,
                    proxy_replacements_total=proxy_replacements_total,
                    subusers_total=subusers_total,
                    is_unlimited_ip_authorizations=is_unlimited_ip_authorizations,
                    is_high_concurrency=is_high_concurrency,
                    is_2x_concurrency=is_2x_concurrency,
                    is_high_priority_network=is_high_priority_network,
                    high_quality_ips_only=high_quality_ips_only,
                    required_site_checks=required_site_checks,
                    term=term,
                    recaptcha=recaptcha,
                ),
            ).with_options(timeout, headers, max_retries, subuser_id, federated_user_id),
            CheckoutResponse,
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

    async def upgrade(
        self,
        id: int,
        *,
        proxy_type: ProxyType | None = None,
        proxy_subtype: ProxySubtype | None = None,
        proxy_countries: Mapping[str, int] | None = None,
        bandwidth_limit: float | None = None,
        on_demand_refreshes_total: int | None = None,
        automatic_refresh_frequency: int | None = None,
        proxy_replacements_total: int | None = None,
        subusers_total: int | None = None,
        is_unlimited_ip_authorizations: bool | None = None,
        is_high_concurrency: bool | None = None,
        is_2x_concurrency: bool | None = None,
        is_high_priority_network: bool | None = None,
        high_quality_ips_only: bool | None = None,
        required_site_checks: Sequence[str] | None = None,
        term: Term | None = None,
        payment_method: int | str | None = None,
        recaptcha: str | None = None,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> CheckoutResponse:
        """Upgrade a plan (checkout-shaped response; recaptcha only when a
        payment is required)."""
        return await self._client.request_model(
            _upgrade_spec(
                id,
                payment_method=payment_method,
                body=_checkout_body(
                    proxy_type=proxy_type,
                    proxy_subtype=proxy_subtype,
                    proxy_countries=proxy_countries,
                    bandwidth_limit=bandwidth_limit,
                    on_demand_refreshes_total=on_demand_refreshes_total,
                    automatic_refresh_frequency=automatic_refresh_frequency,
                    proxy_replacements_total=proxy_replacements_total,
                    subusers_total=subusers_total,
                    is_unlimited_ip_authorizations=is_unlimited_ip_authorizations,
                    is_high_concurrency=is_high_concurrency,
                    is_2x_concurrency=is_2x_concurrency,
                    is_high_priority_network=is_high_priority_network,
                    high_quality_ips_only=high_quality_ips_only,
                    required_site_checks=required_site_checks,
                    term=term,
                    recaptcha=recaptcha,
                ),
            ).with_options(timeout, headers, max_retries, subuser_id, federated_user_id),
            CheckoutResponse,
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
