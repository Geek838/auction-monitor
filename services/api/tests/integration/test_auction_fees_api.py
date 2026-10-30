"""Fee estimate contract: explicit consent, exact binding and no fake fallback."""
from decimal import Decimal
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.auction_fees.runtime import FeeClient, FeeSourceFailure

INPUT = {'consent_to_send': True, 'bid_amount': '5000.00', 'auction': 'copart',
         'bid_type': 'online', 'bid_pay': 'secured', 'bid_vehicle': 'standard', 'volume': 'low'}


def source(bid='5000', fee='1030', total='6030'):
    return {'quote': {'bidAmount': Decimal(bid), 'auctionFees': {'auctionFee': Decimal(fee),
            'totalAmount': Decimal(total)}}, 'towing': None}


def test_explicit_request_returns_undated_unverified_estimate(monkeypatch):
    sent = []
    def request(self, req):
        sent.append(req.model_dump())
        return source()
    monkeypatch.setattr(FeeClient, 'request_json', request)
    with TestClient(app) as client:
        response = client.post('/api/v1/auction-fees/estimate', json=INPUT)
    assert response.status_code == 200
    report = response.json()
    assert sent == [INPUT]
    assert report['outcome'] == 'ESTIMATED'
    assert report['source_kind'] == 'INDICATIVE_EXTERNAL_UNVERIFIED'
    assert report['auction_fee'] == '1030.00' and report['total_amount'] == '6030.00'
    assert report['schedule_as_of'] is None and report['errors'] == []
    assert response.headers['cache-control'].startswith('no-store')


@pytest.mark.parametrize('patch', [
    {'consent_to_send': False}, {'consent_to_send': 'true'}, {'bid_amount': 5000},
    {'bid_amount': '0'}, {'bid_amount': '-1'}, {'bid_amount': '1.234'},
    {'bid_pay': 'high'}, {'bid_vehicle': 'licensed'}, {'volume': None},
    {'source_url': 'http://127.0.0.1'}, {'fromCity': 'Tbilisi'},
])
def test_invalid_or_unconsented_input_does_not_contact_source(monkeypatch, patch):
    def forbidden(*args): pytest.fail('invalid inputs must not contact source')
    monkeypatch.setattr(FeeClient, 'request_json', forbidden)
    with TestClient(app) as client:
        result = client.post('/api/v1/auction-fees/estimate', json=INPUT | patch)
    assert result.status_code == 422


@pytest.mark.parametrize('body', [
    source('5001'), source(total='6031'), source(fee='-1'), source(fee='0.001'),
    {'quote': {}}, {'quote': {'bidAmount': Decimal('5000'), 'auctionFees': {'auctionFee': True, 'totalAmount': Decimal('5001')}}},
    source() | {'towing': {'price': 1}},
])
def test_untrusted_or_mismatched_data_withholds_amount(monkeypatch, body):
    monkeypatch.setattr(FeeClient, 'request_json', lambda self, req: body)
    with TestClient(app) as client:
        report = client.post('/api/v1/auction-fees/estimate', json=INPUT).json()
    assert report['outcome'] == 'UNAVAILABLE'
    assert report['auction_fee'] is None and report['total_amount'] is None
    assert report['errors'][0]['code'] == 'INVALID_RESPONSE'


def test_provider_failure_never_becomes_zero_fee(monkeypatch):
    def fail(*args): raise FeeSourceFailure('RATE_LIMITED', 'Source rate limit.')
    monkeypatch.setattr(FeeClient, 'request_json', fail)
    with TestClient(app) as client:
        report = client.post('/api/v1/auction-fees/estimate', json=INPUT).json()
    assert report['outcome'] == 'UNAVAILABLE' and report['auction_fee'] is None
    assert report['errors'][0]['code'] == 'RATE_LIMITED'


def test_iaai_options_and_body_limit(monkeypatch):
    monkeypatch.setattr(FeeClient, 'request_json', lambda self, req: source())
    data = INPUT | {'auction': 'iaai', 'bid_pay': 'standard', 'bid_vehicle': 'licensed', 'volume': None}
    with TestClient(app) as client:
        assert client.post('/api/v1/auction-fees/estimate', json=data).json()['outcome'] == 'ESTIMATED'
        assert client.post('/api/v1/auction-fees/estimate', json=data | {'volume': 'low'}).status_code == 422
        assert client.post('/api/v1/auction-fees/estimate', content=b' ' * 4097).status_code == 413
