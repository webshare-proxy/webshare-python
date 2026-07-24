"""The proxy configuration resource (`client.proxy_config`).

Reads live on v3 (``/api/v3/proxy/config``, no trailing slash, ``plan_id``
required) while writes live on v2 (``PATCH /api/v2/proxy/config/``) and return
the full config object.
"""

from __future__ import annotations

from collections.abc import Mapping

from .._http import RequestSpec, drop_json_nulls
from .._requester import AsyncResource, SyncResource
from ..types.proxy import ProxyConfig, ProxyListConfig, ProxyListStats, ProxyListStatus


def _get_spec(*, plan_id: int) -> RequestSpec:
    return RequestSpec(method="GET", path="/api/v3/proxy/config", query={"plan_id": plan_id})


def _get_stats_spec(*, plan_id: int) -> RequestSpec:
    return RequestSpec(method="GET", path="/api/v3/proxy/list/stats", query={"plan_id": plan_id})


def _get_status_spec(*, plan_id: int) -> RequestSpec:
    return RequestSpec(method="GET", path="/api/v3/proxy/list/status", query={"plan_id": plan_id})


def _update_spec(
    *,
    plan_id: int | None,
    username: str | None,
    password: str | None,
    request_timeout: int | None,
    request_idle_timeout: int | None,
    ip_authorization_country_codes: list[str] | None,
    ip_authorization_city: str | None,
    ip_authorization_asn: str | None,
    auto_replace_invalid_proxies: bool | None,
    auto_replace_low_country_confidence_proxies: bool | None,
    auto_replace_out_of_rotation_proxies: bool | None,
    auto_replace_failed_site_check_proxies: bool | None,
) -> RequestSpec:
    return RequestSpec(
        method="PATCH",
        path="/api/v2/proxy/config/",
        query={"plan_id": plan_id},
        json_body=drop_json_nulls(
            {
                "username": username,
                "password": password,
                "request_timeout": request_timeout,
                "request_idle_timeout": request_idle_timeout,
                "ip_authorization_country_codes": ip_authorization_country_codes,
                "ip_authorization_city": ip_authorization_city,
                "ip_authorization_asn": ip_authorization_asn,
                "auto_replace_invalid_proxies": auto_replace_invalid_proxies,
                "auto_replace_low_country_confidence_proxies": auto_replace_low_country_confidence_proxies,
                "auto_replace_out_of_rotation_proxies": auto_replace_out_of_rotation_proxies,
                "auto_replace_failed_site_check_proxies": auto_replace_failed_site_check_proxies,
            }
        ),
    )


def _allocate_spec(*, new_countries: Mapping[str, int], plan_id: int | None) -> RequestSpec:
    return RequestSpec(
        method="POST",
        path="/api/v2/proxy/config/allocate_unallocated_countries/",
        query={"plan_id": plan_id},
        json_body={"new_countries": dict(new_countries)},
    )


