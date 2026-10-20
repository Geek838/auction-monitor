"""Provider-neutral listing identities and evidence contracts."""
from datetime import datetime
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class AuctionHouse(StrEnum):
    COPART = "COPART"
    IAAI = "IAAI"


class ResolutionStatus(StrEnum):
    MATCHED = "MATCHED"
    AMBIGUOUS = "AMBIGUOUS"
    NOT_FOUND = "NOT_FOUND"
    UNRESOLVED_ID = "UNRESOLVED_ID"
    SOURCE_UNAVAILABLE = "SOURCE_UNAVAILABLE"
    NOT_AUTHORIZED = "NOT_AUTHORIZED"


class AuctionReference(BaseModel):
    house: AuctionHouse
    url: str
    lot_number: str | None = None
    stock_number: str | None = None
    page_id: str | None = None


class ListingIdentity(BaseModel):
    house: AuctionHouse
    lot_or_stock_number: str


class Vehicle(BaseModel):
    vin: str | None = None
    year: int | None = None
    make: str | None = None
    model: str | None = None
    trim: str | None = None
    primary_damage: str | None = None


class Provenance(BaseModel):
    provider: str
    source_name: str
    source_url: str
    retrieved_at: datetime
    license_scope: str
    data_type: Literal["MOCK", "LICENSED"]
    realtime: bool = False


class FieldEvidence(BaseModel):
    kind: Literal["OBSERVED", "SUPPLIED", "INFERRED", "MISSING"]
    source: str
    note: str


class VehicleSnapshot(BaseModel):
    record_id: str
    identity: ListingIdentity
    vehicle: Vehicle
    provenance: Provenance
    event_status: Literal["FIXTURE", "ARCHIVED"] = "FIXTURE"
    event_date: str | None = None
    field_evidence: dict[str, FieldEvidence] = Field(default_factory=dict)


class ProviderResolution(BaseModel):
    identity: ListingIdentity | None = None
    # Independent reference metadata, when available, gates exact matching.
    expected_vehicle: Vehicle | None = None
    candidates: list[VehicleSnapshot] = Field(default_factory=list)


class ResolutionResult(BaseModel):
    status: ResolutionStatus
    reference: AuctionReference
    identity: ListingIdentity | None = None
    vehicle: Vehicle | None = None
    candidates: list[VehicleSnapshot] = Field(default_factory=list)
    provenance: Provenance | None = None
    field_evidence: dict[str, FieldEvidence] = Field(default_factory=dict)
    event_status: str | None = None
    event_date: str | None = None
    evidence: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    reasons: list[str] = Field(default_factory=list)


class ResolveRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    url: str = Field(min_length=1, max_length=2048)
