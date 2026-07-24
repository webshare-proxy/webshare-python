"""The proxy usage stats resource (`client.stats`)."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime

from .._http import RequestSpec
from .._requester import AsyncResource, SyncResource
from ..types.proxy import AggregateStats, ProxyStat


def _list_spec(
    *,
    timestamp__lte: str | datetime | None,
    timestamp__gte: str | datetime | None,
    plan_id: int | None,
) -> RequestSpec:
    return RequestSpec(
        method="GET",
        path="/api/v2/stats/",
        query={
            "timestamp__lte": timestamp__lte,
            "timestamp__gte": timestamp__gte,
            "plan_id": plan_id,
        },
    )


def _aggregate_spec(
    *,
    timestamp__lte: str | datetime | None,
    timestamp__gte: str | datetime | None,
    plan_id: int | None,
) -> RequestSpec:
    return RequestSpec(
        method="GET",
        path="/api/v2/stats/aggregate/",
        query={
            "timestamp__lte": timestamp__lte,
            "timestamp__gte": timestamp__gte,
            "plan_id": plan_id,
        },
    )


class Stats(SyncResource):
    def list(
        self,
        *,
        timestamp__lte: str | datetime | None = None,
        timestamp__gte: str | datetime | None = None,
        plan_id: int | None = None,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> list[ProxyStat]:
        """List hourly proxy stats. This endpoint is NOT paginated; it returns
        a bare array. Request a future ``timestamp__lte`` for projected stats."""
        return self._client.request_model_list(
            _list_spec(
                timestamp__lte=timestamp__lte,
                timestamp__gte=timestamp__gte,
                plan_id=plan_id,
            ).with_options(timeout, headers, max_retries, subuser_id, federated_user_id),
            ProxyStat,
        )

    def aggregate(
        self,
        *,
        timestamp__lte: str | datetime | None = None,
        timestamp__gte: str | datetime | None = None,
        plan_id: int | None = None,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> AggregateStats:
        """Aggregate the proxy stats for the given period."""
        return self._client.request_model(
            _aggregate_spec(
                timestamp__lte=timestamp__lte,
                timestamp__gte=timestamp__gte,
                plan_id=plan_id,
            ).with_options(timeout, headers, max_retries, subuser_id, federated_user_id),
            AggregateStats,
        )


class AsyncStats(AsyncResource):
    async def list(
        self,
        *,
        timestamp__lte: str | datetime | None = None,
        timestamp__gte: str | datetime | None = None,
        plan_id: int | None = None,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> list[ProxyStat]:
        """List hourly proxy stats (bare array; NOT paginated)."""
        return await self._client.request_model_list(
            _list_spec(
                timestamp__lte=timestamp__lte,
                timestamp__gte=timestamp__gte,
                plan_id=plan_id,
            ).with_options(timeout, headers, max_retries, subuser_id, federated_user_id),
            ProxyStat,
        )

    async def aggregate(
        self,
        *,
        timestamp__lte: str | datetime | None = None,
        timestamp__gte: str | datetime | None = None,
        plan_id: int | None = None,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> AggregateStats:
        """Aggregate the proxy stats for the given period."""
        return await self._client.request_model(
            _aggregate_spec(
                timestamp__lte=timestamp__lte,
                timestamp__gte=timestamp__gte,
                plan_id=plan_id,
            ).with_options(timeout, headers, max_retries, subuser_id, federated_user_id),
            AggregateStats,
        )
