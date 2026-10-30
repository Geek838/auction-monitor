"""Official-source conversion arithmetic and conservative temporal semantics."""
from copy import deepcopy
from datetime import datetime, timezone
from decimal import Decimal

from fastapi.testclient import TestClient
import pytest

from app.main import app
from app.exchange import service
from app.exchange.runtime import ExchangeSourceFailure, NbgClient

NOW = datetime(2026, 10, 30, 10, tzinfo=timezone.utc)
PAYLOAD = {'amount': '100.00', 'from_currency': 'USD', 'to_currency': 'GEL'}


def source(effective='2026-10-30', rate='2.5959', quantity=1):
    return [{'date': effective + 'T00:00:00.000Z', 'currencies': [{
        'code': 'USD', 'quantity': quantity, 'rate': Decimal(rate), 'rateFormated': rate,
        'date': effective + 'T00:00:00.000Z', 'validFromDate': effective + 'T00:00:00.000Z'}]}]


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(service, 'utc_now', lambda: NOW)
    monkeypatch.setattr(NbgClient, 'request_json', lambda self: source())
    with TestClient(app) as value:
        yield value


def test_official_quote_conversion_keeps_effective_and_retrieval_provenance(client):
    response = client.post('/api/v1/exchange/convert', json=PAYLOAD)
    assert response.status_code == 200
    result = response.json()
    assert result['outcome'] == 'CONVERTED' and result['converted_amount'] == '259.59'
    assert result['source'] == 'NATIONAL_BANK_OF_GEORGIA'
    assert result['quote'] == {'currency': 'USD', 'quantity': 1, 'rate_gel': '2.5959',
        'gel_per_usd': '2.5959', 'effective_date': '2026-10-30', 'published_at': '2026-10-30T00:00:00Z',
        'age_days': 0, 'freshness': 'EFFECTIVE_TODAY'}
    assert result['retrieved_at'] == '2026-10-30T10:00:00Z'
    assert result['rounding'] == 'ROUND_HALF_UP_2_DECIMAL_PLACES'
    assert result['warnings'] and result['request'] == PAYLOAD
    assert 'no-store' in response.headers['cache-control']
    assert response.headers['x-content-type-options'] == 'nosniff'


@pytest.mark.parametrize('amount,rate,direction,expected', [
    ('0', '2.5959', 'USD', '0.00'), ('0.01', '2.5', 'USD', '0.03'),
    ('1', '2.0001', 'USD', '2.00'), ('2.5959', '2.5959', 'GEL', None),
    ('1.00', '8', 'GEL', '0.13'), ('259.59', '2.5959', 'GEL', '100.00'),
    ('1000000000.00', '1000000', 'USD', '1000000000000000.00'),
    ('1.00', '0.000001', 'GEL', '1000000.00'),
])
def test_exact_decimal_and_half_up_rounding(client, monkeypatch, amount, rate, direction, expected):
    monkeypatch.setattr(NbgClient, 'request_json', lambda self: source(rate=rate))
    response = client.post('/api/v1/exchange/convert', json={
        'amount': amount, 'from_currency': direction, 'to_currency': 'GEL' if direction == 'USD' else 'USD'})
    if expected is None:
        assert response.status_code == 422  # Fractional input beyond cents is never silently rounded.
    else:
        assert response.status_code == 200
        assert response.json()['converted_amount'] == expected


def test_quote_quantity_is_normalized_before_conversion(client, monkeypatch):
    monkeypatch.setattr(NbgClient, 'request_json', lambda self: source(rate='259.59', quantity=100))
    report = client.post('/api/v1/exchange/convert', json=PAYLOAD).json()
    assert report['quote']['quantity'] == 100
    assert report['quote']['gel_per_usd'] == '2.5959'
    assert report['converted_amount'] == '259.59'


@pytest.mark.parametrize('effective,outcome,freshness,age,amount', [
    ('2026-10-29', 'CONVERTED', 'PREVIOUS_EFFECTIVE_DATE', 1, '259.59'),
    ('2026-10-26', 'CONVERTED', 'PREVIOUS_EFFECTIVE_DATE', 4, '259.59'),
    ('2026-10-25', 'STALE', 'STALE', 5, None),
])
def test_application_age_threshold_is_explicit_not_a_statutory_expiry(client, monkeypatch, effective, outcome, freshness, age, amount):
    monkeypatch.setattr(NbgClient, 'request_json', lambda self: source(effective))
    report = client.post('/api/v1/exchange/convert', json=PAYLOAD).json()
    assert report['outcome'] == outcome and report['converted_amount'] == amount
    assert report['quote']['age_days'] == age and report['quote']['freshness'] == freshness
    assert report['max_age_days'] == 4
    assert any('application freshness policy' in warning for warning in report['warnings'])


