"""Decimal string contracts; official reference rates are not executable bank quotes."""
from datetime import date
from typing import Literal

from pydantic import AwareDatetime, Field, model_validator

from app.budgets.models import Contract, Money

Currency = Literal['USD', 'GEL']


class ConversionRequest(Contract):
    amount: Money
    from_currency: Currency
    to_currency: Currency

    @model_validator(mode='after')
    def different_currencies(self):
        if self.from_currency == self.to_currency:
            raise ValueError('Choose different source and destination currencies.')
        return self


class ExchangeQuote(Contract):
    currency: Literal['USD'] = 'USD'
    quantity: int
    rate_gel: str
    gel_per_usd: str
    effective_date: date
    published_at: AwareDatetime
    age_days: int
    freshness: Literal['EFFECTIVE_TODAY', 'PREVIOUS_EFFECTIVE_DATE', 'STALE', 'FUTURE_EFFECTIVE_DATE']


class ExchangeError(Contract):
    code: str
    message: str


class ConversionReport(Contract):
    schema_version: Literal['exchange-v1'] = 'exchange-v1'
    source: Literal['NATIONAL_BANK_OF_GEORGIA'] = 'NATIONAL_BANK_OF_GEORGIA'
    source_url: str
    source_request_date: date | None = None
    outcome: Literal['CONVERTED', 'STALE', 'UNAVAILABLE', 'NOT_YET_EFFECTIVE']
    request: ConversionRequest
    converted_amount: str | None = None
    quote: ExchangeQuote | None = None
    retrieved_at: AwareDatetime
    rounding: Literal['ROUND_HALF_UP_2_DECIMAL_PLACES'] = 'ROUND_HALF_UP_2_DECIMAL_PLACES'
    max_age_days: Literal[4] = 4
    errors: list[ExchangeError] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
