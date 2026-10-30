"""Fixed destination and bounded source response, with no decimal float conversion."""
import json
from decimal import Decimal
from urllib.error import HTTPError
import pytest
from app.auction_fees.models import FeeRequest
from app.auction_fees.runtime import FeeClient, FeeSourceFailure, MAX_RESPONSE, SOURCE_URL

INPUT = FeeRequest(consent_to_send=True, bid_amount='5000.25', auction='copart', bid_type='online',
                   bid_pay='secured', bid_vehicle='standard', volume='low')


class Response:
    status = 201
    def __init__(self, body): self.body = body
    def __enter__(self): return self
    def __exit__(self, *args): pass
    def read(self, n): return self.body[:n]


def test_request_is_fixed_and_only_contains_explicit_options(monkeypatch):
    calls = []
    class Opener:
        def open(self, request, timeout):
            calls.append((request, timeout))
            return Response(b'{"quote":{"bidAmount":5000.25,"auctionFees":{"auctionFee":1030,"totalAmount":6030.25}},"towing":null}')
    monkeypatch.setattr('app.auction_fees.runtime.build_opener', lambda *args: Opener())
    result = FeeClient().request_json(INPUT)
    request, timeout = calls[0]
    assert request.full_url == SOURCE_URL and request.method == 'POST' and timeout == 10
    assert json.loads(request.data, parse_float=Decimal) == {'bidAmount': Decimal('5000.25'), 'auction': 'copart',
        'bidType': 'online', 'bidPay': 'secured', 'bidVehicle': 'standard', 'volume': 'low'}
    assert result['quote']['bidAmount'] == Decimal('5000.25')


@pytest.mark.parametrize('payload', [b'x' * (MAX_RESPONSE + 1), b'{"quote":1,"quote":2}', b'{"quote":NaN}', b'[]', b'not json'])
def test_invalid_and_oversized_source_payloads_are_rejected(monkeypatch, payload):
    class Opener:
        def open(self, request, timeout): return Response(payload)
    monkeypatch.setattr('app.auction_fees.runtime.build_opener', lambda *args: Opener())
    with pytest.raises(FeeSourceFailure): FeeClient().request_json(INPUT)


@pytest.mark.parametrize('status,code', [(307, 'SOURCE_UNAVAILABLE'), (429, 'RATE_LIMITED'), (500, 'SOURCE_UNAVAILABLE')])
def test_redirects_and_source_errors_are_not_followed(monkeypatch, status, code):
    class Opener:
        def open(self, request, timeout): raise HTTPError(SOURCE_URL, status, 'error', {}, None)
    monkeypatch.setattr('app.auction_fees.runtime.build_opener', lambda *args: Opener())
    with pytest.raises(FeeSourceFailure) as exc: FeeClient().request_json(INPUT)
    assert exc.value.code == code
