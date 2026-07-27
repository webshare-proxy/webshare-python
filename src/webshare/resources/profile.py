"""The user profile resource (`client.profile`)."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime

from webshare._http import RequestSpec, drop_json_nulls
from webshare._requester import AsyncResource, SyncResource
from webshare.types.account import Profile, ProfilePreferences


def _get_spec() -> RequestSpec:
    return RequestSpec(method="GET", path="/api/v2/profile/")


def _update_spec(
    *,
    first_name: str | None,
    last_name: str | None,
    timezone: str | None,
    subscribed_bandwidth_usage_notifications: bool | None,
    subscribed_subscription_notifications: bool | None,
    subscribed_proxy_usage_statistics: bool | None,
    subscribed_usage_warnings: bool | None,
    subscribed_guides_and_tips: bool | None,
    subscribed_survey_emails: bool | None,
) -> RequestSpec:
    return RequestSpec(
        method="PATCH",
        path="/api/v2/profile/",
        json_body=drop_json_nulls(
            {
                "first_name": first_name,
                "last_name": last_name,
                "timezone": timezone,
                "subscribed_bandwidth_usage_notifications": subscribed_bandwidth_usage_notifications,
                "subscribed_subscription_notifications": subscribed_subscription_notifications,
                "subscribed_proxy_usage_statistics": subscribed_proxy_usage_statistics,
                "subscribed_usage_warnings": subscribed_usage_warnings,
                "subscribed_guides_and_tips": subscribed_guides_and_tips,
                "subscribed_survey_emails": subscribed_survey_emails,
            }
        ),
    )


def _get_preferences_spec() -> RequestSpec:
    return RequestSpec(method="GET", path="/api/v2/profile/preferences/")


def _dt(value: str | datetime | None) -> str | None:
    return value.isoformat() if isinstance(value, datetime) else value


def _update_preferences_spec(
    *,
    customer_satisfaction_survey_last_dismissed_at: str | datetime | None,
    customer_satisfaction_survey_last_completed_at: str | datetime | None,
    onboarding_activity_page_viewed_at: str | datetime | None,
) -> RequestSpec:
    return RequestSpec(
        method="PATCH",
        path="/api/v2/profile/preferences/",
        json_body=drop_json_nulls(
            {
                "customer_satisfaction_survey_last_dismissed_at": _dt(
                    customer_satisfaction_survey_last_dismissed_at
                ),
                "customer_satisfaction_survey_last_completed_at": _dt(
                    customer_satisfaction_survey_last_completed_at
                ),
                "onboarding_activity_page_viewed_at": _dt(onboarding_activity_page_viewed_at),
            }
        ),
    )


class ProfileResource(SyncResource):
    def get(
        self,
        *,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> Profile:
        """Retrieve the user profile."""
        return self._client.request_model(
            _get_spec().with_options(timeout, headers, max_retries, subuser_id, federated_user_id),
            Profile,
        )

    def update(
        self,
        *,
        first_name: str | None = None,
        last_name: str | None = None,
        timezone: str | None = None,
        subscribed_bandwidth_usage_notifications: bool | None = None,
        subscribed_subscription_notifications: bool | None = None,
        subscribed_proxy_usage_statistics: bool | None = None,
        subscribed_usage_warnings: bool | None = None,
        subscribed_guides_and_tips: bool | None = None,
        subscribed_survey_emails: bool | None = None,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> Profile:
        """Partially update the user profile."""
        return self._client.request_model(
            _update_spec(
                first_name=first_name,
                last_name=last_name,
                timezone=timezone,
                subscribed_bandwidth_usage_notifications=subscribed_bandwidth_usage_notifications,
                subscribed_subscription_notifications=subscribed_subscription_notifications,
                subscribed_proxy_usage_statistics=subscribed_proxy_usage_statistics,
                subscribed_usage_warnings=subscribed_usage_warnings,
                subscribed_guides_and_tips=subscribed_guides_and_tips,
                subscribed_survey_emails=subscribed_survey_emails,
            ).with_options(timeout, headers, max_retries, subuser_id, federated_user_id),
            Profile,
        )

    def get_preferences(
        self,
        *,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> ProfilePreferences:
        """Retrieve the user preferences."""
        return self._client.request_model(
            _get_preferences_spec().with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            ProfilePreferences,
        )

    def update_preferences(
        self,
        *,
        customer_satisfaction_survey_last_dismissed_at: str | datetime | None = None,
        customer_satisfaction_survey_last_completed_at: str | datetime | None = None,
        onboarding_activity_page_viewed_at: str | datetime | None = None,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> ProfilePreferences:
        """Update the user preferences (any subset of the fields)."""
        return self._client.request_model(
            _update_preferences_spec(
                customer_satisfaction_survey_last_dismissed_at=customer_satisfaction_survey_last_dismissed_at,
                customer_satisfaction_survey_last_completed_at=customer_satisfaction_survey_last_completed_at,
                onboarding_activity_page_viewed_at=onboarding_activity_page_viewed_at,
            ).with_options(timeout, headers, max_retries, subuser_id, federated_user_id),
            ProfilePreferences,
        )


class AsyncProfileResource(AsyncResource):
    async def get(
        self,
        *,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> Profile:
        """Retrieve the user profile."""
        return await self._client.request_model(
            _get_spec().with_options(timeout, headers, max_retries, subuser_id, federated_user_id),
            Profile,
        )

    async def update(
        self,
        *,
        first_name: str | None = None,
        last_name: str | None = None,
        timezone: str | None = None,
        subscribed_bandwidth_usage_notifications: bool | None = None,
        subscribed_subscription_notifications: bool | None = None,
        subscribed_proxy_usage_statistics: bool | None = None,
        subscribed_usage_warnings: bool | None = None,
        subscribed_guides_and_tips: bool | None = None,
        subscribed_survey_emails: bool | None = None,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> Profile:
        """Partially update the user profile."""
        return await self._client.request_model(
            _update_spec(
                first_name=first_name,
                last_name=last_name,
                timezone=timezone,
                subscribed_bandwidth_usage_notifications=subscribed_bandwidth_usage_notifications,
                subscribed_subscription_notifications=subscribed_subscription_notifications,
                subscribed_proxy_usage_statistics=subscribed_proxy_usage_statistics,
                subscribed_usage_warnings=subscribed_usage_warnings,
                subscribed_guides_and_tips=subscribed_guides_and_tips,
                subscribed_survey_emails=subscribed_survey_emails,
            ).with_options(timeout, headers, max_retries, subuser_id, federated_user_id),
            Profile,
        )

    async def get_preferences(
        self,
        *,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> ProfilePreferences:
        """Retrieve the user preferences."""
        return await self._client.request_model(
            _get_preferences_spec().with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            ProfilePreferences,
        )

    async def update_preferences(
        self,
        *,
        customer_satisfaction_survey_last_dismissed_at: str | datetime | None = None,
        customer_satisfaction_survey_last_completed_at: str | datetime | None = None,
        onboarding_activity_page_viewed_at: str | datetime | None = None,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> ProfilePreferences:
        """Update the user preferences (any subset of the fields)."""
        return await self._client.request_model(
            _update_preferences_spec(
                customer_satisfaction_survey_last_dismissed_at=customer_satisfaction_survey_last_dismissed_at,
                customer_satisfaction_survey_last_completed_at=customer_satisfaction_survey_last_completed_at,
                onboarding_activity_page_viewed_at=onboarding_activity_page_viewed_at,
            ).with_options(timeout, headers, max_retries, subuser_id, federated_user_id),
            ProfilePreferences,
        )
