"""Requester protocols implemented by the sync and async clients.

Resource classes depend only on these protocols, keeping resources decoupled
from the concrete transports.
"""

from __future__ import annotations

from typing import Any, Protocol, TypeVar

from ._http import RequestSpec
from ._pagination import AsyncPage, SyncPage

ModelT = TypeVar("ModelT")


class SyncRequester(Protocol):
    def request_none(self, spec: RequestSpec) -> None: ...

    def request_json(self, spec: RequestSpec) -> Any: ...

    def request_model(self, spec: RequestSpec, cls: type[ModelT]) -> ModelT: ...

    def request_model_list(self, spec: RequestSpec, cls: type[ModelT]) -> list[ModelT]: ...

    def request_model_dict(self, spec: RequestSpec, cls: type[ModelT]) -> dict[str, ModelT]: ...

    def request_text(self, spec: RequestSpec) -> str: ...

    def request_bytes(self, spec: RequestSpec) -> bytes: ...

    def request_page(self, spec: RequestSpec, item_cls: type[ModelT]) -> SyncPage[ModelT]: ...


class AsyncRequester(Protocol):
    async def request_none(self, spec: RequestSpec) -> None: ...

    async def request_json(self, spec: RequestSpec) -> Any: ...

    async def request_model(self, spec: RequestSpec, cls: type[ModelT]) -> ModelT: ...

    async def request_model_list(self, spec: RequestSpec, cls: type[ModelT]) -> list[ModelT]: ...

    async def request_model_dict(
        self, spec: RequestSpec, cls: type[ModelT]
    ) -> dict[str, ModelT]: ...

    async def request_text(self, spec: RequestSpec) -> str: ...

    async def request_bytes(self, spec: RequestSpec) -> bytes: ...

    async def request_page(
        self, spec: RequestSpec, item_cls: type[ModelT]
    ) -> AsyncPage[ModelT]: ...


class SyncResource:
    """Base class for synchronous resource groups."""

    def __init__(self, client: SyncRequester) -> None:
        self._client = client


class AsyncResource:
    """Base class for asynchronous resource groups."""

    def __init__(self, client: AsyncRequester) -> None:
        self._client = client
