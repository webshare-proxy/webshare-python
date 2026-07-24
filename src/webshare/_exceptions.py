"""Exception hierarchy for the Webshare SDK.

``WebshareError`` is the base class for everything raised by this library.
API failures raise a status-specific subclass of ``APIError``; transport
failures raise ``APIConnectionError`` (or ``APITimeoutError`` for timeouts).
"""

from __future__ import annotations

__all__ = [
    "APIConnectionError",
    "APIError",
    "APITimeoutError",
    "AuthenticationError",
    "BadRequestError",
    "InternalServerError",
    "NotFoundError",
    "PermissionDeniedError",
    "RateLimitError",
    "WebshareError",
]


class WebshareError(Exception):
    """Base class for all errors raised by the Webshare SDK."""


class APIError(WebshareError):
    """An error response returned by the Webshare API.

    Attributes:
        status_code: HTTP status code of the response.
        code: API error code string (e.g. ``2fa_needed``), when present.
        request_id: Value of the ``X-Request-ID`` response header, when present.
        detail: Human-readable error message.
        field_errors: Field validation errors, mapping field name to a list of
            messages (e.g. ``{"mode": ["This field is required."]}``).
        body: The parsed response body (or raw text when not JSON).
    """

    def __init__(
        self,
        message: str,
        *,
        status_code: int,
        code: str | None = None,
        request_id: str | None = None,
        detail: str | None = None,
        field_errors: dict[str, list[str]] | None = None,
        body: object = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.request_id = request_id
        self.detail = detail
        self.field_errors = field_errors or {}
        self.body = body


class BadRequestError(APIError):
    """400 Bad Request."""


class AuthenticationError(APIError):
    """401 Unauthorized."""


class PermissionDeniedError(APIError):
    """403 Forbidden.

    Check ``code`` for account-state reasons every call can hit:
    ``2fa_needed``, ``account_deleted``, ``account_suspended``.
    """


class NotFoundError(APIError):
    """404 Not Found."""


class RateLimitError(APIError):
    """429 Too Many Requests."""


class InternalServerError(APIError):
    """5xx server error."""


class APIConnectionError(WebshareError):
    """The request could not be completed because of a connection problem."""

    def __init__(self, message: str = "Connection error.") -> None:
        super().__init__(message)


class APITimeoutError(APIConnectionError):
    """The request timed out."""

    def __init__(self, message: str = "Request timed out.") -> None:
        super().__init__(message)
