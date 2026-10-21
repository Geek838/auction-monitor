"""Small allowlisted authored raster catalog. Never read a caller-supplied path."""
from dataclasses import dataclass
from datetime import datetime
import hashlib
from io import BytesIO
import json
from pathlib import Path
import re
import warnings

from PIL import Image
from pydantic import AwareDatetime, BaseModel, ConfigDict, Field

from app.domain.models import AuctionReference, ProviderContext, ResolutionResult, ResolutionStatus
from app.inspections.binding import content_projection, digest
from app.providers.fixture import FixtureProvider
from app.providers.simulation import SimulationProvider

ASSET_ROOT = Path(__file__).with_name("assets")
MAX_ASSET_BYTES = 1024 * 1024
MAX_ASSET_PIXELS = 2048 * 2048
MAX_ASSETS = 6
# Seed observations are approved for these exact reviewed bytes, independently
# of mutable display/rights metadata. Rehashing arbitrary replacement PNGs in
# the manifest must not make them eligible for canned observations.
APPROVED_CONTENT = {
    "front-illustration-v1": "74315563e1574796cbf3aea5d5774530f0b978daa88d8c88214e2f5b5216e1eb",
    "side-illustration-v1": "e0083791fd7263f7fe45d20befb046b58e2a9727d45c2aac937df4f259aca535",
    "rear-illustration-v1": "695e99e3c7b854dd0123d6af8596d004936cb36000061f1cfa3fdbf48223ee01",
}


class AssetUnavailable(ValueError):
    """Safe, bounded reason for excluding an asset; never includes local paths."""


class AssetRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")
    asset_id: str = Field(pattern=r"^[a-z0-9-]{1,80}$")
    filename: str = Field(pattern=r"^[a-z0-9-]{1,80}\.png$")
    sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    width: int = Field(gt=0, le=2048)
    height: int = Field(gt=0, le=2048)
    mime_type: str = "image/png"
    view_label: str = Field(min_length=1, max_length=100, pattern=r"\S")
    alt_text: str = Field(min_length=1, max_length=1200, pattern=r"\S")
    source_kind: str = "SELF_AUTHORED_FIXTURE"
    author: str = Field(min_length=1, max_length=200, pattern=r"\S")
    rights_reference: str = Field(min_length=1, max_length=500, pattern=r"\S")
    reviewed_by: str = Field(min_length=1, max_length=200, pattern=r"\S")
    title: str | None = Field(default=None, min_length=1, max_length=200, pattern=r"\S")
    permissions: dict[str, bool] = Field(default_factory=dict)
    revoked: bool = False
    expires_at: AwareDatetime | None = None


@dataclass(frozen=True)
class Scenario:
    scenario_id: str
    record_id: str
    asset_ids: tuple[str, ...]
    excluded_ids: tuple[str, ...] = ()
    fail_engine: bool = False
    no_visible_marks: bool = False


SCENARIOS = {
    "copart-demo": Scenario("copart-front-example", "copart-demo", ("front-illustration-v1", "side-illustration-v1")),
    "iaai-demo": Scenario("iaai-front-example", "iaai-demo", ("front-illustration-v1", "side-illustration-v1")),
    "copart-archive": Scenario("historical-partial-example", "copart-archive", ("front-illustration-v1", "side-illustration-v1"), ("side-illustration-v1",)),
    "copart-engine-failure": Scenario("engine-failure-example", "copart-engine-failure", ("front-illustration-v1",), fail_engine=True),
    "copart-no-visible": Scenario("no-visible-marks-example", "copart-no-visible", ("rear-illustration-v1",), no_visible_marks=True),
}


