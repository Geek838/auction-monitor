"""Decimal-string inputs; user declarations never become independently verified prices."""
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from typing import Annotated, Literal

from pydantic import AfterValidator, AwareDatetime, BaseModel, ConfigDict, Field, field_validator, model_validator

CENT = Decimal("0.01")
MAX_AMOUNT = Decimal("1000000000.00")
CATEGORIES = (
    "auction_broker", "us_transport", "ocean_port", "georgia_clearance", "registration",
    "parts", "labor", "diagnostics", "contingency", "other",
)
Category = Literal[
    "auction_broker", "us_transport", "ocean_port", "georgia_clearance", "registration",
    "parts", "labor", "diagnostics", "contingency", "other",
]
EvidenceKind = Literal["QUOTE", "ASSUMPTION"]


def business_today() -> date:
    # This Georgia planning workbench uses calendar dates at UTC+04:00.
    # No system timezone database or platform-specific tzdata dependency is needed.
    return (datetime.now(timezone.utc) + timedelta(hours=4)).date()


def normalize_money(value: str) -> str:
    amount = Decimal(value)
    if amount > MAX_AMOUNT:
        raise ValueError("Amounts must not exceed USD 1,000,000,000.")
    return format(amount, ".2f")


def normalize_percent(value: str) -> str:
    amount = Decimal(value)
    if amount > 100:
        raise ValueError("Fee percent must be between 0 and 100.")
    return format(amount, ".4f")


Money = Annotated[str, Field(strict=True, min_length=1, max_length=13, pattern=r"^(?:0|[1-9][0-9]*)(?:\.[0-9]{1,2})?$"), AfterValidator(normalize_money)]
Percent = Annotated[str, Field(strict=True, min_length=1, max_length=9, pattern=r"^(?:0|[1-9][0-9]*)(?:\.[0-9]{1,4})?$"), AfterValidator(normalize_percent)]
Text = Annotated[str, Field(min_length=1, max_length=200, pattern=r"\S")]


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Evidence(Contract):
    kind: EvidenceKind
    source: Text | None = None
    as_of: date | None = None
    expires_on: date | None = None

    @field_validator("as_of", "expires_on", mode="before")
    @classmethod
    def date_strings_only(cls, value):
        if value is not None and not isinstance(value, (str, date)):
            raise ValueError("Use an ISO calendar date, not a numeric timestamp.")
        if isinstance(value, datetime):
            raise ValueError("Use an ISO calendar date, not a timestamp.")
        if isinstance(value, str) and (len(value) != 10 or value[4] != "-" or value[7] != "-"):
            raise ValueError("Use a YYYY-MM-DD calendar date.")
        return value

    @model_validator(mode="after")
    def dates_are_consistent(self):
        if self.as_of is not None and self.as_of > business_today():
            raise ValueError("A source date cannot be in the future.")
        if self.as_of is not None and self.expires_on is not None and self.expires_on < self.as_of:
            raise ValueError("Expiry cannot precede the source date.")
        return self


class CostLine(Evidence):
    category: Category
    label: Text
    low: Money
    base: Money
    high: Money

    @model_validator(mode="after")
    def ordered_range(self):
        if not Decimal(self.low) <= Decimal(self.base) <= Decimal(self.high):
            raise ValueError("A cost range must satisfy low <= base <= high.")
        return self


class NotApplicable(Contract):
    category: Category
    reason: Text


class FeeTier(Contract):
    from_bid: Money
    to_bid: Money | None = None
    flat: Money
    percent: Percent

    @model_validator(mode="after")
    def positive_span(self):
        if self.to_bid is not None and Decimal(self.to_bid) <= Decimal(self.from_bid):
            raise ValueError("A fee tier upper bound must exceed its inclusive lower bound.")
        return self


class AuctionFees(Evidence):
    tiers: list[FeeTier] = Field(min_length=1, max_length=30)

    @model_validator(mode="after")
    def complete_monotonic_schedule(self):
        if Decimal(self.tiers[0].from_bid) != 0:
            raise ValueError("Fee coverage must start at a zero bid.")
        if self.tiers[-1].to_bid is not None:
            raise ValueError("The final fee tier must have an open upper bound (null).")
        for index, tier in enumerate(self.tiers):
            if index == len(self.tiers) - 1:
                continue
            following = self.tiers[index + 1]
            if tier.to_bid is None or tier.to_bid != following.from_bid:
                raise ValueError("Fee tiers must be ordered, contiguous and non-overlapping.")
            boundary = Decimal(following.from_bid)
            preceding_fee = (Decimal(tier.flat) + (boundary - CENT) * Decimal(tier.percent) / 100).quantize(CENT, rounding="ROUND_HALF_UP")
            following_fee = (Decimal(following.flat) + boundary * Decimal(following.percent) / 100).quantize(CENT, rounding="ROUND_HALF_UP")
            if following_fee < preceding_fee:
                raise ValueError("Fee schedules must not decrease at tier boundaries.")
        return self


class BudgetRequest(Contract):
    currency: Literal["USD"] = "USD"
    hammer_bid: Money
    costs: list[CostLine] = Field(default_factory=list, max_length=60)
    not_applicable: list[NotApplicable] = Field(default_factory=list, max_length=len(CATEGORIES))
    auction_fees: AuctionFees | None = None
    market_value: Money | None = None
    required_savings: Money | None = None
    risk_reserve: Money | None = None

    @model_validator(mode="after")
    def coverage_does_not_conflict(self):
        excluded = [item.category for item in self.not_applicable]
        if len(set(excluded)) != len(excluded):
            raise ValueError("A category may only be marked not applicable once.")
        if set(excluded) & {item.category for item in self.costs}:
            raise ValueError("A category cannot be both costed and marked not applicable.")
        return self


class Totals(Contract):
    # Aggregated values may exceed the per-input amount limit.
    low: str
    base: str
    high: str


class Issue(Contract):
    code: str
    category: Category | None = None
    message: str


class BidCeiling(Contract):
    status: Literal["INDICATIVE", "WITHHELD", "NO_FEASIBLE_BID"]
    amount: str | None
    reason: str
    high_non_bid_total: str
    auction_fee_at_max: str | None


class BudgetReport(Contract):
    schema_version: Literal["budget-v1"] = "budget-v1"
    currency: Literal["USD"] = "USD"
    source_kind: Literal["USER_SUPPLIED_UNVERIFIED"] = "USER_SUPPLIED_UNVERIFIED"
    status: Literal["COMPLETE", "INCOMPLETE"]
    request: BudgetRequest
    hammer_bid: str
    costs: list[CostLine]
    not_applicable: list[NotApplicable]
    missing_categories: list[Category]
    issues: list[Issue]
    known_non_bid_totals: Totals
    auction_fee_at_bid: str | None
    known_total_at_bid: Totals
    total_at_bid: Totals | None
    max_bid: BidCeiling
    warnings: list[str]
    generated_at: AwareDatetime
