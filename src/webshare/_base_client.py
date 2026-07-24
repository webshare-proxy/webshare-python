"""Configuration and decode logic shared by the sync and async clients."""

from __future__ import annotations

import os
from collections.abc import Mapping
from typing import Any, TypeVar
from urllib.parse import urljoin

import httpx

from ._exceptions import WebshareError
from ._http import (
    DEFAULT_BASE_URL,
    DEFAULT_TIMEOUT,
    RequestSpec,
    build_headers,
    encode_query,
    is_idempotent,
    join_url,
    make_api_error,
    prepare_files,
)
from ._models import decode
from ._version import __version__

API_KEY_ENV_VAR = "WEBSHARE_API_KEY"

ModelT = TypeVar("ModelT")

_MISSING_CREDENTIALS_MESSAGE = (
    "No API key provided. Pass api_key=..., set the WEBSHARE_API_KEY environment "
    "variable, or pass credentials_provider=... to the client constructor."
)


def resolve_static_api_key(api_key: str | None) -> str | None:
    """Resolve an explicit API key, falling back to ``WEBSHARE_API_KEY``."""
    if api_key is not None:
        return api_key
    return os.environ.get(API_KEY_ENV_VAR)


def missing_credentials_error() -> WebshareError:
    return WebshareError(_MISSING_CREDENTIALS_MESSAGE)


class BaseClient:
    """Common configuration shared by ``Webshare`` and ``AsyncWebshare``."""

    def __init__(
        self,
        *,
        base_url: str | None,
        timeout: float | None,
        max_retries: int,
        default_headers: Mapping[str, str] | None,
        subuser_id: int | str | None,
        federated_user_id: int | str | None,
        retry_non_idempotent: bool,
    ) -> None:
        self.base_url = (base_url or DEFAULT_BASE_URL).rstrip("/")
        self.timeout = DEFAULT_TIMEOUT if timeout is None else timeout
        self.max_retries = max_retries
        self.default_headers = dict(default_headers) if default_headers else None
        self.subuser_id = subuser_id
        self.federated_user_id = federated_user_id
        self.retry_non_idempotent = retry_non_idempotent
        self.user_agent = f"webshare-python/{__version__}"

    # -- request assembly ------------------------------------------------

    def _request_url(self, spec: RequestSpec) -> str:
        if spec.absolute_url is not None:
            # Pagination `next` URLs are followed verbatim; resolve relative
            # URLs against the configured base URL.
            return urljoin(self.base_url + "/", spec.absolute_url)
        return join_url(self.base_url, spec.path)

    def _request_kwargs(self, spec: RequestSpec, token: str | None) -> dict[str, Any]:
        options = spec.options
        headers = build_headers(
            token=token,
            user_agent=self.user_agent,
            default_headers=self.default_headers,
            client_subuser_id=self.subuser_id,
            client_federated_user_id=self.federated_user_id,
            options=options,
            has_json_body=spec.json_body is not None,
        )
        kwargs: dict[str, Any] = {
            "headers": headers,
            "timeout": options.timeout if options.timeout is not None else self.timeout,
        }
        if spec.absolute_url is None:
            query = encode_query(spec.query)
            if query:
                kwargs["params"] = query
        if spec.json_body is not None:
            kwargs["json"] = spec.json_body
        if spec.multipart_data is not None or spec.multipart_files is not None:
            files = prepare_files(spec.multipart_files) if spec.multipart_files else []
            if files:
                kwargs["files"] = files
                if spec.multipart_data:
                    kwargs["data"] = dict(spec.multipart_data)
            else:
                # No file parts: still force multipart/form-data encoding by
                # sending the text fields as filename-less parts.
                kwargs["files"] = [
                    (key, (None, value)) for key, value in (spec.multipart_data or {}).items()
                ]
        return kwargs

    def _spec_max_retries(self, spec: RequestSpec) -> int:
        if spec.options.max_retries is not None:
            return spec.options.max_retries
        return self.max_retries

    def _retry_allowed(self, spec: RequestSpec) -> bool:
        return is_idempotent(spec.method) or self.retry_non_idempotent

    # -- response handling -----------------------------------------------

    @staticmethod
    def _raise_for_status(response: httpx.Response) -> None:
        if response.status_code >= 400:
            raise make_api_error(
                status_code=response.status_code,
                body_text=response.text,
                request_id=response.headers.get("X-Request-ID"),
            )

    @staticmethod
    def _json(response: httpx.Response) -> Any:
        if response.status_code == 204 or not response.content:
            return None
        return response.json()

    @staticmethod
    def _decode_model(data: Any, cls: type[ModelT]) -> ModelT:
        return decode(cls, data)

    @staticmethod
    def _decode_model_list(data: Any, cls: type[ModelT]) -> list[ModelT]:
        if not isinstance(data, list):
            raise TypeError(f"Expected a JSON array of {cls.__name__} objects")
        return [decode(cls, item) for item in data]

    @staticmethod
    def _decode_model_dict(data: Any, cls: type[ModelT]) -> dict[str, ModelT]:
        if not isinstance(data, dict):
            raise TypeError(f"Expected a JSON object mapping keys to {cls.__name__} objects")
        return {key: decode(cls, value) for key, value in data.items()}

    @staticmethod
    def _parse_envelope(
        data: Any,
    ) -> tuple[list[Any], int | None, str | None, str | None]:
        if not isinstance(data, dict):
            raise TypeError("Expected a paginated envelope object")
        results = data.get("results")
        if not isinstance(results, list):
            results = []
        count = data.get("count")
        next_url = data.get("next")
        previous = data.get("previous")
        return (
            results,
            count if isinstance(count, int) else None,
            next_url if isinstance(next_url, str) else None,
            previous if isinstance(previous, str) else None,
        )