class AssetCatalog:
    def __init__(self, root: Path = ASSET_ROOT):
        self.root = Path(root)
        self._records: dict[str, AssetRecord] | None = None
        self._manifest_digest: str | None = None
        self.scenarios = dict(SCENARIOS)

    @property
    def records(self) -> dict[str, AssetRecord]:
        try:
            manifest = self.root / "manifest.json"
            if manifest.is_symlink():
                raise ValueError("Invalid manifest link.")
            with manifest.open("rb") as handle:
                raw = handle.read(65537)
            if len(raw) > 65536:
                raise ValueError("Invalid manifest size.")
            current_digest = hashlib.sha256(raw).hexdigest()
            if self._records is None or current_digest != self._manifest_digest:
                data = json.loads(raw)
                if data.get("schema_version") != "1" or not 0 < len(data["assets"]) <= MAX_ASSETS:
                    raise ValueError("Invalid manifest shape.")
                parsed = [AssetRecord.model_validate(item) for item in data["assets"]]
                if len({item.asset_id for item in parsed}) != len(parsed):
                    raise ValueError("Duplicate asset IDs.")
                self._records = {item.asset_id: item for item in parsed}
                self._manifest_digest = current_digest
        except Exception as exc:
            raise AssetUnavailable("Authored asset catalog is unavailable or invalid.") from exc
        return self._records

    def scenario_for(self, result: ResolutionResult) -> Scenario | None:
        if result.status != "MATCHED" or result.provider_context.mode not in {"FIXTURE", "SIMULATED"}:
            return None
        expected_id = "fixture" if result.provider_context.mode == "FIXTURE" else "simulation"
        if result.provider_context.id != expected_id:
            return None
        scenario = self.scenarios.get(result.record_id or "")
        if not scenario:
            return None
        # Compare against pristine authored data, not the candidate being validated.
        trusted = FixtureProvider() if expected_id == "fixture" else SimulationProvider()
        snapshot = trusted.records.get(scenario.record_id)
        if not snapshot:
            return None
        expected = ResolutionResult(status=ResolutionStatus.MATCHED,
            reference=AuctionReference(house=snapshot.identity.house, url="fixture://binding"),
            provider_context=ProviderContext(id=expected_id, mode=result.provider_context.mode),
            identity=snapshot.identity, vehicle=snapshot.vehicle, record_id=snapshot.record_id,
            event_id=snapshot.event_id, event_status=snapshot.event_status, event_date=snapshot.event_date,
            provenance=snapshot.provenance)
        return scenario if digest(content_projection(result)) == digest(content_projection(expected)) else None

    def validated_bytes(self, asset_id: str, *, now: datetime) -> tuple[AssetRecord, bytes]:
        if not re.fullmatch(r"[a-z0-9-]{1,80}", asset_id):
            raise AssetUnavailable("Unknown authored asset.")
        record = self.records.get(asset_id)
        if record is None:
            raise AssetUnavailable("Unknown authored asset.")
        if record.revoked or (record.expires_at is not None and now >= record.expires_at):
            raise AssetUnavailable("Authored asset permission is expired or revoked.")
        if not record.permissions.get("image_display", False) or not record.permissions.get("mock_preview", False):
            raise AssetUnavailable("Authored asset display or mock-preview permission is absent.")
        if record.source_kind != "SELF_AUTHORED_FIXTURE" or record.mime_type != "image/png":
            raise AssetUnavailable("Unsupported authored asset format or origin.")
        if APPROVED_CONTENT.get(asset_id) != record.sha256:
            raise AssetUnavailable("Asset bytes are not approved for this versioned mock scenario.")
        try:
            path = self.root / record.filename
            if path.is_symlink() or path.resolve().parent != self.root.resolve():
                raise ValueError("Asset is outside the catalog.")
            with path.open("rb") as handle:
                payload = handle.read(MAX_ASSET_BYTES + 1)
            if len(payload) > MAX_ASSET_BYTES or hashlib.sha256(payload).hexdigest() != record.sha256:
                raise ValueError("Asset content digest mismatch.")
            with warnings.catch_warnings():
                warnings.simplefilter("error", Image.DecompressionBombWarning)
                with Image.open(BytesIO(payload)) as image:
                    if image.format != "PNG" or image.size != (record.width, record.height) or image.width * image.height > MAX_ASSET_PIXELS:
                        raise ValueError("Invalid decoded image dimensions or format.")
                    image.verify()
                with Image.open(BytesIO(payload)) as image:
                    image.load()
                    if getattr(image, "n_frames", 1) != 1:
                        raise ValueError("Animated assets are not supported.")
        except Exception as exc:
            raise AssetUnavailable("Authored asset bytes, digest or decoded image are invalid.") from exc
        return record, payload
