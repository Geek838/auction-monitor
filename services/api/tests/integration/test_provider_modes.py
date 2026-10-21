import socket

import pytest
from fastapi.testclient import TestClient

from app.main import app, get_provider
from app.providers.registry import build_provider, get_selected_provider


@pytest.fixture
def client_for():
    def configured(mode):
        provider = build_provider(mode)
        app.dependency_overrides[get_provider] = lambda: provider
        return TestClient(app)

    yield configured
    app.dependency_overrides.pop(get_provider, None)


@pytest.mark.parametrize("mode,context_mode,data_type,available", [
    ("fixture", "FIXTURE", "MOCK", True),
    ("simulation", "SIMULATED", "SIMULATED", True),
    ("bidcars", "EXTERNAL", "UNAVAILABLE", False),
])
def test_health_reports_selected_provider_without_claiming_disabled_access(client_for, mode, context_mode, data_type, available):
    with client_for(mode) as client:
        response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["provider_context"]["id"] == mode
    assert data["provider_context"]["mode"] == context_mode
    assert data["provider_context"]["available"] is available
    assert data["data_type"] == data_type
    if mode == "bidcars":
        assert data["provider_context"]["authorization"] == "DENIED"
        assert data["provider_context"]["enabled"] is False


@pytest.mark.parametrize("mode", ["fixture", "simulation"])
@pytest.mark.parametrize("url,status", [
    ("https://copart.com/lot/51374586", "MATCHED"),
    ("https://copart.com/lot/70000001", "AMBIGUOUS"),
    ("https://copart.com/lot/99999999", "NOT_FOUND"),
    ("https://iaai.com/VehicleDetail/45371195~US", "UNRESOLVED_ID"),
    ("https://copart.com/lot/70000003", "SOURCE_UNAVAILABLE"),
    ("https://copart.com/lot/70000004", "NOT_AUTHORIZED"),
])
def test_each_resolution_outcome_preserves_actual_mode_context(client_for, mode, url, status):
    with client_for(mode) as client:
        response = client.post("/api/v1/auction/resolve", json={"url": url})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == status
    assert data["provider_context"]["id"] == mode
    assert data["provider_context"]["mode"] == ("FIXTURE" if mode == "fixture" else "SIMULATED")
    if status == "MATCHED":
        assert data["provenance"]["data_type"] == ("MOCK" if mode == "fixture" else "SIMULATED")
        assert data["provenance"]["realtime"] is False
    else:
        assert data["vehicle"] is None and data["provenance"] is None
    if status in {"SOURCE_UNAVAILABLE", "NOT_AUTHORIZED"}:
        assert data["provider_context"]["available"] is False
    if status == "NOT_AUTHORIZED":
        assert data["provider_context"]["authorization"] == "DENIED"


@pytest.mark.parametrize("mode", ["fixture", "simulation", "bidcars"])
def test_registry_operations_remain_offline_and_never_silently_fall_back(client_for, mode, monkeypatch):
    def no_network(*args, **kwargs):
        pytest.fail("Offline provider selection or resolution attempted external networking")

    monkeypatch.setattr(socket, "getaddrinfo", no_network)
    monkeypatch.setattr(socket.socket, "connect", no_network)
    with client_for(mode) as client:
        data = client.post("/api/v1/auction/resolve", json={
            "url": "https://copart.com/lot/51374586?redirect=http://169.254.169.254/"}).json()
    assert data["provider_context"]["id"] == mode
    if mode == "bidcars":
        assert data["status"] == "NOT_AUTHORIZED"
        assert data["vehicle"] is None and data["candidates"] == []
    elif mode == "simulation":
        assert data["status"] == "MATCHED"
        assert data["provenance"]["data_type"] == "SIMULATED"
        assert data["provenance"]["provider"] != "FIXTURE"


def test_iaai_mapping_evidence_and_event_fields_are_returned(client_for):
    with client_for("fixture") as client:
        response = client.post("/api/v1/auction/resolve", json={"url": "https://iaai.com/VehicleDetail/41000001~US"})
    data = response.json()
    assert data["status"] == "MATCHED"
    mapping = data["mapping_evidence"]
    assert mapping["page_id"] == "41000001" and mapping["country"] == "US"
    assert mapping["identity"]["lot_or_stock_number"] == "45371195"
    assert mapping["origin"]["reference"] != data["provenance"]["source_url"]
    assert data["reference_evidence"]["origin"]["observed_at"]
    assert data["event_id"] and data["record_id"] and data["event_id"] != data["record_id"]
    for key in ["identity.house", "identity.lot_or_stock_number", "event_id", "event_date", "event_status"]:
        assert data["field_evidence"][key]["kind"] == "SUPPLIED"


@pytest.mark.parametrize("mode", ["fixture", "simulation"])
def test_unsupported_iaai_market_cannot_match_a_us_fixture(client_for, mode):
    with client_for(mode) as client:
        data = client.post("/api/v1/auction/resolve", json={"url": "https://iaai.com/VehicleDetail/41000001~CA"}).json()
    assert data["status"] == "UNRESOLVED_ID"
    assert data["reference"]["country"] == "CA"
    assert data["vehicle"] is None


def test_unknown_selected_provider_is_rejected_without_fixture_fallback(monkeypatch):
    monkeypatch.setenv("AUCTION_PROVIDER", "unregistered-provider")
    get_selected_provider.cache_clear()
    try:
        with pytest.raises(ValueError, match="Unsupported AUCTION_PROVIDER"):
            get_selected_provider()
    finally:
        get_selected_provider.cache_clear()


@pytest.mark.parametrize("failure", [RuntimeError("private-provider-secret"), TimeoutError("private-provider-secret"), ValueError("private-provider-secret")])
def test_provider_failure_details_are_not_exposed_or_misreported(failure, caplog):
    class FailingProvider:
        async def resolve(self, reference):
            raise failure

    app.dependency_overrides[get_provider] = lambda: FailingProvider()
    try:
        with TestClient(app) as client:
            response = client.post("/api/v1/auction/resolve", json={"url": "https://copart.com/lot/51374586"})
        assert response.status_code == 200
        assert response.json()["status"] == "SOURCE_UNAVAILABLE"
        assert response.json()["vehicle"] is None
        assert "private-provider-secret" not in response.text
        assert "private-provider-secret" not in caplog.text
    finally:
        app.dependency_overrides.pop(get_provider, None)
