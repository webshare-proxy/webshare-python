"""Happy-path coverage across resource groups: paths, encoding, decoding."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pytest

from tests.conftest import MockServer
from webshare import Webshare


@pytest.fixture
def client(server: MockServer) -> Webshare:
    return Webshare(base_url=server.base_url, api_key="k")


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
