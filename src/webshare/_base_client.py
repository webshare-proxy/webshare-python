"""Configuration and decode logic shared by the sync and async clients."""

from __future__ import annotations

import os
import platform
from collections.abc import Mapping
from typing import Any, TypeVar
from urllib.parse import urljoin

import httpx

from webshare._exceptions import ResponseDecodeError, WebshareError
from webshare._http import (
    DEFAULT_BASE_URL,
    DEFAULT_TIMEOUT,
    RequestSpec,
    build_headers,
    encode_query,
    is_idempotent,
    join_url,
    make_api_error,
    parse_retry_after,
    prepare_files,
    same_origin,
    truncate_text,
)
from webshare._models import decode
from webshare._version import __version__

API_KEY_ENV_VAR = "WEBSHARE_API_KEY"

ModelT = TypeVar("ModelT")


class _NotGiven:
    """Sentinel distinguishing an omitted ``timeout`` from an explicit
    ``timeout=None`` (which requests httpx's no-timeout / infinite-wait
    behavior)."""

    def __repr__(self) -> str:
        return "NOT_GIVEN"


NOT_GIVEN = _NotGiven()

_BODY_SNIPPET_CHARS = 2048

_MISSING_CREDENTIALS_MESSAGE = (
    "No API key provided. Pass api_key=..., set the WEBSHARE_API_KEY environment "
    "variable, or pass credentials_provider=... to the client constructor."
)

_CONFLICTING_CREDENTIALS_MESSAGE = (
    "Pass either api_key= or credentials_provider= to the client constructor, not "
    "both — credentials_provider would otherwise silently take precedence and the "
    "api_key would be ignored."
)

_AUTH_REQUIRED_MESSAGE = (
    "This operation requires authentication, but the client was constructed "
    "with unauthenticated=True. Construct the client with api_key=..., the "
    "WEBSHARE_API_KEY environment variable, or credentials_provider=... to "
    "call it."
)


def resolve_static_api_key(api_key: str | None) -> str | None:
    """Resolve an explicit API key, falling back to ``WEBSHARE_API_KEY``.

    Empty strings (explicit or from the environment) are treated as absent.
    """
    if api_key:
        return api_key
    return os.environ.get(API_KEY_ENV_VAR) or None


def missing_credentials_error() -> WebshareError:
    return WebshareError(_MISSING_CREDENTIALS_MESSAGE)


def conflicting_credentials_error() -> WebshareError:
    return WebshareError(_CONFLICTING_CREDENTIALS_MESSAGE)


def auth_required_error() -> WebshareError:
    return WebshareError(_AUTH_REQUIRED_MESSAGE)


def _body_snippet(response: httpx.Response) -> str:
    return truncate_text(response.text, _BODY_SNIPPET_CHARS)


