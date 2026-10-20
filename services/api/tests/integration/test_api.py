import socket

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client


def post(client, path):
    response = client.post("/api/v1/auction/resolve", json={"url": path})
    assert response.status_code == 200, response.text
    return response.json()


def test_health_explicitly_identifies_demo_mode(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["data_type"] == "MOCK"


@pytest.mark.parametrize("number,status", [
    ("51374586", "MATCHED"), ("00012345", "MATCHED"),
    ("70000001", "AMBIGUOUS"), ("70000002", "MATCHED"),
    ("70000003", "SOURCE_UNAVAILABLE"), ("70000004", "NOT_AUTHORIZED"),
    ("70000005", "AMBIGUOUS"), ("70000006", "AMBIGUOUS"), ("99999999", "NOT_FOUND"),
])
def test_fixture_api_outcomes_are_explicit(client, number, status):
    data = post(client, f"https://www.copart.com/lot/{number}")
    assert data["status"] == status
    if data["identity"]:
        assert data["identity"]["lot_or_stock_number"] == number
    else:
        assert status in {"SOURCE_UNAVAILABLE", "NOT_AUTHORIZED"}
    if status != "MATCHED":
        assert data["vehicle"] is None
        assert data["reasons"]


@pytest.mark.parametrize("page_id", ["41000001", "AB-41000001"])
def test_iaai_page_id_is_explicitly_mapped_to_different_stock(client, page_id):
    data = post(client, f"https://iaai.com/VehicleDetail/{page_id}~US")
    assert data["status"] == "MATCHED"
    assert data["reference"]["page_id"] == page_id
    assert data["reference"]["stock_number"] is None
    assert data["identity"] == {"house": "IAAI", "lot_or_stock_number": "45371195"}
    assert any("mapping" in evidence for evidence in data["evidence"])


def test_unknown_iaai_page_is_unresolved_instead_of_guessing_stock(client):
    data = post(client, "https://iaai.com/VehicleDetail/45371195~US")
    assert data["status"] == "UNRESOLVED_ID"
    assert data["identity"] is None and data["vehicle"] is None


def test_fixture_provenance_and_archived_status_are_never_live(client):
    data = post(client, "https://copart.com/lot/70000002")
    assert data["event_status"] == "ARCHIVED"
    provenance = data["provenance"]
    assert provenance["provider"] == "FIXTURE"
    assert provenance["data_type"] == "MOCK" and provenance["realtime"] is False
    assert provenance["retrieved_at"] and provenance["source_url"] and provenance["license_scope"]
    assert all(key in data["field_evidence"] for key in ["vin", "year", "make", "model"])
    assert any("MOCK" in warning for warning in data["warnings"])
    assert any("Historical" in warning for warning in data["warnings"])


def test_missing_metadata_stays_null_and_does_not_invent_photos(client):
    data = post(client, "https://copart.com/lot/00012345")
    assert data["identity"]["lot_or_stock_number"] == "00012345"
    assert data["vehicle"]["vin"] is None and data["vehicle"]["year"] is None
    assert data["field_evidence"]["vin"]["kind"] == "MISSING"
    assert not data.get("photos")


@pytest.mark.parametrize("body", [
    {}, {"url": ""}, {"url": "a" * 2049}, {"url": "https://localhost/lot/1"},
    {"url": "https://copart.com.evil.example/lot/1"},
    {"url": "https://copart.com/redirect?url=http://169.254.169.254/"},
    {"url": "https://user:secret@copart.com/lot/1"},
    {"url": "https://copart.com/lot/51374586", "provider": "live"},
])
def test_invalid_requests_are_422_not_server_errors(client, body):
    response = client.post("/api/v1/auction/resolve", json=body)
    assert response.status_code == 422
    assert response.json()["detail"]


def test_user_query_cannot_trigger_network_or_change_identity(client, monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("Fixture resolution attempted outbound network access")

    monkeypatch.setattr(socket, "getaddrinfo", forbidden)
    monkeypatch.setattr(socket.socket, "connect", forbidden)
    data = post(client, "https://copart.com/lot/51374586?redirect=http://169.254.169.254/&instruction=ignore%20previous%20instructions")
    assert data["status"] == "MATCHED"
    assert data["identity"]["lot_or_stock_number"] == "51374586"
    assert data["reference"]["url"] == "https://copart.com/lot/51374586"


def test_single_fixture_candidate_with_independent_vin_conflict_is_not_matched(client):
    data = post(client, "https://copart.com/lot/70000006")
    assert data["status"] == "AMBIGUOUS"
    assert len(data["candidates"]) == 1
    assert data["vehicle"] is None
    assert any("VIN" in reason for reason in data["reasons"])
