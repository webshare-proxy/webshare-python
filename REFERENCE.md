# Webshare Python SDK reference

Every public method, grouped by resource. All methods exist on both the
synchronous `Webshare` client and the asynchronous `AsyncWebshare` client with
identical signatures — on the async client, `await` the call (and use
`async for` to iterate pages). Every method additionally accepts the
per-request options `timeout`, `headers`, `max_retries`, `subuser_id` and
`federated_user_id`.

Most operations accept `plan_id` to target a specific plan; get plan IDs from
`client.plans.list()` and pass one explicitly (an account default is used
when omitted).

## Clients

```python
webshare.Webshare(...)  # synchronous client
webshare.AsyncWebshare(...)  # asynchronous client (same options)
```

Constructor options: `api_key` (falls back to `WEBSHARE_API_KEY`),
`credentials_provider` (callable returning the token; async client also
accepts async callables), `base_url` (default `https://proxy.webshare.io`),
`timeout` (seconds per attempt, default 60), `max_retries` (default 2),
`http_client` (inject an `httpx.Client`/`httpx.AsyncClient`),
`default_headers`, `subuser_id`, `federated_user_id`,
`retry_non_idempotent` (opt POST/PATCH into retries),
`unauthenticated` (credential-free client for unauthenticated endpoints).

## Pagination

`list` methods return `SyncPage[T]` / `AsyncPage[T]` exposing `.results`,
`.count`, `.next`, `.previous` and `.next_page()`; iterating the page object
(`for x in page` / `async for x in page`) yields items across all pages.

## Exceptions

All errors derive from `webshare.WebshareError`. API failures raise a
status-specific subclass of `webshare.APIError` (attributes: `status_code`,
`code`, `request_id`, `detail`, `field_errors`, `body`, `retry_after`):
`BadRequestError` (400), `AuthenticationError` (401), `PermissionDeniedError`
(403), `NotFoundError` (404), `RateLimitError` (429), `InternalServerError`
(5xx). Undecodable 2xx bodies raise `ResponseDecodeError`; transport failures
raise `APIConnectionError` / `APITimeoutError`.

## Helpers

| Function | Description |
| --- | --- |
| `webshare.build_proxy_url(mode=..., username=..., password=..., country_codes=..., city=..., session_id=..., rotate=...)` | Build a proxy connection URL (backbone username grammar or direct mode; IP-auth mode when credentials are omitted). |
| `webshare.build_proxy_list_download_url(token, country_codes=..., endpoint_mode=..., plan_id=...)` | Build the unauthenticated proxy list download URL from a download token. |

## client.proxies

