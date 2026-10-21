import asyncio
from datetime import datetime, timedelta, timezone
import hashlib
from io import BytesIO
import json
from pathlib import Path
import shutil

from PIL import Image
import pytest

from app.inspections.binding import stable_snapshot_fingerprint
from app.inspections.catalog import ASSET_ROOT, MAX_ASSET_BYTES, AssetCatalog, AssetUnavailable
from app.providers.registry import build_provider
from app.resolution.parser import parse_auction_url
from app.resolution.resolver import resolve_auction

NOW = datetime(2026, 10, 21, 12, tzinfo=timezone.utc)
FRONT = "front-illustration-v1"


@pytest.fixture
def local_catalog(tmp_path):
    for source in ASSET_ROOT.iterdir():
        if source.suffix in {".json", ".png"}:
            shutil.copy2(source, tmp_path / source.name)
    return AssetCatalog(tmp_path)


def resolved():
    return asyncio.run(resolve_auction(parse_auction_url("https://copart.com/lot/51374586"), build_provider("fixture"), now=NOW))


def test_authored_catalog_describes_real_bounded_pngs_with_matching_digests(local_catalog):
    assert 0 < len(local_catalog.records) <= 6
    for asset_id, record in local_catalog.records.items():
        verified, data = local_catalog.validated_bytes(asset_id, now=NOW)
        assert verified.asset_id == asset_id
        assert hashlib.sha256(data).hexdigest() == record.sha256
        with Image.open(BytesIO(data)) as image:
            image.load()
            assert image.size == (record.width, record.height)
            assert image.format == "PNG"
        assert record.source_kind == "SELF_AUTHORED_FIXTURE"
        assert record.author and record.rights_reference
        assert record.permissions["image_display"] is True
        assert record.permissions["mock_preview"] is True
        assert record.permissions.get("ai_inference", False) is False
        assert record.permissions.get("model_training", False) is False


@pytest.mark.parametrize("asset_id", ["unknown", "../front-illustration-v1", "%2e%2e", "/etc/passwd", "data:image/png;base64,AAAA", "https://evil.example/a.png"])
def test_asset_identifiers_cannot_select_paths_urls_or_arbitrary_bytes(local_catalog, asset_id):
    with pytest.raises(AssetUnavailable):
        local_catalog.validated_bytes(asset_id, now=NOW)


@pytest.mark.parametrize("change", ["revoked", "expired", "no-display", "no-preview", "wrong-origin", "wrong-mime", "wrong-dimensions", "digest", "truncated", "oversized", "symlink"])
def test_unusable_or_unpermitted_asset_bytes_are_not_released(local_catalog, tmp_path, change):
    record = local_catalog.records[FRONT]
    image_path = local_catalog.root / record.filename
    if change == "revoked":
        record.revoked = True
    elif change == "expired":
        record.expires_at = NOW
    elif change == "no-display":
        record.permissions["image_display"] = False
    elif change == "no-preview":
        record.permissions["mock_preview"] = False
    elif change == "wrong-origin":
        record.source_kind = "UNVERIFIED_AUCTION_PHOTO"
    elif change == "wrong-mime":
        record.mime_type = "image/svg+xml"
    elif change == "wrong-dimensions":
        record.width += 1
    elif change == "digest":
        image_path.write_bytes(image_path.read_bytes() + b"changed bytes")
    elif change == "truncated":
        payload = image_path.read_bytes()[:50]
        image_path.write_bytes(payload)
        record.sha256 = hashlib.sha256(payload).hexdigest()
    elif change == "oversized":
        image_path.write_bytes(b"x" * (MAX_ASSET_BYTES + 1))
    else:
        outside = tmp_path.parent / (tmp_path.name + "-outside.png")
        shutil.copy2(image_path, outside)
        image_path.unlink()
        try:
            image_path.symlink_to(outside)
        except OSError:
            pytest.skip("Creating symlinks is unavailable in this operating-system configuration")
    with pytest.raises(AssetUnavailable) as failure:
        local_catalog.validated_bytes(FRONT, now=NOW)
    assert str(tmp_path) not in str(failure.value)


