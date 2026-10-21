"""Strict, bounded metadata-only contracts for a manually compiled review."""
from datetime import datetime, timezone
from typing import Literal

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, field_validator, model_validator

from app.domain.models import AuctionHouse, AuctionReference

PROHIBITED_ASSERTIONS = ("safe to drive", "roadworthy", "no hidden damage", "airbags work", "structure is sound")


def reject_known_safety_assertions(text: str) -> None:
    # A narrow contract guard, not a general automotive/natural-language classifier.
    if any(token in text.casefold() for token in PROHIBITED_ASSERTIONS):
        raise ValueError("Unsupported safety-verdict wording is not accepted in a manual review.")


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ManualVehicle(Contract):
    vin: str | None = Field(default=None, min_length=17, max_length=17)
    year: int | None = Field(default=None, strict=True, ge=1900, le=2100)
    make: str | None = Field(default=None, min_length=1, max_length=80, pattern=r"\S")
    model: str | None = Field(default=None, min_length=1, max_length=80, pattern=r"\S")

    @field_validator("vin", mode="before")
    @classmethod
    def normalize_vin(cls, value):
        return value.strip().upper() if isinstance(value, str) else value

    @field_validator("vin")
    @classmethod
    def vin_characters(cls, value):
        if value is not None and (not value.isascii() or any(c not in "0123456789ABCDEFGHJKLMNPRSTUVWXYZ" for c in value)):
            raise ValueError("VIN must contain 17 ASCII letters/digits excluding I, O and Q.")
        return value

    @field_validator("year")
    @classmethod
    def reasonable_year(cls, value):
        if value is not None and value > datetime.now(timezone.utc).year + 2:
            raise ValueError("Year is beyond the supported model-year range.")
        return value


class ManualPhoto(Contract):
    photo_id: str = Field(min_length=1, max_length=80, pattern=r"^[A-Za-z0-9_-]+$")
    sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    width: int = Field(strict=True, gt=0, le=2048)
    height: int = Field(strict=True, gt=0, le=2048)
    label: str = Field(min_length=1, max_length=160, pattern=r"\S")


class DeclaredPhoto(ManualPhoto):
    verification_status: Literal["CLIENT_DECLARED_NOT_SERVER_VERIFIED"] = "CLIENT_DECLARED_NOT_SERVER_VERIFIED"


class ManualFinding(Contract):
    photo_id: str | None = Field(default=None, min_length=1, max_length=80, pattern=r"^[A-Za-z0-9_-]+$")
    classification: Literal["OBSERVED", "SUSPECTED", "UNKNOWN"]
    component: str = Field(min_length=1, max_length=100, pattern=r"\S")
    description: str = Field(min_length=1, max_length=1200, pattern=r"\S")

    @model_validator(mode="after")
    def visible_evidence_required(self):
        if self.classification in {"OBSERVED", "SUSPECTED"} and self.photo_id is None:
            raise ValueError("User-reported observations and suspicions require a referenced photo.")
        reject_known_safety_assertions(" ".join((self.component, self.description)))
        return self


class ManualReviewRequest(Contract):
    url: str = Field(min_length=1, max_length=2048)
    stock_number: str | None = Field(default=None, min_length=1, max_length=32, pattern=r"^[0-9]+$")
    vehicle: ManualVehicle = Field(default_factory=ManualVehicle)
    photos: list[ManualPhoto] = Field(default_factory=list, max_length=6)
    findings: list[ManualFinding] = Field(default_factory=list, max_length=30)
    notes: str = Field(default="", max_length=2000)

    @model_validator(mode="after")
    def linked_user_evidence(self):
        ids = {photo.photo_id for photo in self.photos}
        if len(ids) != len(self.photos):
            raise ValueError("Photo IDs must be distinct within a manual review.")
        if any(finding.photo_id is not None and finding.photo_id not in ids for finding in self.findings):
            raise ValueError("A finding references photo metadata outside this manual review.")
        reject_known_safety_assertions(self.notes)
        return self


class CanonicalClaim(Contract):
    house: AuctionHouse
    lot_or_stock_number: str | None = None
    verification_status: Literal["UNVERIFIED"] = "UNVERIFIED"


class ReportedFinding(ManualFinding):
    source_kind: Literal["USER_REPORTED"] = "USER_REPORTED"


class PhysicalCheck(Contract):
    system: str
    status: Literal["UNKNOWN"] = "UNKNOWN"
    recommendation: str


class ManualReviewReport(Contract):
    schema_version: Literal["manual-review-v1"] = "manual-review-v1"
    source_kind: Literal["USER_SUPPLIED_UNVERIFIED"] = "USER_SUPPLIED_UNVERIFIED"
    verification_status: Literal["UNVERIFIED"] = "UNVERIFIED"
    reference: AuctionReference
    canonical_claim: CanonicalClaim
    vehicle: ManualVehicle
    photos: list[DeclaredPhoto]
    findings: list[ReportedFinding]
    notes: str
    checks: list[PhysicalCheck]
    warnings: list[str]
    generated_at: AwareDatetime
