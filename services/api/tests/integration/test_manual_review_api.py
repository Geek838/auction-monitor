"""Manual reports never acquire provider verification or send photo bytes externally."""
import asyncio
from copy import deepcopy
import json
import socket

from fastapi.testclient import TestClient
import pytest

from app.main import app
from app.inspections.body_limit import PreviewBodyLimit
from app.providers.registry import get_selected_provider

COPART = "https://copart.com/lot/00012345?tracking=ignored"
IAAI = "https://iaai.com/VehicleDetail/41000001~US"


@pytest.fixture
def client():
    with TestClient(app) as value:
        yield value


def case():
    return {
        "url": COPART,
        "vehicle": {"vin": "1hgcm82633a004352", "year": 2021, "make": "Example", "model": "Engineering fixture"},
        "photos": [{"photo_id": "front-1", "sha256": "a" * 64, "width": 80, "height": 60, "label": "Front"}],
        "findings": [
            {"photo_id": "front-1", "classification": "OBSERVED", "component": "Panel", "description": "User reports a visible mark."},
            {"photo_id": "front-1", "classification": "SUSPECTED", "component": "Attachment", "description": "User asks whether an attachment needs checking."},
            {"classification": "UNKNOWN", "component": "Underside", "description": "No underside evidence is supplied."},
        ],
        "notes": "Engineering fixture only, not a real assessment.",
    }


def test_report_is_manual_unverified_and_does_not_manufacture_auction_or_model_evidence(client):
    payload = case()
    response = client.post("/api/v1/manual-reviews", json=payload)
    assert response.status_code == 200, response.text
    report = response.json()
    assert report["schema_version"] == "manual-review-v1"
    assert report["source_kind"] == "USER_SUPPLIED_UNVERIFIED"
    assert report["verification_status"] == "UNVERIFIED"
    assert report["reference"]["url"] == "https://copart.com/lot/00012345"
    assert report["reference"]["lot_number"] == "00012345"
    assert report["canonical_claim"] == {"house": "COPART", "lot_or_stock_number": "00012345", "verification_status": "UNVERIFIED"}
    assert report["vehicle"]["vin"] == "1HGCM82633A004352"
    assert all(item["source_kind"] == "USER_REPORTED" for item in report["findings"])
    assert report["photos"][0]["verification_status"] == "CLIENT_DECLARED_NOT_SERVER_VERIFIED"
    assert report["photos"][0]["sha256"] == payload["photos"][0]["sha256"]
    assert {item["system"] for item in report["checks"]} == {"Structural integrity", "SRS and airbags", "ADAS", "Cooling", "Suspension", "Mechanical condition"}
    assert all(item["status"] == "UNKNOWN" and item["recommendation"] for item in report["checks"])
    assert "status" not in report and "provider_context" not in report and "provenance" not in report
    assert "no-store" in response.headers["cache-control"]
    assert response.headers["x-content-type-options"] == "nosniff"
    assert any("metadata only" in item for item in report["warnings"])
    assert any("No image analysis" in item for item in report["warnings"])


@pytest.mark.parametrize("stock", [None, "00098765", "41000001"])
def test_iaai_page_country_and_even_equal_claimed_stock_stay_distinct_unverified_fields(client, stock):
    response = client.post("/api/v1/manual-reviews", json={"url": IAAI, "stock_number": stock})
    assert response.status_code == 200, response.text
    report = response.json()
    assert report["reference"]["page_id"] == "41000001"
    assert report["reference"]["country"] == "US"
    assert report["reference"]["stock_number"] is None
    assert report["canonical_claim"]["lot_or_stock_number"] == stock
    assert report["canonical_claim"]["verification_status"] == "UNVERIFIED"
    assert "mapping_evidence" not in report


def test_empty_evidence_report_never_gains_canned_observations(client):
    response = client.post("/api/v1/manual-reviews", json={"url": COPART})
    assert response.status_code == 200
    report = response.json()
    assert report["photos"] == [] and report["findings"] == []
    assert report["vehicle"] == {"vin": None, "year": None, "make": None, "model": None}
    assert len(report["checks"]) == 6


def test_copart_conflicting_manual_identifier_is_rejected_without_guessing(client):
    response = client.post("/api/v1/manual-reviews", json={"url": COPART, "stock_number": "12345"})
    assert response.status_code == 422
    assert "conflicts" in response.json()["detail"]


@pytest.mark.parametrize("field,value", [
    ("vin", "1HGCM82633A00435I"), ("vin", "1HGCM82633A00435O"), ("vin", "1HGCM82633A00435Q"),
    ("vin", "1HGCM82633A00435"), ("vin", "１HGCM82633A004352"),
    ("year", True), ("year", "2021"), ("year", 1899), ("year", 2099),
    ("make", " "), ("model", "x" * 81),
])
def test_invalid_vehicle_claims_are_rejected_at_the_actual_field(client, field, value):
    payload = case()
    payload["vehicle"][field] = value
    response = client.post("/api/v1/manual-reviews", json=payload)
    assert response.status_code == 422
    assert any(error["loc"][-1] == field for error in response.json()["detail"])


@pytest.mark.parametrize("kind", ["OBSERVED", "SUSPECTED"])
def test_visible_user_findings_require_a_referenced_local_photo_claim(client, kind):
    payload = case()
    payload["findings"] = [{"classification": kind, "component": "Panel", "description": "A user report."}]
    assert client.post("/api/v1/manual-reviews", json=payload).status_code == 422