@pytest.mark.parametrize("change", ["too-many", "duplicate-id", "unknown-field", "traversal-filename", "non-json", "blank-author", "blank-rights", "blank-review"])
def test_manifest_cannot_expand_the_allowlist_or_smuggle_paths(local_catalog, change):
    manifest_path = local_catalog.root / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    if change == "too-many":
        manifest["assets"] = manifest["assets"] * 3
    elif change == "duplicate-id":
        manifest["assets"].append(manifest["assets"][0])
    elif change == "unknown-field":
        manifest["assets"][0]["remote_url"] = "https://evil.example/image.png"
    elif change == "traversal-filename":
        manifest["assets"][0]["filename"] = "../private.png"
    elif change == "blank-author":
        manifest["assets"][0]["author"] = " "
    elif change == "blank-rights":
        manifest["assets"][0]["rights_reference"] = " "
    elif change == "blank-review":
        manifest["assets"][0]["reviewed_by"] = " "
    else:
        manifest_path.write_text("not JSON")
    if change != "non-json":
        manifest_path.write_text(json.dumps(manifest))
    with pytest.raises(AssetUnavailable):
        local_catalog.records


def test_snapshot_fingerprint_ignores_request_only_timing_and_permission_context():
    result = resolved()
    initial = stable_snapshot_fingerprint(result)
    result.provenance.retrieved_at += timedelta(hours=12)
    result.freshness.evaluated_at += timedelta(hours=12)
    result.freshness.status = "STALE"
    result.provider_context.available = False
    result.provider_context.authorization = "DENIED"
    result.warnings.append("An unrelated presentation warning")
    assert stable_snapshot_fingerprint(result) == initial


@pytest.mark.parametrize("change", ["provider", "mode", "record", "event", "identity", "vehicle", "source-reference", "market"])
def test_snapshot_fingerprint_changes_when_its_actual_target_content_changes(change):
    result = resolved()
    initial = stable_snapshot_fingerprint(result)
    if change == "provider":
        result.provider_context.id = "simulation"
    elif change == "mode":
        result.provider_context.mode = "SIMULATED"
    elif change == "record":
        result.record_id = "different-record"
    elif change == "event":
        result.event_id = "different-event"
    elif change == "identity":
        result.identity.lot_or_stock_number = "051374586"
    elif change == "vehicle":
        result.vehicle.trim = "Revised snapshot trim"
    elif change == "source-reference":
        result.provenance.source_url = "fixture://another/source-record"
    else:
        result.reference.country = "CA"
    assert stable_snapshot_fingerprint(result) != initial


def test_image_scenario_cannot_follow_a_different_event_or_similar_vehicle(local_catalog):
    result = resolved()
    assert local_catalog.scenario_for(result) is not None
    result.event_id = "same-vin-different-sale"
    assert local_catalog.scenario_for(result) is None
    result = resolved()
    result.vehicle.trim = "Plausible but different revision"
    assert local_catalog.scenario_for(result) is None


def test_manifest_rights_revocation_is_observed_after_a_successful_catalog_read(local_catalog):
    local_catalog.validated_bytes(FRONT, now=NOW)
    manifest_path = local_catalog.root / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    next(item for item in manifest["assets"] if item["asset_id"] == FRONT)["revoked"] = True
    manifest_path.write_text(json.dumps(manifest))
    with pytest.raises(AssetUnavailable, match="revoked"):
        local_catalog.validated_bytes(FRONT, now=NOW)


@pytest.mark.parametrize("change", ["source-observation", "reference-origin", "field-origin"])
def test_genuine_source_and_corroboration_revisions_change_snapshot_precondition(change):
    result = resolved()
    initial = stable_snapshot_fingerprint(result)
    if change == "source-observation":
        result.provenance.source_observed_at += timedelta(hours=1)
    elif change == "reference-origin":
        result.reference_evidence.origin.reference = "fixture://independent/revised-reference"
    else:
        result.field_evidence["trim"].note = "A revised source evidence note"
    assert stable_snapshot_fingerprint(result) != initial