class BaseClient:
    """Common configuration shared by ``Webshare`` and ``AsyncWebshare``."""

    def __init__(
        self,
        *,
        base_url: str | None,
        timeout: float | _NotGiven | None,
        max_retries: int,
        default_headers: Mapping[str, str] | None,
        subuser_id: int | str | None,
        federated_user_id: int | str | None,
        retry_non_idempotent: bool,
        source: str | None,
    ) -> None:
        self.base_url = (base_url or DEFAULT_BASE_URL).rstrip("/")
        self.timeout = DEFAULT_TIMEOUT if isinstance(timeout, _NotGiven) else timeout
        self.max_retries = max_retries
        self.default_headers = dict(default_headers) if default_headers else None
        self.subuser_id = subuser_id
        self.federated_user_id = federated_user_id
        self.retry_non_idempotent = retry_non_idempotent
        self.user_agent = f"webshare-python/{__version__}"
        # X-Webshare-Source identifies the caller for API-side tracking; the
        # `source` option replaces the whole value.
        self.source = source or (f"WebshareSDK/{__version__} (Python; {platform.python_version()})")
        # When the user injects an http_client without an explicit timeout,
        # the injected client's own timeout configuration is respected.
        self._defer_timeout_to_http_client = False

    # -- request assembly ------------------------------------------------

    def _request_url(self, spec: RequestSpec) -> str:
        if spec.absolute_url is not None:
            # Pagination `next` URLs are followed verbatim; resolve relative
            # URLs against the configured base URL, and refuse to follow
            # cross-origin URLs (the auth token must never leave the
            # configured origin).
            url = urljoin(self.base_url + "/", spec.absolute_url)
            if not same_origin(url, self.base_url):
                raise WebshareError(
                    f"Refusing to follow cross-origin URL {url!r}: it does not "
                    f"match the client base URL origin ({self.base_url!r})."
                )
            return url
        return join_url(self.base_url, spec.path)

    def _request_kwargs(self, spec: RequestSpec, token: str | None) -> dict[str, Any]:
        options = spec.options
        headers = build_headers(
            token=token,
            user_agent=self.user_agent,
            source=self.source,
            default_headers=self.default_headers,
            client_subuser_id=self.subuser_id,
            client_federated_user_id=self.federated_user_id,
            options=options,
            has_json_body=spec.json_body is not None,
        )
        if options.timeout is not None:
            timeout: Any = options.timeout
        elif self._defer_timeout_to_http_client:
            timeout = httpx.USE_CLIENT_DEFAULT
        else:
            timeout = self.timeout
        kwargs: dict[str, Any] = {"headers": headers, "timeout": timeout}
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
                retry_after=parse_retry_after(response.headers.get("Retry-After")),
            )

    @staticmethod
    def _json(response: httpx.Response) -> Any:
        if response.status_code == 204 or not response.content:
            return None
        try:
            return response.json()
        except ValueError as exc:
            raise ResponseDecodeError(
                f"Expected a JSON response body (HTTP {response.status_code})",
                status_code=response.status_code,
                body=_body_snippet(response),
            ) from exc

    @classmethod
    def _decode_model(cls, response: httpx.Response, model: type[ModelT]) -> ModelT:
        data = cls._json(response)
        if not isinstance(data, dict):
            raise ResponseDecodeError(
                f"Expected a JSON object for {model.__name__} (HTTP {response.status_code})",
                status_code=response.status_code,
                body=_body_snippet(response),
            )
        return decode(model, data)

    @classmethod
    def _decode_model_list(cls, response: httpx.Response, model: type[ModelT]) -> list[ModelT]:
        data = cls._json(response)
        if not isinstance(data, list) or not all(isinstance(item, dict) for item in data):
            raise ResponseDecodeError(
                f"Expected a JSON array of {model.__name__} objects (HTTP {response.status_code})",
                status_code=response.status_code,
                body=_body_snippet(response),
            )
        return [decode(model, item) for item in data]

    @classmethod
    def _decode_model_dict(cls, response: httpx.Response, model: type[ModelT]) -> dict[str, ModelT]:
        data = cls._json(response)
        if not isinstance(data, dict) or not all(
            isinstance(value, dict) for value in data.values()
        ):
            raise ResponseDecodeError(
                f"Expected a JSON object mapping keys to {model.__name__} objects "
                f"(HTTP {response.status_code})",
                status_code=response.status_code,
                body=_body_snippet(response),
            )
        return {key: decode(model, value) for key, value in data.items()}

    @classmethod
    def _parse_envelope(
        cls, response: httpx.Response
    ) -> tuple[list[Any], int | None, str | None, str | None]:
        data = cls._json(response)
        results = data.get("results") if isinstance(data, dict) else None
        if (
            not isinstance(data, dict)
            or not isinstance(results, list)
            or not all(isinstance(item, dict) for item in results)
        ):
            raise ResponseDecodeError(
                "Expected a pagination envelope with a `results` array "
                f"(HTTP {response.status_code})",
                status_code=response.status_code,
                body=_body_snippet(response),
            )
        count = data.get("count")
        next_url = data.get("next")
        previous = data.get("previous")
        return (
            results,
            count if isinstance(count, int) else None,
            next_url if isinstance(next_url, str) else None,
            previous if isinstance(previous, str) else None,
        )