@pytest.mark.parametrize("mutation", ["dangling", "duplicate", "dimension", "dimension_bool", "digest", "remote_photo_id", "seven_photos", "31_findings"])
def test_bad_evidence_links_and_bounds_cannot_be_reported_as_valid(client, mutation):
    payload = case()
    if mutation == "dangling": payload["findings"][0]["photo_id"] = "other-photo"
    elif mutation == "duplicate": payload["photos"].append(deepcopy(payload["photos"][0]))
    elif mutation == "dimension": payload["photos"][0]["width"] = 2049
    elif mutation == "dimension_bool": payload["photos"][0]["width"] = True
    elif mutation == "digest": payload["photos"][0]["sha256"] = "z" * 64
    elif mutation == "remote_photo_id": payload["photos"][0]["photo_id"] = "https://evil.invalid/photo"
    elif mutation == "seven_photos": payload["photos"] += [{**payload["photos"][0], "photo_id": f"photo-{i}"} for i in range(6)]
    elif mutation == "31_findings": payload["findings"] = [{"classification": "UNKNOWN", "component": "Panel", "description": "Not assessed"}] * 31
    response = client.post("/api/v1/manual-reviews", json=payload)
    assert response.status_code == 422, response.text


@pytest.mark.parametrize("location,key,value", [
    ("root", "provider", "fixture"), ("root", "verification_status", "MATCHED"),
    ("root", "expected_snapshot_fingerprint", "a" * 64), ("root", "price", 100),
    ("photo", "data_url", "data:image/png;base64,AAAA"), ("photo", "bytes", "AAAA"),
    ("photo", "asset_url", "https://evil.invalid/photo.png"), ("photo", "verification_status", "VERIFIED"),
    ("finding", "confidence", 0.99), ("finding", "model_id", "invented-model"),
    ("finding", "part_number", "invented"), ("finding", "repair_cost", 50),
])
def test_client_cannot_submit_image_payloads_or_promote_manual_metadata_to_verified_model_output(client, location, key, value):
    payload = case()
    target = payload if location == "root" else payload["photos" if location == "photo" else "findings"][0]
    target[key] = value
    response = client.post("/api/v1/manual-reviews", json=payload)
    assert response.status_code == 422
    assert any(error["type"] == "extra_forbidden" and error["loc"][-1] == key for error in response.json()["detail"])


@pytest.mark.parametrize("url", [
    "http://copart.com/lot/123", "https://copart.com.evil.invalid/lot/123", "https://127.0.0.1/lot/123",
    "https://user:password@copart.com/lot/123", "https://copart.com/lot/%31", "file:///etc/passwd",
])
def test_manual_review_reuses_the_safe_parser_for_original_auction_urls(client, url):
    assert client.post("/api/v1/manual-reviews", json={"url": url}).status_code == 422


@pytest.mark.parametrize("phrase", ["safe to drive", "ROADWORTHY", "no hidden damage", "airbags work", "structure is sound"])
def test_known_unsupported_safety_verdicts_do_not_enter_the_report(client, phrase):
    payload = case()
    payload["findings"][0]["description"] = phrase
    response = client.post("/api/v1/manual-reviews", json=payload)
    assert response.status_code == 422
    assert "safety" in str(response.json()["detail"]).lower()


def test_hostile_text_is_preserved_as_data_for_the_consumer_to_escape(client):
    caption = '<img src=x onerror="alert(1)">'
    payload = case()
    payload["photos"][0]["label"] = caption
    payload["findings"][0]["description"] = caption
    payload["notes"] = caption
    response = client.post("/api/v1/manual-reviews", json=payload)
    assert response.status_code == 200
    report = response.json()
    assert report["notes"] == report["photos"][0]["label"] == report["findings"][0]["description"] == caption
    assert response.headers["content-type"].startswith("application/json")


def test_manual_review_operates_with_denied_provider_without_outbound_socket_or_dns(client, monkeypatch):
    monkeypatch.setenv("AUCTION_PROVIDER", "bidcars")
    get_selected_provider.cache_clear()
    assert client.get("/api/v1/health").json()["provider_context"]["available"] is False
    def unexpected_network(*args, **kwargs):
        raise AssertionError("manual review attempted outbound I/O")
    monkeypatch.setattr(socket.socket, "connect", unexpected_network)
    monkeypatch.setattr(socket, "getaddrinfo", unexpected_network)
    response = client.post("/api/v1/manual-reviews", json=case())
    assert response.status_code == 200
    assert response.json()["source_kind"] == "USER_SUPPLIED_UNVERIFIED"


def test_manual_json_has_32kib_preparse_limit_without_increasing_resolver_limit(client):
    base = json.dumps({"url": COPART}).encode()
    exact = base + b" " * (32 * 1024 - len(base))
    assert client.post("/api/v1/manual-reviews", content=exact, headers={"Content-Type": "application/json"}).status_code == 200
    over = client.post("/api/v1/manual-reviews", content=exact + b" ", headers={"Content-Type": "application/json"})
    assert over.status_code == 413 and "32 KiB" in over.text
    assert "no-store" in over.headers["cache-control"]
    assert client.post("/api/v1/auction/resolve", content=exact[:17 * 1024], headers={"Content-Type": "application/json"}).status_code == 413


def test_manual_streaming_body_without_content_length_cannot_bypass_32kib_cap():
    sent, called = [], []
    chunks = iter([{"type": "http.request", "body": b"x" * 20000, "more_body": True},
                   {"type": "http.request", "body": b"y" * 13000, "more_body": False}])
    async def receive(): return next(chunks)
    async def send(message): sent.append(message)
    async def downstream(scope, receive, send): called.append(True)
    scope = {"type": "http", "method": "POST", "path": "/api/v1/manual-reviews", "headers": []}
    asyncio.run(PreviewBodyLimit(downstream)(scope, receive, send))
    assert called == []
    assert next(item["status"] for item in sent if item["type"] == "http.response.start") == 413
