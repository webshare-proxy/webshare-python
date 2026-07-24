"""Shared, transport-agnostic HTTP plumbing.

Everything in this module is a pure function or a plain data holder: the sync
and async clients share this single code path for building requests, encoding
query strings, computing retry schedules and mapping error responses. Only the
transport (``httpx.Client`` vs ``httpx.AsyncClient``) differs between the two
clients.
"""

from __future__ import annotations

import json
import math
import os
import random
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import IO, Any, Literal
from urllib.parse import urlsplit

from ._exceptions import (
    APIError,
    AuthenticationError,
    BadRequestError,
    InternalServerError,
    NotFoundError,
    PermissionDeniedError,
    RateLimitError,
)

DEFAULT_BASE_URL = "https://proxy.webshare.io"
DEFAULT_TIMEOUT = 60.0
DEFAULT_MAX_RETRIES = 2

RETRY_STATUS_CODES = frozenset({408, 429, 500, 502, 503, 504})
IDEMPOTENT_METHODS = frozenset({"GET", "HEAD", "OPTIONS", "PUT", "DELETE"})

BACKOFF_BASE = 0.5
BACKOFF_CAP = 8.0
RETRY_AFTER_CAP = 60.0

# Error-body capture is capped; the human-facing detail is truncated further.
MAX_ERROR_BODY_BYTES = 1024 * 1024
MAX_DETAIL_CHARS = 2048

QueryValue = str | int | float | bool | datetime | Sequence[str] | None
FileInput = str | os.PathLike[str] | bytes | IO[bytes] | tuple[str, "bytes | IO[bytes]"]

AuthMode = Literal["required", "none"]


@dataclass(frozen=True)
class RequestOptions:
    """Per-request overrides accepted by every SDK method."""

    timeout: float | None = None
    headers: Mapping[str, str] | None = None
    max_retries: int | None = None
    subuser_id: int | str | None = None
    federated_user_id: int | str | None = None

    def is_empty(self) -> bool:
        return (
            self.timeout is None
            and self.headers is None
            and self.max_retries is None
            and self.subuser_id is None
            and self.federated_user_id is None
        )


@dataclass(frozen=True)
class RequestSpec:
    """A fully described API operation, independent of any transport."""

    method: str
    path: str
    query: Mapping[str, QueryValue] | None = None
    json_body: Any | None = None
    multipart_data: Mapping[str, str] | None = None
    multipart_files: Sequence[FileInput] | None = None
    auth: AuthMode = "required"
    absolute_url: str | None = None
    options: RequestOptions = field(default_factory=RequestOptions)

    def with_options(
        self,
        timeout: float | None,
        headers: Mapping[str, str] | None,
        max_retries: int | None,
        subuser_id: int | str | None,
        federated_user_id: int | str | None,
    ) -> RequestSpec:
        return replace(
            self,
            options=RequestOptions(
                timeout=timeout,
                headers=headers,
                max_retries=max_retries,
                subuser_id=subuser_id,
                federated_user_id=federated_user_id,
            ),
        )

    def for_url(self, url: str) -> RequestSpec:
        """A follow-up GET of ``url`` (used to follow pagination ``next`` links)."""
        return replace(
            self,
            method="GET",
            query=None,
            json_body=None,
            multipart_data=None,
            multipart_files=None,
            absolute_url=url,
        )


def encode_query(params: Mapping[str, QueryValue] | None) -> dict[str, str]:
    """Serialize query parameters.

    ``None`` values are omitted, booleans become ``true``/``false``, datetimes
    are ISO 8601 encoded and sequences are comma-joined (for ``__in`` filters).
    """
    out: dict[str, str] = {}
    if not params:
        return out
    for key, value in params.items():
        if value is None:
            continue
        if isinstance(value, bool):
            out[key] = "true" if value else "false"
        elif isinstance(value, datetime):
            out[key] = value.isoformat()
        elif isinstance(value, str):
            out[key] = value
        elif isinstance(value, (int, float)):
            out[key] = str(value)
        else:
            out[key] = ",".join(str(item) for item in value)
    return out


def join_url(base_url: str, path: str) -> str:
    """Join the configured base URL with a full ``/api/vN/...`` path.

    Trailing slashes in ``path`` are preserved exactly as documented.
    """
    return base_url.rstrip("/") + path


_DEFAULT_PORTS = {"http": 80, "https": 443}


