"""The IP authorization resource (`client.ip_authorizations`)."""

from __future__ import annotations

from collections.abc import Mapping

from webshare._http import RequestSpec
from webshare._pagination import AsyncPage, SyncPage
from webshare._requester import AsyncResource, SyncResource
from webshare.types.proxy import IPAuthorization, WhatsMyIP


def _list_spec(*, plan_id: int | None, page: int | None, page_size: int | None) -> RequestSpec:
    return RequestSpec(
        method="GET",
        path="/api/v2/proxy/ipauthorization/",
        query={"plan_id": plan_id, "page": page, "page_size": page_size},
    )


def _create_spec(*, ip_address: str, plan_id: int | None) -> RequestSpec:
    return RequestSpec(
        method="POST",
        path="/api/v2/proxy/ipauthorization/",
        query={"plan_id": plan_id},
        json_body={"ip_address": ip_address},
    )


def _get_spec(id: int, *, plan_id: int | None) -> RequestSpec:
    return RequestSpec(
        method="GET",
        path=f"/api/v2/proxy/ipauthorization/{id}/",
        query={"plan_id": plan_id},
    )


def _delete_spec(id: int, *, plan_id: int | None) -> RequestSpec:
    return RequestSpec(
        method="DELETE",
        path=f"/api/v2/proxy/ipauthorization/{id}/",
        query={"plan_id": plan_id},
    )


def _whats_my_ip_spec() -> RequestSpec:
    return RequestSpec(method="GET", path="/api/v2/proxy/ipauthorization/whatsmyip/")


class IPAuthorizations(SyncResource):
    def list(
        self,
        *,
        plan_id: int | None = None,
        page: int | None = None,
        page_size: int | None = None,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> SyncPage[IPAuthorization]:
        """List IP authorizations."""
        return self._client.request_page(
            _list_spec(plan_id=plan_id, page=page, page_size=page_size).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            IPAuthorization,
        )

    def create(
        self,
        *,
        ip_address: str,
        plan_id: int | None = None,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> IPAuthorization:
        """Authorize an IP address. May return a 400 error if the IP address is
        already authorized in the system."""
        return self._client.request_model(
            _create_spec(ip_address=ip_address, plan_id=plan_id).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            IPAuthorization,
        )

    def get(
        self,
        id: int,
        *,
        plan_id: int | None = None,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> IPAuthorization:
        """Get an IP authorization."""
        return self._client.request_model(
            _get_spec(id, plan_id=plan_id).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            IPAuthorization,
        )

    def delete(
        self,
        id: int,
        *,
        plan_id: int | None = None,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> None:
        """Delete an IP authorization."""
        return self._client.request_none(
            _delete_spec(id, plan_id=plan_id).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            )
        )

    def whats_my_ip(
        self,
        *,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> WhatsMyIP:
        """Return your public IP address (useful before ``create``)."""
        return self._client.request_model(
            _whats_my_ip_spec().with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            WhatsMyIP,
        )


class AsyncIPAuthorizations(AsyncResource):
    async def list(
        self,
        *,
        plan_id: int | None = None,
        page: int | None = None,
        page_size: int | None = None,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> AsyncPage[IPAuthorization]:
        """List IP authorizations."""
        return await self._client.request_page(
            _list_spec(plan_id=plan_id, page=page, page_size=page_size).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            IPAuthorization,
        )

    async def create(
        self,
        *,
        ip_address: str,
        plan_id: int | None = None,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> IPAuthorization:
        """Authorize an IP address."""
        return await self._client.request_model(
            _create_spec(ip_address=ip_address, plan_id=plan_id).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            IPAuthorization,
        )

    async def get(
        self,
        id: int,
        *,
        plan_id: int | None = None,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> IPAuthorization:
        """Get an IP authorization."""
        return await self._client.request_model(
            _get_spec(id, plan_id=plan_id).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            IPAuthorization,
        )

    async def delete(
        self,
        id: int,
        *,
        plan_id: int | None = None,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> None:
        """Delete an IP authorization."""
        return await self._client.request_none(
            _delete_spec(id, plan_id=plan_id).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            )
        )

    async def whats_my_ip(
        self,
        *,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> WhatsMyIP:
        """Return your public IP address (useful before ``create``)."""
        return await self._client.request_model(
            _whats_my_ip_spec().with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            WhatsMyIP,
        )
