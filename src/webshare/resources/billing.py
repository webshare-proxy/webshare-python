"""The billing information resource (`client.billing`)."""

from __future__ import annotations

from collections.abc import Mapping

from .._http import RequestSpec, drop_json_nulls
from .._requester import AsyncResource, SyncResource
from ..types.commerce import BillingInfo


def _get_info_spec() -> RequestSpec:
    return RequestSpec(method="GET", path="/api/v2/subscription/billing_info/")


def _update_info_spec(
    *, name: str | None, address: str | None, billing_email: str | None
) -> RequestSpec:
    return RequestSpec(
        method="PATCH",
        path="/api/v2/subscription/billing_info/",
        json_body=drop_json_nulls(
            {"name": name, "address": address, "billing_email": billing_email}
        ),
    )


class Billing(SyncResource):
    def get_info(
        self,
        *,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> BillingInfo:
        """Get the billing information (a singleton per account)."""
        return self._client.request_model(
            _get_info_spec().with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            BillingInfo,
        )

    def update_info(
        self,
        *,
        name: str | None = None,
        address: str | None = None,
        billing_email: str | None = None,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> BillingInfo:
        """Update the billing information."""
        return self._client.request_model(
            _update_info_spec(name=name, address=address, billing_email=billing_email).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            BillingInfo,
        )


class AsyncBilling(AsyncResource):
    async def get_info(
        self,
        *,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> BillingInfo:
        """Get the billing information (a singleton per account)."""
        return await self._client.request_model(
            _get_info_spec().with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            BillingInfo,
        )

    async def update_info(
        self,
        *,
        name: str | None = None,
        address: str | None = None,
        billing_email: str | None = None,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> BillingInfo:
        """Update the billing information."""
        return await self._client.request_model(
            _update_info_spec(name=name, address=address, billing_email=billing_email).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            BillingInfo,
        )
