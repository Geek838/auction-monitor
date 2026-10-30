"""Free manufacturer decoding enriches facts without proving auction identity."""
from copy import deepcopy

from fastapi.testclient import TestClient
import pytest

from app.main import app
from app.vin_lookup.service import VpicClient

VIN = '1HGCM82633A004352'


@pytest.fixture
def client():
    with TestClient(app) as value:
        yield value


def source_row():
    return {'VIN': VIN, 'Make': 'HONDA', 'Model': 'Accord', 'ModelYear': '2003', 'ErrorCode': '0', 'ErrorText': '0 - VIN decoded clean. Engineering response fixture.'}


def source_double(monkeypatch, row=None, value=None):
    calls = []
    def request(self, vin):
        calls.append(vin)
        return deepcopy(value if value is not None else {'Count': 1, 'Results': [row if row is not None else source_row()]})
    monkeypatch.setattr(VpicClient, 'request_json', request)
    return calls


def test_manufacturer_facts_are_decoded_from_the_free_source_without_becoming_an_auction_match(client, monkeypatch):
    calls = source_double(monkeypatch)
    response = client.post('/api/v1/vehicles/decode-vin', json={'vin': ' 1hgcm82633a004352 '})
    assert response.status_code == 200, response.text
    report = response.json()
    assert calls == [VIN]
    assert report['schema_version'] == 'vin-decode-v1'
    assert report['vin'] == VIN and report['outcome'] == 'DECODED'
    assert report['source'] == 'NHTSA_VPIC'
    assert report['identity_status'] == 'NOT_AUCTION_VERIFIED'
    assert report['vehicle'] == {'year': 2003, 'make': 'HONDA', 'model': 'Accord', 'body_class': None, 'drive_type': None, 'fuel_type': None, 'engine_displacement_cc': None}
    assert report['source_url'].startswith('https://vpic.nhtsa.dot.gov/')
    assert report['retrieved_at'] and report['warnings']
    assert 'MATCHED' not in report.values() and 'auction_house' not in report and 'record_id' not in report
    assert 'no-store' in response.headers['cache-control']


@pytest.mark.parametrize('vin', ['1HGCM82633A00435', '1HGCM82633A0043523', '1HGCM82633A00435I', '1HGCM82633A00435O', '1HGCM82633A00435Q', '１HGCM82633A004352', 'https://evil.test/', 12345678901234567, True])
def test_invalid_vin_syntax_is_rejected_before_any_source_request(client, monkeypatch, vin):
    calls = source_double(monkeypatch)
    response = client.post('/api/v1/vehicles/decode-vin', json={'vin': vin})
    assert response.status_code == 422
    assert calls == []


def test_a_client_cannot_supply_a_different_provider_url_or_verified_identity(client, monkeypatch):
    calls = source_double(monkeypatch)
    response = client.post('/api/v1/vehicles/decode-vin', json={'vin': VIN, 'source_url': 'http://127.0.0.1/admin', 'identity_status': 'MATCHED'})
    assert response.status_code == 422 and calls == []


@pytest.mark.parametrize('mutation', ['nonzero_error', 'missing_model', 'missing_year'])
def test_partial_decodes_are_not_promoted_to_fully_decoded_facts(client, monkeypatch, mutation):
    row = source_row()
    if mutation == 'nonzero_error': row.update(ErrorCode='1,5', ErrorText='Check digit/other source caveat')
    elif mutation == 'missing_model': row['Model'] = ''
    elif mutation == 'missing_year': row['ModelYear'] = ''
    source_double(monkeypatch, row=row)
    response = client.post('/api/v1/vehicles/decode-vin', json={'vin': VIN})
    assert response.status_code == 200
    report = response.json()
    assert report['outcome'] == 'PARTIAL'
    assert report['identity_status'] == 'NOT_AUCTION_VERIFIED'
    assert report['vehicle']['make'] == 'HONDA'


def test_source_invalid_vin_response_with_no_useful_fields_remains_invalid(client, monkeypatch):
    row = source_row(); row.update(Make='', Model='', ModelYear='', ErrorCode='7', ErrorText='VIN is not decodable')
    source_double(monkeypatch, row=row)
    response = client.post('/api/v1/vehicles/decode-vin', json={'vin': VIN})
    assert response.status_code == 200
    report = response.json()
    assert report['outcome'] == 'INVALID_VIN'
    assert report['vehicle'] == {'year': None, 'make': None, 'model': None, 'body_class': None, 'drive_type': None, 'fuel_type': None, 'engine_displacement_cc': None}
    assert report['errors']


