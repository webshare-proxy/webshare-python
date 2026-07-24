"""The subscription resource (`client.subscription`).

``customize`` and ``pricing`` hide the API quirk where the whole request
object is JSON-encoded into a single ``query`` GET parameter.

Checkout endpoints (``purchase``/``renew``) require recaptcha only when a
payment is required; the docs state that when a payment is required they
should only be used from the Webshare dashboard. The credits-covered path
works programmatically.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Literal

from .._http import RequestSpec, drop_json_nulls, encode_json_query
from .._requester import AsyncResource, SyncResource
from ..types.commerce import (
    AssetInfo,
    CheckoutResponse,
    CustomizationOptions,
    Pricing,
    Subscription,
)

ProxyType = Literal["free", "shared", "semidedicated", "dedicated"]
ProxySubtype = Literal["default", "premium", "isp", "residential", "datacenter_and_isp"]
Term = Literal["monthly", "yearly"]
PricingBehavior = Literal["replace", "add", "upgrade"]
PurchaseBehavior = Literal["replace", "add"]


def _get_spec() -> RequestSpec:
    return RequestSpec(method="GET", path="/api/v2/subscription/")


def _assets_spec() -> RequestSpec:
    return RequestSpec(method="GET", path="/api/v2/subscription/available_assets/")


def _customize_spec(
    *,
    proxy_type: ProxyType | None,
    proxy_subtype: ProxySubtype | None,
    proxy_countries: Mapping[str, int] | None,
    required_site_checks: Sequence[str] | None,
    high_quality_ips_only: bool | None,
    plan_id: int | None,
) -> RequestSpec:
    payload = {
        "proxy_type": proxy_type,
        "proxy_subtype": proxy_subtype,
        "proxy_countries": dict(proxy_countries) if proxy_countries is not None else None,
        "required_site_checks": (
            list(required_site_checks) if required_site_checks is not None else None
        ),
        "high_quality_ips_only": high_quality_ips_only,
    }
    return RequestSpec(
        method="GET",
        path="/api/v2/subscription/customize/",
        query={"query": encode_json_query(payload), "plan_id": plan_id},
    )


def _pricing_spec(
    *,
    behavior: PricingBehavior | None,
    proxy_type: ProxyType | None,
    proxy_subtype: ProxySubtype | None,
    proxy_countries: Mapping[str, int] | None,
    bandwidth_limit: float | None,
    on_demand_refreshes_total: int | None,
    automatic_refresh_frequency: int | None,
    proxy_replacements_total: int | None,
    subusers_total: int | None,
    is_unlimited_ip_authorizations: bool | None,
    is_high_concurrency: bool | None,
    is_2x_concurrency: bool | None,
    is_high_priority_network: bool | None,
    high_quality_ips_only: bool | None,
    term: Term | None,
    required_site_checks: Sequence[str] | None,
    with_tax: bool | None,
    plan_id: int | None,
) -> RequestSpec:
    payload = {
        "behavior": behavior,
        "proxy_type": proxy_type,
        "proxy_subtype": proxy_subtype,
        "proxy_countries": dict(proxy_countries) if proxy_countries is not None else None,
        "bandwidth_limit": bandwidth_limit,
        "on_demand_refreshes_total": on_demand_refreshes_total,
        "automatic_refresh_frequency": automatic_refresh_frequency,
        "proxy_replacements_total": proxy_replacements_total,
        "subusers_total": subusers_total,
        "is_unlimited_ip_authorizations": is_unlimited_ip_authorizations,
        "is_high_concurrency": is_high_concurrency,
        "is_2x_concurrency": is_2x_concurrency,
        "is_high_priority_network": is_high_priority_network,
        "high_quality_ips_only": high_quality_ips_only,
        "term": term,
        "required_site_checks": (
            list(required_site_checks) if required_site_checks is not None else None
        ),
        "with_tax": with_tax,
    }
    return RequestSpec(
        method="GET",
        path="/api/v2/subscription/pricing/",
        query={"query": encode_json_query(payload), "plan_id": plan_id},
    )


def _checkout_body(
    *,
    proxy_type: ProxyType | None,
    proxy_subtype: ProxySubtype | None,
    proxy_countries: Mapping[str, int] | None,
    bandwidth_limit: float | None,
    on_demand_refreshes_total: int | None,
    automatic_refresh_frequency: int | None,
    proxy_replacements_total: int | None,
    subusers_total: int | None,
    is_unlimited_ip_authorizations: bool | None,
    is_high_concurrency: bool | None,
    is_2x_concurrency: bool | None,
    is_high_priority_network: bool | None,
    high_quality_ips_only: bool | None,
    required_site_checks: Sequence[str] | None,
    term: Term | None,
    recaptcha: str | None,
) -> dict[str, object]:
    return drop_json_nulls(
        {
            "proxy_type": proxy_type,
            "proxy_subtype": proxy_subtype,
            "proxy_countries": dict(proxy_countries) if proxy_countries is not None else None,
            "bandwidth_limit": bandwidth_limit,
            "on_demand_refreshes_total": on_demand_refreshes_total,
            "automatic_refresh_frequency": automatic_refresh_frequency,
            "proxy_replacements_total": proxy_replacements_total,
            "subusers_total": subusers_total,
            "is_unlimited_ip_authorizations": is_unlimited_ip_authorizations,
            "is_high_concurrency": is_high_concurrency,
            "is_2x_concurrency": is_2x_concurrency,
            "is_high_priority_network": is_high_priority_network,
            "high_quality_ips_only": high_quality_ips_only,
            "required_site_checks": (
                list(required_site_checks) if required_site_checks is not None else None
            ),
            "term": term,
            "recaptcha": recaptcha,
        }
    )


def _purchase_spec(
    *,
    behavior: PurchaseBehavior | None,
    payment_method: int | str | None,
    body: dict[str, object],
) -> RequestSpec:
    json_body = dict(body)
    if behavior is not None:
        json_body["behavior"] = behavior
    # payment_method is tri-modal: None (payment on file), a Webshare
    # PaymentMethod ID, or a Stripe PaymentMethod string ("pm_...").
    json_body["payment_method"] = payment_method
    return RequestSpec(
        method="POST", path="/api/v2/subscription/checkout/purchase/", json_body=json_body
    )


def _renew_spec(
    *, payment_method: int | None, term: Term | None, recaptcha: str | None
) -> RequestSpec:
    json_body: dict[str, object] = drop_json_nulls({"term": term, "recaptcha": recaptcha})
    json_body["payment_method"] = payment_method
    return RequestSpec(
        method="POST", path="/api/v2/subscription/checkout/renew/", json_body=json_body
    )


def _enable_renewal_spec() -> RequestSpec:
    return RequestSpec(method="PUT", path="/api/v2/subscription/renewal/")


def _cancel_renewal_spec() -> RequestSpec:
    return RequestSpec(method="DELETE", path="/api/v2/subscription/renewal/")


def _decode_assets(data: object) -> dict[str, dict[str, AssetInfo]]:
    from .._models import decode

    out: dict[str, dict[str, AssetInfo]] = {}
    if isinstance(data, dict):
        for category, subtypes in data.items():
            if isinstance(subtypes, dict):
                out[category] = {
                    subtype: decode(AssetInfo, info)
                    for subtype, info in subtypes.items()
                    if isinstance(info, dict)
                }
    return out


class SubscriptionResource(SyncResource):
    def get(
        self,
        *,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> Subscription:
        """Get the subscription (a singleton per account)."""
        return self._client.request_model(
            _get_spec().with_options(timeout, headers, max_retries, subuser_id, federated_user_id),
            Subscription,
        )

    def get_available_assets(
        self,
        *,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> dict[str, dict[str, AssetInfo]]:
        """Get available assets per proxy category and subtype."""
        return _decode_assets(
            self._client.request_json(
                _assets_spec().with_options(
                    timeout, headers, max_retries, subuser_id, federated_user_id
                )
            )
        )

    def customize(
        self,
        *,
        proxy_type: ProxyType | None = None,
        proxy_subtype: ProxySubtype | None = None,
        proxy_countries: Mapping[str, int] | None = None,
        required_site_checks: Sequence[str] | None = None,
        high_quality_ips_only: bool | None = None,
        plan_id: int | None = None,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> CustomizationOptions:
        """Get the customization limits/options for a plan configuration."""
        return self._client.request_model(
            _customize_spec(
                proxy_type=proxy_type,
                proxy_subtype=proxy_subtype,
                proxy_countries=proxy_countries,
                required_site_checks=required_site_checks,
                high_quality_ips_only=high_quality_ips_only,
                plan_id=plan_id,
            ).with_options(timeout, headers, max_retries, subuser_id, federated_user_id),
            CustomizationOptions,
        )

    def pricing(
        self,
        *,
        behavior: PricingBehavior | None = None,
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
        term: Term | None = None,
        required_site_checks: Sequence[str] | None = None,
        with_tax: bool | None = None,
        plan_id: int | None = None,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> Pricing:
        """Get the pricing for a custom plan configuration."""
        return self._client.request_model(
            _pricing_spec(
                behavior=behavior,
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
                term=term,
                required_site_checks=required_site_checks,
                with_tax=with_tax,
                plan_id=plan_id,
            ).with_options(timeout, headers, max_retries, subuser_id, federated_user_id),
            Pricing,
        )

    def purchase(
        self,
        *,
        behavior: PurchaseBehavior | None = None,
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
        """Purchase a new plan.

        Recaptcha is required only when a payment is required; if account
        credits cover the change, no payment (and no recaptcha) is needed.
        """
        return self._client.request_model(
            _purchase_spec(
                behavior=behavior,
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

    def renew(
        self,
        *,
        payment_method: int | None = None,
        term: Term | None = None,
        recaptcha: str | None = None,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> CheckoutResponse:
        """Renew the subscription (recaptcha only when a payment is required)."""
        return self._client.request_model(
            _renew_spec(payment_method=payment_method, term=term, recaptcha=recaptcha).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            CheckoutResponse,
        )

    def enable_auto_renewal(
        self,
        *,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> Subscription:
        """Enable auto-renewal (a payment method must already be on file)."""
        return self._client.request_model(
            _enable_renewal_spec().with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            Subscription,
        )

    def cancel_auto_renewal(
        self,
        *,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> Subscription:
        """Cancel auto-renewal. Also removes the payment method; returns 200
        with the subscription object (not 204)."""
        return self._client.request_model(
            _cancel_renewal_spec().with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            Subscription,
        )


class AsyncSubscriptionResource(AsyncResource):
    async def get(
        self,
        *,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> Subscription:
        """Get the subscription (a singleton per account)."""
        return await self._client.request_model(
            _get_spec().with_options(timeout, headers, max_retries, subuser_id, federated_user_id),
            Subscription,
        )

    async def get_available_assets(
        self,
        *,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> dict[str, dict[str, AssetInfo]]:
        """Get available assets per proxy category and subtype."""
        return _decode_assets(
            await self._client.request_json(
                _assets_spec().with_options(
                    timeout, headers, max_retries, subuser_id, federated_user_id
                )
            )
        )

    async def customize(
        self,
        *,
        proxy_type: ProxyType | None = None,
        proxy_subtype: ProxySubtype | None = None,
        proxy_countries: Mapping[str, int] | None = None,
        required_site_checks: Sequence[str] | None = None,
        high_quality_ips_only: bool | None = None,
        plan_id: int | None = None,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> CustomizationOptions:
        """Get the customization limits/options for a plan configuration."""
        return await self._client.request_model(
            _customize_spec(
                proxy_type=proxy_type,
                proxy_subtype=proxy_subtype,
                proxy_countries=proxy_countries,
                required_site_checks=required_site_checks,
                high_quality_ips_only=high_quality_ips_only,
                plan_id=plan_id,
            ).with_options(timeout, headers, max_retries, subuser_id, federated_user_id),
            CustomizationOptions,
        )

    async def pricing(
        self,
        *,
        behavior: PricingBehavior | None = None,
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
        term: Term | None = None,
        required_site_checks: Sequence[str] | None = None,
        with_tax: bool | None = None,
        plan_id: int | None = None,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> Pricing:
        """Get the pricing for a custom plan configuration."""
        return await self._client.request_model(
            _pricing_spec(
                behavior=behavior,
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
                term=term,
                required_site_checks=required_site_checks,
                with_tax=with_tax,
                plan_id=plan_id,
            ).with_options(timeout, headers, max_retries, subuser_id, federated_user_id),
            Pricing,
        )

    async def purchase(
        self,
        *,
        behavior: PurchaseBehavior | None = None,
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
        """Purchase a new plan (recaptcha only when a payment is required)."""
        return await self._client.request_model(
            _purchase_spec(
                behavior=behavior,
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

    async def renew(
        self,
        *,
        payment_method: int | None = None,
        term: Term | None = None,
        recaptcha: str | None = None,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> CheckoutResponse:
        """Renew the subscription (recaptcha only when a payment is required)."""
        return await self._client.request_model(
            _renew_spec(payment_method=payment_method, term=term, recaptcha=recaptcha).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            CheckoutResponse,
        )

    async def enable_auto_renewal(
        self,
        *,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> Subscription:
        """Enable auto-renewal (a payment method must already be on file)."""
        return await self._client.request_model(
            _enable_renewal_spec().with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            Subscription,
        )

    async def cancel_auto_renewal(
        self,
        *,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> Subscription:
        """Cancel auto-renewal. Also removes the payment method; returns 200
        with the subscription object (not 204)."""
        return await self._client.request_model(
            _cancel_renewal_spec().with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            Subscription,
        )
