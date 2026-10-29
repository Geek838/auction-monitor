"""User-declared financial scenarios: exact arithmetic, missing evidence and bid limits."""
from copy import deepcopy
from datetime import date, timedelta
from decimal import Decimal
import socket

from fastapi.testclient import TestClient
import pytest

from app.main import app
from app.budgets.models import business_today

CATEGORIES = ['auction_broker', 'us_transport', 'ocean_port', 'georgia_clearance', 'registration', 'parts', 'labor', 'diagnostics', 'contingency', 'other']


@pytest.fixture
def client():
    with TestClient(app) as value:
        yield value


def scenario():
    today = business_today()
    evidence = {'kind': 'QUOTE', 'source': 'Engineering quote, not a real supplier', 'as_of': today.isoformat(), 'expires_on': (today + timedelta(days=1)).isoformat()}
    return {
        'currency': 'USD', 'hammer_bid': '5000.00',
        'costs': [{'category': 'parts', 'label': 'Engineering fixture parts', 'low': '100.00', 'base': '200.00', 'high': '300.00', **evidence}],
        'not_applicable': [{'category': category, 'reason': 'Explicitly excluded for this arithmetic test only'} for category in CATEGORIES if category != 'parts'],
        'auction_fees': {'tiers': [{'from_bid': '0.00', 'to_bid': None, 'flat': '50.00', 'percent': '10.0000'}], **evidence},
        'market_value': '10000.00', 'required_savings': '1000.00', 'risk_reserve': '500.00',
    }


def evaluate(client, payload):
    response = client.post('/api/v1/budgets/evaluate', json=payload)
    assert response.status_code == 200, response.text
    return response, response.json()


def test_complete_user_scenario_totals_and_indicative_maximum_are_decimal_safe(client):
    response, report = evaluate(client, scenario())
    assert report['schema_version'] == 'budget-v1'
    assert report['source_kind'] == 'USER_SUPPLIED_UNVERIFIED'
    assert report['status'] == 'COMPLETE'
    assert report['known_non_bid_totals'] == {'low': '100.00', 'base': '200.00', 'high': '300.00'}
    assert report['auction_fee_at_bid'] == '550.00'
    assert report['total_at_bid'] == {'low': '5650.00', 'base': '5750.00', 'high': '5850.00'}
    assert report['max_bid']['status'] == 'INDICATIVE'
    assert report['max_bid']['amount'] == '7409.09'
    assert report['max_bid']['auction_fee_at_max'] == '790.91'
    assert report['missing_categories'] == []
    assert 'no-store' in response.headers['cache-control']
    assert response.headers['x-content-type-options'] == 'nosniff'
    assert all(isinstance(report['total_at_bid'][key], str) for key in ['low', 'base', 'high'])


def test_maximum_bid_fits_and_one_cent_more_does_not(client):
    payload = scenario()
    _, report = evaluate(client, payload)
    maximum = report['max_bid']['amount']
    bound = Decimal(payload['market_value']) - Decimal(payload['required_savings']) - Decimal(payload['risk_reserve'])
    payload['hammer_bid'] = maximum
    _, at_limit = evaluate(client, payload)
    assert Decimal(at_limit['total_at_bid']['high']) <= bound
    payload['hammer_bid'] = f'{Decimal(maximum) + Decimal("0.01"):.2f}'
    _, over_limit = evaluate(client, payload)
    assert Decimal(over_limit['total_at_bid']['high']) > bound


def test_fee_jump_can_make_the_cent_below_a_boundary_the_maximum(client):
    payload = scenario()
    payload['costs'][0].update(low='0.00', base='0.00', high='0.00')
    payload['auction_fees']['tiers'] = [
        {'from_bid': '0.00', 'to_bid': '5000.00', 'flat': '100.00', 'percent': '0'},
        {'from_bid': '5000.00', 'to_bid': None, 'flat': '500.00', 'percent': '0'},
    ]
    payload.update(market_value='5300.00', required_savings='0.00', risk_reserve='0.00')
    _, report = evaluate(client, payload)
    assert report['max_bid']['amount'] == '4999.99'
    payload['hammer_bid'] = '4999.99'
    _, before = evaluate(client, payload)
    payload['hammer_bid'] = '5000.00'
    _, after = evaluate(client, payload)
    assert before['auction_fee_at_bid'] == '100.00'
    assert after['auction_fee_at_bid'] == '500.00'
    assert Decimal(before['total_at_bid']['high']) < Decimal('5300') < Decimal(after['total_at_bid']['high'])


