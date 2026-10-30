"""Component-only rules checked against independently observed official RS calculator cases.

Official UI execution evidence is documented separately; this deterministic suite does
not submit to Revenue Service or establish its upstream availability.
"""
from datetime import datetime, timezone

from fastapi.testclient import TestClient
import pytest

from app.main import app
from app.georgia_excise import service

PAYLOAD = {
    'declaration_year': 2026, 'planned_declaration_date': '2026-10-30',
    'production_year': 2021, 'production_year_confirmed': True, 'engine_cc': 2000,
    'commodity_code': '8703', 'vehicle_category': 'ORDINARY_PASSENGER',
    'powertrain': 'PETROL', 'steering': 'ORIGINAL_LEFT',
    'procedure': 'GEORGIA_FREE_CIRCULATION', 'exemption_claimed': False, 'special_status': False,
}


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(service, 'utc_now', lambda: datetime(2026, 10, 30, 12, tzinfo=timezone.utc))
    with TestClient(app) as value:
        yield value


@pytest.mark.parametrize('year,cc,expected,rate,age', [
    (2021, 2000, '3000.00', '1.50', 5), (2020, 2000, '3000.00', '1.50', 6),
    (2019, 2000, '9000.00', '4.50', 7), (2026, 2000, '3000.00', '1.50', 0),
    (2021, 1000, '1500.00', '1.50', 5), (2021, 1500, '2250.00', '1.50', 5),
    (2019, 3500, '15750.00', '4.50', 7),
])
def test_observed_official_calculator_cases_are_reproduced_as_only_excise(client, year, cc, expected, rate, age):
    response = client.post('/api/v1/georgia/excise', json=PAYLOAD | {'production_year': year, 'engine_cc': cc})
    assert response.status_code == 200
    report = response.json()
    assert report['outcome'] == 'CALCULATED_COMPONENT'
    assert report['excise_amount'] == expected and report['rate_gel_per_cc'] == rate and report['age_years'] == age
    assert report['currency'] == 'GEL' and report['other_clearance_components'] == 'NOT_CALCULATED'
    assert report['source_kind'] == 'STATUTORY_COMPONENT_USER_DECLARED_FACTS'
    assert report['rule']['source_clauses'] == ['Article 188(12)', 'Article 188(13)', 'Article 188(14)', 'Article 188(15)', 'Article 188(16)', 'Article 188(18)']
    assert report['rule']['source_url'].endswith('/ka/document/view/1043717?publication=247')
    assert report['rule']['reviewed_on'] == '2026-10-31' and report['issues'] == []
    assert report['warnings'] and 'no-store' in response.headers['cache-control']
    assert response.headers['x-content-type-options'] == 'nosniff'
    assert 'total_clearance' not in report and 'import_duty' not in report and 'vat' not in report


def test_diesel_same_supported_ordinary_rate_and_exact_half_gel_arithmetic(client):
    report = client.post('/api/v1/georgia/excise', json=PAYLOAD | {'powertrain': 'DIESEL', 'engine_cc': 1999}).json()
    assert report['outcome'] == 'CALCULATED_COMPONENT' and report['excise_amount'] == '2998.50'


@pytest.mark.parametrize('field', list(PAYLOAD))
def test_no_missing_eligibility_fact_is_silently_assumed(client, field):
    payload = {key: value for key, value in PAYLOAD.items() if key != field}
    report = client.post('/api/v1/georgia/excise', json=payload).json()
    assert report['outcome'] == 'WITHHELD'
    assert report['excise_amount'] is None and report['rate_gel_per_cc'] is None and report['age_years'] is None
    assert report['issues']