def same_origin(url_a: str, url_b: str) -> bool:
    """Whether two URLs share an origin (scheme + host + port)."""
    a, b = urlsplit(url_a), urlsplit(url_b)
    scheme_a, scheme_b = a.scheme.lower(), b.scheme.lower()
    port_a = a.port if a.port is not None else _DEFAULT_PORTS.get(scheme_a)
    port_b = b.port if b.port is not None else _DEFAULT_PORTS.get(scheme_b)
    host_a = (a.hostname or "").lower()
    host_b = (b.hostname or "").lower()
    return scheme_a == scheme_b and host_a == host_b and port_a == port_b


def truncate_text(text: str, limit: int) -> str:
    """Truncate ``text`` to at most ``limit`` characters with a marker."""
    if len(text) <= limit:
        return text
    return text[:limit] + "... (truncated)"


def drop_json_nulls(body: Mapping[str, Any]) -> dict[str, Any]:
    """Remove unset (``None``) fields from a JSON request body."""
    return {key: value for key, value in body.items() if value is not None}


def encode_json_query(payload: Mapping[str, Any]) -> str:
    """JSON-encode a request object destined for a ``query`` GET parameter.

    Used by ``/subscription/customize/`` and ``/subscription/pricing/`` which
    take their whole request JSON-encoded in a single GET parameter.
    """
    return json.dumps(drop_json_nulls(payload), separators=(",", ":"))


def _merge_headers(target: dict[str, str], updates: Mapping[str, str]) -> None:
    """Merge ``updates`` into ``target`` case-insensitively (updates win)."""
    for key, value in updates.items():
        lower = key.lower()
        for existing in list(target):
            if existing.lower() == lower:
                del target[existing]
        target[key] = value


def build_headers(
    *,
    token: str | None,
    user_agent: str,
    source: str,
    default_headers: Mapping[str, str] | None,
    client_subuser_id: int | str | None,
    client_federated_user_id: int | str | None,
    options: RequestOptions,
    has_json_body: bool,
) -> dict[str, str]:
    """Build the final header map for a request.

    Merging is case-insensitive with documented precedence (lowest to
    highest): SDK defaults < client ``default_headers`` < auth/subuser/
    federated headers < per-request headers. A single place constructs the
    ``Authorization`` header so the token scheme is never hard-coded at call
    sites.
    """
    headers: dict[str, str] = {
        "Accept": "application/json",
        "User-Agent": user_agent,
        "X-Webshare-Source": source,
    }
    if has_json_body:
        headers["Content-Type"] = "application/json"
    if default_headers:
        _merge_headers(headers, default_headers)
    controlled: dict[str, str] = {}
    if token is not None:
        controlled["Authorization"] = f"Token {token}"
    subuser_id = options.subuser_id if options.subuser_id is not None else client_subuser_id
    if subuser_id is not None:
        controlled["X-Subuser"] = str(subuser_id)
    federated = (
        options.federated_user_id
        if options.federated_user_id is not None
        else client_federated_user_id
    )
    if federated is not None:
        controlled["X-Webshare-Federated-Access"] = str(federated)
    _merge_headers(headers, controlled)
    if options.headers:
        _merge_headers(headers, options.headers)
    return headers


def buffer_files(files: Sequence[FileInput]) -> list[tuple[str, bytes]]:
    """Buffer accepted file inputs fully to ``(filename, bytes)`` pairs.

    Called at request-build time (when the request spec is constructed) so
    that multipart bodies are replayable: a retried attempt re-sends the
    buffered bytes instead of reading an exhausted stream.
    """
    buffered: list[tuple[str, bytes]] = []
    for item in files:
        if isinstance(item, (str, os.PathLike)):
            path = Path(item)
            buffered.append((path.name, path.read_bytes()))
        elif isinstance(item, bytes):
            buffered.append(("upload", item))
        elif isinstance(item, tuple):
            filename, content = item
            if not isinstance(content, bytes):
                content = content.read()
            buffered.append((filename, content))
        else:
            name = os.path.basename(str(getattr(item, "name", "upload")))
            buffered.append((name, item.read()))
    return buffered


def prepare_files(
    files: Sequence[FileInput],
) -> list[tuple[str, tuple[str, bytes]]]:
    """Convert (already buffered) file inputs into httpx multipart entries."""
    return [("files", pair) for pair in buffer_files(files)]


