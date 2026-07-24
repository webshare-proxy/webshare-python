"""The ID verification resource (`client.id_verification`), backed by Stripe
Identity."""

from __future__ import annotations

from collections.abc import Mapping

from .._http import RequestSpec
from .._requester import AsyncResource, SyncResource
from ..types.account import IDVerification


def _get_spec() -> RequestSpec:
    return RequestSpec(method="GET", path="/api/v2/idverification/")


def _start_spec() -> RequestSpec:
    return RequestSpec(method="POST", path="/api/v2/idverification/start/")


def _complete_spec() -> RequestSpec:
    return RequestSpec(method="POST", path="/api/v2/idverification/complete/")


class IDVerificationResource(SyncResource):
    def get(
        self,
        *,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> IDVerification:
        """Get the ID verification object."""
        return self._client.request_model(
            _get_spec().with_options(timeout, headers, max_retries, subuser_id, federated_user_id),
            IDVerification,
        )

    def start(
        self,
        *,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> IDVerification:
        """Start an ID verification; the response carries the Stripe
        ``client_secret`` and the state becomes ``pending``."""
        return self._client.request_model(
            _start_spec().with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            IDVerification,
        )

    def complete(
        self,
        *,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> IDVerification:
        """Complete an ID verification after finishing the Stripe JS flow; the
        state becomes ``processing``."""
        return self._client.request_model(
            _complete_spec().with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            IDVerification,
        )


class AsyncIDVerificationResource(AsyncResource):
    async def get(
        self,
        *,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> IDVerification:
        """Get the ID verification object."""
        return await self._client.request_model(
            _get_spec().with_options(timeout, headers, max_retries, subuser_id, federated_user_id),
            IDVerification,
        )

    async def start(
        self,
        *,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> IDVerification:
        """Start an ID verification; the response carries the Stripe
        ``client_secret`` and the state becomes ``pending``."""
        return await self._client.request_model(
            _start_spec().with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            IDVerification,
        )

    async def complete(
        self,
        *,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> IDVerification:
        """Complete an ID verification after finishing the Stripe JS flow; the
        state becomes ``processing``."""
        return await self._client.request_model(
            _complete_spec().with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            IDVerification,
        )
