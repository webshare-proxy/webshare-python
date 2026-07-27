"""Happy-path coverage across resource groups: paths, encoding, decoding."""

from __future__ import annotations

from collections.abc import Callable, Iterator
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

import pytest

from tests.conftest import MockServer
from webshare import Webshare


@pytest.fixture
def client(server: MockServer) -> Iterator[Webshare]:
    with Webshare(base_url=server.base_url, api_key="k") as c:
        yield c


def test_proxies_list_decodes_models(server: MockServer, client: Webshare) -> None:
    server.enqueue(
        json_body={
            "count": 1,
            "next": None,
            "previous": None,
            "results": [
                {
                    "id": "d-10513",
                    "username": "user",
                    "password": "pass",
                    "proxy_address": "1.2.3.4",
                    "port": 8168,
                    "valid": True,
                    "last_verification": "2019-06-09T23:34:00.095501-07:00",
                    "country_code": "US",
                    "city_name": "New York",
                    "created_at": "2022-06-14T11:58:10.246406-07:00",
                    "some_future_field": {"ignored": True},
                }
            ],
        }
    )
    page = client.proxies.list(mode="direct", country_code__in=["FR", "US"], valid=True)
    proxy = page.results[0]
    assert proxy.id == "d-10513"
    assert proxy.port == 8168
    assert isinstance(proxy.created_at, datetime)
    request = server.requests[0]
    assert request.path == "/api/v2/proxy/list/"
    # Sequences are comma-joined and booleans serialized as true/false.
    assert request.query["country_code__in"] == ["FR,US"]
    assert request.query["valid"] == ["true"]
    assert request.query["mode"] == ["direct"]


def test_proxies_download_is_unauthenticated_text(server: MockServer, client: Webshare) -> None:
    server.enqueue(text="10.1.2.3:9421:user:pass\n10.1.2.4:6511:user:pass\n")
    body = client.proxies.download("tok", country_codes=["us"], plan_id=7)
    assert body.startswith("10.1.2.3:9421")
    request = server.requests[0]
    assert request.path == "/api/v2/proxy/list/download/tok/US/any/username/direct/-/"
    assert request.query == {"plan_id": ["7"]}
    assert "Authorization" not in request.headers


def test_proxy_config_get_uses_v3_path(server: MockServer, client: Webshare) -> None:
    server.enqueue(json_body={"request_timeout": 86400, "proxy_list_download_token": "t"})
    config = client.proxy_config.get(plan_id=5)
    assert config.request_timeout == 86400
    request = server.requests[0]
    assert request.path == "/api/v3/proxy/config"  # v3, no trailing slash
    assert request.query == {"plan_id": ["5"]}


def test_proxy_config_update_decodes_asns_tuple(server: MockServer, client: Webshare) -> None:
    server.enqueue(
        json_body={
            "id": 1,
            "state": "completed",
            "asns": {"6137": ["ASN NAME", 105]},
            "available_asns": {},
        }
    )
    config = client.proxy_config.update(username="new_username")
    assert config.asns == {"6137": ("ASN NAME", 105)}
    request = server.requests[0]
    assert request.method == "PATCH"
    assert request.json() == {"username": "new_username"}


def test_stats_list_returns_bare_array(server: MockServer, client: Webshare) -> None:
    server.enqueue(
        json_body=[
            {
                "timestamp": "2022-08-11T17:00:00-07:00",
                "is_projected": False,
                "bandwidth_total": 5000,
                "requests_total": 5,
                "error_reasons": [{"reason": "x", "type": "connection", "count": 1}],
            }
        ]
    )
    stats = client.stats.list(timestamp__gte="2022-08-01T00:00:00Z")
    assert len(stats) == 1
    assert stats[0].bandwidth_total == 5000
    assert stats[0].error_reasons is not None
    assert stats[0].error_reasons[0].reason == "x"
    assert server.requests[0].path == "/api/v2/stats/"