def is_idempotent(method: str) -> bool:
    return method.upper() in IDEMPOTENT_METHODS


def parse_retry_after(header: str | None) -> float | None:
    """Parse a ``Retry-After`` header (delta-seconds or HTTP-date).

    Returns the delay in seconds capped at 60, or ``None`` when the header is
    absent or invalid (empty, non-finite, negative, or unparseable). Naive
    HTTP-dates are interpreted as UTC.
    """
    if header is None:
        return None
    text = header.strip()
    if not text:
        return None
    try:
        seconds = float(text)
    except ValueError:
        try:
            target = parsedate_to_datetime(text)
        except (TypeError, ValueError):
            return None
        if target.tzinfo is None:
            target = target.replace(tzinfo=timezone.utc)
        seconds = (target - datetime.now(timezone.utc)).total_seconds()
    if not math.isfinite(seconds) or seconds < 0:
        return None
    return min(seconds, RETRY_AFTER_CAP)


def compute_backoff(attempt: int) -> float:
    """Exponential backoff with full jitter: base 0.5s, cap 8s."""
    ceiling = min(BACKOFF_CAP, BACKOFF_BASE * (2**attempt))
    return random.uniform(0, ceiling)


def retry_delay(attempt: int, retry_after_header: str | None) -> float:
    """Delay before retry ``attempt`` (0-based), honoring ``Retry-After``."""
    retry_after = parse_retry_after(retry_after_header)
    if retry_after is not None:
        return retry_after
    return compute_backoff(attempt)


_ERROR_CLASSES: dict[int, type[APIError]] = {
    400: BadRequestError,
    401: AuthenticationError,
    403: PermissionDeniedError,
    404: NotFoundError,
    429: RateLimitError,
}


def _extract_field_messages(value: object) -> list[str] | None:
    """Extract validation messages for a single field.

    The docs show lists of strings, but the live API returns lists of objects
    (``[{"message": "...", "code": "..."}]``); bare strings also occur. All
    three shapes are accepted.
    """
    if isinstance(value, str):
        return [value]
    if not isinstance(value, list):
        return None
    messages: list[str] = []
    for item in value:
        if isinstance(item, str):
            messages.append(item)
        elif isinstance(item, dict) and isinstance(item.get("message"), str):
            messages.append(item["message"])
        else:
            return None
    return messages or None


def make_api_error(
    *,
    status_code: int,
    body_text: str,
    request_id: str | None,
    retry_after: float | None = None,
) -> APIError:
    """Map an error response onto the typed exception hierarchy.

    Body parsing is tolerant: DRF ``{"detail": ...}`` bodies, field-error maps
    (both string-list and message-object forms), bare JSON strings and
    non-JSON bodies are all accepted. The captured body is capped at 1 MiB and
    the human-facing detail truncated to ~2 KB.
    """
    body_text = body_text[:MAX_ERROR_BODY_BYTES]
    parsed: object
    try:
        parsed = json.loads(body_text) if body_text else None
    except ValueError:
        parsed = body_text

    detail: str | None = None
    code: str | None = None
    field_errors: dict[str, list[str]] = {}
    if isinstance(parsed, str):
        detail = parsed
    elif isinstance(parsed, dict):
        raw_detail = parsed.get("detail")
        if isinstance(raw_detail, str):
            detail = raw_detail
        raw_code = parsed.get("code")
        if isinstance(raw_code, str):
            code = raw_code
        for key, value in parsed.items():
            if key in ("detail", "code"):
                continue
            messages = _extract_field_messages(value)
            if messages:
                field_errors[key] = messages
    elif parsed is None and body_text:
        detail = body_text

    if detail is None and body_text and not isinstance(parsed, (dict, list)):
        detail = body_text

    if detail is not None:
        detail = truncate_text(detail, MAX_DETAIL_CHARS)
    message = detail or f"HTTP {status_code} error"
    if field_errors and detail is None:
        message = truncate_text(
            f"HTTP {status_code} error: {json.dumps(field_errors)}", MAX_DETAIL_CHARS
        )
    error_cls = _ERROR_CLASSES.get(status_code)
    if error_cls is None:
        error_cls = InternalServerError if status_code >= 500 else APIError
    return error_cls(
        message,
        status_code=status_code,
        code=code,
        request_id=request_id,
        detail=detail,
        field_errors=field_errors,
        body=parsed if parsed is not None else body_text,
        retry_after=retry_after,
    )
