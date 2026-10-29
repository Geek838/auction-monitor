"""Cent-exact scenario totals and a monotonic fee-aware planning ceiling; no I/O."""
from datetime import date, datetime, timezone
from decimal import Decimal, ROUND_HALF_UP

from app.budgets.models import (
    AuctionFees, BidCeiling, BudgetReport, BudgetRequest, CATEGORIES, CENT, Evidence,
    Issue, Totals, business_today,
)


def money(value: Decimal) -> str:
    return format(value.quantize(CENT, rounding=ROUND_HALF_UP), ".2f")


def fee_for_bid(schedule: AuctionFees, bid: Decimal) -> Decimal:
    if bid < 0 or bid != bid.quantize(CENT):
        raise ValueError("Bid must be a nonnegative whole-cent amount.")
    for tier in schedule.tiers:
        if bid >= Decimal(tier.from_bid) and (tier.to_bid is None or bid < Decimal(tier.to_bid)):
            return (Decimal(tier.flat) + bid * Decimal(tier.percent) / 100).quantize(CENT, rounding=ROUND_HALF_UP)
    raise ValueError("The fee schedule does not cover this bid.")


def evidence_issues(evidence: Evidence, category: str | None, today: date) -> list[Issue]:
    problems: list[Issue] = []
    if evidence.source is None:
        problems.append(Issue(code="MISSING_SOURCE", category=category, message="A supplied cost or fee schedule has no source/assumption reference."))
    if evidence.as_of is None:
        problems.append(Issue(code="MISSING_SOURCE_DATE", category=category, message="A supplied cost or fee schedule has no dated basis."))
    elif evidence.as_of > today:
        problems.append(Issue(code="FUTURE_SOURCE_DATE", category=category, message="A supplied source date is later than the evaluation date."))
    if evidence.kind == "QUOTE" and evidence.expires_on is None:
        problems.append(Issue(code="MISSING_QUOTE_EXPIRY", category=category, message="A quoted amount needs an explicit validity end date; no freshness period is assumed."))
    if evidence.expires_on is not None and evidence.expires_on < today:
        problems.append(Issue(code="EXPIRED_SOURCE", category=category, message="A supplied cost or fee schedule has expired."))
    return problems


def evaluate_budget(request: BudgetRequest, *, today: date | None = None) -> BudgetReport:
    today = today or business_today()
    covered = {row.category for row in request.costs} | {row.category for row in request.not_applicable}
    missing = [category for category in CATEGORIES if category not in covered]
    issues = [Issue(code="MISSING_CATEGORY", category=category, message=f"No amount or explicit not-applicable reason was supplied for {category}.") for category in missing]
    for cost in request.costs:
        issues.extend(evidence_issues(cost, cost.category, today))
    if request.auction_fees is None:
        issues.append(Issue(code="MISSING_AUCTION_FEES", message="The auction fee schedule is unknown; it has not been treated as zero."))
    else:
        issues.extend(evidence_issues(request.auction_fees, None, today))
    non_bid = {scenario: sum((Decimal(getattr(row, scenario)) for row in request.costs), Decimal(0)) for scenario in ("low", "base", "high")}
    fee = fee_for_bid(request.auction_fees, Decimal(request.hammer_bid)) if request.auction_fees else None
    # Known totals are explicitly partial when fees or categories are absent.
    known = {scenario: amount + Decimal(request.hammer_bid) + (fee if fee is not None else Decimal(0)) for scenario, amount in non_bid.items()}
    complete = not issues
    maximum = BidCeiling(status="WITHHELD", amount=None,
        reason="Complete current cost coverage and a sourced fee schedule are required before a planning ceiling can be calculated.",
        high_non_bid_total=money(non_bid["high"]), auction_fee_at_max=None)
    if complete:
        absent = [label for label, value in (("market value", request.market_value), ("required savings", request.required_savings), ("additional risk reserve", request.risk_reserve)) if value is None]
        if absent:
            maximum.reason = "Planning ceiling withheld: explicitly supply " + ", ".join(absent) + "; zero must be entered deliberately."
        else:
            available = Decimal(request.market_value) - Decimal(request.required_savings) - Decimal(request.risk_reserve)
            # Search integer cents, including fee jumps. The complete validated fee
            # schedule is monotonic; no closed-form flat-fee subtraction is assumed.
            lower, upper, best = 0, int(Decimal(request.market_value) * 100), -1
            while lower <= upper:
                middle = (lower + upper) // 2
                bid = Decimal(middle) / 100
                acquisition = bid + fee_for_bid(request.auction_fees, bid) + non_bid["high"]
                if acquisition <= available:
                    best = middle
                    lower = middle + 1
                else:
                    upper = middle - 1
            if best <= 0:
                maximum.status = "NO_FEASIBLE_BID"
                maximum.reason = "No positive whole-cent bid fits the supplied conservative value, high costs, savings and additional reserve."
            else:
                ceiling = Decimal(best) / 100
                maximum = BidCeiling(status="INDICATIVE", amount=money(ceiling),
                    reason="Highest whole-cent planning bid fitting the user-supplied value minus high costs, bid-dependent auction fees, required savings and additional risk reserve. This is not a validated market recommendation.",
                    high_non_bid_total=money(non_bid["high"]), auction_fee_at_max=money(fee_for_bid(request.auction_fees, ceiling)))
    return BudgetReport(
        status="COMPLETE" if complete else "INCOMPLETE", request=request,
        hammer_bid=request.hammer_bid, costs=request.costs, not_applicable=request.not_applicable,
        missing_categories=missing, issues=issues,
        known_non_bid_totals=Totals(**{key: money(value) for key, value in non_bid.items()}),
        auction_fee_at_bid=money(fee) if fee is not None else None,
        known_total_at_bid=Totals(**{key: money(value) for key, value in known.items()}),
        total_at_bid=Totals(**{key: money(value) for key, value in known.items()}) if complete else None,
        max_bid=maximum,
        warnings=[
            "All inputs, including QUOTE labels and market value, are user-supplied and unverified; no supplier, auction or market API was queried.",
            "COMPLETE means all required categories were explicitly addressed with currently usable declared sources; it does not establish real-world accuracy or that all damage was identified.",
            "Unknown costs and fees are not zero. Known totals are only a subtotal when coverage or source evidence is incomplete.",
            "Known subtotals retain entered amounts even when their source is missing or expired; review every issue before relying on them.",
            "The auction_broker category covers broker/other fixed fees only; exclude the auction fees already represented by the fee schedule to avoid double counting.",
            "The additional risk reserve is deducted separately from any contingency cost line. Review both amounts to avoid unintended double counting.",
            "No Georgian tax rule, parts compatibility, labor price, resale value or currency conversion was inferred. USD is the only calculation currency.",
            "The planning ceiling uses the high cost scenario and supplied market value. It is indicative, not an instruction to bid or a professional valuation.",
            "Quote validity dates are evaluated at Georgia calendar date (UTC+04:00); dates and expiry are declarations, not independently checked supplier guarantees.",
        ],
        generated_at=datetime.now(timezone.utc),
    )
