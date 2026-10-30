"""Normalize the NBG quote without treating its publication time as its effective date."""
import asyncio
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP, localcontext
from threading import BoundedSemaphore

from app.exchange.models import ConversionReport, ConversionRequest, ExchangeError, ExchangeQuote
from app.exchange.runtime import ExchangeSourceFailure, NbgClient, SOURCE_URL

REQUEST_SLOTS = BoundedSemaphore(2)
MAX_AGE_DAYS = 4  # Application freshness policy, not an assertion of statutory expiry.
WARNINGS = [
    'NBG publishes an indicative official reference rate; it is not a bank, card, broker or cash-exchange offer and excludes spreads and fees.',
    'The official exchange rate is indicative and its use is not obligatory except where relevant legal requirements apply.',
    'Publication timestamp and effective date differ. A previous effective date can be normal on weekends or holidays; displayed age is not proof of statutory expiry.',
    'This application withholds conversion when the quote is future-effective or more than four calendar days old; that is an application freshness policy.',
    'Conversion is a display/planning aid. It does not change the USD budget ledger or constitute an official customs assessment.',
]


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _timestamp(value) -> datetime:
    if not isinstance(value, str) or len(value) > 40 or not value.endswith('Z'):
        raise ValueError('Missing source UTC timestamp')
    result = datetime.fromisoformat(value[:-1] + '+00:00')
    if result.utcoffset() != timedelta(0):
        raise ValueError('Unsupported source timestamp')
    return result


def _quote(body, now: datetime) -> ExchangeQuote:
    if not isinstance(body, list) or len(body) != 1 or not isinstance(body[0], dict):
        raise ValueError('Expected one source date')
    envelope = body[0]
    effective = _timestamp(envelope.get('date'))
    # These timestamps encode the source's effective calendar day, not UTC+04
    # publication times. Do not move the day when displaying it in Georgia.
    if effective.time().isoformat() != '00:00:00':
        raise ValueError('Unexpected effective date format')
    rows = envelope.get('currencies')
    if not isinstance(rows, list) or not 1 <= len(rows) <= 100 or any(not isinstance(row, dict) for row in rows):
        raise ValueError('Expected bounded currency list')
    usd_rows = [row for row in rows if row.get('code') == 'USD']
    if len(usd_rows) != 1:
        raise ValueError('Expected exactly one USD quote')
    row = usd_rows[0]
    if row.get('code') != 'USD' or _timestamp(row.get('validFromDate')) != effective:
        raise ValueError('Currency or effective date mismatch')
    quantity = row.get('quantity')
    if type(quantity) is not int or not 1 <= quantity <= 1000000:
        raise ValueError('Invalid quote quantity')
    # Production JSON parsing retains source numeric precision as Decimal.
    rate_value = row.get('rate')
    if not isinstance(rate_value, (Decimal, int)) or isinstance(rate_value, bool):
        raise ValueError('Invalid decimal rate')
    rate = Decimal(rate_value)
    if not rate.is_finite() or not Decimal('0.000001') <= rate <= Decimal('1000000') or rate.as_tuple().exponent < -12:
        raise ValueError('Invalid decimal rate')
    published = _timestamp(row.get('date'))
    if published > now + timedelta(minutes=5) or published.date() > effective.date():
        raise ValueError('Unexpected publication date')
    today = (now + timedelta(hours=4)).date()
    age = (today - effective.date()).days
    freshness = ('FUTURE_EFFECTIVE_DATE' if age < 0 else 'STALE' if age > MAX_AGE_DAYS
                 else 'EFFECTIVE_TODAY' if age == 0 else 'PREVIOUS_EFFECTIVE_DATE')
    with localcontext() as context:
        context.prec = 40
        unit_rate = rate / quantity
    return ExchangeQuote(quantity=quantity, rate_gel=format(rate, 'f'), gel_per_usd=format(unit_rate, 'f'),
                         effective_date=effective.date(), published_at=published,
                         age_days=age, freshness=freshness)


def _convert(request: ConversionRequest) -> ConversionReport:
    report = ConversionReport(request=request, source_url=SOURCE_URL, outcome='UNAVAILABLE',
                              retrieved_at=utc_now(), warnings=list(WARNINGS))
    if not REQUEST_SLOTS.acquire(blocking=False):
        report.errors = [ExchangeError(code='BUSY', message='Two exchange-rate requests are already in progress; retry shortly.')]
        return report
    try:
        body = NbgClient().request_json()
        now = utc_now()
        quote = _quote(body, now)
        report.quote = quote
        if quote.freshness == 'FUTURE_EFFECTIVE_DATE':
            report.outcome = 'NOT_YET_EFFECTIVE'
            report.errors = [ExchangeError(code='FUTURE_EFFECTIVE_DATE', message='The returned official rate is not effective yet; no conversion was produced.')]
        elif quote.freshness == 'STALE':
            report.outcome = 'STALE'
            report.errors = [ExchangeError(code='STALE_RATE', message='The quote exceeds this application’s four-calendar-day freshness limit; no conversion was produced.')]
        else:
            with localcontext() as context:
                context.prec = 40
                amount, rate = Decimal(request.amount), Decimal(quote.gel_per_usd)
                converted = amount * rate if request.from_currency == 'USD' else amount / rate
                report.converted_amount = format(converted.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP), '.2f')
            report.outcome = 'CONVERTED'
        return report
    except ExchangeSourceFailure as exc:
        report.errors = [ExchangeError(code=exc.code, message=exc.message)]
        return report
    except (ValueError, TypeError, KeyError, AttributeError, InvalidOperation, OverflowError):
        report.quote = None
        report.converted_amount = None
        report.outcome = 'UNAVAILABLE'
        report.errors = [ExchangeError(code='INVALID_RESPONSE', message='Official exchange-rate data could not be validated.')]
        return report
    finally:
        report.retrieved_at = utc_now()
        REQUEST_SLOTS.release()


async def convert_currency(request: ConversionRequest) -> ConversionReport:
    return await asyncio.to_thread(_convert, request)
