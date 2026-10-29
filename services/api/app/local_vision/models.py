"""Strict contracts for private, unverified local photo analysis."""
from typing import Literal

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, model_validator

from app.domain.models import AuctionReference
from app.manual_reviews.models import PhysicalCheck, reject_known_safety_assertions

MAX_IMAGE_BYTES = 2 * 1024 * 1024
MAX_TOTAL_BYTES = 6 * 1024 * 1024
MAX_BASE64_LENGTH = 4 * ((MAX_IMAGE_BYTES + 2) // 3)


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ImageInput(Contract):
    image_id: str = Field(min_length=1, max_length=80, pattern=r"^[A-Za-z0-9_-]+$")
    label: str = Field(min_length=1, max_length=160, pattern=r"\S")
    content_base64: str = Field(min_length=1, max_length=MAX_BASE64_LENGTH)
    sha256: str = Field(pattern=r"^[a-f0-9]{64}$")


class LocalInspectionRequest(Contract):
    url: str = Field(min_length=1, max_length=2048)
    local_processing_permission: bool = Field(strict=True)
    images: list[ImageInput] = Field(min_length=1, max_length=3)

    @model_validator(mode="after")
    def explicit_private_input(self):
        if not self.local_processing_permission:
            raise ValueError("Explicit permission for local image processing is required.")
        if len({image.image_id for image in self.images}) != len(self.images):
            raise ValueError("Image identifiers must be distinct.")
        return self


class LocalFinding(Contract):
    classification: Literal["OBSERVED", "SUSPECTED", "UNKNOWN"]
    component: str = Field(min_length=1, max_length=100, pattern=r"\S")
    region: str = Field(min_length=1, max_length=100, pattern=r"\S")
    description: str = Field(min_length=1, max_length=1200, pattern=r"\S")
    rationale: str = Field(min_length=1, max_length=1200, pattern=r"\S")
    confirmation: str = Field(min_length=1, max_length=1200, pattern=r"\S")
    image_ids: list[str] = Field(max_length=3)
    confidence: None = None

    @model_validator(mode="after")
    def evidence_and_wording(self):
        if len(set(self.image_ids)) != len(self.image_ids):
            raise ValueError("Finding image references must be distinct.")
        if self.classification in {"OBSERVED", "SUSPECTED"} and not self.image_ids:
            raise ValueError("Observations and suspicions require image evidence.")
        reject_known_safety_assertions(" ".join((self.component, self.region, self.description,
                                                self.rationale, self.confirmation)))
        return self


class ModelOutput(Contract):
    findings: list[LocalFinding] = Field(max_length=20)
    limitations: list[str] = Field(min_length=1, max_length=10)

    @model_validator(mode="after")
    def bounded_limitations(self):
        for text in self.limitations:
            if not text.strip() or len(text) > 600:
                raise ValueError("Model limitations must be nonblank and bounded.")
            reject_known_safety_assertions(text)
        return self


class PreparedImage(Contract):
    image_id: str
    label: str
    source_sha256: str
    inference_sha256: str
    width: int
    height: int


class LocalVisionStatus(Contract):
    enabled: bool
    available: bool
    reason_code: str
    message: str
    model: str | None = None
    endpoint: Literal["LOCAL_LOOPBACK"] = "LOCAL_LOOPBACK"
    max_images: Literal[3] = 3
    max_image_bytes: Literal[2097152] = MAX_IMAGE_BYTES


class LocalProvenance(Contract):
    mode: Literal["LOCAL_MODEL"] = "LOCAL_MODEL"
    model: str
    model_digest: str
    adapter_version: Literal["ollama-local-v1"] = "ollama-local-v1"
    prompt_version: Literal["visible-evidence-v2"] = "visible-evidence-v2"
    schema_version: Literal["local-inspection-v1"] = "local-inspection-v1"
    image_digests: dict[str, str]
    generated_at: AwareDatetime
    elapsed_ms: int = Field(ge=0)
    prompt_eval_count: int | None = Field(default=None, strict=True, ge=0, le=1_000_000_000)
    eval_count: int | None = Field(default=None, strict=True, ge=0, le=1_000_000_000)


class LocalInspectionReport(Contract):
    schema_version: Literal["local-inspection-v1"] = "local-inspection-v1"
    outcome: Literal["COMPLETED", "BLOCKED", "FAILED"]
    reason_code: str
    reasons: list[str]
    verification_status: Literal["UNVERIFIED"] = "UNVERIFIED"
    review_status: Literal["EXPERIMENTAL_UNREVIEWED"] = "EXPERIMENTAL_UNREVIEWED"
    reference: AuctionReference
    images: list[PreparedImage] = Field(default_factory=list, max_length=3)
    findings: list[LocalFinding] = Field(default_factory=list, max_length=20)
    checks: list[PhysicalCheck] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    provenance: LocalProvenance | None = None

    @model_validator(mode="after")
    def exact_evidence(self):
        if self.outcome != "COMPLETED":
            if self.images or self.findings or self.provenance:
                raise ValueError("Blocked or failed experiments cannot contain findings or model provenance.")
            return self
        if not self.images or self.provenance is None:
            raise ValueError("A completed experiment needs actual image/model provenance.")
        ids = {image.image_id for image in self.images}
        if len(ids) != len(self.images):
            raise ValueError("Image identifiers must be distinct.")
        if self.provenance.image_digests != {image.image_id: image.inference_sha256 for image in self.images}:
            raise ValueError("Inference digests do not match report images.")
        if any(not set(finding.image_ids) <= ids for finding in self.findings):
            raise ValueError("Model output references an image outside this experiment.")
        return self