def test_fee_half_cent_rounds_up_instead_of_binary_float_rounding(client):
    payload = scenario()
    payload['hammer_bid'] = '0.05'
    payload['auction_fees']['tiers'][0].update(flat='0.00', percent='10')
    _, report = evaluate(client, payload)
    assert report['auction_fee_at_bid'] == '0.01'


@pytest.mark.parametrize('missing', CATEGORIES)
def test_missing_category_is_unknown_not_zero_and_withholds_all_in_and_max_bid(client, missing):
    payload = scenario()
    payload['costs'] = [item for item in payload['costs'] if item['category'] != missing]
    payload['not_applicable'] = [item for item in payload['not_applicable'] if item['category'] != missing]
    _, report = evaluate(client, payload)
    assert report['status'] == 'INCOMPLETE'
    assert missing in report['missing_categories']
    assert report['total_at_bid'] is None
    assert report['max_bid']['status'] == 'WITHHELD'
    assert report['max_bid']['amount'] is None
    assert report['known_total_at_bid'] is not None


@pytest.mark.parametrize('location,field', [('cost', 'source'), ('cost', 'as_of'), ('cost', 'expires_on'), ('fees', 'source'), ('fees', 'as_of'), ('fees', 'expires_on')])
def test_missing_quote_evidence_does_not_become_a_complete_estimate(client, location, field):
    payload = scenario()
    target = payload['costs'][0] if location == 'cost' else payload['auction_fees']
    target[field] = None
    _, report = evaluate(client, payload)
    assert report['status'] == 'INCOMPLETE'
    assert report['issues']
    assert report['total_at_bid'] is None
    assert report['max_bid']['status'] == 'WITHHELD'


@pytest.mark.parametrize('location', ['cost', 'fees'])
def test_expired_quote_is_kept_in_known_subtotal_but_blocks_confident_outputs(client, location):
    payload = scenario()
    target = payload['costs'][0] if location == 'cost' else payload['auction_fees']
    target['as_of'] = (business_today() - timedelta(days=2)).isoformat()
    target['expires_on'] = (business_today() - timedelta(days=1)).isoformat()
    _, report = evaluate(client, payload)
    assert report['status'] == 'INCOMPLETE'
    assert report['known_non_bid_totals']['high'] == '300.00'
    assert report['total_at_bid'] is None
    assert report['max_bid']['status'] == 'WITHHELD'


def test_assumptions_can_only_produce_an_explicitly_indicative_scenario(client):
    payload = scenario()
    for target in [payload['costs'][0], payload['auction_fees']]:
        target.update(kind='ASSUMPTION', expires_on=None)
    _, report = evaluate(client, payload)
    assert report['status'] == 'COMPLETE'
    assert report['max_bid']['status'] == 'INDICATIVE'
    assert report['source_kind'] == 'USER_SUPPLIED_UNVERIFIED'
    assert report['warnings']


@pytest.mark.parametrize('field', ['market_value', 'required_savings', 'risk_reserve'])
def test_missing_bid_decision_input_withholds_bid_without_invalidating_known_totals(client, field):
    payload = scenario()
    payload[field] = None
    _, report = evaluate(client, payload)
    assert report['status'] == 'COMPLETE'
    assert report['total_at_bid'] is not None
    assert report['max_bid']['status'] == 'WITHHELD'
    assert report['max_bid']['amount'] is None


def test_known_costs_exceeding_market_budget_has_no_feasible_bid(client):
    payload = scenario()
    payload.update(market_value='100.00', required_savings='0.00', risk_reserve='0.00')
    _, report = evaluate(client, payload)
    assert report['max_bid']['status'] == 'NO_FEASIBLE_BID'
    assert report['max_bid']['amount'] is None


@pytest.mark.parametrize('value', [10, 0.1, True, '-0.01', '1e3', 'NaN', 'Infinity', '0.001', '1000000000.01', '', ' 1.00'])
def test_money_requires_nonnegative_bounded_decimal_strings(client, value):
    payload = scenario()
    payload['hammer_bid'] = value
    assert client.post('/api/v1/budgets/evaluate', json=payload).status_code == 422