def test_download_token_and_activity_download(server: MockServer, client: Webshare) -> None:
    server.enqueue(json_body={"id": 56, "key": "abc", "scope": "activity", "expire_at": None})
    token = client.download_tokens.get("activity")
    assert token.key == "abc"
    assert server.requests[0].path == "/api/v2/download_token/activity/"

    server.enqueue(text="Time,Hostname\n")
    csv = client.proxy_activity.download(download_token="abc")
    assert csv.startswith("Time,")
    request = server.requests[1]
    assert request.path == "/api/v2/proxy/activity/download/"
    assert request.query["download_token"] == ["abc"]
    assert "Authorization" not in request.headers


def test_notifications_dismiss_posts(server: MockServer, client: Webshare) -> None:
    server.enqueue(json_body={"id": 13, "type": "x", "dismissed_at": "2022-06-14T11:58:10Z"})
    notification = client.notifications.dismiss(13)
    assert notification.id == 13
    request = server.requests[0]
    assert request.method == "POST"
    assert request.path == "/api/v2/notification/13/dismiss/"


def test_submit_evidence_multipart(server: MockServer, client: Webshare, tmp_path: Path) -> None:
    evidence = tmp_path / "evidence.txt"
    evidence.write_bytes(b"proof-bytes")
    server.enqueue(json_body={"id": 1, "type": "abuse_report", "state": "inflow"})
    flow = client.verification.flows.submit_evidence(
        1,
        explanation="explanation text",
        files=[evidence, ("inline.txt", b"inline-bytes")],
    )
    assert flow.id == 1
    request = server.requests[0]
    assert request.method == "POST"
    assert request.path == "/api/v2/verification/flow/1/submit_evidence/"
    assert request.headers["Content-Type"].startswith("multipart/form-data")
    assert b"proof-bytes" in request.body
    assert b"inline-bytes" in request.body
    assert b"explanation text" in request.body
    assert b'filename="evidence.txt"' in request.body


def test_submit_answer_multipart(server: MockServer, client: Webshare) -> None:
    server.enqueue(json_body={"id": 1, "answer": "the answer"})
    answer = client.verification.questions.submit_answer(9, answer="the answer")
    assert answer.answer == "the answer"
    request = server.requests[0]
    assert request.path == "/api/v2/verification/question/9/answer/"
    assert request.headers["Content-Type"].startswith("multipart/form-data")


def test_verification_categories_map(server: MockServer, client: Webshare) -> None:
    server.enqueue(
        json_body={
            "requests_to_financial_institutions": {
                "description": "d",
                "request_threshold": None,
                "id_verification_required": True,
                "id_verification_restores_access": True,
            }
        }
    )
    categories = client.verification.get_categories()
    assert categories["requests_to_financial_institutions"].id_verification_required is True


def test_subscription_pricing_json_query_param(server: MockServer, client: Webshare) -> None:
    server.enqueue(
        json_body={
            "price": 13.94,
            "paid_today": 8.94,
            "proxy_count_discount_tiers": [
                {"from": 0, "to": 250, "discount_percentage": 0, "per_proxy_price": 0.0299}
            ],
        }
    )
    pricing = client.subscription.pricing(
        proxy_type="shared",
        proxy_countries={"US": 100},
        bandwidth_limit=250,
        term="monthly",
        plan_id=3,
    )
    assert pricing.price == 13.94
    tiers = pricing.proxy_count_discount_tiers
    assert tiers is not None
    assert tiers[0].from_ == 0 and tiers[0].to == 250
    request = server.requests[0]
    assert request.path == "/api/v2/subscription/pricing/"
    assert request.query["plan_id"] == ["3"]
    import json

    payload = json.loads(request.query["query"][0])
    assert payload == {
        "proxy_type": "shared",
        "proxy_countries": {"US": 100},
        "bandwidth_limit": 250,
        "term": "monthly",
    }


