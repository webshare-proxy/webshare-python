"""Models for the API key, profile, notification, auth and verification APIs."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

__all__ = [
    "APIKey",
    "AbuseReport",
    "ActivationStatus",
    "IDVerification",
    "LoginResponse",
    "Notification",
    "Profile",
    "ProfilePreferences",
    "RegisterResponse",
    "Suspension",
    "TwoFactorAuthMethod",
    "TwoFactorEmailResend",
    "VerificationAnswer",
    "VerificationAppeal",
    "VerificationCategory",
    "VerificationEvidence",
    "VerificationFile",
    "VerificationFlow",
    "VerificationLimits",
    "VerificationQuestion",
    "VerificationThreshold",
]


@dataclass
class APIKey:
    id: int
    key: str | None
    label: str | None
    created_at: datetime | None
    updated_at: datetime | None


@dataclass
class Profile:
    id: int
    email: str | None
    first_name: str | None
    last_name: str | None
    last_login: datetime | None
    timezone: str | None
    subscribed_bandwidth_usage_notifications: bool | None
    subscribed_subscription_notifications: bool | None
    subscribed_proxy_usage_statistics: bool | None
    subscribed_usage_warnings: bool | None
    subscribed_guides_and_tips: bool | None
    subscribed_survey_emails: bool | None
    tracking_id: str | None
    # Observed on the live API but undocumented.
    announce_kit_user_token: str | None
    helpscout_beacon_signature: str | None
    intercom_signature: str | None
    is_vip_customer: bool | None
    created_at: datetime | None
    updated_at: datetime | None


@dataclass
class ProfilePreferences:
    id: int
    customer_satisfaction_survey_last_dismissed_at: datetime | None
    customer_satisfaction_survey_last_completed_at: datetime | None
    onboarding_activity_page_viewed_at: datetime | None
    # Observed on the live API but undocumented.
    created_at: datetime | None
    updated_at: datetime | None


@dataclass
class Notification:
    """An account notification. ``context`` keys vary by notification ``type``."""

    id: int
    type: str | None
    is_dismissable: bool | None
    context: dict[str, Any] | None
    created_at: datetime | None
    updated_at: datetime | None
    dismissed_at: datetime | None


@dataclass
class RegisterResponse:
    token: str | None
    logged_in_existing_user: bool | None


@dataclass
class LoginResponse:
    token: str | None


@dataclass
class ActivationStatus:
    email_is_verified: bool | None
    last_time_email_verification_email_sent: datetime | None
    created_at: datetime | None
    updated_at: datetime | None


@dataclass
class TwoFactorAuthMethod:
    """A 2FA method.

    ``secret_key`` (hex TOTP secret) is only present in the response that
    creates a ``device_totp`` method; surface it to the user immediately.
    """

    id: int
    type: str | None
    active: bool | None
    secret_key: str | None
    created_at: datetime | None
    updated_at: datetime | None


@dataclass
class TwoFactorEmailResend:
    email_sent: bool | None


@dataclass
class IDVerification:
    """ID verification via Stripe Identity.

    States: ``not-required``, ``requested``, ``pending``, ``processing``,
    ``failed``, ``verified``.
    """

    id: int
    state: str | None
    client_secret: str | None
    verification_failure_times: int | None
    max_verification_failure_times: int | None
    created_at: datetime | None
    updated_at: datetime | None
    verified_at: datetime | None


@dataclass
class VerificationFile:
    id: int
    file: str | None
    created_at: datetime | None


@dataclass
class VerificationEvidence:
    id: int
    explanation: str | None
    created_at: datetime | None
    updated_at: datetime | None
    files: list[VerificationFile] | None


@dataclass
class VerificationFlow:
    """An account verification flow.

    Types: ``acceptable_use_violation``, ``abuse_report``,
    ``fraudulent_payment``. States: ``inflow``, ``successful_verification``,
    ``failed_verification``.
    """

    id: int
    type: str | None
    state: str | None
    started_at: datetime | None
    updated_at: datetime | None
    needs_evidence: bool | None
    evidence: VerificationEvidence | None
    id_verification_restores_access: bool | None
    id_verification_required: bool | None


@dataclass
class VerificationAnswer:
    id: int
    answer: str | None
    created_at: datetime | None
    updated_at: datetime | None
    files: list[VerificationFile] | None


@dataclass
class VerificationQuestion:
    id: int
    question: str | None
    created_at: datetime | None
    updated_at: datetime | None
    flow: int | None
    answer: VerificationAnswer | None


@dataclass
class VerificationAppeal:
    id: int
    appeal: str | None
    state: str | None
    created_at: datetime | None
    updated_at: datetime | None


@dataclass
class AbuseReport:
    id: int
    content: str | None
    flow: int | None
    created_at: datetime | None
    updated_at: datetime | None


@dataclass
class Suspension:
    created_at: datetime | None
    reason: str | None


@dataclass
class VerificationCategory:
    """A verification category; the API returns a map keyed by category name."""

    description: str | None
    request_threshold: int | None
    id_verification_required: bool | None
    id_verification_restores_access: bool | None


@dataclass
class VerificationLimits:
    proxy_state: str | None


@dataclass
class VerificationThreshold:
    """A verification threshold; the API returns a map keyed by category name."""

    description: str | None
    id_verification_required: bool | None
    id_verification_restores_access: bool | None
    request_count: int | None
    request_threshold: int | None
    triggered: bool | None
