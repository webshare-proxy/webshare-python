"""The referral / affiliate resource (`client.referral`)."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Literal

from webshare._http import RequestSpec, drop_json_nulls
from webshare._pagination import AsyncPage, SyncPage
from webshare._requester import AsyncResource, SyncResource
from webshare.types.commerce import (
    CouponCode,
    ReferralChannel,
    ReferralCodeInfo,
    ReferralConfig,
    ReferralCredit,
    ReferralEarnout,
)

ReferralMode = Literal["payout", "credits"]
CreditStatus = Literal["pending", "available", "reverted"]


def _get_config_spec() -> RequestSpec:
    return RequestSpec(method="GET", path="/api/v2/referral/config/")


def _update_config_spec(
    *, mode: ReferralMode | None, paypal_payout_email: str | None
) -> RequestSpec:
    return RequestSpec(
        method="PATCH",
        path="/api/v2/referral/config/",
        json_body=drop_json_nulls({"mode": mode, "paypal_payout_email": paypal_payout_email}),
    )


def _get_coupon_code_spec() -> RequestSpec:
    return RequestSpec(method="GET", path="/api/v2/referral/coupon-code/")


def _apply_coupon_code_spec(*, code: str) -> RequestSpec:
    return RequestSpec(
        method="POST", path="/api/v2/referral/coupon-code/", json_body={"code": code}
    )


def _remove_coupon_code_spec() -> RequestSpec:
    return RequestSpec(method="DELETE", path="/api/v2/referral/coupon-code/")


def _list_channels_spec() -> RequestSpec:
    return RequestSpec(method="GET", path="/api/v2/referral/channel/")


def _list_credits_spec(
    *,
    page: int | None,
    page_size: int | None,
    mode: ReferralMode | None,
    status: CreditStatus | None,
    referral_channel: int | None,
    ordering: str | None,
) -> RequestSpec:
    return RequestSpec(
        method="GET",
        path="/api/v2/referral/credit/",
        query={
            "page": page,
            "page_size": page_size,
            "mode": mode,
            "status": status,
            "referral_channel": referral_channel,
            "ordering": ordering,
        },
    )


def _get_credit_spec(id: int) -> RequestSpec:
    return RequestSpec(method="GET", path=f"/api/v2/referral/credit/{id}/")


def _list_earnouts_spec(*, page: int | None, page_size: int | None) -> RequestSpec:
    # Verified against the live API: the docs record this list path without a
    # trailing slash, but the server 301s that to the slashed path.
    return RequestSpec(
        method="GET",
        path="/api/v2/referral/earnout/",
        query={"page": page, "page_size": page_size},
    )


def _get_earnout_spec(id: int) -> RequestSpec:
    return RequestSpec(method="GET", path=f"/api/v2/referral/earnout/{id}/")


def _get_code_info_spec(*, referral_code: str) -> RequestSpec:
    return RequestSpec(
        method="GET",
        path="/api/v2/referral/code/info/",
        query={"referral_code": referral_code},
        auth="none",
    )


class Referral(SyncResource):
    def get_config(
        self,
        *,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> ReferralConfig:
        """Get the referral config."""
        return self._client.request_model(
            _get_config_spec().with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            ReferralConfig,
        )

    def update_config(
        self,
        *,
        mode: ReferralMode | None = None,
        paypal_payout_email: str | None = None,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> ReferralConfig:
        """Update the referral config (only ``mode`` and
        ``paypal_payout_email`` are writable)."""
        return self._client.request_model(
            _update_config_spec(mode=mode, paypal_payout_email=paypal_payout_email).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            ReferralConfig,
        )

    def get_coupon_code(
        self,
        *,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> CouponCode:
        """Get the currently applied coupon code (all fields ``None`` when no
        code is applied)."""
        return self._client.request_model(
            _get_coupon_code_spec().with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            CouponCode,
        )

    def apply_coupon_code(
        self,
        *,
        code: str,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> CouponCode:
        """Apply a coupon code (replaces any previously applied code).

        Rate limited to 5 requests/minute. Documented 400 error codes:
        ``not_found``, ``code_inactive``, ``code_expired``, ``self_referral``,
        ``already_redeemed``.
        """
        return self._client.request_model(
            _apply_coupon_code_spec(code=code).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            CouponCode,
        )

    def remove_coupon_code(
        self,
        *,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> None:
        """Remove the applied coupon code (redeemed codes are unaffected)."""
        return self._client.request_none(
            _remove_coupon_code_spec().with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            )
        )

    def list_channels(
        self,
        *,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> list[ReferralChannel]:
        """List referral channels (bare array; NOT paginated)."""
        return self._client.request_model_list(
            _list_channels_spec().with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            ReferralChannel,
        )

    def list_credits(
        self,
        *,
        page: int | None = None,
        page_size: int | None = None,
        mode: ReferralMode | None = None,
        status: CreditStatus | None = None,
        referral_channel: int | None = None,
        ordering: str | None = None,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> SyncPage[ReferralCredit]:
        """List referral credits."""
        return self._client.request_page(
            _list_credits_spec(
                page=page,
                page_size=page_size,
                mode=mode,
                status=status,
                referral_channel=referral_channel,
                ordering=ordering,
            ).with_options(timeout, headers, max_retries, subuser_id, federated_user_id),
            ReferralCredit,
        )

    def get_credit(
        self,
        id: int,
        *,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> ReferralCredit:
        """Get a referral credit."""
        return self._client.request_model(
            _get_credit_spec(id).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            ReferralCredit,
        )

    def list_earnouts(
        self,
        *,
        page: int | None = None,
        page_size: int | None = None,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> SyncPage[ReferralEarnout]:
        """List earn outs."""
        return self._client.request_page(
            _list_earnouts_spec(page=page, page_size=page_size).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            ReferralEarnout,
        )

    def get_earnout(
        self,
        id: int,
        *,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> ReferralEarnout:
        """Get an earn out."""
        return self._client.request_model(
            _get_earnout_spec(id).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            ReferralEarnout,
        )

    def get_code_info(
        self,
        *,
        referral_code: str,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> ReferralCodeInfo:
        """Get the public information of a referral code (unauthenticated)."""
        return self._client.request_model(
            _get_code_info_spec(referral_code=referral_code).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            ReferralCodeInfo,
        )


class AsyncReferral(AsyncResource):
    async def get_config(
        self,
        *,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> ReferralConfig:
        """Get the referral config."""
        return await self._client.request_model(
            _get_config_spec().with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            ReferralConfig,
        )

    async def update_config(
        self,
        *,
        mode: ReferralMode | None = None,
        paypal_payout_email: str | None = None,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> ReferralConfig:
        """Update the referral config (only ``mode`` and
        ``paypal_payout_email`` are writable)."""
        return await self._client.request_model(
            _update_config_spec(mode=mode, paypal_payout_email=paypal_payout_email).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            ReferralConfig,
        )

    async def get_coupon_code(
        self,
        *,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> CouponCode:
        """Get the currently applied coupon code."""
        return await self._client.request_model(
            _get_coupon_code_spec().with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            CouponCode,
        )

    async def apply_coupon_code(
        self,
        *,
        code: str,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> CouponCode:
        """Apply a coupon code (5 requests/minute rate limit)."""
        return await self._client.request_model(
            _apply_coupon_code_spec(code=code).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            CouponCode,
        )

    async def remove_coupon_code(
        self,
        *,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> None:
        """Remove the applied coupon code (redeemed codes are unaffected)."""
        return await self._client.request_none(
            _remove_coupon_code_spec().with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            )
        )

    async def list_channels(
        self,
        *,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> list[ReferralChannel]:
        """List referral channels (bare array; NOT paginated)."""
        return await self._client.request_model_list(
            _list_channels_spec().with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            ReferralChannel,
        )

    async def list_credits(
        self,
        *,
        page: int | None = None,
        page_size: int | None = None,
        mode: ReferralMode | None = None,
        status: CreditStatus | None = None,
        referral_channel: int | None = None,
        ordering: str | None = None,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> AsyncPage[ReferralCredit]:
        """List referral credits."""
        return await self._client.request_page(
            _list_credits_spec(
                page=page,
                page_size=page_size,
                mode=mode,
                status=status,
                referral_channel=referral_channel,
                ordering=ordering,
            ).with_options(timeout, headers, max_retries, subuser_id, federated_user_id),
            ReferralCredit,
        )

    async def get_credit(
        self,
        id: int,
        *,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> ReferralCredit:
        """Get a referral credit."""
        return await self._client.request_model(
            _get_credit_spec(id).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            ReferralCredit,
        )

    async def list_earnouts(
        self,
        *,
        page: int | None = None,
        page_size: int | None = None,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> AsyncPage[ReferralEarnout]:
        """List earn outs."""
        return await self._client.request_page(
            _list_earnouts_spec(page=page, page_size=page_size).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            ReferralEarnout,
        )

    async def get_earnout(
        self,
        id: int,
        *,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> ReferralEarnout:
        """Get an earn out."""
        return await self._client.request_model(
            _get_earnout_spec(id).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            ReferralEarnout,
        )

    async def get_code_info(
        self,
        *,
        referral_code: str,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> ReferralCodeInfo:
        """Get the public information of a referral code (unauthenticated)."""
        return await self._client.request_model(
            _get_code_info_spec(referral_code=referral_code).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            ReferralCodeInfo,
        )
