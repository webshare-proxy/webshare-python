# Webshare Python SDK

Official Python SDK for the [Webshare](https://www.webshare.io) proxy API.

[![CI](https://github.com/webshare-proxy/webshare-python/actions/workflows/ci.yml/badge.svg)](https://github.com/webshare-proxy/webshare-python/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/webshare-sdk)](https://pypi.org/project/webshare-sdk/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## Install

```
pip install webshare-sdk
```

Requires Python 3.10+. The only runtime dependency is [httpx](https://www.python-httpx.org).

## Quickstart

```python
import webshare

with webshare.Webshare() as client:  # reads WEBSHARE_API_KEY from the environment
    for proxy in client.proxies.list(mode="direct"):
        print(f"{proxy.proxy_address}:{proxy.port}")
```

Async variant:

```python
import asyncio
import webshare


async def main() -> None:
    async with webshare.AsyncWebshare() as client:
        page = await client.proxies.list(mode="direct")
        async for proxy in page:
            print(f"{proxy.proxy_address}:{proxy.port}")


asyncio.run(main())
```

## Working with plans

Most proxy operations are plan-scoped: they accept a `plan_id` and use an
account default when it is omitted. The standard pattern is to list your
plans, pick the one you want, and pass its id explicitly:

```python
with webshare.Webshare() as client:
    plan = next(p for p in client.plans.list() if p.status == "active")

    proxies = client.proxies.list(mode="direct", plan_id=plan.id)
    config = client.proxy_config.get(plan_id=plan.id)
    stats = client.proxy_config.get_stats(plan_id=plan.id)
    status = client.proxy_config.get_status(plan_id=plan.id)
    url = client.proxies.download_url(config.proxy_list_download_token, plan_id=plan.id)
```

The plan id is also visible in the dashboard URL when viewing a plan. The
active plan of the subscription is `client.subscription.get().plan`.

## Key functions

| Function | Description |
| --- | --- |
| `client.plans.list()` | List your plans; the ids scope most other calls. |
| `client.proxies.list(mode=..., plan_id=...)` | List proxies (paginated). |
| `client.proxies.download(token, plan_id=...)` | Download the proxy list as `address:port:username:password` text. |
| `client.proxy_config.get(plan_id=...)` | Get the proxy config (timeouts, IP-auth targeting, download token). |
| `client.stats.aggregate(plan_id=...)` | Aggregate proxy usage stats for a period. |
| `webshare.build_proxy_url(...)` | Build proxy connection URLs (backbone sessions/rotation or direct mode). |

See [REFERENCE.md](REFERENCE.md) for every method.

## Authentication

Pass the API key explicitly, or set the `WEBSHARE_API_KEY` environment
variable:

```python
client = webshare.Webshare(api_key="your-api-key")
```

For advanced use (for example OAuth tokens that need refreshing), pass a
`credentials_provider` callable returning the token; it is called once per
attempt (so refreshed tokens are picked up on retries, not just on the first
call). The async client also accepts async callables. `api_key` is shorthand
for a static provider.

```python
client = webshare.Webshare(credentials_provider=lambda: load_token())
```

The constructor raises `webshare.WebshareError` when no credential is
available (empty strings are treated as absent). A handful of endpoints are
unauthenticated (for example `client.referral.get_code_info` and the download
URLs); the SDK never sends the token to them. To call only those without any
credential, construct the client with `unauthenticated=True` — authenticated
operations on such a client raise a clear error.

## Pagination

Every `list` method returns a page object exposing the raw envelope
(`results`, `count`, `next`, `previous`) and `next_page()`. Iterating the page
object yields items across all pages automatically:

```python
page = client.proxies.list(mode="direct", page_size=100)
print(page.count)  # total number of results
for proxy in page:  # iterates across every page
    ...

next_page = page.next_page()  # or fetch one page at a time
```

The async client works the same way with `async for` and
`await page.next_page()`.

## Error handling

All SDK errors derive from `webshare.WebshareError`. API failures raise a
status-specific subclass of `webshare.APIError`:

```python
import webshare

try:
    client.proxies.list(mode="direct")
except webshare.RateLimitError as err:
    print(err.status_code, err.detail)
except webshare.PermissionDeniedError as err:
    if err.code == "account_suspended":
        ...  # see client.verification.get_suspension()
except webshare.APIError as err:
    print(err.status_code, err.code, err.field_errors, err.request_id)
```

| Exception | Status |
| --- | --- |
| `BadRequestError` | 400 |
| `AuthenticationError` | 401 |
| `PermissionDeniedError` | 403 (check `code`: `account_suspended`, `account_deleted`) |
| `NotFoundError` | 404 |
| `RateLimitError` | 429 |
| `InternalServerError` | 5xx |
| `ResponseDecodeError` | 2xx with an undecodable body |
| `APIConnectionError` / `APITimeoutError` | transport failures |

Validation failures populate `err.field_errors`, e.g.
`{"mode": ["This field is required."]}` (both the documented string-list and
the live API's message-object forms are parsed). When the server sends a valid
`Retry-After` header, `err.retry_after` carries the parsed seconds so callers
can self-throttle calls the SDK does not retry (such as a 429 on POST). If you
authenticate with a login token via `credentials_provider` (rather than an API
key), calls can additionally return 403 with code `2fa_needed`; API keys are
never 2FA-challenged.

## Retries

Failed requests are retried automatically with exponential backoff and full
jitter (base 0.5s, cap 8s): connection errors, timeouts, and status codes 408,
429, 500, 502, 503 and 504 (not every 5xx). `Retry-After` headers are honored
(capped at 60s). The default is
`max_retries=2` (three attempts total), configurable per client and per
request. Only idempotent requests (GET/PUT/DELETE) are retried by default;
pass `retry_non_idempotent=True` to the client to opt in POST/PATCH.

## Timeouts

The default request timeout is 60 seconds and bounds a single HTTP attempt,
including reading the response body; the total call time may exceed it when
retries and `Retry-After` waits occur. Override it per client
(`Webshare(timeout=10.0)`) or per request:

```python
client.profile.get(timeout=5.0)
```

Pass `timeout=None` explicitly for no timeout (httpx's infinite wait) — this
is distinct from omitting `timeout` entirely, which uses the 60-second
default. If you inject your own `http_client` and omit `timeout` entirely, the
injected client's timeout configuration is used instead.

Every method also accepts per-request `headers`, `max_retries`, `subuser_id`
(sent as `X-Subuser` for sub-user masquerading) and `federated_user_id` (sent
as `X-Webshare-Federated-Access`, admin only); the last two can also be set on
the client.

## Proxy connection helper

`webshare.build_proxy_url` builds proxy connection URLs, including the
backbone username grammar for geo targeting, sticky sessions and rotation:

```python
from webshare import build_proxy_url

# Backbone mode with country targeting and a sticky session
url = build_proxy_url(
    username="user",
    password="pass",
    country_codes=["US"],
    session_id=1234,
)
# -> "http://user-us-1234:pass@p.webshare.io:80"

# Direct mode using an entry from client.proxies.list()
url = build_proxy_url(
    mode="direct",
    username=proxy.username,
    password=proxy.password,
    proxy_address=proxy.proxy_address,
    port=proxy.port,
)
```

`webshare.build_proxy_list_download_url` (also available as
`client.proxies.download_url`) builds the unauthenticated proxy list download
URL from the config's `proxy_list_download_token`;
`client.proxies.download(...)` fetches it directly and returns the text.

## Identification header

Every request carries an `X-Webshare-Source` header identifying the caller
for API-side tracking. It names only the SDK and the Python runtime version
(default `WebshareSDK/<version> (Python; <python version>)`) — no user data.
Tools built on the SDK can replace it via the `source` client option, and
per-request headers override it as usual.

## Supported versions

| Python | Supported |
| --- | --- |
| 3.10 / 3.11 / 3.12 / 3.13 | yes |

API reference: https://apidocs.webshare.io

## License

MIT. Issues and pull requests are welcome.