class ProxyConfigResource(SyncResource):
    def get(
        self,
        *,
        plan_id: int,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> ProxyListConfig:
        """Get the proxy config (v3). ``plan_id`` is required."""
        return self._client.request_model(
            _get_spec(plan_id=plan_id).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            ProxyListConfig,
        )

    def get_stats(
        self,
        *,
        plan_id: int,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> ProxyListStats:
        """Get the proxy list composition stats (v3). ``plan_id`` is required."""
        return self._client.request_model(
            _get_stats_spec(plan_id=plan_id).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            ProxyListStats,
        )

    def get_status(
        self,
        *,
        plan_id: int,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> ProxyListStatus:
        """Get the proxy list status (v3). ``plan_id`` is required."""
        return self._client.request_model(
            _get_status_spec(plan_id=plan_id).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            ProxyListStatus,
        )

    def update(
        self,
        *,
        plan_id: int | None = None,
        username: str | None = None,
        password: str | None = None,
        request_timeout: int | None = None,
        request_idle_timeout: int | None = None,
        ip_authorization_country_codes: list[str] | None = None,
        ip_authorization_city: str | None = None,
        ip_authorization_asn: str | None = None,
        auto_replace_invalid_proxies: bool | None = None,
        auto_replace_low_country_confidence_proxies: bool | None = None,
        auto_replace_out_of_rotation_proxies: bool | None = None,
        auto_replace_failed_site_check_proxies: bool | None = None,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> ProxyConfig:
        """Partially update the proxy config (v2); returns the full config object."""
        return self._client.request_model(
            _update_spec(
                plan_id=plan_id,
                username=username,
                password=password,
                request_timeout=request_timeout,
                request_idle_timeout=request_idle_timeout,
                ip_authorization_country_codes=ip_authorization_country_codes,
                ip_authorization_city=ip_authorization_city,
                ip_authorization_asn=ip_authorization_asn,
                auto_replace_invalid_proxies=auto_replace_invalid_proxies,
                auto_replace_low_country_confidence_proxies=auto_replace_low_country_confidence_proxies,
                auto_replace_out_of_rotation_proxies=auto_replace_out_of_rotation_proxies,
                auto_replace_failed_site_check_proxies=auto_replace_failed_site_check_proxies,
            ).with_options(timeout, headers, max_retries, subuser_id, federated_user_id),
            ProxyConfig,
        )

    def allocate_unallocated_countries(
        self,
        *,
        new_countries: Mapping[str, int],
        plan_id: int | None = None,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> ProxyConfig:
        """Allocate proxies in ``unallocated_countries``; the ``new_countries``
        totals must exactly match the number of unallocated proxies."""
        return self._client.request_model(
            _allocate_spec(new_countries=new_countries, plan_id=plan_id).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            ProxyConfig,
        )


class AsyncProxyConfigResource(AsyncResource):
    async def get(
        self,
        *,
        plan_id: int,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> ProxyListConfig:
        """Get the proxy config (v3). ``plan_id`` is required."""
        return await self._client.request_model(
            _get_spec(plan_id=plan_id).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            ProxyListConfig,
        )

    async def get_stats(
        self,
        *,
        plan_id: int,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> ProxyListStats:
        """Get the proxy list composition stats (v3). ``plan_id`` is required."""
        return await self._client.request_model(
            _get_stats_spec(plan_id=plan_id).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            ProxyListStats,
        )

    async def get_status(
        self,
        *,
        plan_id: int,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> ProxyListStatus:
        """Get the proxy list status (v3). ``plan_id`` is required."""
        return await self._client.request_model(
            _get_status_spec(plan_id=plan_id).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            ProxyListStatus,
        )

    async def update(
        self,
        *,
        plan_id: int | None = None,
        username: str | None = None,
        password: str | None = None,
        request_timeout: int | None = None,
        request_idle_timeout: int | None = None,
        ip_authorization_country_codes: list[str] | None = None,
        ip_authorization_city: str | None = None,
        ip_authorization_asn: str | None = None,
        auto_replace_invalid_proxies: bool | None = None,
        auto_replace_low_country_confidence_proxies: bool | None = None,
        auto_replace_out_of_rotation_proxies: bool | None = None,
        auto_replace_failed_site_check_proxies: bool | None = None,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> ProxyConfig:
        """Partially update the proxy config (v2); returns the full config object."""
        return await self._client.request_model(
            _update_spec(
                plan_id=plan_id,
                username=username,
                password=password,
                request_timeout=request_timeout,
                request_idle_timeout=request_idle_timeout,
                ip_authorization_country_codes=ip_authorization_country_codes,
                ip_authorization_city=ip_authorization_city,
                ip_authorization_asn=ip_authorization_asn,
                auto_replace_invalid_proxies=auto_replace_invalid_proxies,
                auto_replace_low_country_confidence_proxies=auto_replace_low_country_confidence_proxies,
                auto_replace_out_of_rotation_proxies=auto_replace_out_of_rotation_proxies,
                auto_replace_failed_site_check_proxies=auto_replace_failed_site_check_proxies,
            ).with_options(timeout, headers, max_retries, subuser_id, federated_user_id),
            ProxyConfig,
        )

    async def allocate_unallocated_countries(
        self,
        *,
        new_countries: Mapping[str, int],
        plan_id: int | None = None,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> ProxyConfig:
        """Allocate proxies in ``unallocated_countries``; the ``new_countries``
        totals must exactly match the number of unallocated proxies."""
        return await self._client.request_model(
            _allocate_spec(new_countries=new_countries, plan_id=plan_id).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            ProxyConfig,
        )
