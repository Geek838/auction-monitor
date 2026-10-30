"""Unknown eligibility remains unknown; no decoded VIN supplies these declarations."""
from datetime import date, datetime
from typing import Annotated, Literal

from pydantic import AwareDatetime, Field, field_validator

from app.budgets.models import Contract

Year = Annotated[int, Field(strict=True, ge=1886, le=2100)]
EngineCc = Annotated[int, Field(strict=True, ge=1, le=20000)]


class ExciseRequest(Contract):
    declaration_year: Year | None = None
    planned_declaration_date: date | None = None
    production_year: Year | None = None
    production_year_confirmed: Annotated[bool, Field(strict=True)] | None = None
    engine_cc: EngineCc | None = None
    commodity_code: Literal['8703', 'OTHER', 'UNKNOWN'] = 'UNKNOWN'
    vehicle_category: Literal['ORDINARY_PASSENGER', 'SPORT', 'CLASSIC', 'OTHER', 'UNKNOWN'] = 'UNKNOWN'
    powertrain: Literal['PETROL', 'DIESEL', 'HYBRID', 'ELECTRIC', 'OTHER', 'UNKNOWN'] = 'UNKNOWN'
    steering: Literal['ORIGINAL_LEFT', 'RIGHT', 'CONVERTED', 'UNKNOWN'] = 'UNKNOWN'
    procedure: Literal['GEORGIA_FREE_CIRCULATION', 'RE_EXPORT', 'OTHER', 'UNKNOWN'] = 'UNKNOWN'
    exemption_claimed: Annotated[bool, Field(strict=True)] | None = None
    special_status: Annotated[bool, Field(strict=True)] | None = None


    @field_validator('planned_declaration_date', mode='before')
    @classmethod
    def calendar_date_only(cls, value):
        if value is None or (isinstance(value, date) and not isinstance(value, datetime)):
            return value
        if not isinstance(value, str) or len(value) != 10 or value[4] != '-' or value[7] != '-':
            raise ValueError('Use a YYYY-MM-DD planned declaration date, not a timestamp.')
        return value


class ExciseRule(Contract):
    id: str
    source_url: str
    source_publication: str
    source_clauses: list[str]
    reviewed_on: date
    supported_declaration_year: Literal[2026] = 2026
    application_review_expires_on: date


class ExciseIssue(Contract):
    code: str
    message: str


class ExciseReport(Contract):
    schema_version: Literal['georgia-excise-v1'] = 'georgia-excise-v1'
    outcome: Literal['CALCULATED_COMPONENT', 'WITHHELD']
    currency: Literal['GEL'] = 'GEL'
    source_kind: Literal['STATUTORY_COMPONENT_USER_DECLARED_FACTS'] = 'STATUTORY_COMPONENT_USER_DECLARED_FACTS'
    request: ExciseRequest
    excise_amount: str | None = None
    age_years: int | None = None
    rate_gel_per_cc: str | None = None
    rule: ExciseRule
    issues: list[ExciseIssue] = Field(default_factory=list)
    other_clearance_components: Literal['NOT_CALCULATED'] = 'NOT_CALCULATED'
    warnings: list[str] = Field(default_factory=list)
    generated_at: AwareDatetime
