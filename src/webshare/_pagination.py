"""Page containers returned by ``list`` methods.

A page exposes the raw envelope (``results``, ``count``, ``next``,
``previous``) and iterating the page object yields items across *all* pages by
following the envelope ``next`` URL verbatim. Both the ``page``/``page_size``
and the ``starting_after`` server pagination variants use these types.
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Awaitable, Iterator
from typing import Generic, Protocol, TypeVar

from webshare._http import RequestSpec

T = TypeVar("T")


class _SyncPageFetcher(Protocol):
    def request_page(self, spec: RequestSpec, item_cls: type[T]) -> SyncPage[T]: ...


class _AsyncPageFetcher(Protocol):
    def request_page(self, spec: RequestSpec, item_cls: type[T]) -> Awaitable[AsyncPage[T]]: ...


class SyncPage(Generic[T]):
    """One page of results from the synchronous client."""

    def __init__(
        self,
        *,
        results: list[T],
        count: int | None,
        next: str | None,
        previous: str | None,
        client: _SyncPageFetcher,
        item_cls: type[T],
        spec: RequestSpec,
    ) -> None:
        self.results = results
        self.count = count
        self.next = next
        self.previous = previous
        self._client = client
        self._item_cls = item_cls
        self._spec = spec

    def next_page(self) -> SyncPage[T] | None:
        """Fetch the next page, or ``None`` when this is the last page."""
        if not self.next:
            return None
        return self._client.request_page(self._spec.for_url(self.next), self._item_cls)

    def __iter__(self) -> Iterator[T]:
        """Iterate over all items across every page."""
        page: SyncPage[T] | None = self
        while page is not None:
            yield from page.results
            page = page.next_page()

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(results={self.results!r}, count={self.count!r}, "
            f"next={self.next!r}, previous={self.previous!r})"
        )


class AsyncPage(Generic[T]):
    """One page of results from the asynchronous client."""

    def __init__(
        self,
        *,
        results: list[T],
        count: int | None,
        next: str | None,
        previous: str | None,
        client: _AsyncPageFetcher,
        item_cls: type[T],
        spec: RequestSpec,
    ) -> None:
        self.results = results
        self.count = count
        self.next = next
        self.previous = previous
        self._client = client
        self._item_cls = item_cls
        self._spec = spec

    async def next_page(self) -> AsyncPage[T] | None:
        """Fetch the next page, or ``None`` when this is the last page."""
        if not self.next:
            return None
        return await self._client.request_page(self._spec.for_url(self.next), self._item_cls)

    async def __aiter__(self) -> AsyncIterator[T]:
        """Iterate over all items across every page."""
        page: AsyncPage[T] | None = self
        while page is not None:
            for item in page.results:
                yield item
            page = await page.next_page()

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(results={self.results!r}, count={self.count!r}, "
            f"next={self.next!r}, previous={self.previous!r})"
        )
