"""User-supplied request and unverified third-party estimate contracts."""
from decimal import Decimal
from typing import Literal
from pydantic import AwareDatetime, Field, model_validator
from app.budgets.models import Contract, Money


class FeeRequest(Contract):
    consent_to_send: bool = Field(strict=True)
    bid_amount: Money
    auction: Literal['copart', 'iaai']
    bid_type: Literal['online', 'kiosk', 'non-kiosk']
    bid_pay: Literal['secured', 'unsecured', 'high', 'standard']
    bid_vehicle: Literal['standard', 'heavy', 'crashedToys', 'licensed', 'non-licensed', 'recRides']
    volume: Literal['low', 'high'] | None = None

    @model_validator(mode='after')
    def combinations(self):
        if not self.consent_to_send:
            raise ValueError('Consent to send the selected bid and options is required.')
        if Decimal(self.bid_amount) <= 0:
            raise ValueError('Bid amount must be greater than zero.')
        if self.auction == 'copart':
            if self.bid_pay not in {'secured', 'unsecured'} or self.bid_vehicle not in {'standard', 'heavy', 'crashedToys'} or self.volume is None:
                raise ValueError('Choose valid Copart payment, vehicle and volume options.')
        elif self.bid_pay not in {'high', 'standard'} or self.bid_vehicle not in {'licensed', 'non-licensed', 'recRides', 'heavy'} or self.volume is not None:
            raise ValueError('Choose valid IAAI payment and vehicle options; volume is not used.')
        return self


class FeeError(Contract):
    code: str
    message: str


class FeeReport(Contract):
    schema_version: Literal['auction-fee-estimate-v1'] = 'auction-fee-estimate-v1'
    source_kind: Literal['INDICATIVE_EXTERNAL_UNVERIFIED'] = 'INDICATIVE_EXTERNAL_UNVERIFIED'
    source_url: Literal['https://api.auctionfeescalculator.com'] = 'https://api.auctionfeescalculator.com'
    outcome: Literal['ESTIMATED', 'UNAVAILABLE']
    request: FeeRequest
    currency: Literal['USD'] = 'USD'
    bid_amount: str
    auction_fee: str | None = None
    total_amount: str | None = None
    schedule_as_of: None = None
    retrieved_at: AwareDatetime
    errors: list[FeeError] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
