"""The invoice resource (`client.invoices`)."""

from __future__ import annotations

from collections.abc import Mapping

from webshare._http import RequestSpec
from webshare._requester import AsyncResource, SyncResource


def _download_spec(*, subscription_transaction_id: int | str) -> RequestSpec:
    # Note: this path has no trailing slash, unlike most endpoints.
    return RequestSpec(
        method="GET",
        path="/api/v2/invoices/download",
        query={"subscription_transaction_id": subscription_transaction_id},
    )


class Invoices(SyncResource):
    def download(
        self,
        *,
        subscription_transaction_id: int | str,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> bytes:
        """Download an invoice as PDF bytes.

        ``subscription_transaction_id`` accepts the ``Transaction.id`` integer
        directly (sent as a string query parameter either way).
        """
        return self._client.request_bytes(
            _download_spec(subscription_transaction_id=subscription_transaction_id).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            )
        )


class AsyncInvoices(AsyncResource):
    async def download(
        self,
        *,
        subscription_transaction_id: int | str,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> bytes:
        """Download an invoice as PDF bytes.

        ``subscription_transaction_id`` accepts the ``Transaction.id`` integer
        directly (sent as a string query parameter either way).
        """
        return await self._client.request_bytes(
            _download_spec(subscription_transaction_id=subscription_transaction_id).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            )
        )
