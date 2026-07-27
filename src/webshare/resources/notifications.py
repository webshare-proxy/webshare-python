"""The notification resource (`client.notifications`)."""

from __future__ import annotations

from collections.abc import Mapping

from webshare._http import RequestSpec
from webshare._pagination import AsyncPage, SyncPage
from webshare._requester import AsyncResource, SyncResource
from webshare.types.account import Notification


def _list_spec(
    *,
    dismissed_at__isnull: bool | None,
    ordering: str | None,
    type: str | None,
    page: int | None,
    page_size: int | None,
) -> RequestSpec:
    return RequestSpec(
        method="GET",
        path="/api/v2/notification/",
        query={
            "dismissed_at__isnull": dismissed_at__isnull,
            "ordering": ordering,
            "type": type,
            "page": page,
            "page_size": page_size,
        },
    )


def _get_spec(id: int) -> RequestSpec:
    return RequestSpec(method="GET", path=f"/api/v2/notification/{id}/")


def _dismiss_spec(id: int) -> RequestSpec:
    return RequestSpec(method="POST", path=f"/api/v2/notification/{id}/dismiss/")


def _restore_spec(id: int) -> RequestSpec:
    return RequestSpec(method="POST", path=f"/api/v2/notification/{id}/restore/")


class Notifications(SyncResource):
    def list(
        self,
        *,
        dismissed_at__isnull: bool | None = None,
        ordering: str | None = None,
        type: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> SyncPage[Notification]:
        """List account notifications."""
        return self._client.request_page(
            _list_spec(
                dismissed_at__isnull=dismissed_at__isnull,
                ordering=ordering,
                type=type,
                page=page,
                page_size=page_size,
            ).with_options(timeout, headers, max_retries, subuser_id, federated_user_id),
            Notification,
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
    ) -> Notification:
        """Get a notification."""
        return self._client.request_model(
            _get_spec(id).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            Notification,
        )

    def dismiss(
        self,
        id: int,
        *,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> Notification:
        """Dismiss a notification."""
        return self._client.request_model(
            _dismiss_spec(id).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            Notification,
        )

    def restore(
        self,
        id: int,
        *,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> Notification:
        """Restore a dismissed notification."""
        return self._client.request_model(
            _restore_spec(id).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            Notification,
        )


class AsyncNotifications(AsyncResource):
    async def list(
        self,
        *,
        dismissed_at__isnull: bool | None = None,
        ordering: str | None = None,
        type: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> AsyncPage[Notification]:
        """List account notifications."""
        return await self._client.request_page(
            _list_spec(
                dismissed_at__isnull=dismissed_at__isnull,
                ordering=ordering,
                type=type,
                page=page,
                page_size=page_size,
            ).with_options(timeout, headers, max_retries, subuser_id, federated_user_id),
            Notification,
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
    ) -> Notification:
        """Get a notification."""
        return await self._client.request_model(
            _get_spec(id).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            Notification,
        )

    async def dismiss(
        self,
        id: int,
        *,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> Notification:
        """Dismiss a notification."""
        return await self._client.request_model(
            _dismiss_spec(id).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            Notification,
        )

    async def restore(
        self,
        id: int,
        *,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> Notification:
        """Restore a dismissed notification."""
        return await self._client.request_model(
            _restore_spec(id).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            Notification,
        )