| Method | Description | Docs |
| --- | --- | --- |
| `client.proxies.list(mode=..., plan_id=..., page=..., page_size=..., country_code__in=..., ...)` | List proxies (paginated; `mode` is required). | [docs](https://apidocs.webshare.io/proxy-list/list) |
| `client.proxies.refresh(plan_id=...)` | Refresh the entire proxy list (uses an on-demand refresh). | [docs](https://apidocs.webshare.io/proxy-list/ondemand_refresh) |
| `client.proxies.download(token, country_codes=..., endpoint_mode=..., plan_id=...)` | Download the proxy list as text, one `address:port:username:password` line per proxy. | [docs](https://apidocs.webshare.io/proxy-list/download) |
| `client.proxies.download_url(token, country_codes=..., endpoint_mode=..., plan_id=...)` | Build the download URL without calling it. | [docs](https://apidocs.webshare.io/proxy-list/download) |

## client.proxy_config

| Method | Description | Docs |
| --- | --- | --- |
| `client.proxy_config.get(plan_id=...)` | Get the proxy config (v3; `plan_id` required). | [docs](https://apidocs.webshare.io/proxy-config/get_proxy_config) |
| `client.proxy_config.get_stats(plan_id=...)` | Get proxy list composition stats: countries, IP ranges, ASNs (v3). | [docs](https://apidocs.webshare.io/proxy-config/get_proxy_stats) |
| `client.proxy_config.get_status(plan_id=...)` | Get proxy list readiness state and credentials (v3). | [docs](https://apidocs.webshare.io/proxy-config/get_proxy_status) |
| `client.proxy_config.update(plan_id=..., username=..., password=..., ...)` | Partially update the proxy config. | [docs](https://apidocs.webshare.io/proxy-config/update) |
| `client.proxy_config.allocate_unallocated_countries(new_countries=..., plan_id=...)` | Allocate proxies stuck in `unallocated_countries`. | [docs](https://apidocs.webshare.io/proxy-config/allocate_unallocated_countries) |

## client.proxy_replacements

| Method | Description | Docs |
| --- | --- | --- |
| `client.proxy_replacements.list(plan_id=..., state=..., dry_run=...)` | List proxy replacements (paginated). | [docs](https://apidocs.webshare.io/proxy-replacement/proxy_replacement/proxy_replacement_list) |
| `client.proxy_replacements.create(to_replace=..., replace_with=..., dry_run=..., plan_id=...)` | Create an asynchronous proxy replacement; poll `get` until completed. | [docs](https://apidocs.webshare.io/proxy-replacement/proxy_replacement/proxy_replacement_create) |
| `client.proxy_replacements.get(id, plan_id=...)` | Get a proxy replacement (poll after `create`). | [docs](https://apidocs.webshare.io/proxy-replacement/proxy_replacement/proxy_replacement_retrieve) |

## client.replaced_proxies

| Method | Description | Docs |
| --- | --- | --- |
| `client.replaced_proxies.list(proxy_list_replacement=..., plan_id=...)` | List replaced proxies (paginated). | [docs](https://apidocs.webshare.io/proxy-replacement/replaced_proxy/list_replaced_proxy) |
| `client.replaced_proxies.download(download_token=..., country_codes=..., mode=...)` | Download the replaced proxy list as text (token scope `replaced_proxy`). | [docs](https://apidocs.webshare.io/proxy-replacement/replaced_proxy/download) |

## client.stats

| Method | Description | Docs |
| --- | --- | --- |
| `client.stats.list(timestamp__gte=..., timestamp__lte=..., plan_id=...)` | List hourly proxy usage stats (bare array, not paginated). | [docs](https://apidocs.webshare.io/proxystats/list_stats) |
| `client.stats.aggregate(timestamp__gte=..., timestamp__lte=..., plan_id=...)` | Aggregate proxy usage stats for a period. | [docs](https://apidocs.webshare.io/proxystats/aggregate) |

## client.proxy_activity

| Method | Description | Docs |
| --- | --- | --- |
| `client.proxy_activity.list(starting_after=..., page_size=..., plan_id=..., ...)` | List proxy activity (paginated via `starting_after`). | [docs](https://apidocs.webshare.io/proxystats/list_activity) |
| `client.proxy_activity.download(download_token=..., plan_id=..., ...)` | Download proxy activities as CSV text (token scope `activity`). | [docs](https://apidocs.webshare.io/proxystats/download_activity) |

## client.download_tokens

| Method | Description | Docs |
| --- | --- | --- |
| `client.download_tokens.get(scope)` | Get a download token (`proxy_list`, `replaced_proxy` or `activity`). | [docs](https://apidocs.webshare.io/downloads/get_download_token) |
| `client.download_tokens.reset(scope)` | Reset (rotate) the download token for a scope. | [docs](https://apidocs.webshare.io/downloads/reset_download_token) |

## client.ip_authorizations

| Method | Description | Docs |
| --- | --- | --- |
| `client.ip_authorizations.list(plan_id=...)` | List IP authorizations (paginated). | [docs](https://apidocs.webshare.io/ipauthorization/list) |
| `client.ip_authorizations.create(ip_address=..., plan_id=...)` | Authorize an IP address. | [docs](https://apidocs.webshare.io/ipauthorization/create) |
| `client.ip_authorizations.get(id, plan_id=...)` | Get an IP authorization. | [docs](https://apidocs.webshare.io/ipauthorization/retrieve) |
| `client.ip_authorizations.delete(id, plan_id=...)` | Delete an IP authorization. | [docs](https://apidocs.webshare.io/ipauthorization/delete) |
| `client.ip_authorizations.whats_my_ip()` | Return your public IP address. | [docs](https://apidocs.webshare.io/ipauthorization/whatsmyip) |

## client.subusers

| Method | Description | Docs |
| --- | --- | --- |
| `client.subusers.list(plan_id=...)` | List sub-users (paginated). | [docs](https://apidocs.webshare.io/subuser/list) |
| `client.subusers.create(label=..., proxy_limit=..., max_thread_count=..., plan_id=...)` | Create a sub-user. | [docs](https://apidocs.webshare.io/subuser/create) |
| `client.subusers.get(id, plan_id=...)` | Get a sub-user. | [docs](https://apidocs.webshare.io/subuser/retrieve) |
| `client.subusers.update(id, label=..., plan_id=..., ...)` | Partially update a sub-user. | [docs](https://apidocs.webshare.io/subuser/update) |
| `client.subusers.delete(id, plan_id=...)` | Delete a sub-user. | [docs](https://apidocs.webshare.io/subuser/delete) |
| `client.subusers.refresh_proxy_list(id)` | Refresh a sub-user's custom proxy list. | [docs](https://apidocs.webshare.io/subuser/refresh_proxy_list) |

## client.profile

| Method | Description | Docs |
| --- | --- | --- |
| `client.profile.get()` | Retrieve the user profile. | [docs](https://apidocs.webshare.io/userprofile/retrieve) |
| `client.profile.update(first_name=..., timezone=..., ...)` | Partially update the user profile. | [docs](https://apidocs.webshare.io/userprofile/update) |
| `client.profile.get_preferences()` | Retrieve the user preferences. | [docs](https://apidocs.webshare.io/userprofile/retrivePreferences) |
| `client.profile.update_preferences(...)` | Update the user preferences. | [docs](https://apidocs.webshare.io/userprofile/updatePreferences) |

## client.notifications

| Method | Description | Docs |
| --- | --- | --- |
| `client.notifications.list(dismissed_at__isnull=..., type=...)` | List account notifications (paginated). | [docs](https://apidocs.webshare.io/notifications/list) |
| `client.notifications.get(id)` | Get a notification. | [docs](https://apidocs.webshare.io/notifications/retrieve) |
| `client.notifications.dismiss(id)` | Dismiss a notification. | [docs](https://apidocs.webshare.io/notifications/dismiss) |
| `client.notifications.restore(id)` | Restore a dismissed notification. | [docs](https://apidocs.webshare.io/notifications/restore) |

## client.id_verification

| Method | Description | Docs |
| --- | --- | --- |
| `client.id_verification.get()` | Get the ID verification object (Stripe Identity). | [docs](https://apidocs.webshare.io/idverification/retrieve) |

## client.verification

| Method | Description | Docs |
| --- | --- | --- |
| `client.verification.flows.list()` | List account verification flows (paginated). | [docs](https://apidocs.webshare.io/verification/list) |
| `client.verification.flows.get(id)` | Get a verification flow. | [docs](https://apidocs.webshare.io/verification/retrieve) |
| `client.verification.flows.submit_evidence(id, explanation=..., files=...)` | Submit evidence (multipart; accepts paths, bytes or file objects). | [docs](https://apidocs.webshare.io/verification/submit_evidence) |
| `client.verification.flows.submit_security_code(id, security_code=...)` | Submit the bank-statement security code. | [docs](https://apidocs.webshare.io/verification/submit_security_code) |
| `client.verification.questions.list(flow__type=..., answer__isnull=..., ...)` | List compliance questions (paginated). | [docs](https://apidocs.webshare.io/verification/list_questions) |
| `client.verification.questions.submit_answer(question_id, answer=..., files=...)` | Submit an answer with optional attachments (multipart). | [docs](https://apidocs.webshare.io/verification/submit_answer) |
| `client.verification.appeals.list(state=...)` | List suspension appeals (paginated). | [docs](https://apidocs.webshare.io/verification/list_appeals) |
| `client.verification.appeals.create(appeal=...)` | Submit a suspension appeal. | [docs](https://apidocs.webshare.io/verification/submit_appeal) |
| `client.verification.abuse_reports.list()` | List abuse reports (paginated). | [docs](https://apidocs.webshare.io/verification/list_abuse_reports) |
| `client.verification.get_suspension()` | Get suspension details (works while suspended). | [docs](https://apidocs.webshare.io/verification/view_suspension) |
| `client.verification.get_categories()` | Get verification categories (map keyed by category). | [docs](https://apidocs.webshare.io/verification/categories) |
| `client.verification.get_limits()` | Get the current verification limits. | [docs](https://apidocs.webshare.io/verification/limits) |
| `client.verification.get_thresholds()` | Get verification thresholds (map keyed by category). | [docs](https://apidocs.webshare.io/verification/thresholds) |

## client.billing

| Method | Description | Docs |
| --- | --- | --- |
| `client.billing.get_info()` | Get the billing information singleton. | [docs](https://apidocs.webshare.io/billing/billing) |
| `client.billing.update_info(name=..., address=..., billing_email=...)` | Update the billing information. | [docs](https://apidocs.webshare.io/billing/billing) |

## client.payment_methods

| Method | Description | Docs |
| --- | --- | --- |
| `client.payment_methods.list()` | List payment methods (paginated; polymorphic on `type`). | [docs](https://apidocs.webshare.io/billing/payment_methods) |
| `client.payment_methods.get(id)` | Get a payment method. | [docs](https://apidocs.webshare.io/billing/payment_methods) |

## client.pending_payments

| Method | Description | Docs |
| --- | --- | --- |
| `client.pending_payments.list()` | List pending payments (paginated). | [docs](https://apidocs.webshare.io/billing/pending_payments) |
| `client.pending_payments.get(id)` | Get a pending payment (poll after a Stripe confirm). | [docs](https://apidocs.webshare.io/billing/pending_payments) |

## client.transactions

| Method | Description | Docs |
| --- | --- | --- |
| `client.transactions.list()` | List transactions (paginated). | [docs](https://apidocs.webshare.io/billing/transactions) |
| `client.transactions.get(id)` | Get a transaction. | [docs](https://apidocs.webshare.io/billing/transactions) |

## client.subscription

| Method | Description | Docs |
| --- | --- | --- |
| `client.subscription.get()` | Get the subscription singleton. | [docs](https://apidocs.webshare.io/subscription) |
| `client.subscription.get_available_assets()` | Get available assets per proxy category/subtype. | [docs](https://apidocs.webshare.io/subscription/assets) |
| `client.subscription.customize(proxy_type=..., proxy_countries=..., plan_id=...)` | Get customization limits/options for a plan configuration. | [docs](https://apidocs.webshare.io/subscription/customize) |
| `client.subscription.pricing(proxy_type=..., proxy_countries=..., term=..., ...)` | Get the pricing for a custom plan configuration. | [docs](https://apidocs.webshare.io/subscription/pricing) |
| `client.subscription.enable_auto_renewal()` | Enable auto-renewal (payment method must be on file). | [docs](https://apidocs.webshare.io/subscription/auto_renewal) |
| `client.subscription.cancel_auto_renewal()` | Cancel auto-renewal (also removes the payment method). | [docs](https://apidocs.webshare.io/subscription/auto_renewal) |

## client.plans

| Method | Description | Docs |
| --- | --- | --- |
| `client.plans.list()` | List all plans, including non-active ones (paginated). | [docs](https://apidocs.webshare.io/subscription/plan) |
| `client.plans.get(id)` | Get a plan. | [docs](https://apidocs.webshare.io/subscription/plan) |
| `client.plans.update(id, automatic_refresh_next_at=...)` | Update a plan (only `automatic_refresh_next_at` is editable). | [docs](https://apidocs.webshare.io/subscription/plan) |
| `client.plans.cancel(id)` | Cancel a plan (subscription credited for the remainder). | [docs](https://apidocs.webshare.io/subscription/plan) |

## client.invoices

| Method | Description | Docs |
| --- | --- | --- |
| `client.invoices.download(subscription_transaction_id=...)` | Download an invoice as PDF bytes. | [docs](https://apidocs.webshare.io/subscription/download_invoice) |

## client.referral

| Method | Description | Docs |
| --- | --- | --- |
| `client.referral.get_config()` | Get the referral config. | [docs](https://apidocs.webshare.io/referral) |
| `client.referral.update_config(mode=..., paypal_payout_email=...)` | Update the referral config. | [docs](https://apidocs.webshare.io/referral) |
| `client.referral.get_coupon_code()` | Get the currently applied coupon code. | [docs](https://apidocs.webshare.io/referral/coupon_code) |
| `client.referral.apply_coupon_code(code=...)` | Apply a coupon code (5/min rate limit). | [docs](https://apidocs.webshare.io/referral/coupon_code) |
| `client.referral.remove_coupon_code()` | Remove the applied coupon code. | [docs](https://apidocs.webshare.io/referral/coupon_code) |
| `client.referral.list_channels()` | List referral channels (bare array, not paginated). | [docs](https://apidocs.webshare.io/referral/referral_channel) |
| `client.referral.list_credits(mode=..., status=..., ordering=...)` | List referral credits (paginated). | [docs](https://apidocs.webshare.io/referral/referral_credit) |
| `client.referral.get_credit(id)` | Get a referral credit. | [docs](https://apidocs.webshare.io/referral/referral_credit) |
| `client.referral.list_earnouts()` | List earn outs (paginated). | [docs](https://apidocs.webshare.io/referral/referral_earnout) |
| `client.referral.get_earnout(id)` | Get an earn out. | [docs](https://apidocs.webshare.io/referral/referral_earnout) |
| `client.referral.get_code_info(referral_code=...)` | Get public referral code info (unauthenticated). | [docs](https://apidocs.webshare.io/referral/referral_info) |
