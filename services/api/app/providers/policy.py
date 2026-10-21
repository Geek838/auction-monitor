"""Static, fail-closed permission configuration. This module performs no network I/O."""
from datetime import datetime, timezone
from enum import StrEnum
import os
from collections.abc import Callable

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, model_validator

from app.domain.models import AuctionHouse, AuctionReference, ProviderContext, ProviderResolution, VehicleSnapshot
from app.providers.base import AuctionSource, NotAuthorized, SourceUnavailable


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Purpose(StrEnum):
    METADATA_LOOKUP = "metadata_lookup"
    METADATA_DISPLAY = "metadata_display"
    METADATA_CACHE = "metadata_cache"
    IMAGE_RETRIEVAL = "image_retrieval"
    IMAGE_DISPLAY = "image_display"
    IMAGE_STORAGE = "image_storage"
    AI_INFERENCE = "ai_inference"
    MODEL_TRAINING = "model_training"
    REDISTRIBUTION = "redistribution"


class AuthorizationEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid")
    reference: str = Field(min_length=1, pattern=r"\S")
    reviewer: str = Field(min_length=1, pattern=r"\S")
    reviewed_at: AwareDatetime
    effective_at: AwareDatetime
    expires_at: AwareDatetime | None = None
    revoked: bool = False
    purposes: set[Purpose] = Field(default_factory=set)

    @model_validator(mode="after")
    def valid_window(self):
        if self.expires_at is not None and self.expires_at <= self.effective_at:
            raise ValueError("Authorization expiry must follow its effective date.")
        return self


class ProviderPolicy(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    mode: str = "EXTERNAL"
    enabled: bool = False
    capabilities: set[str] = Field(default_factory=set)
    houses: set[AuctionHouse] = Field(default_factory=set)
    permissions: dict[Purpose, bool] = Field(default_factory=dict)
    authorization: AuthorizationEvidence | None = None
    required_credentials: list[str] = Field(default_factory=list)
    cache_ttl_seconds: int | None = Field(default=None, gt=0)
    max_retention_seconds: int | None = Field(default=None, gt=0)
    freshness_threshold_seconds: int | None = Field(default=None, gt=0)
    freshness_basis: str | None = None

    @model_validator(mode="after")
    def consistent_policy(self):
        if self.mode not in {"FIXTURE", "SIMULATED", "EXTERNAL"}:
            raise ValueError("Unknown provider mode.")
        if self.cache_ttl_seconds is not None:
            if not self.permissions.get(Purpose.METADATA_CACHE, False):
                raise ValueError("A cache TTL requires explicit cache permission.")
            if self.max_retention_seconds is None or self.cache_ttl_seconds > self.max_retention_seconds:
                raise ValueError("Cache TTL must not exceed explicit maximum retention.")
        if self.permissions.get(Purpose.METADATA_CACHE, False) and self.cache_ttl_seconds is None:
            raise ValueError("Cache permission requires an explicit TTL and retention ceiling.")
        if self.freshness_threshold_seconds is not None and not self.freshness_basis:
            raise ValueError("Freshness thresholds require a documented basis.")
        if any(not name.isidentifier() for name in self.required_credentials):
            raise ValueError("Credential names must be variable identifiers.")
        return self


class GuardedProvider:
    """Check the current policy before either provider operation, including after revocation."""
    def __init__(self, provider: AuctionSource, policy: ProviderPolicy, *,
                 clock: Callable[[], datetime] = utc_now,
                 credential_present: Callable[[str], bool] | None = None):
        self.provider = provider
        self.policy = policy
        self.clock = clock
        self.credential_present = credential_present or (lambda name: bool(os.environ.get(name)))

    @property
    def warnings(self) -> list[str]:
        return list(getattr(self.provider, "warnings", []))

    def authorize(self, purpose: Purpose) -> None:
        policy = self.policy
        if not policy.enabled:
            raise NotAuthorized("Provider is disabled.")
        if not policy.permissions.get(purpose, False):
            raise NotAuthorized("Permission for the requested use is absent.")
        if policy.mode == "EXTERNAL":
            now = self.clock()
            evidence = policy.authorization
            if evidence is None or evidence.revoked or purpose not in evidence.purposes:
                raise NotAuthorized("Reviewed authorization for this use is absent or revoked.")
            if evidence.reviewed_at > now or evidence.effective_at > now or (evidence.expires_at is not None and now >= evidence.expires_at):
                raise NotAuthorized("Authorization is not currently valid.")
            if any(not self.credential_present(name) for name in policy.required_credentials):
                raise NotAuthorized("Required provider credentials are unavailable.")

    def context(self) -> ProviderContext:
        reasons: list[str] = []
        try:
            self.authorize(Purpose.METADATA_LOOKUP)
            self.authorize(Purpose.METADATA_DISPLAY)
        except NotAuthorized as exc:
            reasons.append(str(exc))
        authorized = not reasons
        return ProviderContext(
            id=self.policy.id, name=self.policy.name, mode=self.policy.mode,
            authorization=("NOT_REQUIRED" if self.policy.mode != "EXTERNAL" else "APPROVED") if authorized else "DENIED",
            enabled=self.policy.enabled, available=authorized, reasons=reasons,
        )

    def validate_snapshot(self, snapshot: VehicleSnapshot) -> None:
        expected_type = {"FIXTURE": "MOCK", "SIMULATED": "SIMULATED", "EXTERNAL": "LICENSED"}[self.policy.mode]
        if snapshot.provenance.data_type != expected_type:
            raise SourceUnavailable("Provider returned data from a different mode; synthetic fallback is not permitted.")
        if snapshot.identity.house not in self.policy.houses:
            raise SourceUnavailable("Provider returned an unsupported auction house.")

    async def resolve(self, reference: AuctionReference) -> ProviderResolution:
        self.authorize(Purpose.METADATA_LOOKUP)
        self.authorize(Purpose.METADATA_DISPLAY)
        if reference.house not in self.policy.houses:
            raise SourceUnavailable("Provider does not support this auction house.")
        if "canonical_lookup" not in self.policy.capabilities:
            raise SourceUnavailable("Provider does not support canonical lookup.")
        if reference.page_id and "page_mapping" not in self.policy.capabilities:
            return ProviderResolution()
        lookup = await self.provider.resolve(reference)
        # Permission can expire or be revoked while a provider operation is in flight.
        self.authorize(Purpose.METADATA_LOOKUP)
        self.authorize(Purpose.METADATA_DISPLAY)
        if reference.house not in self.policy.houses:
            raise NotAuthorized("Auction-house scope changed during lookup.")
        if not isinstance(lookup, ProviderResolution):
            raise SourceUnavailable("Provider returned an invalid schema.")
        for candidate in lookup.candidates:
            self.validate_snapshot(candidate)
        return lookup

    async def get_vehicle(self, listing_id: str) -> VehicleSnapshot:
        self.authorize(Purpose.METADATA_LOOKUP)
        self.authorize(Purpose.METADATA_DISPLAY)
        if "vehicle_lookup" not in self.policy.capabilities:
            raise SourceUnavailable("Provider does not support vehicle lookup.")
        snapshot = await self.provider.get_vehicle(listing_id)
        self.authorize(Purpose.METADATA_LOOKUP)
        self.authorize(Purpose.METADATA_DISPLAY)
        if not isinstance(snapshot, VehicleSnapshot):
            raise SourceUnavailable("Provider returned an invalid vehicle schema.")
        self.validate_snapshot(snapshot)
        return snapshot


def provider_context(provider: AuctionSource) -> ProviderContext:
    context = getattr(provider, "context", None)
    return context() if callable(context) else ProviderContext()
