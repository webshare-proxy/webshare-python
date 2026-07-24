"""The API key resource (`client.api_keys`)."""

from __future__ import annotations

from collections.abc import Mapping

from .._http import RequestSpec, drop_json_nulls
from .._pagination import AsyncPage, SyncPage
from .._requester import AsyncResource, SyncResource
from ..types.account import APIKey


def _list_spec(*, page: int | None, page_size: int | None) -> RequestSpec:
    return RequestSpec(
        method="GET", path="/api/v2/apikey/", query={"page": page, "page_size": page_size}
    )


def _create_spec(*, label: str | None) -> RequestSpec:
    return RequestSpec(
        method="POST", path="/api/v2/apikey/", json_body=drop_json_nulls({"label": label})
    )


def _get_spec(id: int) -> RequestSpec:
    return RequestSpec(method="GET", path=f"/api/v2/apikey/{id}/")


def _update_spec(id: int, *, label: str | None) -> RequestSpec:
    return RequestSpec(
        method="PATCH", path=f"/api/v2/apikey/{id}/", json_body=drop_json_nulls({"label": label})
    )


def _delete_spec(id: int) -> RequestSpec:
    return RequestSpec(method="DELETE", path=f"/api/v2/apikey/{id}/")


class APIKeys(SyncResource):
    def list(
        self,
        *,
        page: int | None = None,
        page_size: int | None = None,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> SyncPage[APIKey]:
        """List API keys."""
        return self._client.request_page(
            _list_spec(page=page, page_size=page_size).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            APIKey,
        )

    def create(
        self,
        *,
        label: str | None = None,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> APIKey:
        """Create an API key. The response is the only place the full ``key``
        appears."""
        return self._client.request_model(
            _create_spec(label=label).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            APIKey,
        )

    def get(
        self,
        id: int,
        *,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> APIKey:
        """Get an API key."""
        return self._client.request_model(
            _get_spec(id).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            APIKey,
        )

    def update(
        self,
        id: int,
        *,
        label: str | None = None,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> APIKey:
        """Update an API key."""
        return self._client.request_model(
            _update_spec(id, label=label).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            APIKey,
        )

    def delete(
        self,
        id: int,
        *,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> None:
        """Delete an API key."""
        return self._client.request_none(
            _delete_spec(id).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            )
        )


class AsyncAPIKeys(AsyncResource):
    async def list(
        self,
        *,
        page: int | None = None,
        page_size: int | None = None,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> AsyncPage[APIKey]:
        """List API keys."""
        return await self._client.request_page(
            _list_spec(page=page, page_size=page_size).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            APIKey,
        )

    async def create(
        self,
        *,
        label: str | None = None,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> APIKey:
        """Create an API key. The response is the only place the full ``key``
        appears."""
        return await self._client.request_model(
            _create_spec(label=label).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            APIKey,
        )

    async def get(
        self,
        id: int,
        *,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> APIKey:
        """Get an API key."""
        return await self._client.request_model(
            _get_spec(id).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            APIKey,
        )

    async def update(
        self,
        id: int,
        *,
        label: str | None = None,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> APIKey:
        """Update an API key."""
        return await self._client.request_model(
            _update_spec(id, label=label).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            APIKey,
        )

    async def delete(
        self,
        id: int,
        *,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> None:
        """Delete an API key."""
        return await self._client.request_none(
            _delete_spec(id).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            )
        )
