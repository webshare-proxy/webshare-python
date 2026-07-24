"""The two-factor authentication resource (`client.two_factor_auth`).

2FA only applies to login tokens; API keys are never challenged. When 2FA is
required, any API call returns 403 with code ``2fa_needed``; submit the code
via ``submit_code`` and replay the original request.

Note: the live API restricts ``get_method`` (``/twofactorauth/method/current/``)
to session (login) tokens. Calling it with an API key returns 403 with code
``api_key_not_allowed``.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Literal

from .._http import RequestSpec
from .._requester import AsyncResource, SyncResource
from ..types.account import TwoFactorAuthMethod, TwoFactorEmailResend


def _get_method_spec() -> RequestSpec:
    return RequestSpec(method="GET", path="/api/v2/twofactorauth/method/current/")


def _change_method_spec(*, type: Literal["email_code", "device_totp"]) -> RequestSpec:
    return RequestSpec(
        method="POST", path="/api/v2/twofactorauth/method/", json_body={"type": type}
    )


def _activate_method_spec(id: int, *, code_1: str, code_2: str) -> RequestSpec:
    return RequestSpec(
        method="POST",
        path=f"/api/v2/twofactorauth/method/{id}/activate/",
        json_body={"code_1": code_1, "code_2": code_2},
    )


def _submit_code_spec(*, code: str, recaptcha: str) -> RequestSpec:
    return RequestSpec(
        method="POST",
        path="/api/v2/twofactorauth/codeauth/",
        json_body={"code": code, "recaptcha": recaptcha},
    )


def _resend_email_code_spec() -> RequestSpec:
    return RequestSpec(method="POST", path="/api/v2/twofactorauth/email/resend/")


class TwoFactorAuth(SyncResource):
    def get_method(
        self,
        *,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> TwoFactorAuthMethod:
        """Get the active 2FA method for the account."""
        return self._client.request_model(
            _get_method_spec().with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            TwoFactorAuthMethod,
        )

    def change_method(
        self,
        *,
        type: Literal["email_code", "device_totp"],
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> TwoFactorAuthMethod:
        """Change the 2FA method.

        For ``device_totp`` the response's ``secret_key`` is shown only once,
        right after creation; the method then needs ``activate_method``.
        """
        return self._client.request_model(
            _change_method_spec(type=type).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            TwoFactorAuthMethod,
        )

    def activate_method(
        self,
        id: int,
        *,
        code_1: str,
        code_2: str,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> TwoFactorAuthMethod:
        """Activate a TOTP device method with two consecutive codes
        (``code_1`` must differ from ``code_2``)."""
        return self._client.request_model(
            _activate_method_spec(id, code_1=code_1, code_2=code_2).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            TwoFactorAuthMethod,
        )

    def submit_code(
        self,
        *,
        code: str,
        recaptcha: str,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> None:
        """Submit the 2FA code after a 403 with code ``2fa_needed``, then
        replay the originally failed request."""
        return self._client.request_none(
            _submit_code_spec(code=code, recaptcha=recaptcha).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            )
        )

    def resend_email_code(
        self,
        *,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> TwoFactorEmailResend:
        """Resend the 2FA code via email (email method only)."""
        return self._client.request_model(
            _resend_email_code_spec().with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            TwoFactorEmailResend,
        )


class AsyncTwoFactorAuth(AsyncResource):
    async def get_method(
        self,
        *,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> TwoFactorAuthMethod:
        """Get the active 2FA method for the account."""
        return await self._client.request_model(
            _get_method_spec().with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            TwoFactorAuthMethod,
        )

    async def change_method(
        self,
        *,
        type: Literal["email_code", "device_totp"],
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> TwoFactorAuthMethod:
        """Change the 2FA method (``device_totp`` returns a one-time
        ``secret_key``)."""
        return await self._client.request_model(
            _change_method_spec(type=type).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            TwoFactorAuthMethod,
        )

    async def activate_method(
        self,
        id: int,
        *,
        code_1: str,
        code_2: str,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> TwoFactorAuthMethod:
        """Activate a TOTP device method with two consecutive codes."""
        return await self._client.request_model(
            _activate_method_spec(id, code_1=code_1, code_2=code_2).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            TwoFactorAuthMethod,
        )

    async def submit_code(
        self,
        *,
        code: str,
        recaptcha: str,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> None:
        """Submit the 2FA code after a 403 with code ``2fa_needed``."""
        return await self._client.request_none(
            _submit_code_spec(code=code, recaptcha=recaptcha).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            )
        )

    async def resend_email_code(
        self,
        *,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> TwoFactorEmailResend:
        """Resend the 2FA code via email (email method only)."""
        return await self._client.request_model(
            _resend_email_code_spec().with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            TwoFactorEmailResend,
        )
