"""Public preview requests exercise the real resolver, guarded catalog and mock engine."""
import hashlib
from io import BytesIO
import socket
from urllib.parse import urlencode

from fastapi.testclient import TestClient
from PIL import Image
import pytest

from app.main import app, get_provider
from app.providers.registry import build_provider

COPART = "https://copart.com/lot/51374586"
IAAI = "https://iaai.com/VehicleDetail/41000001~US"


@pytest.fixture
def configured_client():
    clients = []

    def create(mode="fixture", provider=None):
        selected = provider or build_provider(mode)
        app.dependency_overrides[get_provider] = lambda: selected
        client = TestClient(app)
        clients.append(client)
        return client, selected

    yield create
    for client in clients:
        client.close()
    app.dependency_overrides.pop(get_provider, None)


def resolve(client, url=COPART):
    response = client.post("/api/v1/auction/resolve", json={"url": url})
    assert response.status_code == 200, response.text
    return response.json()


def preview(client, url=COPART, fingerprint=None):
    if fingerprint is None:
        fingerprint = resolve(client, url)["snapshot_fingerprint"]
    response = client.post("/api/v1/inspections", json={"url": url, "expected_snapshot_fingerprint": fingerprint})
    assert response.status_code == 200, response.text
    return response


@pytest.mark.parametrize("mode", ["fixture", "simulation"])
@pytest.mark.parametrize("url", [COPART, IAAI])
def test_complete_preview_binds_authorized_raster_bytes_to_exact_target_and_seeded_evidence(configured_client, mode, url):
    client, _ = configured_client(mode)
    listing = resolve(client, url)
    assert listing["status"] == "MATCHED"
    assert listing["preview_eligibility"]["available"] is True
    assert len(listing["snapshot_fingerprint"]) == 64
    response = preview(client, url, listing["snapshot_fingerprint"])
    report = response.json()
    assert report["outcome"] == "COMPLETED"
    assert report["target"]["snapshot_fingerprint"] == listing["snapshot_fingerprint"]
    assert report["target"]["record_id"] == listing["record_id"]
    assert report["target"]["event_id"] == listing["event_id"]
    assert report["target"]["provider_context"]["mode"] == listing["provider_context"]["mode"]
    assert report["provenance"]["mode"] == "MOCK"
    assert all(report["provenance"][field] is None for field in ["model_provider", "model_id", "prompt_version"])
    assert {finding["classification"] for finding in report["findings"]} == {"OBSERVED", "SUSPECTED", "UNKNOWN"}
    assert all(finding["confidence"] is None and finding["localization"] is None for finding in report["findings"])
    assert report["checks"] and report["limitations"]
    assert "no-store" in response.headers["cache-control"]
    asset_ids = {asset["asset_id"] for asset in report["assets"]}
    for finding in report["findings"]:
        assert set(finding["image_ids"]) <= asset_ids
    for asset in report["assets"]:
        image_response = client.get(asset["asset_url"])
        assert image_response.status_code == 200, image_response.text
        assert image_response.headers["content-type"].startswith("image/png")
        assert image_response.headers["x-content-type-options"] == "nosniff"
        assert "no-store" in image_response.headers["cache-control"]
        assert hashlib.sha256(image_response.content).hexdigest() == asset["content_sha256"]
        with Image.open(BytesIO(image_response.content)) as image:
            image.load()
            assert image.size == (asset["width"], asset["height"])
            assert image.format == "PNG"
        assert asset["source_kind"] == "SELF_AUTHORED_FIXTURE"
        assert asset["capture_time"] is None
        assert asset["rights_reference"] and asset["author"]


def test_iaai_preview_keeps_page_country_stock_and_event_separate(configured_client):
    client, _ = configured_client()
    report = preview(client, IAAI).json()
    target = report["target"]
    assert target["reference"]["page_id"] == "41000001"
    assert target["reference"]["country"] == "US"
    assert target["reference"]["stock_number"] is None
    assert target["identity"]["lot_or_stock_number"] == "45371195"
    assert target["record_id"] != target["event_id"]


@pytest.mark.parametrize("url,status", [
    ("https://copart.com/lot/70000001", "AMBIGUOUS"),
    ("https://copart.com/lot/99999999", "NOT_FOUND"),
    ("https://iaai.com/VehicleDetail/41000001~CA", "UNRESOLVED_ID"),
    ("https://copart.com/lot/70000003", "SOURCE_UNAVAILABLE"),
    ("https://copart.com/lot/70000004", "NOT_AUTHORIZED"),
])
def test_non_matched_resolution_cannot_be_promoted_to_an_inspection(configured_client, url, status):
    client, _ = configured_client()
    report = preview(client, url, "a" * 64).json()
    assert report["outcome"] == "BLOCKED"
    assert report["resolver_status"] == status
    assert report["assets"] == [] and report["findings"] == [] and report["provenance"] is None


@pytest.mark.parametrize("url", ["https://copart.com/lot/00012345", "https://copart.com/lot/70000007", "https://copart.com/lot/70000008"])
def test_explicit_missing_failed_and_unknown_only_scenarios_never_claim_a_clean_vehicle(configured_client, url):
    client, _ = configured_client()
    listing = resolve(client, url)
    assert listing["status"] == "MATCHED"
    report = preview(client, url, listing["snapshot_fingerprint"]).json()
    if url.endswith("00012345"):
        assert listing["preview_eligibility"]["available"] is False
        assert report["outcome"] == "BLOCKED"
        assert report["findings"] == [] and report["assets"] == []
    elif url.endswith("70000007"):
        assert report["outcome"] == "FAILED"
        assert report["findings"] == [] and report["assets"] == [] and report["provenance"] is None
    else:
        assert report["outcome"] == "COMPLETED"
        assert report["findings"] and all(item["classification"] == "UNKNOWN" for item in report["findings"])
        assert report["checks"] and report["limitations"]