def test_cancel_auto_renewal_delete_returns_subscription(
    server: MockServer, client: Webshare
) -> None:
    server.enqueue(json_body={"id": 1, "plan": 2, "renewals_enabled": False})
    subscription = client.subscription.cancel_auto_renewal()
    assert subscription.renewals_enabled is False
    request = server.requests[0]
    assert request.method == "DELETE"
    assert request.path == "/api/v2/subscription/renewal/"


def test_invoice_download_returns_bytes(server: MockServer, client: Webshare) -> None:
    server.enqueue(body=b"%PDF-1.7 fake", content_type="application/pdf")
    pdf = client.invoices.download(subscription_transaction_id="tr_1")
    assert pdf == b"%PDF-1.7 fake"
    request = server.requests[0]
    assert request.path == "/api/v2/invoices/download"  # no trailing slash
    assert request.query == {"subscription_transaction_id": ["tr_1"]}


def test_referral_channels_bare_array(server: MockServer, client: Webshare) -> None:
    server.enqueue(json_body=[{"id": 1, "code": "SUMMER20", "promo_value": "0.20"}])
    channels = client.referral.list_channels()
    assert channels[0].code == "SUMMER20"
    assert server.requests[0].path == "/api/v2/referral/channel/"


def test_available_assets_nested_map(server: MockServer, client: Webshare) -> None:
    server.enqueue(
        json_body={"shared": {"default": {"total_subnets": 1, "available_countries": {"US": 1000}}}}
    )
    assets = client.subscription.get_available_assets()
    assert assets["shared"]["default"].total_subnets == 1
    assert assets["shared"]["default"].available_countries == {"US": 1000}


def test_ip_authorization_roundtrip(server: MockServer, client: Webshare) -> None:
    server.enqueue(json_body={"ip_address": "1.2.3.4"})
    assert client.ip_authorizations.whats_my_ip().ip_address == "1.2.3.4"
    server.enqueue(json_body={"id": 1337, "ip_address": "1.2.3.4"})
    created = client.ip_authorizations.create(ip_address="1.2.3.4")
    assert created.id == 1337
    assert server.requests[1].json() == {"ip_address": "1.2.3.4"}
    server.enqueue(status=204)
    client.ip_authorizations.delete(1337)
    assert server.requests[2].method == "DELETE"
    assert server.requests[2].path == "/api/v2/proxy/ipauthorization/1337/"


# -- Table-driven request-shape coverage for the previously-untested thin
# wrappers: billing, transactions, plans, profile preferences, proxy
# replacements, replaced proxies, referral, notifications, subusers
# create/update/delete, proxy_config stats/status. Each case checks that the
# method sends the right method/path/query/body, not the response decoding
# (already covered above and in test_models.py).

_NO_BODY = object()
_EMPTY_PAGE: dict[str, object] = {"count": 0, "next": None, "previous": None, "results": []}


@dataclass
class _Case:
    label: str
    call: Callable[[Webshare], object]
    method: str
    path: str
    query: dict[str, list[str]] = field(default_factory=dict)
    body: object = _NO_BODY
    response: object = field(default_factory=dict)