@pytest.mark.parametrize('field,value,code', [
    ('commodity_code', 'OTHER', 'COMMODITY_CODE_UNSUPPORTED'),
    ('commodity_code', 'UNKNOWN', 'COMMODITY_CODE_UNKNOWN'),
    ('vehicle_category', 'SPORT', 'VEHICLE_CATEGORY_UNSUPPORTED'),
    ('vehicle_category', 'CLASSIC', 'VEHICLE_CATEGORY_UNSUPPORTED'),
    ('vehicle_category', 'OTHER', 'VEHICLE_CATEGORY_UNSUPPORTED'),
    ('powertrain', 'ELECTRIC', 'POWERTRAIN_UNSUPPORTED'),
    ('powertrain', 'OTHER', 'POWERTRAIN_UNSUPPORTED'), ('steering', 'UNKNOWN', 'STEERING_UNKNOWN'),
    ('procedure', 'RE_EXPORT', 'PROCEDURE_UNSUPPORTED'),
    ('procedure', 'OTHER', 'PROCEDURE_UNSUPPORTED'), ('exemption_claimed', True, 'EXEMPTION_CLAIMED_UNSUPPORTED'),
    ('special_status', True, 'SPECIAL_STATUS_UNSUPPORTED'),
    ('production_year_confirmed', False, 'PRODUCTION_YEAR_NOT_CONFIRMED'),
    ('declaration_year', 2025, 'DECLARATION_YEAR_UNSUPPORTED'),
    ('declaration_year', 2027, 'DECLARATION_YEAR_UNSUPPORTED'),
    ('production_year', 2027, 'NEGATIVE_VEHICLE_AGE'),
    ('planned_declaration_date', '2026-10-29', 'PLANNED_DATE_UNSUPPORTED'),
    ('planned_declaration_date', '2026-04-01', 'PLANNED_DATE_UNSUPPORTED'),
    ('planned_declaration_date', '2027-01-01', 'PLANNED_DATE_UNSUPPORTED'),
])
def test_unsupported_cases_never_receive_ordinary_rate(client, field, value, code):
    report = client.post('/api/v1/georgia/excise', json=PAYLOAD | {field: value}).json()
    assert report['outcome'] == 'WITHHELD' and report['excise_amount'] is None
    assert code in [item['code'] for item in report['issues']]


def test_conflicting_declaration_year_date_is_explicit(client):
    report = client.post('/api/v1/georgia/excise', json=PAYLOAD | {'declaration_year': 2027}).json()
    assert 'DECLARATION_DATE_YEAR_CONFLICT' in [item['code'] for item in report['issues']]


def test_planned_date_inside_review_horizon_is_only_current_rules_planning(client):
    report = client.post('/api/v1/georgia/excise', json=PAYLOAD | {'planned_declaration_date': '2026-12-31'}).json()
    assert report['outcome'] == 'CALCULATED_COMPONENT'
    assert any('Amendments' in text for text in report['warnings'])


@pytest.mark.parametrize('now', [datetime(2026, 10, 29, 12, tzinfo=timezone.utc), datetime(2027, 1, 1, 0, tzinfo=timezone.utc)])
def test_rule_is_not_used_before_review_or_after_application_review_horizon(client, monkeypatch, now):
    monkeypatch.setattr(service, 'utc_now', lambda: now)
    report = client.post('/api/v1/georgia/excise', json=PAYLOAD).json()
    assert report['outcome'] == 'WITHHELD' and report['excise_amount'] is None
    assert 'RULE_REVIEW_OUTSIDE_WINDOW' in [item['code'] for item in report['issues']]


def test_review_expiry_uses_georgia_midnight(client, monkeypatch):
    monkeypatch.setattr(service, 'utc_now', lambda: datetime(2026, 12, 31, 20, tzinfo=timezone.utc))
    report = client.post('/api/v1/georgia/excise', json=PAYLOAD | {'planned_declaration_date': '2026-12-31'}).json()
    assert report['outcome'] == 'WITHHELD'
    assert 'RULE_REVIEW_OUTSIDE_WINDOW' in [item['code'] for item in report['issues']]


@pytest.mark.parametrize('field,value', [
    ('engine_cc', 2.0), ('engine_cc', '2000'), ('engine_cc', True), ('engine_cc', 0), ('engine_cc', -1), ('engine_cc', 20001),
    ('production_year', 2021.0), ('production_year', '2021'), ('production_year', True),
    ('declaration_year', 2026.0), ('declaration_year', True),
    ('exemption_claimed', 0), ('special_status', 'false'), ('production_year_confirmed', 1),
    ('planned_declaration_date', 1793318400), ('planned_declaration_date', '2026-10-30T00:00:00Z'),
    ('planned_declaration_date', '2026-02-30'), ('powertrain', 'GAS'),
])
def test_invalid_types_units_or_dates_are_rejected_at_http_boundary(client, field, value):
    assert client.post('/api/v1/georgia/excise', json=PAYLOAD | {field: value}).status_code == 422


