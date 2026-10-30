"""Provider-neutral identities, independently sourced evidence and result contracts."""
from datetime import datetime
from enum import StrEnum
from typing import Literal

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field


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


class ProviderContext(BaseModel):
    id: str = "unknown"
    name: str = "Unconfigured provider"
    mode: Literal["FIXTURE", "SIMULATED", "EXTERNAL"] = "EXTERNAL"
    authorization: Literal["NOT_REQUIRED", "APPROVED", "UNVERIFIED", "DENIED"] = "DENIED"
    enabled: bool = False
    available: bool = False
    contract_version: str = "provider-contract-v1"
    reasons: list[str] = Field(default_factory=list)


class AuctionReference(BaseModel):
    house: AuctionHouse
    url: str
    lot_number: str | None = None
    stock_number: str | None = None
    page_id: str | None = None
    country: str | None = None


class ListingIdentity(BaseModel):
    house: AuctionHouse
    lot_or_stock_number: str = Field(min_length=1, pattern=r"\S")


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
    retrieved_at: AwareDatetime
    source_observed_at: AwareDatetime | None = None
    license_scope: str
    data_type: Literal["MOCK", "SIMULATED", "LICENSED", "EXTERNAL_UNVERIFIED"]
    realtime: bool = False


class FieldEvidence(BaseModel):
    kind: Literal["OBSERVED", "SUPPLIED", "INFERRED", "MISSING"]
    source: str
    note: str


class EvidenceOrigin(BaseModel):
    """A separate evidence channel, never generated from a candidate under test."""
    source: str = Field(min_length=1, pattern=r"\S")
    reference: str = Field(min_length=1, pattern=r"\S")
    channel: str = Field(min_length=1, pattern=r"\S")
    observed_at: AwareDatetime
    kind: Literal["OBSERVED", "SUPPLIED", "INFERRED", "MISSING"] = "SUPPLIED"


class MappingEvidence(BaseModel):
    page_id: str = Field(min_length=1, pattern=r"\S")
    country: str | None = None
    identity: ListingIdentity
    origin: EvidenceOrigin


class ReferenceEvidence(BaseModel):
    vehicle: Vehicle
    origin: EvidenceOrigin


class Freshness(BaseModel):
    status: Literal["FRESH", "STALE", "UNKNOWN", "HISTORICAL"] = "UNKNOWN"
    source_observed_at: datetime | None = None
    evaluated_at: datetime
    threshold_seconds: int | None = None
    basis: str


class VehicleSnapshot(BaseModel):
    record_id: str
    event_id: str | None = None
    identity: ListingIdentity
    vehicle: Vehicle
    provenance: Provenance
    event_status: Literal["FIXTURE", "ARCHIVED", "ACTIVE", "SOLD", "UNKNOWN"] = "FIXTURE"
    event_date: str | None = None
    field_evidence: dict[str, FieldEvidence] = Field(default_factory=dict)


class ProviderResolution(BaseModel):
    identity: ListingIdentity | None = None
    expected_vehicle: Vehicle | None = None  # Legacy conflict checks only; never proves independent corroboration.
    reference_evidence: ReferenceEvidence | None = None
    mapping_evidence: MappingEvidence | None = None
    candidates: list[VehicleSnapshot] = Field(default_factory=list)


class PreviewEligibility(BaseModel):
    available: bool = False
    reason: str = "No eligible authored inspection preview is available."
    scenario_id: str | None = None


class ResolutionResult(BaseModel):
    status: ResolutionStatus
    reference: AuctionReference
    provider_context: ProviderContext = Field(default_factory=ProviderContext)
    identity: ListingIdentity | None = None
    vehicle: Vehicle | None = None
    candidates: list[VehicleSnapshot] = Field(default_factory=list)
    provenance: Provenance | None = None
    field_evidence: dict[str, FieldEvidence] = Field(default_factory=dict)
    mapping_evidence: MappingEvidence | None = None
    reference_evidence: ReferenceEvidence | None = None
    record_id: str | None = None
    event_id: str | None = None
    event_status: str | None = None
    event_date: str | None = None
    freshness: Freshness | None = None
    evidence: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    reasons: list[str] = Field(default_factory=list)
    snapshot_fingerprint: str | None = None
    preview_eligibility: PreviewEligibility = Field(default_factory=PreviewEligibility)


class ResolveRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    url: str = Field(min_length=1, max_length=2048)
