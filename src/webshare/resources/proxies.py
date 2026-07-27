"""The proxy list resource (`client.proxies`)."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import datetime
from typing import Literal

from webshare._http import RequestSpec
from webshare._pagination import AsyncPage, SyncPage
from webshare._proxy_url import build_proxy_list_download_url, proxy_list_download_path
from webshare._requester import AsyncResource, SyncResource
from webshare.types.proxy import Proxy


def _list_spec(
    *,
    mode: Literal["direct", "backbone"],
    plan_id: int | None,
    page: int | None,
    page_size: int | None,
    country_code__in: str | Sequence[str] | None,
    search: str | None,
    ordering: str | None,
    created_at: str | datetime | None,
    proxy_address: str | None,
    proxy_address__in: str | Sequence[str] | None,
    valid: bool | None,
    asn_number: str | None,
    asn_name: str | None,
) -> RequestSpec:
    return RequestSpec(
        method="GET",
        path="/api/v2/proxy/list/",
        query={
            "mode": mode,
            "plan_id": plan_id,
            "page": page,
            "page_size": page_size,
            "country_code__in": country_code__in,
            "search": search,
            "ordering": ordering,
            "created_at": created_at,
            "proxy_address": proxy_address,
            "proxy_address__in": proxy_address__in,
            "valid": valid,
            "asn_number": asn_number,
            "asn_name": asn_name,
        },
    )


def _refresh_spec(*, plan_id: int | None) -> RequestSpec:
    return RequestSpec(
        method="POST",
        path="/api/v2/proxy/list/refresh/",
        query={"plan_id": plan_id},
    )


def _download_spec(
    token: str,
    *,
    country_codes: Sequence[str] | None,
    proxy_protocol: str,
    authentication_method: Literal["username", "sourceip"],
    endpoint_mode: Literal["direct", "backbone"],
    search: str | None,
    plan_id: int | None,
) -> RequestSpec:
    return RequestSpec(
        method="GET",
        path=proxy_list_download_path(
            token,
            country_codes=country_codes,
            proxy_protocol=proxy_protocol,
            authentication_method=authentication_method,
            endpoint_mode=endpoint_mode,
            search=search,
        ),
        query={"plan_id": plan_id},
        auth="none",
    )


class Proxies(SyncResource):
    def list(
        self,
        *,
        mode: Literal["direct", "backbone"],
        plan_id: int | None = None,
        page: int | None = None,
        page_size: int | None = None,
        country_code__in: str | Sequence[str] | None = None,
        search: str | None = None,
        ordering: str | None = None,
        created_at: str | datetime | None = None,
        proxy_address: str | None = None,
        proxy_address__in: str | Sequence[str] | None = None,
        valid: bool | None = None,
        asn_number: str | None = None,
        asn_name: str | None = None,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> SyncPage[Proxy]:
        """List proxies. ``mode`` is required and must be ``backbone`` for
        residential plans; most other filters do not work in backbone mode."""
        return self._client.request_page(
            _list_spec(
                mode=mode,
                plan_id=plan_id,
                page=page,
                page_size=page_size,
                country_code__in=country_code__in,
                search=search,
                ordering=ordering,
                created_at=created_at,
                proxy_address=proxy_address,
                proxy_address__in=proxy_address__in,
                valid=valid,
                asn_number=asn_number,
                asn_name=asn_name,
            ).with_options(timeout, headers, max_retries, subuser_id, federated_user_id),
            Proxy,
        )

    def refresh(
        self,
        *,
        plan_id: int | None = None,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> None:
        """Refresh the entire proxy list (requires available on-demand refreshes)."""
        return self._client.request_none(
            _refresh_spec(plan_id=plan_id).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            )
        )

    def download(
        self,
        token: str,
        *,
        country_codes: Sequence[str] | None = None,
        proxy_protocol: str = "any",
        authentication_method: Literal["username", "sourceip"] = "username",
        endpoint_mode: Literal["direct", "backbone"] = "direct",
        search: str | None = None,
        plan_id: int | None = None,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> str:
        """Download the proxy list as text, one
        ``address:port:username:password`` record per line.

        ``token`` is the ``proxy_list_download_token`` from the proxy config
        API; the endpoint itself is unauthenticated.
        """
        return self._client.request_text(
            _download_spec(
                token,
                country_codes=country_codes,
                proxy_protocol=proxy_protocol,
                authentication_method=authentication_method,
                endpoint_mode=endpoint_mode,
                search=search,
                plan_id=plan_id,
            ).with_options(timeout, headers, max_retries, subuser_id, federated_user_id)
        )

    @staticmethod
    def download_url(
        token: str,
        *,
        country_codes: Sequence[str] | None = None,
        proxy_protocol: str = "any",
        authentication_method: Literal["username", "sourceip"] = "username",
        endpoint_mode: Literal["direct", "backbone"] = "direct",
        search: str | None = None,
        plan_id: int | None = None,
    ) -> str:
        """Build the unauthenticated proxy list download URL without calling it."""
        return build_proxy_list_download_url(
            token,
            country_codes=country_codes,
            proxy_protocol=proxy_protocol,
            authentication_method=authentication_method,
            endpoint_mode=endpoint_mode,
            search=search,
            plan_id=plan_id,
        )


class AsyncProxies(AsyncResource):
    async def list(
        self,
        *,
        mode: Literal["direct", "backbone"],
        plan_id: int | None = None,
        page: int | None = None,
        page_size: int | None = None,
        country_code__in: str | Sequence[str] | None = None,
        search: str | None = None,
        ordering: str | None = None,
        created_at: str | datetime | None = None,
        proxy_address: str | None = None,
        proxy_address__in: str | Sequence[str] | None = None,
        valid: bool | None = None,
        asn_number: str | None = None,
        asn_name: str | None = None,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> AsyncPage[Proxy]:
        """List proxies. ``mode`` is required and must be ``backbone`` for
        residential plans; most other filters do not work in backbone mode."""
        return await self._client.request_page(
            _list_spec(
                mode=mode,
                plan_id=plan_id,
                page=page,
                page_size=page_size,
                country_code__in=country_code__in,
                search=search,
                ordering=ordering,
                created_at=created_at,
                proxy_address=proxy_address,
                proxy_address__in=proxy_address__in,
                valid=valid,
                asn_number=asn_number,
                asn_name=asn_name,
            ).with_options(timeout, headers, max_retries, subuser_id, federated_user_id),
            Proxy,
        )

    async def refresh(
        self,
        *,
        plan_id: int | None = None,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> None:
        """Refresh the entire proxy list (requires available on-demand refreshes)."""
        return await self._client.request_none(
            _refresh_spec(plan_id=plan_id).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            )
        )

    async def download(
        self,
        token: str,
        *,
        country_codes: Sequence[str] | None = None,
        proxy_protocol: str = "any",
        authentication_method: Literal["username", "sourceip"] = "username",
        endpoint_mode: Literal["direct", "backbone"] = "direct",
        search: str | None = None,
        plan_id: int | None = None,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> str:
        """Download the proxy list as text, one
        ``address:port:username:password`` record per line.

        ``token`` is the ``proxy_list_download_token`` from the proxy config
        API; the endpoint itself is unauthenticated.
        """
        return await self._client.request_text(
            _download_spec(
                token,
                country_codes=country_codes,
                proxy_protocol=proxy_protocol,
                authentication_method=authentication_method,
                endpoint_mode=endpoint_mode,
                search=search,
                plan_id=plan_id,
            ).with_options(timeout, headers, max_retries, subuser_id, federated_user_id)
        )

    @staticmethod
    def download_url(
        token: str,
        *,
        country_codes: Sequence[str] | None = None,
        proxy_protocol: str = "any",
        authentication_method: Literal["username", "sourceip"] = "username",
        endpoint_mode: Literal["direct", "backbone"] = "direct",
        search: str | None = None,
        plan_id: int | None = None,
    ) -> str:
        """Build the unauthenticated proxy list download URL without calling it."""
        return build_proxy_list_download_url(
            token,
            country_codes=country_codes,
            proxy_protocol=proxy_protocol,
            authentication_method=authentication_method,
            endpoint_mode=endpoint_mode,
            search=search,
            plan_id=plan_id,
        )