def test_partial_archive_excludes_unpermitted_evidence_without_refreshing_history(configured_client):
    client, _ = configured_client()
    report = preview(client, "https://copart.com/lot/70000002").json()
    assert report["outcome"] == "PARTIAL"
    assert report["target"]["freshness"]["status"] == "HISTORICAL"
    assert report["target"]["event_status"] == "ARCHIVED"
    assert report["assets"] and report["exclusions"]
    excluded = {item["asset_id"] for item in report["exclusions"]}
    assert all(not (set(item["image_ids"]) & excluded) for item in report["findings"])


@pytest.mark.parametrize("field", ["record_id", "event_id", "vehicle", "source-observation", "field-evidence"])
def test_changed_snapshot_content_on_same_url_requires_resolution_refresh(configured_client, field):
    client, provider = configured_client()
    original = resolve(client)
    record = provider.provider.records["copart-demo"]
    if field == "vehicle":
        # A partial field outside identity cross-checks still changes snapshot content.
        record.vehicle.trim = "Different trim revision"
    elif field == "source-observation":
        from datetime import timedelta
        record.provenance.source_observed_at += timedelta(seconds=1)
    elif field == "field-evidence":
        record.field_evidence["trim"].note = "Revised source metadata evidence"
    else:
        setattr(record, field, "changed-" + getattr(record, field))
    report = preview(client, COPART, original["snapshot_fingerprint"]).json()
    assert report["outcome"] == "BLOCKED"
    assert report["reason_code"] == "TARGET_CHANGED"
    assert report["assets"] == [] and report["findings"] == []


def test_a_fingerprint_from_another_provider_mode_or_vehicle_does_not_authorize_preview(configured_client):
    client, _ = configured_client("fixture")
    fingerprint = resolve(client)["snapshot_fingerprint"]
    simulation_client, _ = configured_client("simulation")
    report = preview(simulation_client, COPART, fingerprint).json()
    assert report["outcome"] == "BLOCKED" and report["reason_code"] == "TARGET_CHANGED"
    iaai = preview(simulation_client, IAAI, fingerprint).json()
    assert iaai["outcome"] == "BLOCKED"


def test_disabled_external_provider_has_no_inspection_or_image_fallback(configured_client):
    client, _ = configured_client("bidcars")
    result = resolve(client)
    assert result["status"] == "NOT_AUTHORIZED"
    report = preview(client, COPART, "a" * 64).json()
    assert report["outcome"] == "BLOCKED" and report["resolver_status"] == "NOT_AUTHORIZED"
    assert report["findings"] == [] and report["assets"] == []
    response = client.get('/api/v1/inspection-assets/front-illustration-v1?' + urlencode({"url": COPART, "expected_snapshot_fingerprint": "a" * 64}))
    assert response.status_code in {403, 409}
    assert not response.headers.get("content-type", "").startswith("image/")


@pytest.mark.parametrize("body", [
    {}, {"url": COPART}, {"url": COPART, "expected_snapshot_fingerprint": "x"},
    {"url": COPART, "expected_snapshot_fingerprint": "a" * 64, "findings": []},
    {"url": COPART, "expected_snapshot_fingerprint": "a" * 64, "provider": "licensed"},
    {"url": "https://127.0.0.1/lot/1", "expected_snapshot_fingerprint": "a" * 64},
])
def test_invalid_or_privilege_extending_preview_requests_are_rejected(configured_client, body):
    client, _ = configured_client()
    response = client.post("/api/v1/inspections", json=body)
    assert response.status_code == 422


def test_preview_and_asset_delivery_do_not_access_network(configured_client, monkeypatch):
    client, _ = configured_client()

    def forbidden(*args, **kwargs):
        pytest.fail("Inspection preview or local asset delivery attempted outbound access")

    monkeypatch.setattr(socket, "getaddrinfo", forbidden)
    monkeypatch.setattr(socket.socket, "connect", forbidden)
    report = preview(client).json()
    assert report["outcome"] == "COMPLETED"
    assert client.get(report["assets"][0]["asset_url"]).status_code == 200


@pytest.mark.parametrize("asset_id", ["rear-illustration-v1", "unknown-image", "../manifest.json", "data:image/png;base64,AAAA"])
def test_asset_route_cannot_serve_a_known_but_unbound_view_or_an_arbitrary_path(configured_client, asset_id):
    client, _ = configured_client()
    fingerprint = resolve(client)["snapshot_fingerprint"]
    response = client.get(f'/api/v1/inspection-assets/{asset_id}?' + urlencode({"url": COPART, "expected_snapshot_fingerprint": fingerprint}))
    assert response.status_code in {404, 422}
    assert not response.headers.get("content-type", "").startswith("image/")


@pytest.mark.parametrize("endpoint", ["/api/v1/inspections", "/api/v1/auction/resolve"])
def test_json_body_limit_precedes_unbounded_document_parsing(configured_client, endpoint):
    client, _ = configured_client()
    response = client.post(endpoint, content=b"x" * (16 * 1024 + 1), headers={"Content-Type": "application/json"})
    assert response.status_code == 413
    assert "no-store" in response.headers["cache-control"]


@pytest.mark.parametrize("endpoint", ["/api/v1/inspections", "/api/v1/auction/resolve"])
def test_small_malformed_json_is_a_client_error_not_a_server_failure(configured_client, endpoint):
    client, _ = configured_client()
    response = client.post(endpoint, content=b'{"url":', headers={"Content-Type": "application/json"})
    assert response.status_code == 422
