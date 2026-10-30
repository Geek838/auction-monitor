"""Documented Apibara contract exercised with transport doubles, never live data."""
import json
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlsplit

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.providers import apibara
from app.providers.registry import get_selected_provider

URL = 'https://www.copart.com/lot/00012345?tracking=discard#x'
FAKE_KEY = 'test-key-not-real'


class Response:
    def __init__(self, value): self.value = value
    def __enter__(self): return self
    def __exit__(self, *args): pass
    def read(self, count): return self.value[:count]


def source(**overrides):
    data = {'platform': 'copart', 'lot_number': '00012345', 'vin': '1HGCM82633A004352',
            'year': 2003, 'make': 'HONDA', 'model': 'Accord', 'damage': 'FRONT',
            'media': {'images': ['https://untrusted.example/image.jpg']}}
    data.update(overrides)
    return json.dumps({'data': data}).encode()


@pytest.fixture
def configured(monkeypatch):
    monkeypatch.setenv('AUCTION_PROVIDER', 'apibara')
    monkeypatch.setenv('APIBARA_ENABLE', '1')
    monkeypatch.setenv('APIBARA_API_KEY', FAKE_KEY)
    get_selected_provider.cache_clear()
    yield
    get_selected_provider.cache_clear()


def transport(monkeypatch, content=None, error=None):
    seen = []
    class Opener:
        def open(self, req, timeout):
            seen.append((req, timeout))
            if error: raise error
            return Response(content if content is not None else source())
    monkeypatch.setattr(apibara, 'build_opener', lambda *args: Opener())
    return seen


def post(client, url=URL):
    result = client.post('/api/v1/auction/resolve', json={'url': url})
    assert result.status_code == 200
    return result.json()


def test_exact_copart_provider_record_is_attributed_without_license_or_live_claims(configured, monkeypatch):
    seen = transport(monkeypatch)
    with TestClient(app) as client: result = post(client)
    assert result['status'] == 'MATCHED'
    assert result['identity']['lot_or_stock_number'] == '00012345'
    assert result['provider_context']['authorization'] == 'UNVERIFIED'
    assert result['provenance']['data_type'] == 'EXTERNAL_UNVERIFIED'
    assert result['provenance']['source_observed_at'] is None
    assert not result['provenance']['realtime'] and result['event_status'] == 'UNKNOWN'
    assert result['freshness']['status'] == 'UNKNOWN'
    assert not result['preview_eligibility']['available']
    assert 'untrusted.example' not in json.dumps(result)
    assert FAKE_KEY not in json.dumps(result)
    req, timeout = seen[0]
    assert req.full_url.startswith(apibara.ENDPOINT + '?') and timeout == 15
    assert parse_qs(urlsplit(req.full_url).query) == {'url': ['https://www.copart.com/lot/00012345']}
    assert req.get_header('X-api-key') == FAKE_KEY


def test_health_describes_configured_external_provider_without_claiming_live_access(configured):
    with TestClient(app) as client:
        response = client.get('/api/v1/health')
    assert response.json()['data_type'] == 'EXTERNAL_UNVERIFIED'
    assert response.json()['provider_context']['authorization'] == 'UNVERIFIED'


def test_iaai_page_is_unresolved_without_spending_an_api_request(configured, monkeypatch):
    seen = transport(monkeypatch)
    with TestClient(app) as client: result = post(client, 'https://iaai.com/VehicleDetail/00004567~US')
    assert result['status'] == 'UNRESOLVED_ID' and result['identity'] is None
    assert result['reference']['page_id'] == '00004567' and not seen


@pytest.mark.parametrize('payload', [source(lot_number='12345'), source(platform='iaai')])
def test_mismatching_lot_or_auction_cannot_match(configured, monkeypatch, payload):
    transport(monkeypatch, payload)
    with TestClient(app) as client: result = post(client)
    assert result['status'] == 'AMBIGUOUS' and result['vehicle'] is None


@pytest.mark.parametrize('payload', [b'{}', b'{"data":null}', b'{"data":{"platform":"copart"}}',
    b'{"data":{"platform":"copart","lot_number":12345}}', b'{"data":{"platform":"copart","platform":"iaai"}}',
    b'x' * (1024 * 1024 + 1)])
def test_malformed_or_oversized_responses_are_unavailable_not_missing(configured, monkeypatch, payload):
    transport(monkeypatch, payload)
    with TestClient(app) as client: result = post(client)
    assert result['status'] == 'SOURCE_UNAVAILABLE' and result['vehicle'] is None


@pytest.mark.parametrize('code,status', [(401, 'NOT_AUTHORIZED'), (403, 'NOT_AUTHORIZED'), (404, 'NOT_FOUND'),
                                         (429, 'SOURCE_UNAVAILABLE'), (500, 'SOURCE_UNAVAILABLE'), (302, 'SOURCE_UNAVAILABLE')])
def test_provider_http_errors_are_distinct(configured, monkeypatch, code, status):
    error = HTTPError('https://example.invalid', code, 'private detail', {}, None)
    transport(monkeypatch, error=error)
    with TestClient(app) as client: result = post(client)
    assert result['status'] == status and 'private detail' not in json.dumps(result)


def test_missing_opt_in_or_key_never_contacts_provider(configured, monkeypatch):
    seen = transport(monkeypatch)
    for variable in ['APIBARA_ENABLE', 'APIBARA_API_KEY']:
        old = __import__('os').environ[variable]
        monkeypatch.delenv(variable)
        get_selected_provider.cache_clear()
        with TestClient(app) as client: result = post(client)
        assert result['status'] == 'NOT_AUTHORIZED'
        monkeypatch.setenv(variable, old)
    assert not seen


def test_missing_or_masked_vin_not_invented(configured, monkeypatch):
    transport(monkeypatch, source(vin='1HGCM826****'))
    with TestClient(app) as client: result = post(client)
    assert result['status'] == 'MATCHED' and result['vehicle']['vin'] is None
    assert any('VIN is unavailable' in warning for warning in result['warnings'])


def test_network_failure_never_returns_not_found(configured, monkeypatch):
    transport(monkeypatch, error=URLError('private network information'))
    with TestClient(app) as client: result = post(client)
    assert result['status'] == 'SOURCE_UNAVAILABLE' and 'private network information' not in json.dumps(result)