@pytest.mark.parametrize('mutation', ['reversed_range', 'duplicate_na', 'cost_and_na', 'future_quote', 'expires_before_source', 'empty_na_reason', 'wrong_currency', 'financial_extra'])
def test_invalid_or_conflicting_evidence_is_rejected(client, mutation):
    payload = scenario()
    if mutation == 'reversed_range': payload['costs'][0]['low'] = '999.00'
    elif mutation == 'duplicate_na': payload['not_applicable'].append(deepcopy(payload['not_applicable'][0]))
    elif mutation == 'cost_and_na': payload['not_applicable'].append({'category': 'parts', 'reason': 'Contradicting the included cost'})
    elif mutation == 'future_quote': payload['costs'][0]['as_of'] = (business_today() + timedelta(days=1)).isoformat()
    elif mutation == 'expires_before_source': payload['costs'][0]['expires_on'] = (business_today() - timedelta(days=1)).isoformat()
    elif mutation == 'empty_na_reason': payload['not_applicable'][0]['reason'] = ' '
    elif mutation == 'wrong_currency': payload['currency'] = 'GEL'
    elif mutation == 'financial_extra': payload['official_georgian_tax'] = 'invented-rule'
    assert client.post('/api/v1/budgets/evaluate', json=payload).status_code == 422


@pytest.mark.parametrize('tiers', [
    [{'from_bid': '1.00', 'to_bid': None, 'flat': '0', 'percent': '0'}],
    [{'from_bid': '0', 'to_bid': '100', 'flat': '0', 'percent': '0'}, {'from_bid': '101', 'to_bid': None, 'flat': '0', 'percent': '0'}],
    [{'from_bid': '0', 'to_bid': '100', 'flat': '0', 'percent': '0'}, {'from_bid': '99', 'to_bid': None, 'flat': '0', 'percent': '0'}],
    [{'from_bid': '0', 'to_bid': '100', 'flat': '50', 'percent': '0'}, {'from_bid': '100', 'to_bid': None, 'flat': '10', 'percent': '0'}],
    [{'from_bid': '0', 'to_bid': '100', 'flat': '0', 'percent': '0'}],
    [{'from_bid': '0', 'to_bid': None, 'flat': '0', 'percent': '100.0001'}],
])
def test_fee_schedules_cannot_have_gaps_overlaps_decreasing_fees_or_unbounded_percentages(client, tiers):
    payload = scenario()
    payload['auction_fees']['tiers'] = tiers
    assert client.post('/api/v1/budgets/evaluate', json=payload).status_code == 422


def test_calculator_does_not_need_network_or_selected_provider_access(client, monkeypatch):
    def unexpected(*args, **kwargs):
        raise AssertionError('budget evaluation attempted outbound network access')
    monkeypatch.setattr(socket.socket, 'connect', unexpected)
    monkeypatch.setattr(socket, 'getaddrinfo', unexpected)
    _, report = evaluate(client, scenario())
    assert report['status'] == 'COMPLETE'


def test_unknown_fee_schedule_withholds_total_and_is_not_treated_as_a_free_auction(client):
    payload = scenario(); payload['auction_fees'] = None
    _, report = evaluate(client, payload)
    assert report['auction_fee_at_bid'] is None
    assert report['known_total_at_bid']['high'] == '5300.00'
    assert report['total_at_bid'] is None
    assert report['max_bid']['status'] == 'WITHHELD'
    assert any(issue['code'] == 'MISSING_AUCTION_FEES' for issue in report['issues'])


def test_budget_body_limit_is_64_kib_and_streamed_excess_is_not_parsed(client):
    import json
    base = json.dumps({'hammer_bid': '1.00'}).encode()
    exact = base + b' ' * (64 * 1024 - len(base))
    assert client.post('/api/v1/budgets/evaluate', content=exact, headers={'Content-Type': 'application/json'}).status_code == 200
    response = client.post('/api/v1/budgets/evaluate', content=iter([exact, b' ']), headers={'Content-Type': 'application/json'})
    assert response.status_code == 413
    assert '64 KiB' in response.json()['detail']
