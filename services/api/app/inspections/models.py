"""Bounded preview contracts. These findings are distinct from metadata evidence."""
from typing import Literal

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, model_validator

from app.domain.models import AuctionReference, Freshness, ListingIdentity, ProviderContext, PreviewEligibility, ResolutionStatus


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid")


class PreviewRequest(Contract):
    url: str = Field(min_length=1, max_length=2048)
    expected_snapshot_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")


class InspectionTarget(Contract):
    reference: AuctionReference
    provider_context: ProviderContext
    identity: ListingIdentity
    record_id: str
    event_id: str | None = None
    event_status: str | None = None
    event_date: str | None = None
    snapshot_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")
    content_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")
    vin: str | None = None
    source_observed_at: AwareDatetime | None = None
    retrieved_at: AwareDatetime
    freshness: Freshness | None = None


class PhotoAsset(Contract):
    asset_id: str
    title: str
    alt_text: str
    view_label: str
    content_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    width: int = Field(gt=0, le=2048)
    height: int = Field(gt=0, le=2048)
    mime_type: Literal["image/png"] = "image/png"
    source_kind: Literal["SELF_AUTHORED_FIXTURE"] = "SELF_AUTHORED_FIXTURE"
    author: str
    rights_reference: str
    capture_time: AwareDatetime | None = None
    asset_url: str


class Localization(Contract):
    asset_id: str
    content_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    # Only a reviewed normalized box is currently supported; no guessed geometry.
    x: float = Field(ge=0, le=1, allow_inf_nan=False)
    y: float = Field(ge=0, le=1, allow_inf_nan=False)
    width: float = Field(gt=0, le=1, allow_inf_nan=False)
    height: float = Field(gt=0, le=1, allow_inf_nan=False)
    verified_by: str = Field(min_length=1, pattern=r"\S")
    review_basis: str = Field(min_length=1, pattern=r"\S")

    @model_validator(mode="after")
    def within_image(self):
        if self.x + self.width > 1 or self.y + self.height > 1:
            raise ValueError("Localization must remain within its image.")
        return self


class InspectionFinding(Contract):
    finding_id: str = Field(min_length=1, max_length=100, pattern=r"\S")
    classification: Literal["OBSERVED", "SUSPECTED", "UNKNOWN"]
    region: str = Field(min_length=1, max_length=100, pattern=r"\S")
    component: str = Field(min_length=1, max_length=100, pattern=r"\S")
    description: str = Field(min_length=1, max_length=1200, pattern=r"\S")
    rationale: str = Field(min_length=1, max_length=1200, pattern=r"\S")
    severity: Literal["MINOR", "MODERATE", "SEVERE", "UNKNOWN"] = "UNKNOWN"
    confidence: None = None
    confidence_basis: str = "Not scored: hand-authored mock example, not a calibrated model output."
    image_ids: list[str] = Field(default_factory=list, max_length=6)
    confirmation: str = Field(min_length=1, max_length=1200, pattern=r"\S")
    localization: Localization | None = None

    @model_validator(mode="after")
    def honest_evidence(self):
        if self.classification in {"OBSERVED", "SUSPECTED"} and not self.image_ids:
            raise ValueError("Visible observations and suspicions require image evidence.")
        # These tokens are prohibited assertions, not an automotive safety classifier.
        # All seeded wording is also manually reviewed as a fixed fixture contract.
        text = " ".join((self.description, self.rationale, self.confirmation)).casefold()
        if any(token in text for token in ("safe to drive", "roadworthy", "no hidden damage", "airbags work", "structure is sound")):
            raise ValueError("Unsupported safety assertions are not allowed.")
        return self


class Exclusion(Contract):
    asset_id: str | None = None
    reason: str


class InspectionProvenance(Contract):
    mode: Literal["MOCK"] = "MOCK"
    engine_id: Literal["mock-inspection-engine"] = "mock-inspection-engine"
    engine_version: Literal["1.0.0"] = "1.0.0"
    scenario_id: str
    fixture_revision: Literal["inspection-fixtures-v1"] = "inspection-fixtures-v1"
    schema_version: Literal["inspection-preview-v1"] = "inspection-preview-v1"
    generated_at: AwareDatetime
    target_digest: str
    image_digests: dict[str, str]
    model_provider: None = None
    model_id: None = None
    prompt_version: None = None


class InspectionPreview(Contract):
    request_id: str
    outcome: Literal["COMPLETED", "PARTIAL", "BLOCKED", "FAILED"]
    reason_code: str
    resolver_status: ResolutionStatus
    reasons: list[str] = Field(default_factory=list, max_length=30)
    target: InspectionTarget | None = None
    assets: list[PhotoAsset] = Field(default_factory=list, max_length=6)
    findings: list[InspectionFinding] = Field(default_factory=list, max_length=30)
    checks: list[str] = Field(default_factory=list, max_length=20)
    limitations: list[str] = Field(default_factory=list, max_length=20)
    exclusions: list[Exclusion] = Field(default_factory=list, max_length=6)
    provenance: InspectionProvenance | None = None

    @model_validator(mode="after")
    def linked_report(self):
        for text in self.checks + self.limitations + self.reasons:
            if any(token in text.casefold() for token in ("safe to drive", "roadworthy", "no hidden damage", "airbags work", "structure is sound")):
                raise ValueError("Unsupported safety assertions are not allowed in report text.")
        ids = {asset.asset_id for asset in self.assets}
        if len(ids) != len(self.assets):
            raise ValueError("Duplicate image IDs are not allowed.")
        if self.outcome in {"BLOCKED", "FAILED"} and (self.assets or self.findings or self.provenance):
            raise ValueError("Blocked/failed previews cannot carry unvalidated report content.")
        if self.outcome in {"COMPLETED", "PARTIAL"}:
            if not self.target or not self.assets or not self.provenance:
                raise ValueError("A preview needs a target, eligible images and provenance.")
            if self.target.snapshot_fingerprint != self.provenance.target_digest:
                raise ValueError("Report target digest does not match its snapshot.")
            if self.provenance.image_digests != {a.asset_id: a.content_sha256 for a in self.assets}:
                raise ValueError("Report image digests do not match its assets.")
        for finding in self.findings:
            if not set(finding.image_ids) <= ids:
                raise ValueError("Finding references an image outside this report.")
            if finding.localization:
                loc = finding.localization
                asset = next((a for a in self.assets if a.asset_id == loc.asset_id), None)
                if not asset or asset.content_sha256 != loc.content_sha256 or loc.asset_id not in finding.image_ids:
                    raise ValueError("Localization must match its exact evidence image.")
        return self
