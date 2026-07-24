"""Test fixtures: a real local HTTP server with scripted responses.

The server (stdlib ``http.server`` running in a background thread) pops one
scripted response per incoming request, in FIFO order, and records every
request it receives so tests can assert on method, path, query, headers and
body.
"""

from __future__ import annotations

import json
import threading
import time
from collections import deque
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import parse_qs, urlsplit

import pytest


@dataclass
class RecordedRequest:
    method: str
    path: str
    query: dict[str, list[str]]
    headers: dict[str, str]
    raw_headers: list[tuple[str, str]]
    body: bytes

    def json(self) -> Any:
        return json.loads(self.body)


@dataclass
class ScriptedResponse:
    status: int = 200
    body: bytes = b""
    content_type: str = "application/json"
    headers: dict[str, str] = field(default_factory=dict)
    delay: float = 0.0


class MockServer:
    def __init__(self) -> None:
        self.requests: list[RecordedRequest] = []
        self._responses: deque[ScriptedResponse] = deque()
        self._lock = threading.Lock()
        server = self

        class Handler(BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.1"

            def log_message(self, format: str, *args: object) -> None:
                pass

            def _handle(self) -> None:
                length = int(self.headers.get("Content-Length") or 0)
                body = self.rfile.read(length) if length else b""
                split = urlsplit(self.path)
                with server._lock:
                    server.requests.append(
                        RecordedRequest(
                            method=self.command,
                            path=split.path,
                            query=parse_qs(split.query),
                            headers=dict(self.headers.items()),
                            raw_headers=list(self.headers.items()),
                            body=body,
                        )
                    )
                    response = (
                        server._responses.popleft()
                        if server._responses
                        else ScriptedResponse(status=599, body=b"no scripted response")
                    )
                if response.delay:
                    time.sleep(response.delay)
                self.send_response(response.status)
                self.send_header("Content-Type", response.content_type)
                self.send_header("Content-Length", str(len(response.body)))
                for key, value in response.headers.items():
                    self.send_header(key, value)
                self.end_headers()
                self.wfile.write(response.body)

            do_GET = _handle
            do_POST = _handle
            do_PATCH = _handle
            do_PUT = _handle
            do_DELETE = _handle

        self._httpd = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self._thread = threading.Thread(target=self._httpd.serve_forever, daemon=True)
        self._thread.start()

    @property
    def base_url(self) -> str:
        host, port = self._httpd.server_address[:2]
        if isinstance(host, bytes):
            host = host.decode()
        return f"http://{host}:{port}"

    def enqueue(
        self,
        *,
        status: int = 200,
        json_body: Any | None = None,
        text: str | None = None,
        body: bytes | None = None,
        content_type: str | None = None,
        headers: dict[str, str] | None = None,
        delay: float = 0.0,
    ) -> None:
        if json_body is not None:
            payload = json.dumps(json_body).encode()
            ctype = content_type or "application/json"
        elif text is not None:
            payload = text.encode()
            ctype = content_type or "text/plain"
        else:
            payload = body or b""
            ctype = content_type or "application/octet-stream"
        self._responses.append(
            ScriptedResponse(
                status=status,
                body=payload,
                content_type=ctype,
                headers=headers or {},
                delay=delay,
            )
        )

    def close(self) -> None:
        self._httpd.shutdown()
        self._httpd.server_close()
        self._thread.join(timeout=5)


@pytest.fixture
def server() -> Any:
    mock = MockServer()
    yield mock
    mock.close()


@pytest.fixture
def no_sleep(monkeypatch: pytest.MonkeyPatch) -> list[float]:
    """Disable retry backoff sleeps and record the requested delays."""
    from webshare._async_client import AsyncWebshare
    from webshare._client import Webshare

    delays: list[float] = []

    def record(seconds: float) -> None:
        delays.append(seconds)

    async def record_async(seconds: float) -> None:
        delays.append(seconds)

    monkeypatch.setattr(Webshare, "_sleep", staticmethod(record))
    monkeypatch.setattr(AsyncWebshare, "_sleep", staticmethod(record_async))
    return delays
