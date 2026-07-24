"""The session / account lifecycle resource (`client.auth`).

Caveat: the API docs mark ``register``, ``login`` and ``delete_account`` as
dashboard-only (they require a recaptcha token issued by the Webshare
dashboard). They are exposed here for completeness but are not expected to
succeed from arbitrary programmatic contexts.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Literal

from .._http import RequestSpec, drop_json_nulls
from .._requester import AsyncResource, SyncResource
from ..types.account import ActivationStatus, LoginResponse, RegisterResponse


def _register_spec(
    *,
    email: str,
    password: str,
    recaptcha: str,
    tos_accepted: bool,
    marketing_email_accepted: bool | None,
) -> RequestSpec:
    return RequestSpec(
        method="POST",
        path="/api/v2/register/",
        json_body=drop_json_nulls(
            {
                "email": email,
                "password": password,
                "recaptcha": recaptcha,
                "tos_accepted": tos_accepted,
                "marketing_email_accepted": marketing_email_accepted,
            }
        ),
        authenticated=False,
    )


def _register_social_spec(
    *,
    provider: Literal["google"],
    code: str,
    redirect_uri: str,
    tos_accepted: bool,
    marketing_email_accepted: bool | None,
) -> RequestSpec:
    return RequestSpec(
        method="POST",
        path="/api/v2/register/social/",
        json_body=drop_json_nulls(
            {
                "provider": provider,
                "code": code,
                "redirect_uri": redirect_uri,
                "tos_accepted": tos_accepted,
                "marketing_email_accepted": marketing_email_accepted,
            }
        ),
        authenticated=False,
    )


def _login_spec(*, email: str, password: str, recaptcha: str) -> RequestSpec:
    return RequestSpec(
        method="POST",
        path="/api/v2/login/",
        json_body={"email": email, "password": password, "recaptcha": recaptcha},
        authenticated=False,
    )


def _login_social_spec(*, provider: Literal["google"], code: str, redirect_uri: str) -> RequestSpec:
    return RequestSpec(
        method="POST",
        path="/api/v2/login/social/",
        json_body={"provider": provider, "code": code, "redirect_uri": redirect_uri},
        authenticated=False,
    )


def _logout_spec() -> RequestSpec:
    return RequestSpec(method="POST", path="/api/v2/logout/")


def _change_password_spec(*, password: str, new_password: str) -> RequestSpec:
    return RequestSpec(
        method="POST",
        path="/api/v2/changepassword/",
        json_body={"password": password, "new_password": new_password},
    )


def _request_password_reset_spec(*, email: str, recaptcha: str) -> RequestSpec:
    return RequestSpec(
        method="POST",
        path="/api/v2/resetpassword/",
        json_body={"email": email, "recaptcha": recaptcha},
        authenticated=False,
    )


def _complete_password_reset_spec(
    *, password: str, password_reset_token: str, recaptcha: str
) -> RequestSpec:
    return RequestSpec(
        method="POST",
        path="/api/v2/resetpassword/complete/",
        json_body={
            "password": password,
            "password_reset_token": password_reset_token,
            "recaptcha": recaptcha,
        },
        authenticated=False,
    )


def _request_email_change_spec(*, password: str, new_email: str) -> RequestSpec:
    return RequestSpec(
        method="POST",
        path="/api/v2/changeemail/",
        json_body={"password": password, "new_email": new_email},
    )


def _complete_email_change_spec(*, confirmation_code: str) -> RequestSpec:
    return RequestSpec(
        method="POST",
        path="/api/v2/changeemail/complete/",
        json_body={"confirmation_code": confirmation_code},
    )


def _get_activation_spec() -> RequestSpec:
    return RequestSpec(method="GET", path="/api/v2/activation/")


def _resend_activation_spec() -> RequestSpec:
    return RequestSpec(method="POST", path="/api/v2/activation/resend/")


def _complete_activation_spec(*, activation_token: str) -> RequestSpec:
    return RequestSpec(
        method="POST",
        path="/api/v2/activation/complete/",
        json_body={"activation_token": activation_token},
    )


def _delete_account_spec(*, password: str, recaptcha: str) -> RequestSpec:
    return RequestSpec(
        method="POST",
        path="/api/v2/deleteaccount/",
        json_body={"password": password, "recaptcha": recaptcha},
    )


def _delete_account_social_spec(
    *, provider: Literal["google"], code: str, redirect_uri: str
) -> RequestSpec:
    return RequestSpec(
        method="POST",
        path="/api/v2/deleteaccount/social/",
        json_body={"provider": provider, "code": code, "redirect_uri": redirect_uri},
    )


class Auth(SyncResource):
    def register(
        self,
        *,
        email: str,
        password: str,
        recaptcha: str,
        tos_accepted: bool,
        marketing_email_accepted: bool | None = None,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> RegisterResponse:
        """Register a local account. Dashboard-only per the docs (recaptcha)."""
        return self._client.request_model(
            _register_spec(
                email=email,
                password=password,
                recaptcha=recaptcha,
                tos_accepted=tos_accepted,
                marketing_email_accepted=marketing_email_accepted,
            ).with_options(timeout, headers, max_retries, subuser_id, federated_user_id),
            RegisterResponse,
        )

    def register_social(
        self,
        *,
        provider: Literal["google"],
        code: str,
        redirect_uri: str,
        tos_accepted: bool,
        marketing_email_accepted: bool | None = None,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> RegisterResponse:
        """Register an account with a social provider (Google OAuth2)."""
        return self._client.request_model(
            _register_social_spec(
                provider=provider,
                code=code,
                redirect_uri=redirect_uri,
                tos_accepted=tos_accepted,
                marketing_email_accepted=marketing_email_accepted,
            ).with_options(timeout, headers, max_retries, subuser_id, federated_user_id),
            RegisterResponse,
        )

    def login(
        self,
        *,
        email: str,
        password: str,
        recaptcha: str,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> LoginResponse:
        """Sign in with a local account. Dashboard-only per the docs (recaptcha)."""
        return self._client.request_model(
            _login_spec(email=email, password=password, recaptcha=recaptcha).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            LoginResponse,
        )

    def login_social(
        self,
        *,
        provider: Literal["google"],
        code: str,
        redirect_uri: str,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> LoginResponse:
        """Login with a social provider (Google OAuth2)."""
        return self._client.request_model(
            _login_social_spec(
                provider=provider, code=code, redirect_uri=redirect_uri
            ).with_options(timeout, headers, max_retries, subuser_id, federated_user_id),
            LoginResponse,
        )

    def logout(
        self,
        *,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> None:
        """Logout; invalidates the token used to make this request."""
        return self._client.request_none(
            _logout_spec().with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            )
        )

    def change_password(
        self,
        *,
        password: str,
        new_password: str,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> None:
        """Change the password. Disables all API tokens except the current one."""
        return self._client.request_none(
            _change_password_spec(password=password, new_password=new_password).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            )
        )

    def request_password_reset(
        self,
        *,
        email: str,
        recaptcha: str,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> None:
        """Request a password reset email. Always returns 204, even for
        unknown emails."""
        return self._client.request_none(
            _request_password_reset_spec(email=email, recaptcha=recaptcha).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            )
        )

    def complete_password_reset(
        self,
        *,
        password: str,
        password_reset_token: str,
        recaptcha: str,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> LoginResponse:
        """Complete a password reset. Invalidates all previous tokens and
        returns a new one."""
        return self._client.request_model(
            _complete_password_reset_spec(
                password=password,
                password_reset_token=password_reset_token,
                recaptcha=recaptcha,
            ).with_options(timeout, headers, max_retries, subuser_id, federated_user_id),
            LoginResponse,
        )

    def request_email_change(
        self,
        *,
        password: str,
        new_email: str,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> None:
        """Request an email change; a confirmation email is sent."""
        return self._client.request_none(
            _request_email_change_spec(password=password, new_email=new_email).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            )
        )

    def complete_email_change(
        self,
        *,
        confirmation_code: str,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> None:
        """Complete an email change (must be authenticated)."""
        return self._client.request_none(
            _complete_email_change_spec(confirmation_code=confirmation_code).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            )
        )

    def get_activation(
        self,
        *,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> ActivationStatus:
        """Get the account activation status."""
        return self._client.request_model(
            _get_activation_spec().with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            ActivationStatus,
        )

    def resend_activation(
        self,
        *,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> ActivationStatus:
        """Re-send the activation email (rate limited)."""
        return self._client.request_model(
            _resend_activation_spec().with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            ActivationStatus,
        )

    def complete_activation(
        self,
        *,
        activation_token: str,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> LoginResponse:
        """Complete account activation; returns a new token (existing tokens
        keep working)."""
        return self._client.request_model(
            _complete_activation_spec(activation_token=activation_token).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            LoginResponse,
        )

    def delete_account(
        self,
        *,
        password: str,
        recaptcha: str,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> None:
        """Delete the account. Dashboard-only per the docs (recaptcha)."""
        return self._client.request_none(
            _delete_account_spec(password=password, recaptcha=recaptcha).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            )
        )

    def delete_account_social(
        self,
        *,
        provider: Literal["google"],
        code: str,
        redirect_uri: str,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> None:
        """Delete an account registered via a social provider."""
        return self._client.request_none(
            _delete_account_social_spec(
                provider=provider, code=code, redirect_uri=redirect_uri
            ).with_options(timeout, headers, max_retries, subuser_id, federated_user_id)
        )


class AsyncAuth(AsyncResource):
    async def register(
        self,
        *,
        email: str,
        password: str,
        recaptcha: str,
        tos_accepted: bool,
        marketing_email_accepted: bool | None = None,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> RegisterResponse:
        """Register a local account. Dashboard-only per the docs (recaptcha)."""
        return await self._client.request_model(
            _register_spec(
                email=email,
                password=password,
                recaptcha=recaptcha,
                tos_accepted=tos_accepted,
                marketing_email_accepted=marketing_email_accepted,
            ).with_options(timeout, headers, max_retries, subuser_id, federated_user_id),
            RegisterResponse,
        )

    async def register_social(
        self,
        *,
        provider: Literal["google"],
        code: str,
        redirect_uri: str,
        tos_accepted: bool,
        marketing_email_accepted: bool | None = None,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> RegisterResponse:
        """Register an account with a social provider (Google OAuth2)."""
        return await self._client.request_model(
            _register_social_spec(
                provider=provider,
                code=code,
                redirect_uri=redirect_uri,
                tos_accepted=tos_accepted,
                marketing_email_accepted=marketing_email_accepted,
            ).with_options(timeout, headers, max_retries, subuser_id, federated_user_id),
            RegisterResponse,
        )

    async def login(
        self,
        *,
        email: str,
        password: str,
        recaptcha: str,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> LoginResponse:
        """Sign in with a local account. Dashboard-only per the docs (recaptcha)."""
        return await self._client.request_model(
            _login_spec(email=email, password=password, recaptcha=recaptcha).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            LoginResponse,
        )

    async def login_social(
        self,
        *,
        provider: Literal["google"],
        code: str,
        redirect_uri: str,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> LoginResponse:
        """Login with a social provider (Google OAuth2)."""
        return await self._client.request_model(
            _login_social_spec(
                provider=provider, code=code, redirect_uri=redirect_uri
            ).with_options(timeout, headers, max_retries, subuser_id, federated_user_id),
            LoginResponse,
        )

    async def logout(
        self,
        *,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> None:
        """Logout; invalidates the token used to make this request."""
        return await self._client.request_none(
            _logout_spec().with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            )
        )

    async def change_password(
        self,
        *,
        password: str,
        new_password: str,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> None:
        """Change the password. Disables all API tokens except the current one."""
        return await self._client.request_none(
            _change_password_spec(password=password, new_password=new_password).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            )
        )

    async def request_password_reset(
        self,
        *,
        email: str,
        recaptcha: str,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> None:
        """Request a password reset email. Always returns 204, even for
        unknown emails."""
        return await self._client.request_none(
            _request_password_reset_spec(email=email, recaptcha=recaptcha).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            )
        )

    async def complete_password_reset(
        self,
        *,
        password: str,
        password_reset_token: str,
        recaptcha: str,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> LoginResponse:
        """Complete a password reset. Invalidates all previous tokens and
        returns a new one."""
        return await self._client.request_model(
            _complete_password_reset_spec(
                password=password,
                password_reset_token=password_reset_token,
                recaptcha=recaptcha,
            ).with_options(timeout, headers, max_retries, subuser_id, federated_user_id),
            LoginResponse,
        )

    async def request_email_change(
        self,
        *,
        password: str,
        new_email: str,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> None:
        """Request an email change; a confirmation email is sent."""
        return await self._client.request_none(
            _request_email_change_spec(password=password, new_email=new_email).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            )
        )

    async def complete_email_change(
        self,
        *,
        confirmation_code: str,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> None:
        """Complete an email change (must be authenticated)."""
        return await self._client.request_none(
            _complete_email_change_spec(confirmation_code=confirmation_code).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            )
        )

    async def get_activation(
        self,
        *,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> ActivationStatus:
        """Get the account activation status."""
        return await self._client.request_model(
            _get_activation_spec().with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            ActivationStatus,
        )

    async def resend_activation(
        self,
        *,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> ActivationStatus:
        """Re-send the activation email (rate limited)."""
        return await self._client.request_model(
            _resend_activation_spec().with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            ActivationStatus,
        )

    async def complete_activation(
        self,
        *,
        activation_token: str,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> LoginResponse:
        """Complete account activation; returns a new token (existing tokens
        keep working)."""
        return await self._client.request_model(
            _complete_activation_spec(activation_token=activation_token).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            LoginResponse,
        )

    async def delete_account(
        self,
        *,
        password: str,
        recaptcha: str,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> None:
        """Delete the account. Dashboard-only per the docs (recaptcha)."""
        return await self._client.request_none(
            _delete_account_spec(password=password, recaptcha=recaptcha).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            )
        )

    async def delete_account_social(
        self,
        *,
        provider: Literal["google"],
        code: str,
        redirect_uri: str,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> None:
        """Delete an account registered via a social provider."""
        return await self._client.request_none(
            _delete_account_social_spec(
                provider=provider, code=code, redirect_uri=redirect_uri
            ).with_options(timeout, headers, max_retries, subuser_id, federated_user_id)
        )