REQUEST_SHAPE_CASES = [
    _Case(
        "billing.get_info",
        lambda c: c.billing.get_info(),
        "GET",
        "/api/v2/subscription/billing_info/",
    ),
    _Case(
        "billing.update_info",
        lambda c: c.billing.update_info(name="Acme"),
        "PATCH",
        "/api/v2/subscription/billing_info/",
        body={"name": "Acme"},
    ),
    _Case(
        "transactions.list",
        lambda c: c.transactions.list(page=2),
        "GET",
        "/api/v2/payment/transaction/",
        query={"page": ["2"]},
        response=_EMPTY_PAGE,
    ),
    _Case(
        "transactions.get", lambda c: c.transactions.get(5), "GET", "/api/v2/payment/transaction/5/"
    ),
    _Case(
        "plans.list",
        lambda c: c.plans.list(),
        "GET",
        "/api/v2/subscription/plan/",
        response=_EMPTY_PAGE,
    ),
    _Case("plans.get", lambda c: c.plans.get(9), "GET", "/api/v2/subscription/plan/9/"),
    _Case(
        "plans.update (no kwargs is a no-op, not a null-clearing PATCH)",
        lambda c: c.plans.update(9),
        "PATCH",
        "/api/v2/subscription/plan/9/",
        body={},
    ),
    _Case(
        "plans.update (with value)",
        lambda c: c.plans.update(9, automatic_refresh_next_at="2024-01-01T00:00:00Z"),
        "PATCH",
        "/api/v2/subscription/plan/9/",
        body={"automatic_refresh_next_at": "2024-01-01T00:00:00Z"},
    ),
    _Case(
        "plans.cancel", lambda c: c.plans.cancel(9), "POST", "/api/v2/subscription/plan/9/cancel/"
    ),
    _Case(
        "profile.get_preferences",
        lambda c: c.profile.get_preferences(),
        "GET",
        "/api/v2/profile/preferences/",
    ),
    _Case(
        "profile.update_preferences",
        lambda c: c.profile.update_preferences(
            onboarding_activity_page_viewed_at="2024-01-01T00:00:00Z"
        ),
        "PATCH",
        "/api/v2/profile/preferences/",
        body={"onboarding_activity_page_viewed_at": "2024-01-01T00:00:00Z"},
    ),
    _Case(
        "proxy_replacements.list",
        lambda c: c.proxy_replacements.list(),
        "GET",
        "/api/v3/proxy/replace/",
        response=_EMPTY_PAGE,
    ),
    _Case(
        "proxy_replacements.create",
        lambda c: c.proxy_replacements.create(
            to_replace={"type": "ip_address", "ip_address": "1.2.3.4"},
            replace_with=[{"type": "any"}],
        ),
        "POST",
        "/api/v3/proxy/replace/",
        body={
            "to_replace": {"type": "ip_address", "ip_address": "1.2.3.4"},
            "replace_with": [{"type": "any"}],
        },
    ),
    _Case(
        "proxy_replacements.get",
        lambda c: c.proxy_replacements.get(3),
        "GET",
        "/api/v3/proxy/replace/3/",
    ),
    _Case(
        "replaced_proxies.list",
        lambda c: c.replaced_proxies.list(),
        "GET",
        "/api/v2/proxy/list/replaced/",
        response=_EMPTY_PAGE,
    ),
    _Case(
        # Country codes are normalized to uppercase like proxies.download.
        "replaced_proxies.download",
        lambda c: c.replaced_proxies.download(
            download_token="tok",
            country_codes=["us"],
            authentication_type="username",
            mode="direct",
        ),
        "GET",
        "/api/v2/proxy/list/replaced/download/",
        query={
            "download_token": ["tok"],
            "country_codes": ["US"],
            "authentication_type": ["username"],
            "mode": ["direct"],
            "proxy_protocol": ["any"],
        },
        response="",
    ),
    _Case(
        "referral.get_config", lambda c: c.referral.get_config(), "GET", "/api/v2/referral/config/"
    ),
    _Case(
        "referral.update_config",
        lambda c: c.referral.update_config(mode="credits"),
        "PATCH",
        "/api/v2/referral/config/",
        body={"mode": "credits"},
    ),
    _Case(
        "referral.get_coupon_code",
        lambda c: c.referral.get_coupon_code(),
        "GET",
        "/api/v2/referral/coupon-code/",
    ),
    _Case(
        "referral.apply_coupon_code",
        lambda c: c.referral.apply_coupon_code(code="X"),
        "POST",
        "/api/v2/referral/coupon-code/",
        body={"code": "X"},
    ),
    _Case(
        "referral.remove_coupon_code",
        lambda c: c.referral.remove_coupon_code(),
        "DELETE",
        "/api/v2/referral/coupon-code/",
    ),
    _Case(
        "referral.list_credits",
        lambda c: c.referral.list_credits(),
        "GET",
        "/api/v2/referral/credit/",
        response=_EMPTY_PAGE,
    ),
    _Case(
        "referral.get_credit",
        lambda c: c.referral.get_credit(4),
        "GET",
        "/api/v2/referral/credit/4/",
    ),
    _Case(
        # Verified against the live API: the earnout list path needs a
        # trailing slash or the server 301s it.
        "referral.list_earnouts",
        lambda c: c.referral.list_earnouts(),
        "GET",
        "/api/v2/referral/earnout/",
        response=_EMPTY_PAGE,
    ),
    _Case(
        "referral.get_earnout",
        lambda c: c.referral.get_earnout(2),
        "GET",
        "/api/v2/referral/earnout/2/",
    ),
    _Case(
        "notifications.list",
        lambda c: c.notifications.list(),
        "GET",
        "/api/v2/notification/",
        response=_EMPTY_PAGE,
    ),
    _Case("notifications.get", lambda c: c.notifications.get(7), "GET", "/api/v2/notification/7/"),
    _Case(
        "notifications.restore",
        lambda c: c.notifications.restore(7),
        "POST",
        "/api/v2/notification/7/restore/",
    ),
    _Case(
        "subusers.list",
        lambda c: c.subusers.list(),
        "GET",
        "/api/v2/subuser/",
        response=_EMPTY_PAGE,
    ),
    _Case(
        "subusers.create",
        lambda c: c.subusers.create(label="Test"),
        "POST",
        "/api/v2/subuser/",
        body={"label": "Test"},
    ),
    _Case("subusers.get", lambda c: c.subusers.get(2), "GET", "/api/v2/subuser/2/"),
    _Case(
        "subusers.update",
        lambda c: c.subusers.update(2, label="New"),
        "PATCH",
        "/api/v2/subuser/2/",
        body={"label": "New"},
    ),
    _Case(
        "subusers.delete",
        lambda c: c.subusers.delete(2),
        "DELETE",
        "/api/v2/subuser/2/",
        response="",
    ),
    _Case(
        "subusers.refresh_proxy_list",
        lambda c: c.subusers.refresh_proxy_list(2),
        "POST",
        "/api/v2/subuser/2/refresh/",
    ),
    _Case(
        "proxy_config.get_stats",
        lambda c: c.proxy_config.get_stats(plan_id=1),
        "GET",
        "/api/v3/proxy/list/stats",
        query={"plan_id": ["1"]},
    ),
    _Case(
        "proxy_config.get_status",
        lambda c: c.proxy_config.get_status(plan_id=1),
        "GET",
        "/api/v3/proxy/list/status",
        query={"plan_id": ["1"]},
    ),
    _Case(
        "payment_methods.list",
        lambda c: c.payment_methods.list(),
        "GET",
        "/api/v2/payment/method/",
        response=_EMPTY_PAGE,
    ),
    _Case(
        "payment_methods.get",
        lambda c: c.payment_methods.get(3),
        "GET",
        "/api/v2/payment/method/3/",
    ),
    _Case(
        "pending_payments.list",
        lambda c: c.pending_payments.list(),
        "GET",
        "/api/v2/payment/pending/",
        response=_EMPTY_PAGE,
    ),
    _Case(
        "pending_payments.get",
        lambda c: c.pending_payments.get(3),
        "GET",
        "/api/v2/payment/pending/3/",
    ),
]


@pytest.mark.parametrize("case", REQUEST_SHAPE_CASES, ids=[c.label for c in REQUEST_SHAPE_CASES])
def test_resource_request_shapes(server: MockServer, client: Webshare, case: _Case) -> None:
    if case.response == "":
        server.enqueue(status=204)
    else:
        server.enqueue(json_body=case.response)
    case.call(client)
    request = server.requests[-1]
    assert request.method == case.method
    assert request.path == case.path
    assert request.query == case.query
    if case.body is not _NO_BODY:
        assert request.json() == case.body
