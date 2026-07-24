"""The payment method resource (`client.payment_methods`)."""

from __future__ import annotations

from collections.abc import Mapping

from .._http import RequestSpec
from .._pagination import AsyncPage, SyncPage
from .._requester import AsyncResource, SyncResource
from ..types.commerce import PaymentMethod, PaymentMethodSetup


def _list_spec(*, page: int | None, page_size: int | None) -> RequestSpec:
    return RequestSpec(
        method="GET", path="/api/v2/payment/method/", query={"page": page, "page_size": page_size}
    )


def _create_spec(*, recaptcha: str) -> RequestSpec:
    return RequestSpec(
        method="POST", path="/api/v2/payment/method/", json_body={"recaptcha": recaptcha}
    )


def _get_spec(id: int) -> RequestSpec:
    return RequestSpec(method="GET", path=f"/api/v2/payment/method/{id}/")


class PaymentMethods(SyncResource):
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
    ) -> SyncPage[PaymentMethod]:
        """List payment methods (polymorphic on ``type``)."""
        return self._client.request_page(
            _list_spec(page=page, page_size=page_size).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            PaymentMethod,
        )

    def create(
        self,
        *,
        recaptcha: str,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> PaymentMethodSetup:
        """Start the update-payment-method flow (Stripe SetupIntent; requires
        recaptcha). Confirm the returned ``stripe_client_secret`` via Stripe.js."""
        return self._client.request_model(
            _create_spec(recaptcha=recaptcha).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            PaymentMethodSetup,
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
    ) -> PaymentMethod:
        """Get a payment method."""
        return self._client.request_model(
            _get_spec(id).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            PaymentMethod,
        )


class AsyncPaymentMethods(AsyncResource):
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
    ) -> AsyncPage[PaymentMethod]:
        """List payment methods (polymorphic on ``type``)."""
        return await self._client.request_page(
            _list_spec(page=page, page_size=page_size).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            PaymentMethod,
        )

    async def create(
        self,
        *,
        recaptcha: str,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> PaymentMethodSetup:
        """Start the update-payment-method flow (Stripe SetupIntent; requires
        recaptcha)."""
        return await self._client.request_model(
            _create_spec(recaptcha=recaptcha).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            PaymentMethodSetup,
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
    ) -> PaymentMethod:
        """Get a payment method."""
        return await self._client.request_model(
            _get_spec(id).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            PaymentMethod,
        )
