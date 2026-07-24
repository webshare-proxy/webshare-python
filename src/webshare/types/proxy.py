"""Models for the proxy list, config, replacement, stats and sub-user APIs."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

__all__ = [
    "AggregateStats",
    "DownloadToken",
    "ErrorReason",
    "IPAuthorization",
    "Proxy",
    "ProxyActivity",
    "ProxyConfig",
    "ProxyListConfig",
    "ProxyListStats",
    "ProxyListStatus",
    "ProxyReplacement",
    "ProxyStat",
    "ReplacedProxy",
    "Subuser",
    "WhatsMyIP",
]


@dataclass
class Proxy:
    """A proxy list entry. Note: proxy ``id`` is a string (e.g. ``"d-10513"``)."""

    id: str
    username: str | None
    password: str | None
    proxy_address: str | None
    port: int | None
    valid: bool | None
    last_verification: datetime | None
    country_code: str | None
    city_name: str | None
    # Observed on the live API but undocumented.
    asn_name: str | None
    asn_number: int | None
    high_country_confidence: bool | None
    created_at: datetime | None


@dataclass
class ProxyListConfig:
    """The proxy config subset returned by ``GET /api/v3/proxy/config``."""

    request_timeout: int | None
    request_idle_timeout: int | None
    ip_authorization_country_codes: list[str] | None
    ip_authorization_city: str | None
    # ip_authorization_state / ip_authorization_postalcode are referenced in
    # the docs' mutual-exclusion prose and observed on the live API.
    ip_authorization_state: str | None
    ip_authorization_postalcode: str | None
    ip_authorization_asn: str | None
    auto_replace_invalid_proxies: bool | None
    auto_replace_low_country_confidence_proxies: bool | None
    auto_replace_out_of_rotation_proxies: bool | None
    auto_replace_failed_site_check_proxies: bool | None
    proxy_list_download_token: str | None


@dataclass
class ProxyConfig:
    """The full proxy config object returned by the v2 update/allocate endpoints.

    ``asns``/``available_asns`` map ASN number to a ``(asn_name, count)`` tuple.
    """

    id: int
    state: str | None
    countries: dict[str, int] | None
    available_countries: dict[str, int] | None
    unallocated_countries: dict[str, int] | None
    ip_ranges_24: dict[str, int] | None
    ip_ranges_16: dict[str, int] | None
    ip_ranges_8: dict[str, int] | None
    available_ip_ranges_24: dict[str, int] | None
    available_ip_ranges_16: dict[str, int] | None
    available_ip_ranges_8: dict[str, int] | None
    asns: dict[str, tuple[str, int]] | None
    available_asns: dict[str, tuple[str, int]] | None
    username: str | None
    password: str | None
    request_timeout: int | None
    request_idle_timeout: int | None
    ip_authorization_country_codes: list[str] | None
    ip_authorization_city: str | None
    # ip_authorization_state / ip_authorization_postalcode are referenced in
    # the docs' mutual-exclusion prose and observed on the live API.
    ip_authorization_state: str | None
    ip_authorization_postalcode: str | None
    ip_authorization_asn: str | None
    auto_replace_invalid_proxies: bool | None
    auto_replace_low_country_confidence_proxies: bool | None
    auto_replace_out_of_rotation_proxies: bool | None
    auto_replace_failed_site_check_proxies: bool | None
    proxy_list_download_token: str | None
    is_proxy_used: bool | None
    created_at: datetime | None
    updated_at: datetime | None


@dataclass
class ProxyListStats:
    """Proxy list composition returned by ``GET /api/v3/proxy/list/stats``."""

    available_countries: dict[str, int] | None
    ip_ranges_24: dict[str, int] | None
    ip_ranges_16: dict[str, int] | None
    ip_ranges_8: dict[str, int] | None
    available_ip_ranges_24: dict[str, int] | None
    available_ip_ranges_16: dict[str, int] | None
    available_ip_ranges_8: dict[str, int] | None
    asns: dict[str, tuple[str, int]] | None
    available_asns: dict[str, tuple[str, int]] | None


@dataclass
class ProxyListStatus:
    """Proxy list status returned by ``GET /api/v3/proxy/list/status``."""

    state: str | None
    countries: dict[str, int] | None
    unallocated_countries: dict[str, int] | None
    username: str | None
    password: str | None
    is_proxy_used: bool | None


@dataclass
class ProxyReplacement:
    """An asynchronous proxy replacement request.

    Poll ``client.proxy_replacements.get`` until ``state`` is ``completed``
    (or ``failed``, then inspect ``error_code``/``error``).
    """

    id: int
    to_replace: dict[str, Any] | None
    replace_with: list[dict[str, Any]] | None
    dry_run: bool | None
    state: str | None
    proxies_removed: int | None
    proxies_added: int | None
    reason: str | None
    error_code: str | None
    error: str | None
    created_at: datetime | None
    dry_run_completed_at: datetime | None
    completed_at: datetime | None


@dataclass
class ReplacedProxy:
    id: int
    reason: str | None
    proxy: str | None
    proxy_port: int | None
    proxy_country_code: str | None
    replaced_with: str | None
    replaced_with_port: int | None
    replaced_with_country_code: str | None
    created_at: datetime | None


@dataclass
class ErrorReason:
    reason: str | None
    type: str | None
    how_to_fix: str | None
    http_status: int | None
    count: int | None


@dataclass
class ProxyStat:
    """An hourly proxy usage stat entry."""

    timestamp: datetime | None
    is_projected: bool | None
    bandwidth_total: int | None
    bandwidth_average: int | None
    requests_total: int | None
    requests_successful: int | None
    requests_failed: int | None
    error_reasons: list[ErrorReason] | None
    countries_used: dict[str, int] | None
    number_of_proxies_used: int | None
    protocols_used: dict[str, int] | None
    average_concurrency: float | None
    average_rps: float | None
    last_request_sent_at: datetime | None


@dataclass
class AggregateStats:
    """Aggregated proxy usage stats for a period."""

    bandwidth_projected: int | None
    bandwidth_total: int | None
    bandwidth_average: int | None
    requests_total: int | None
    requests_successful: int | None
    requests_failed: int | None
    error_reasons: list[ErrorReason] | None
    countries_used: dict[str, int] | None
    number_of_proxies_used: int | None
    protocols_used: dict[str, int] | None
    average_concurrency: float | None
    average_rps: float | None
    last_request_sent_at: datetime | None


@dataclass
class ProxyActivity:
    """A single authenticated proxy request record."""

    timestamp: datetime | None
    protocol: str | None
    request_duration: float | None
    handshake_duration: float | None
    tunnel_duration: float | None
    error_reason: str | None
    error_reason_how_to_fix: str | None
    auth_username: str | None
    proxy_address: str | None
    bytes: float | None
    client_address: str | None
    ip_address: str | None
    hostname: str | None
    domain: str | None
    port: float | None
    proxy_port: float | None
    listen_address: str | None
    listen_port: float | None


@dataclass
class DownloadToken:
    """A download token for the replaced-proxy / activity download endpoints."""

    id: int
    key: str | None
    scope: str | None
    expire_at: datetime | None


@dataclass
class IPAuthorization:
    id: int
    ip_address: str | None
    created_at: datetime | None
    last_used_at: datetime | None


@dataclass
class WhatsMyIP:
    ip_address: str | None


@dataclass
class Subuser:
    id: int
    label: str | None
    proxy_countries: dict[str, int] | None
    proxy_limit: float | None
    max_thread_count: int | None
    aggregate_stats: AggregateStats | None
    created_at: datetime | None
    updated_at: datetime | None
    bandwidth_use_start_date: datetime | None
    bandwidth_use_end_date: datetime | None
