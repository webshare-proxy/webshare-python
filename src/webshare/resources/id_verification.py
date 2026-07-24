"""The ID verification resource (`client.id_verification`), backed by Stripe
Identity. Read-only: the verification itself is completed in the dashboard."""

from __future__ import annotations

from collections.abc import Mapping

from .._http import RequestSpec
from .._requester import AsyncResource, SyncResource
from ..types.account import IDVerification


def _get_spec() -> RequestSpec:
    return RequestSpec(method="GET", path="/api/v2/idverification/")


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
