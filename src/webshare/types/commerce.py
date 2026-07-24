"""Models for the billing, subscription, plan and referral APIs."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

__all__ = [
    "AssetInfo",
    "AvailableFeature",
    "AvailableSiteCheck",
    "BandwidthDiscountTier",
    "BillingInfo",
    "BundleAddon",
    "BundleInfo",
    "CheckoutResponse",
    "CouponCode",
    "CouponDiscount",
    "CustomizationOptions",
    "CustomizationTerm",
    "FeaturePrice",
    "PaymentMethod",
    "PaymentMethodSetup",
    "PendingPayment",
    "Plan",
    "PlanCancelResponse",
    "Pricing",
    "ProxyCountDiscountTier",
    "ReferralChannel",
    "ReferralCodeInfo",
    "ReferralConfig",
    "ReferralCredit",
    "ReferralEarnout",
    "Subscription",
    "TaxBreakdownEntry",
    "TaxRateDetails",
    "Transaction",
    "TransactionPaymentMethod",
]


@dataclass
class BillingInfo:
    """Billing information; a singleton per account."""

    id: int
    name: str | None
    address: str | None
    billing_email: str | None
    created_at: datetime | None
    updated_at: datetime | None


@dataclass
class PaymentMethod:
    """A payment method. Polymorphic on ``type`` (``StripeCard``,
    ``LinkPayment``); the card fields are only set for ``StripeCard``."""

    id: int
    type: str | None
    brand: str | None
    last4: str | None
    name: str | None
    expiration_year: int | None
    expiration_month: int | None
    created_at: datetime | None
    updated_at: datetime | None
    line: str | None
    city: str | None
    state: str | None
    postal_code: str | None
    country: str | None


@dataclass
class PaymentMethodSetup:
    """Response of the update-payment-method (Stripe SetupIntent) flow."""

    pending_payment: int | None
    stripe_client_secret: str | None
    stripe_setup_intent: str | None
    stripe_payment_intent: str | None


@dataclass
class PendingPayment:
    """A payment that has been initiated but not yet completed.

    ``payment_method``, ``plan`` and ``transaction`` are integer IDs.
    ``transaction`` is only set once ``status`` is ``successful``.
    """

    id: int
    status: str | None
    failure_reason: str | None
    payment_method: int | None
    plan: int | None
    transaction: int | None
    is_renewal: bool | None
    term: str | None
    created_at: datetime | None
    updated_at: datetime | None
    completed_at: datetime | None


@dataclass
class TransactionPaymentMethod:
    id: int
    brand: str | None
    last4: str | None
    name: str | None
    expiration_year: int | None
    expiration_month: int | None
    created_at: datetime | None
    updated_at: datetime | None


@dataclass
class Transaction:
    id: int
    status: str | None
    payment_method: TransactionPaymentMethod | None
    reason: str | None
    amount: float | None
    credits_used: float | None
    credits_gained: float | None
    refund_amount: float | None
    refund_date: datetime | None
    # Observed on the live API but undocumented (only null seen so far).
    line_items: list[Any] | None
    created_at: datetime | None
    updated_at: datetime | None


@dataclass
class Subscription:
    """The account subscription; a singleton whose ID never changes."""

    id: int
    plan: int | None
    payment_method: int | None
    free_credits: float | None
    term: str | None
    start_date: datetime | None
    end_date: datetime | None
    renewals_paid: int | None
    renewals_enabled: bool | None
    failed_payment_times: int | None
    account_discount_percentage: int | None
    promotion_available_first_time_renewal_25_off: bool | None
    customizable: bool | None
    paused: bool | None
    reactivation_date: datetime | None
    reactivation_period_left: str | None
    promo_type: str | None
    promo_value: int | None
    throttled: bool | None
    # Observed on the live API but undocumented.
    will_renew: bool | None
    created_at: datetime | None
    updated_at: datetime | None


@dataclass
class BundleInfo:
    primary_plan_id: int | None
    discount_rate: float | None


@dataclass
class BundleAddon:
    plan_id: int | None
    discount_rate: float | None


@dataclass
class Plan:
    id: int
    status: str | None
    bandwidth_limit: float | None
    monthly_price: float | None
    yearly_price: float | None
    proxy_type: str | None
    proxy_subtype: str | None
    proxy_count: int | None
    proxy_countries: dict[str, int] | None
    required_site_checks: list[str] | None
    on_demand_refreshes_total: int | None
    on_demand_refreshes_used: int | None
    on_demand_refreshes_available: int | None
    automatic_refresh_frequency: int | None
    automatic_refresh_last_at: datetime | None
    automatic_refresh_next_at: datetime | None
    proxy_replacements_total: int | None
    proxy_replacements_used: int | None
    proxy_replacements_available: int | None
    subusers_total: int | None
    subusers_used: int | None
    subusers_available: int | None
    is_unlimited_ip_authorizations: bool | None
    is_high_concurrency: bool | None
    is_2x_concurrency: bool | None
    is_high_priority_network: bool | None
    high_quality_ips_only: bool | None
    bundle_info: BundleInfo | None
    bundle_addons: list[BundleAddon] | None
    created_at: datetime | None
    updated_at: datetime | None


@dataclass
class PlanCancelResponse:
    success: bool | None
    transaction: int | None


@dataclass
class AssetInfo:
    """Available assets for one proxy category/subtype combination."""

    total_subnets: int | None
    available_countries: dict[str, int] | None


@dataclass
class AvailableFeature:
    feature: str | None
    required: bool | None


@dataclass
class AvailableSiteCheck:
    name: str | None


@dataclass
class CustomizationTerm:
    term: str | None
    renewals_paid: int | None


@dataclass
class CustomizationOptions:
    """Limits and options available when customizing a plan."""

    proxy_type: str | None
    proxy_subtype: str | None
    proxy_count_max: int | None
    proxy_count_min: int | None
    available_countries: dict[str, int] | None
    on_demand_refreshes_max: int | None
    on_demand_refreshes_min: int | None
    automatic_refresh_frequency_max: int | None
    automatic_refresh_frequency_min: int | None
    proxy_replacements_max: int | None
    proxy_replacements_min: int | None
    bandwidth_limit_max: int | None
    bandwidth_limit_min: int | None
    subusers_max: int | None
    subusers_min: int | None
    available_features: list[AvailableFeature] | None
    available_site_checks: list[AvailableSiteCheck] | None
    terms: list[CustomizationTerm] | None


@dataclass
class ProxyCountDiscountTier:
    from_: int | None
    to: int | None
    discount_percentage: int | None
    per_proxy_price: float | None


@dataclass
class BandwidthDiscountTier:
    from_: int | None
    to: int | None
    per_gb_price: float | None


@dataclass
class FeaturePrice:
    feature: str | None
    is_selected: bool | None
    price: float | None


@dataclass
class TaxRateDetails:
    percentage_decimal: str | None
    tax_type: str | None


@dataclass
class TaxBreakdownEntry:
    amount: str | None
    tax_rate_details: TaxRateDetails | None
    taxable_amount: str | None


@dataclass
class CouponDiscount:
    code: str | None
    promo_type: str | None
    promo_value: str | None
    is_recurring: bool | None


@dataclass
class Pricing:
    """Pricing for a custom plan configuration."""

    discount_percentage: int | None
    non_discounted_price: float | None
    price: float | None
    paid_today: float | None
    promo_discount: float | None
    credits_added: float | None
    credits_used: float | None
    proxy_count_discount_tiers: list[ProxyCountDiscountTier] | None
    bandwidth_discount_tiers: list[BandwidthDiscountTier] | None
    features: list[FeaturePrice] | None
    tax_breakdown: list[TaxBreakdownEntry] | None
    coupon_discount: CouponDiscount | None


@dataclass
class CheckoutResponse:
    """Shared response shape of purchase/upgrade/renew checkouts.

    If ``payment_required`` is false the change is complete; otherwise confirm
    the Stripe PaymentIntent (Stripe.js) and poll the pending payment.
    """

    payment_required: bool | None
    plan: int | None
    pending_payment: int | None
    stripe_client_secret: str | None
    stripe_payment_intent: str | None
    stripe_payment_method: str | None


@dataclass
class ReferralConfig:
    id: int
    mode: str | None
    paypal_payout_email: str | None
    id_verification_required: bool | None
    credits_earned: float | None
    payouts_earned: float | None
    total_credits_earned: float | None
    total_payouts_earned: float | None
    number_of_users_referred: int | None
    number_of_users_upgraded: int | None
    earn_out_frequency: str | None
    next_earn_out_date: datetime | None
    minimum_earn_out_amount: float | None
    referral_code: str | None
    referral_url: str | None
    referral_maximum_credits: float | None
    referral_credit_ratio: float | None
    referral_payment_pending_days: str | None
    promo_type: str | None
    promo_value: int | None
    # Observed on the live API but undocumented (affiliate commission terms;
    # numeric here, unlike the string-serialized ReferralChannel rates).
    initial_rate: float | None
    ongoing_rate: float | None
    initial_rate_period_days: int | None
    max_earnings_per_referred: float | None
    created_at: datetime | None
    updated_at: datetime | None


@dataclass
class CouponCode:
    """The coupon code applied to the account; all fields are ``None`` when no
    code is applied."""

    code: str | None
    promo_type: str | None
    promo_value: str | None
    description: str | None
    is_recurring: bool | None


@dataclass
class ReferralChannel:
    id: int
    code: str | None
    description: str | None
    promo_type: str | None
    promo_value: str | None
    is_active: bool | None
    is_recurring: bool | None
    start_date: datetime | None
    end_date: datetime | None
    total_uses: int | None
    total_commission: float | None
    total_revenue: float | None
    initial_rate: str | None
    ongoing_rate: str | None
    initial_rate_period_days: int | None
    max_earnings_per_referred: str | None
    created_at: datetime | None


@dataclass
class ReferralCredit:
    id: int
    user_id: int | None
    mode: str | None
    amount: float | None
    status: str | None
    referral_channel: int | None
    referral_channel_code: str | None
    created_at: datetime | None
    updated_at: datetime | None
    reverted_at: datetime | None


@dataclass
class ReferralEarnout:
    id: int
    mode: str | None
    paypal_payout_email: str | None
    amount: float | None
    status: str | None
    error_reason: str | None
    created_at: datetime | None
    updated_at: datetime | None


@dataclass
class ReferralCodeInfo:
    referral_code: str | None
    promo_type: str | None
    promo_value: int | None