@pytest.mark.parametrize('extra', [{'vin_model_year': 2021}, {'vat': '0'}, {'verified': True}, {'rate_gel_per_cc': '0.01'}])
def test_client_cannot_inject_rate_or_verified_eligibility(client, extra):
    assert client.post('/api/v1/georgia/excise', json=PAYLOAD | extra).status_code == 422


def test_empty_request_is_truthful_missing_facts_not_server_error(client):
    report = client.post('/api/v1/georgia/excise', json={}).json()
    assert report['outcome'] == 'WITHHELD' and report['excise_amount'] is None
    assert len(report['issues']) == len(PAYLOAD)


def test_four_kib_limit_is_applied_before_json_parsing(client):
    response = client.post('/api/v1/georgia/excise', content=b' ' * 4097, headers={'Content-Type': 'application/json'})
    assert response.status_code == 413 and 'no-store' in response.headers['cache-control']


@pytest.mark.parametrize('year,cc,code', [(1995, 2000, 'VEHICLE_AGE_UNSUPPORTED'),
    (2021, 99, 'ENGINE_DISPLACEMENT_UNSUPPORTED'), (2021, 7001, 'ENGINE_DISPLACEMENT_UNSUPPORTED')])
def test_frozen_product_support_limits_withhold_without_implying_statutory_exemption(client, year, cc, code):
    report = client.post('/api/v1/georgia/excise', json=PAYLOAD | {'production_year': year, 'engine_cc': cc}).json()
    assert report['outcome'] == 'WITHHELD' and report['excise_amount'] is None
    assert code in [item['code'] for item in report['issues']]


@pytest.mark.parametrize('year,cc,expected', [(1996, 100, '450.00'), (2026, 7000, '10500.00')])
def test_supported_age_displacement_edges_are_inclusive(client, year, cc, expected):
    report = client.post('/api/v1/georgia/excise', json=PAYLOAD | {'production_year': year, 'engine_cc': cc}).json()
    assert report['outcome'] == 'CALCULATED_COMPONENT' and report['excise_amount'] == expected


@pytest.mark.parametrize('year,powertrain,steering,expected', [
    (2021, 'HYBRID', 'ORIGINAL_LEFT', '1200.00'),
    (2020, 'HYBRID', 'ORIGINAL_LEFT', '1200.00'),
    (2021, 'PETROL', 'RIGHT', '9000.00'),
    (2019, 'PETROL', 'RIGHT', '27000.00'),
    (2021, 'DIESEL', 'CONVERTED', '9000.00'),
])
def test_official_hybrid_and_steering_component_cases(client, year, powertrain, steering, expected):
    report = client.post('/api/v1/georgia/excise', json=PAYLOAD | {'production_year': year, 'powertrain': powertrain, 'steering': steering}).json()
    assert report['outcome'] == 'CALCULATED_COMPONENT'
    assert report['excise_amount'] == expected
    assert report['other_clearance_components'] == 'NOT_CALCULATED'


@pytest.mark.parametrize('changes,code', [
    ({'powertrain': 'HYBRID', 'production_year': 2019}, 'HYBRID_AGE_UNSUPPORTED'),
    ({'powertrain': 'HYBRID', 'steering': 'RIGHT'}, 'HYBRID_STEERING_UNSUPPORTED'),
    ({'powertrain': 'HYBRID', 'steering': 'CONVERTED'}, 'HYBRID_STEERING_UNSUPPORTED'),
])
def test_unvalidated_hybrid_cases_withhold(client, changes, code):
    report = client.post('/api/v1/georgia/excise', json=PAYLOAD | changes).json()
    assert report['outcome'] == 'WITHHELD' and report['excise_amount'] is None
    assert code in [issue['code'] for issue in report['issues']]
