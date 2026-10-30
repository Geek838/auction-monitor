"""Versioned 2026 excise-component planning, frozen from official clauses/UI evidence."""
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

from app.georgia_excise.models import ExciseIssue, ExciseReport, ExciseRequest, ExciseRule

REVIEWED_ON = date(2026, 10, 30)
REVIEW_EXPIRES_ON = date(2026, 12, 31)
RULE = ExciseRule(
    id='georgia-8703-ordinary-excise-2026-reviewed-2026-10-30',
    source_url='https://matsne.gov.ge/ka/document/view/1043717?publication=247',
    source_publication='247 (15 October 2026)',
    source_clauses=['Article 188(12)', 'Article 188(13)', 'Article 188(18)'],
    reviewed_on=REVIEWED_ON, application_review_expires_on=REVIEW_EXPIRES_ON,
)
WARNINGS = [
    'This is only a statutory excise component based on user-declared eligibility and facts, not a Revenue Service assessment or complete clearance total.',
    'Import duty, VAT treatment, service charges, registration, transport and other costs are NOT calculated. No zero value is implied for any of them.',
    'Production year is required. VIN model year does not independently establish production year, customs classification, steering, powertrain or exemption eligibility.',
    'Only ordinary 8703 passenger petrol/diesel vehicles with original left steering, age 0–30 years, 100–7000 cm³ displacement, no special status or exemption, and planned Georgia free circulation are supported.',
    'The reviewed current-rule planning subset excludes historical declarations, re-export/refunds, hybrid/electric vehicles, right/converted steering, sport/classic and other special treatment.',
    'Age is planned declaration-registration year minus production year. Rates are GEL 1.50/cm³ at age 0–6 inclusive and GEL 4.50/cm³ above six years.',
    'The 31 December 2026 limit is this application’s review horizon, not a claim that the law expires then. Amendments or actual declaration facts can change the assessment.',
    'This GEL component does not populate clearance or registration in the USD budget; all remaining amounts and any exchange conversion require separate evidence.',
]


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def calculate_excise(request: ExciseRequest) -> ExciseReport:
    now = utc_now()
    today = (now + timedelta(hours=4)).date()
    issues = []

    def issue(code: str, message: str):
        issues.append(ExciseIssue(code=code, message=message))

    if today < REVIEWED_ON or today > REVIEW_EXPIRES_ON:
        issue('RULE_REVIEW_OUTSIDE_WINDOW', 'The current date is outside the application’s reviewed 2026 rule window; no component is calculated.')
    if request.declaration_year is None:
        issue('DECLARATION_YEAR_UNKNOWN', 'Declare the planned customs-registration year; the supported year is 2026.')
    elif request.declaration_year != 2026:
        issue('DECLARATION_YEAR_UNSUPPORTED', 'Only the reviewed current 2026 declaration-year subset is supported.')
    if request.planned_declaration_date is None:
        issue('PLANNED_DATE_UNKNOWN', 'Supply a planned declaration-registration date; historical declarations are outside this tool.')
    else:
        if request.planned_declaration_date < max(today, REVIEWED_ON) or request.planned_declaration_date > REVIEW_EXPIRES_ON:
            issue('PLANNED_DATE_UNSUPPORTED', 'Use a current or future planned declaration date within the reviewed 2026 window; historical or later declarations are withheld.')
        if request.declaration_year is not None and request.planned_declaration_date.year != request.declaration_year:
            issue('DECLARATION_DATE_YEAR_CONFLICT', 'The planned declaration date and declaration year conflict.')
    if request.production_year is None:
        issue('PRODUCTION_YEAR_UNKNOWN', 'Supply production year separately from any VIN model year.')
    elif request.declaration_year is not None and request.production_year > request.declaration_year:
        issue('NEGATIVE_VEHICLE_AGE', 'Production year cannot exceed the planned declaration-registration year.')
    if request.declaration_year is not None and request.production_year is not None and request.declaration_year - request.production_year > 30:
        issue('VEHICLE_AGE_UNSUPPORTED', 'This reviewed subset supports ages zero through 30 only; older vehicles require separate classification review.')
    if request.production_year_confirmed is not True:
        issue('PRODUCTION_YEAR_NOT_CONFIRMED', 'Explicitly confirm that production year is supplied from production evidence, not inferred solely from VIN model year. This declaration is not independently verified.')
    if request.engine_cc is None:
        issue('ENGINE_DISPLACEMENT_UNKNOWN', 'Supply verified engine displacement in integer cubic centimetres, not litres.')
    elif not 100 <= request.engine_cc <= 7000:
        issue('ENGINE_DISPLACEMENT_UNSUPPORTED', 'This reviewed subset supports 100 through 7000 cubic centimetres only.')
    for field, allowed, message in [
        ('commodity_code', {'8703'}, 'Only explicitly declared commodity item 8703 is supported.'),
        ('vehicle_category', {'ORDINARY_PASSENGER'}, 'Only an ordinary passenger vehicle is supported; sport/classic or other categories require separate treatment.'),
        ('powertrain', {'PETROL', 'DIESEL'}, 'Only conventional petrol or diesel is supported; hybrid, electric and other powertrains are outside this subset.'),
        ('steering', {'ORIGINAL_LEFT'}, 'Only original left steering is supported; right or converted steering requires separate treatment.'),
        ('procedure', {'GEORGIA_FREE_CIRCULATION'}, 'Only planned release for free circulation in Georgia is supported; re-export and refunds are not calculated.'),
    ]:
        value = getattr(request, field)
        if value not in allowed:
            issue(field.upper() + ('_UNKNOWN' if value == 'UNKNOWN' else '_UNSUPPORTED'), message)
    for field in ['exemption_claimed', 'special_status']:
        value = getattr(request, field)
        if value is None:
            issue(field.upper() + '_UNKNOWN', 'Explicitly declare whether any exemption or special treatment applies.')
        elif value:
            issue(field.upper() + '_UNSUPPORTED', 'Exemption or special-treatment cases are outside this reviewed ordinary-vehicle subset.')
    report = ExciseReport(outcome='WITHHELD', request=request, rule=RULE.model_copy(deep=True),
                          issues=issues, warnings=list(WARNINGS), generated_at=now)
    if issues:
        return report
    age = request.declaration_year - request.production_year
    rate = Decimal('1.50') if age <= 6 else Decimal('4.50')
    report.age_years = age
    report.rate_gel_per_cc = format(rate, '.2f')
    report.excise_amount = format(rate * request.engine_cc, '.2f')
    report.outcome = 'CALCULATED_COMPONENT'
    return report