@pytest.mark.parametrize('mutation', ['different_vin', 'missing_vin', 'multiple_rows', 'no_results', 'wrong_results_type'])
def test_mismatched_or_malformed_source_rows_do_not_enrich_a_different_vehicle(client, monkeypatch, mutation):
    row = source_row()
    value = {'Count': 1, 'Results': [row]}
    if mutation == 'different_vin': row['VIN'] = '5YJ3E1EA7JF000001'
    elif mutation == 'missing_vin': row.pop('VIN')
    elif mutation == 'multiple_rows': value['Results'].append(deepcopy(row))
    elif mutation == 'no_results': value['Results'] = []
    elif mutation == 'wrong_results_type': value['Results'] = {'VIN': VIN}
    source_double(monkeypatch, value=value)
    response = client.post('/api/v1/vehicles/decode-vin', json={'vin': VIN})
    assert response.status_code == 200
    report = response.json()
    assert report['outcome'] == 'UNAVAILABLE'
    assert report['vehicle'] == {'year': None, 'make': None, 'model': None, 'body_class': None, 'drive_type': None, 'fuel_type': None, 'engine_displacement_cc': None}
    assert report['identity_status'] == 'NOT_AUCTION_VERIFIED'


def test_source_failure_is_sanitized_and_does_not_apply_manufacturing_facts(client, monkeypatch):
    from app.vin_lookup.runtime import VinSourceFailure
    def unavailable(*args, **kwargs):
        raise VinSourceFailure('SOURCE_UNAVAILABLE', 'Manufacturer service unavailable.')
    monkeypatch.setattr(VpicClient, 'request_json', unavailable)
    response = client.post('/api/v1/vehicles/decode-vin', json={'vin': VIN})
    assert response.status_code == 200
    report = response.json()
    assert report['outcome'] == 'UNAVAILABLE'
    assert report['vehicle'] == {'year': None, 'make': None, 'model': None, 'body_class': None, 'drive_type': None, 'fuel_type': None, 'engine_displacement_cc': None}
    assert report['errors'][0]['code'] == 'SOURCE_UNAVAILABLE'


def test_vin_request_body_is_bounded_to_four_kib_before_json_parsing(client):
    import json
    base = json.dumps({'vin': VIN}).encode()
    exact = base + b' ' * (4 * 1024 - len(base))
    response = client.post('/api/v1/vehicles/decode-vin', content=iter([exact, b' ']), headers={'Content-Type': 'application/json'})
    assert response.status_code == 413
    assert '4 KiB' in response.json()['detail']


def test_missing_source_facts_with_clean_decode_code_does_not_prove_a_vin_invalid(client, monkeypatch):
    row = source_row(); row.update(Make='', Model='', ModelYear='', ErrorCode='0')
    source_double(monkeypatch, row=row)
    response = client.post('/api/v1/vehicles/decode-vin', json={'vin': VIN})
    assert response.status_code == 200
    report = response.json()
    assert report['outcome'] == 'PARTIAL'
    assert report['vehicle'] == {'year': None, 'make': None, 'model': None, 'body_class': None, 'drive_type': None, 'fuel_type': None, 'engine_displacement_cc': None}
    assert report['identity_status'] == 'NOT_AUCTION_VERIFIED'


def test_extra_manufacturer_specifications_are_reported_without_verifying_vehicle_or_tax(client, monkeypatch):
    row = source_row()
    row.update(BodyClass='Sedan/Saloon', DriveType='FWD', FuelTypePrimary='Gasoline', DisplacementCC='2400.0')
    source_double(monkeypatch, row=row)
    report = client.post('/api/v1/vehicles/decode-vin', json={'vin': VIN}).json()
    assert report['vehicle']['body_class'] == 'Sedan/Saloon'
    assert report['vehicle']['drive_type'] == 'FWD'
    assert report['vehicle']['fuel_type'] == 'Gasoline'
    assert report['vehicle']['engine_displacement_cc'] == '2400.0'
    assert report['identity_status'] == 'NOT_AUCTION_VERIFIED'


def test_specs_without_basic_vehicle_fields_are_partial_not_invalid(client, monkeypatch):
    row = source_row()
    row.update(Make='', Model='', ModelYear='', ErrorCode='1', BodyClass='Sedan/Saloon')
    source_double(monkeypatch, row=row)
    report = client.post('/api/v1/vehicles/decode-vin', json={'vin': VIN}).json()
    assert report['outcome'] == 'PARTIAL'
    assert report['vehicle']['body_class'] == 'Sedan/Saloon'