def test_weekend_previous_effective_quote_is_not_invented_as_today(client, monkeypatch):
    monkeypatch.setattr(service, 'utc_now', lambda: datetime(2026, 11, 1, 8, tzinfo=timezone.utc))
    report = client.post('/api/v1/exchange/convert', json=PAYLOAD).json()
    assert report['outcome'] == 'CONVERTED'
    assert report['quote']['effective_date'] == '2026-10-30'
    assert report['quote']['age_days'] == 2


def test_georgia_midnight_controls_age_not_server_utc_day(client, monkeypatch):
    monkeypatch.setattr(service, 'utc_now', lambda: datetime(2026, 10, 30, 21, tzinfo=timezone.utc))
    report = client.post('/api/v1/exchange/convert', json=PAYLOAD).json()
    assert report['quote']['age_days'] == 1


def test_source_date_is_captured_before_request_and_age_recalculated_at_midnight(client, monkeypatch):
    times = iter([datetime(2026, 10, 30, 19, 59, tzinfo=timezone.utc),
                  datetime(2026, 10, 30, 19, 59, tzinfo=timezone.utc),
                  datetime(2026, 10, 30, 20, 1, tzinfo=timezone.utc),
                  datetime(2026, 10, 30, 20, 1, tzinfo=timezone.utc)])
    monkeypatch.setattr(service, 'utc_now', lambda: next(times))
    observed = []
    def get(self):
        observed.append(self.requested_on.isoformat())
        return source('2026-10-30')
    monkeypatch.setattr(NbgClient, 'request_json', get)
    report = client.post('/api/v1/exchange/convert', json=PAYLOAD).json()
    assert observed == ['2026-10-30'] and report['source_request_date'] == '2026-10-30'
    assert report['quote']['age_days'] == 1 and report['quote']['freshness'] == 'PREVIOUS_EFFECTIVE_DATE'


def test_next_day_quote_cannot_become_usable_during_midnight_crossing(client, monkeypatch):
    times = iter([datetime(2026, 10, 30, 19, 59, tzinfo=timezone.utc),
                  datetime(2026, 10, 30, 19, 59, tzinfo=timezone.utc),
                  datetime(2026, 10, 30, 20, 1, tzinfo=timezone.utc),
                  datetime(2026, 10, 30, 20, 1, tzinfo=timezone.utc)])
    monkeypatch.setattr(service, 'utc_now', lambda: next(times))
    monkeypatch.setattr(NbgClient, 'request_json', lambda self: source('2026-10-31'))
    report = client.post('/api/v1/exchange/convert', json=PAYLOAD).json()
    assert report['outcome'] == 'UNAVAILABLE' and report['converted_amount'] is None


def test_tomorrow_published_today_is_withheld_until_effective(client, monkeypatch):
    body = source('2026-10-31')
    body[0]['currencies'][0]['date'] = '2026-10-30T08:00:00.000Z'
    monkeypatch.setattr(NbgClient, 'request_json', lambda self: body)
    report = client.post('/api/v1/exchange/convert', json=PAYLOAD).json()
    assert report['outcome'] == 'NOT_YET_EFFECTIVE' and report['converted_amount'] is None
    assert report['quote']['freshness'] == 'FUTURE_EFFECTIVE_DATE'


@pytest.mark.parametrize('amount', [True, 10, 10.25, '-1', 'NaN', 'Infinity', '1e3', '.50', '00.2', '1.234', '1000000000.01'])
def test_invalid_money_rejected_before_network(client, monkeypatch, amount):
    def never(self):
        pytest.fail('No source call for invalid request')
    monkeypatch.setattr(NbgClient, 'request_json', never)
    assert client.post('/api/v1/exchange/convert', json=PAYLOAD | {'amount': amount}).status_code == 422


@pytest.mark.parametrize('extra', [{'to_currency': 'EUR'}, {'from_currency': 'GEL'}, {'source_url': 'http://localhost'}, {'date': '2026-01-01'}])
def test_unsupported_or_caller_controlled_source_fields_rejected(client, extra):
    assert client.post('/api/v1/exchange/convert', json=PAYLOAD | extra).status_code == 422


