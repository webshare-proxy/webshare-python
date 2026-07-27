"""The replaced proxy resource (`client.replaced_proxies`)."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Literal

from webshare._http import RequestSpec
from webshare._pagination import AsyncPage, SyncPage
from webshare._requester import AsyncResource, SyncResource
from webshare.types.proxy import ReplacedProxy


def _list_spec(
    *,
    proxy_list_replacement: int | None,
    plan_id: int | None,
    page: int | None,
    page_size: int | None,
) -> RequestSpec:
    return RequestSpec(
        method="GET",
        path="/api/v2/proxy/list/replaced/",
        query={
            "proxy_list_replacement": proxy_list_replacement,
            "plan_id": plan_id,
            "page": page,
            "page_size": page_size,
        },
    )


def _download_spec(
    *,
    download_token: str,
    country_codes: Sequence[str] | None,
    authentication_type: Literal["username", "sourceip"] | None,
    mode: Literal["backbone", "direct"] | None,
    search: str | None,
    proxy_list_replacement: int | None,
    proxy_protocol: str | None,
) -> RequestSpec:
    return RequestSpec(
        method="GET",
        path="/api/v2/proxy/list/replaced/download/",
        query={
            "download_token": download_token,
            "country_codes": "-".join(country_codes) if country_codes else None,
            "authentication_type": authentication_type,
            "mode": mode,
            "search": search,
            "proxy_list_replacement": proxy_list_replacement,
            "proxy_protocol": proxy_protocol,
        },
        auth="none",
    )


class ReplacedProxies(SyncResource):
    def list(
        self,
        *,
        proxy_list_replacement: int | None = None,
        plan_id: int | None = None,
        page: int | None = None,
        page_size: int | None = None,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> SyncPage[ReplacedProxy]:
        """List replaced proxies."""
        return self._client.request_page(
            _list_spec(
                proxy_list_replacement=proxy_list_replacement,
                plan_id=plan_id,
                page=page,
                page_size=page_size,
            ).with_options(timeout, headers, max_retries, subuser_id, federated_user_id),
            ReplacedProxy,
        )

    def download(
        self,
        *,
        download_token: str,
        country_codes: Sequence[str] | None = None,
        authentication_type: Literal["username", "sourceip"] | None = None,
        mode: Literal["backbone", "direct"] | None = None,
        search: str | None = None,
        proxy_list_replacement: int | None = None,
        proxy_protocol: str | None = "any",
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> str:
        """Download the replaced proxy list as text; each line is
        ``new_address:new_port:username:password:replaced_address``.

        ``download_token`` comes from ``client.download_tokens.get`` with scope
        ``replaced_proxy``; the endpoint itself is unauthenticated.
        """
        return self._client.request_text(
            _download_spec(
                download_token=download_token,
                country_codes=country_codes,
                authentication_type=authentication_type,
                mode=mode,
                search=search,
                proxy_list_replacement=proxy_list_replacement,
                proxy_protocol=proxy_protocol,
            ).with_options(timeout, headers, max_retries, subuser_id, federated_user_id)
        )


class AsyncReplacedProxies(AsyncResource):
    async def list(
        self,
        *,
        proxy_list_replacement: int | None = None,
        plan_id: int | None = None,
        page: int | None = None,
        page_size: int | None = None,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> AsyncPage[ReplacedProxy]:
        """List replaced proxies."""
        return await self._client.request_page(
            _list_spec(
                proxy_list_replacement=proxy_list_replacement,
                plan_id=plan_id,
                page=page,
                page_size=page_size,
            ).with_options(timeout, headers, max_retries, subuser_id, federated_user_id),
            ReplacedProxy,
        )

    async def download(
        self,
        *,
        download_token: str,
        country_codes: Sequence[str] | None = None,
        authentication_type: Literal["username", "sourceip"] | None = None,
        mode: Literal["backbone", "direct"] | None = None,
        search: str | None = None,
        proxy_list_replacement: int | None = None,
        proxy_protocol: str | None = "any",
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> str:
        """Download the replaced proxy list as text; each line is
        ``new_address:new_port:username:password:replaced_address``."""
        return await self._client.request_text(
            _download_spec(
                download_token=download_token,
                country_codes=country_codes,
                authentication_type=authentication_type,
                mode=mode,
                search=search,
                proxy_list_replacement=proxy_list_replacement,
                proxy_protocol=proxy_protocol,
            ).with_options(timeout, headers, max_retries, subuser_id, federated_user_id)
        )
