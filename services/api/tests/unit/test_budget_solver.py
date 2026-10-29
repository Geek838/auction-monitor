"""Independent whole-cent oracle for the monotonic bid/fee solver."""
from datetime import timedelta
from decimal import Decimal, ROUND_HALF_UP

import pytest

from app.budgets.models import BudgetRequest, CATEGORIES, business_today
from app.budgets.service import evaluate_budget


def request_data():
    return {
        'hammer_bid': '1.00', 'currency': 'USD',
        'costs': [{'category': 'parts', 'label': 'Arithmetic test only', 'low': '0', 'base': '0', 'high': '0', 'kind': 'ASSUMPTION', 'source': 'Engineering test assumption', 'as_of': business_today().isoformat()}],
        'not_applicable': [{'category': category, 'reason': 'Explicit engineering-case exclusion'} for category in CATEGORIES if category != 'parts'],
        'auction_fees': {'kind': 'ASSUMPTION', 'source': 'Engineering fee function', 'as_of': business_today().isoformat(), 'tiers': [
            {'from_bid': '0', 'to_bid': '5', 'flat': '0', 'percent': '3.2500'},
            {'from_bid': '5', 'to_bid': None, 'flat': '1', 'percent': '5'},
        ]},
        'market_value': '10', 'required_savings': '0', 'risk_reserve': '0',
    }


@pytest.mark.parametrize('market,savings,reserve,cost', [('10', '0', '0', '0'), ('5.50', '0', '0', '0'), ('10', '1.01', '0.37', '2.13'), ('1', '0.70', '0.29', '0'), ('1', '0.80', '0.20', '0.01')])
def test_binary_search_matches_independent_exhaustive_cent_oracle(market, savings, reserve, cost):
    data = request_data()
    data.update(market_value=market, required_savings=savings, risk_reserve=reserve)
    data['costs'][0].update(low=cost, base=cost, high=cost)
    available = Decimal(market) - Decimal(savings) - Decimal(reserve)
    best = None
    for cents in range(1, int(Decimal(market) * 100) + 1):
        bid = Decimal(cents) / 100
        # Independent direct enumeration; no production fee helper or solver call.
        fee = (bid * Decimal('0.0325') if bid < 5 else 1 + bid * Decimal('0.05')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        if bid + fee + Decimal(cost) <= available: best = f'{bid:.2f}'
    report = evaluate_budget(BudgetRequest.model_validate(data))
    assert report.max_bid.amount == best
    assert report.max_bid.status == ('INDICATIVE' if best is not None else 'NO_FEASIBLE_BID')


def test_aggregation_can_exceed_per_input_limit_without_rounding_or_overflow():
    data = request_data()
    row = data['costs'][0]
    data['costs'] = [{**row, 'label': f'Engineering line {i}', 'low': '1000000000', 'base': '1000000000', 'high': '1000000000'} for i in range(60)]
    report = evaluate_budget(BudgetRequest.model_validate(data))
    assert report.known_non_bid_totals.high == '60000000000.00'
    assert report.max_bid.status == 'NO_FEASIBLE_BID'


def test_expiry_is_inclusive_and_rechecked_on_each_evaluation():
    data = request_data()
    start = business_today() - timedelta(days=10)
    expiry = start + timedelta(days=1)
    for evidence in [data['costs'][0], data['auction_fees']]:
        evidence.update(kind='QUOTE', as_of=start.isoformat(), expires_on=expiry.isoformat())
    request = BudgetRequest.model_validate(data)
    assert evaluate_budget(request, today=expiry).status == 'COMPLETE'
    expired = evaluate_budget(request, today=expiry + timedelta(days=1))
    assert expired.status == 'INCOMPLETE' and expired.max_bid.status == 'WITHHELD'
    assert sum(issue.code == 'EXPIRED_SOURCE' for issue in expired.issues) == 2
