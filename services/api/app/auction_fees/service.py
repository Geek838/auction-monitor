"""Validate source arithmetic and preserve unverified/undated provenance."""
import asyncio
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from threading import BoundedSemaphore
from app.auction_fees.models import FeeError, FeeReport, FeeRequest
from app.auction_fees.runtime import FeeClient, FeeSourceFailure

SLOTS = BoundedSemaphore(2)
WARNINGS = [
    'This is a third-party indicative estimate, not an official or independently verified auction fee quote.',
    'The provider did not supply a fee schedule date, expiry, itemized charges or official source. Actual fees can differ.',
    'The bid and selected auction, payment, bidding, vehicle and volume options are sent to the external service. No location or auction URL is sent.',
    'This estimate does not automatically change or complete your budget. Towing and other costs are not included.',
]


def _amount(value) -> Decimal:
    if not isinstance(value, Decimal) or not value.is_finite() or value < 0 or value > Decimal('2000000000') or value.as_tuple().exponent < -2:
        raise ValueError('Invalid amount')
    return value


def _estimate(request: FeeRequest) -> FeeReport:
    report = FeeReport(outcome='UNAVAILABLE', request=request, bid_amount=request.bid_amount,
                       retrieved_at=datetime.now(timezone.utc), warnings=list(WARNINGS))
    if not SLOTS.acquire(blocking=False):
        report.errors = [FeeError(code='BUSY', message='Two fee estimates are already in progress; retry shortly.')]
        return report
    try:
        result = FeeClient().request_json(request)
        quote = result.get('quote')
        if not isinstance(quote, dict) or not isinstance(quote.get('auctionFees'), dict):
            raise ValueError('Missing quote')
        if result.get('towing') is not None:
            raise ValueError('Unexpected towing data')
        bid = _amount(quote.get('bidAmount'))
        fee = _amount(quote['auctionFees'].get('auctionFee'))
        total = _amount(quote['auctionFees'].get('totalAmount'))
        if bid != Decimal(request.bid_amount) or total != bid + fee:
            raise ValueError('Quote not bound to request or inconsistent')
        report.auction_fee = format(fee, '.2f')
        report.total_amount = format(total, '.2f')
        report.outcome = 'ESTIMATED'
    except FeeSourceFailure as exc:
        report.errors = [FeeError(code=exc.code, message=exc.message)]
    except (ValueError, TypeError, KeyError, AttributeError, InvalidOperation, OverflowError):
        report.errors = [FeeError(code='INVALID_RESPONSE', message='The external fee estimate could not be validated against your bid.')]
    finally:
        report.retrieved_at = datetime.now(timezone.utc)
        SLOTS.release()
    return report


async def estimate_fee(request: FeeRequest) -> FeeReport:
    return await asyncio.to_thread(_estimate, request)