@pytest.mark.parametrize('mutation', [
    'empty', 'multiple_dates', 'wrong_currency', 'duplicate_currency', 'missing_quantity',
    'bool_quantity', 'zero_quantity', 'float_quantity', 'negative_rate', 'zero_rate', 'infinite_rate',
    'float_rate', 'string_rate', 'bool_rate', 'too_precise_rate', 'missing_date', 'mismatched_date',
    'non_midnight_effective', 'future_publication', 'missing_publication', 'invalid_timestamp',
])
def test_untrusted_source_shape_never_releases_a_numeric_conversion(client, monkeypatch, mutation):
    body = source(); row = body[0]['currencies'][0]
    if mutation == 'empty': body = []
    elif mutation == 'multiple_dates': body.append(deepcopy(body[0]))
    elif mutation == 'wrong_currency': row['code'] = 'EUR'
    elif mutation == 'duplicate_currency': body[0]['currencies'].append(deepcopy(row))
    elif mutation == 'missing_quantity': row.pop('quantity')
    elif mutation == 'bool_quantity': row['quantity'] = True
    elif mutation == 'zero_quantity': row['quantity'] = 0
    elif mutation == 'float_quantity': row['quantity'] = 1.0
    elif mutation == 'negative_rate': row['rate'] = Decimal('-2')
    elif mutation == 'zero_rate': row['rate'] = 0
    elif mutation == 'infinite_rate': row['rate'] = Decimal('Infinity')
    elif mutation == 'float_rate': row['rate'] = 2.59
    elif mutation == 'string_rate': row['rate'] = '2.59'
    elif mutation == 'bool_rate': row['rate'] = True
    elif mutation == 'too_precise_rate': row['rate'] = Decimal('2.1234567890123')
    elif mutation == 'missing_date': body[0].pop('date')
    elif mutation == 'mismatched_date': row['validFromDate'] = '2026-10-29T00:00:00Z'
    elif mutation == 'non_midnight_effective': body[0]['date'] = row['validFromDate'] = '2026-10-30T12:00:00Z'
    elif mutation == 'future_publication': row['date'] = '2026-11-01T00:00:00Z'
    elif mutation == 'missing_publication': row.pop('date')
    elif mutation == 'invalid_timestamp': row['date'] = 'yesterday'
    monkeypatch.setattr(NbgClient, 'request_json', lambda self: body)
    report = client.post('/api/v1/exchange/convert', json=PAYLOAD).json()
    assert report['outcome'] == 'UNAVAILABLE' and report['converted_amount'] is None and report['quote'] is None
    assert report['errors'][0]['code'] == 'INVALID_RESPONSE'


def test_upstream_failure_is_sanitized(client, monkeypatch):
    def fail(self):
        raise ExchangeSourceFailure('SOURCE_UNAVAILABLE', 'Official service unavailable.')
    monkeypatch.setattr(NbgClient, 'request_json', fail)
    report = client.post('/api/v1/exchange/convert', json=PAYLOAD).json()
    assert report['outcome'] == 'UNAVAILABLE' and report['converted_amount'] is None
    assert report['errors'][0]['code'] == 'SOURCE_UNAVAILABLE'


def test_busy_has_no_unbounded_queue_or_network_call(client, monkeypatch):
    class Busy:
        def acquire(self, blocking): return False
        def release(self): pytest.fail('Unacquired semaphore cannot be released')
    monkeypatch.setattr(service, 'REQUEST_SLOTS', Busy())
    monkeypatch.setattr(NbgClient, 'request_json', lambda self: pytest.fail('Must not fetch when busy'))
    report = client.post('/api/v1/exchange/convert', json=PAYLOAD).json()
    assert report['outcome'] == 'UNAVAILABLE' and report['errors'][0]['code'] == 'BUSY'


def test_semaphore_is_released_after_invalid_source(client, monkeypatch):
    from threading import BoundedSemaphore
    slots = BoundedSemaphore(1)
    monkeypatch.setattr(service, 'REQUEST_SLOTS', slots)
    monkeypatch.setattr(NbgClient, 'request_json', lambda self: [])
    assert client.post('/api/v1/exchange/convert', json=PAYLOAD).json()['outcome'] == 'UNAVAILABLE'
    assert slots.acquire(blocking=False)
    slots.release()


def test_body_limit_precedes_json_parse(client):
    response = client.post('/api/v1/exchange/convert', content=b' ' * 4097, headers={'Content-Type': 'application/json'})
    assert response.status_code == 413 and 'no-store' in response.headers['cache-control']


def test_full_official_currency_feed_selects_usd_by_code_not_array_position(client, monkeypatch):
    body = source()
    body[0]['currencies'].insert(0, {'code': 'EUR', 'quantity': 1, 'rate': Decimal('3.1')})
    body[0]['currencies'].append({'code': 'JPY', 'quantity': 100, 'rate': Decimal('1.7')})
    monkeypatch.setattr(NbgClient, 'request_json', lambda self: body)
    report = client.post('/api/v1/exchange/convert', json=PAYLOAD).json()
    assert report['outcome'] == 'CONVERTED' and report['converted_amount'] == '259.59'


def test_oversized_currency_row_list_is_rejected(client, monkeypatch):
    body = source()
    body[0]['currencies'].extend({'code': 'EUR'} for _ in range(100))
    monkeypatch.setattr(NbgClient, 'request_json', lambda self: body)
    report = client.post('/api/v1/exchange/convert', json=PAYLOAD).json()
    assert report['outcome'] == 'UNAVAILABLE' and report['converted_amount'] is None
