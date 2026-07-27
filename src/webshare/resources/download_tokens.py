"""The download token resource (`client.download_tokens`)."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Literal

from webshare._http import RequestSpec
from webshare._requester import AsyncResource, SyncResource
from webshare.types.proxy import DownloadToken

TokenScope = Literal["proxy_list", "replaced_proxy", "activity"]


def _get_spec(scope: TokenScope) -> RequestSpec:
    return RequestSpec(method="GET", path=f"/api/v2/download_token/{scope}/")


def _reset_spec(scope: TokenScope) -> RequestSpec:
    return RequestSpec(method="POST", path=f"/api/v2/download_token/{scope}/reset/")


class DownloadTokens(SyncResource):
    def get(
        self,
        scope: TokenScope,
        *,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> DownloadToken:
        """Get a download token for the given scope."""
        return self._client.request_model(
            _get_spec(scope).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            DownloadToken,
        )

    def reset(
        self,
        scope: TokenScope,
        *,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> DownloadToken:
        """Reset (rotate) the download token for the given scope."""
        return self._client.request_model(
            _reset_spec(scope).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            DownloadToken,
        )


class AsyncDownloadTokens(AsyncResource):
    async def get(
        self,
        scope: TokenScope,
        *,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> DownloadToken:
        """Get a download token for the given scope."""
        return await self._client.request_model(
            _get_spec(scope).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            DownloadToken,
        )

    async def reset(
        self,
        scope: TokenScope,
        *,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> DownloadToken:
        """Reset (rotate) the download token for the given scope."""
        return await self._client.request_model(
            _reset_spec(scope).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            DownloadToken,
        )
