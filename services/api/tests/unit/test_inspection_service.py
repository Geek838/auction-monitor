import asyncio
from datetime import datetime, timezone
import hashlib
from io import BytesIO
import json
import shutil

from PIL import Image
import pytest

from app.inspections.binding import stable_snapshot_fingerprint
from app.inspections.catalog import ASSET_ROOT, AssetCatalog, AssetUnavailable
from app.inspections.engine import MockInspectionEngine
from app.inspections.models import InspectionFinding, PreviewRequest
from app.inspections.service import asset_bytes, attach_preview_context, create_preview, public_asset, target_for
from app.providers.base import NotAuthorized
from app.providers.policy import Purpose
from app.providers.registry import build_provider
from app.resolution.parser import parse_auction_url
from app.resolution.resolver import resolve_auction

URL = "https://copart.com/lot/51374586"
FRONT = "front-illustration-v1"


@pytest.fixture
def catalog(tmp_path):
    for source in ASSET_ROOT.iterdir():
        if source.suffix in {".json", ".png"}:
            shutil.copy2(source, tmp_path / source.name)
    return AssetCatalog(tmp_path)


def setup_preview(catalog):
    provider = build_provider("fixture")
    # Explicit local permissions, independent from inference/training rights.
    provider.policy.capabilities.add("mock_inspection_preview")
    provider.policy.permissions[Purpose.IMAGE_RETRIEVAL] = True
    provider.policy.permissions[Purpose.IMAGE_DISPLAY] = True
    result = asyncio.run(resolve_auction(parse_auction_url(URL), provider))
    request = PreviewRequest(url=URL, expected_snapshot_fingerprint=stable_snapshot_fingerprint(result))
    return provider, result, request


@pytest.mark.parametrize("purpose", [Purpose.IMAGE_DISPLAY, Purpose.IMAGE_RETRIEVAL])
def test_metadata_matching_survives_image_permission_denial_but_preview_and_asset_delivery_do_not(catalog, purpose):
    provider, result, request = setup_preview(catalog)
    provider.policy.permissions[purpose] = False
    still_matched = asyncio.run(resolve_auction(parse_auction_url(URL), provider))
    assert still_matched.status == "MATCHED"
    assert attach_preview_context(still_matched, provider, catalog).preview_eligibility.available is False
    report = asyncio.run(create_preview(request, provider, catalog, MockInspectionEngine(catalog)))
    assert report.outcome == "BLOCKED" and report.reason_code == "NOT_AUTHORIZED"
    assert not report.assets and not report.findings
    with pytest.raises(NotAuthorized):
        asyncio.run(asset_bytes(FRONT, request, provider, catalog))


@pytest.mark.parametrize("change", ["provider-right", "asset-revoked", "asset-bytes"])
def test_permission_or_image_changes_during_inspection_prevent_releasing_a_report(catalog, change):
    provider, _, request = setup_preview(catalog)

    class ChangingEngine(MockInspectionEngine):
        async def inspect(self, scenario, target, assets):
            findings = await super().inspect(scenario, target, assets)
            if change == "provider-right":
                provider.policy.permissions[Purpose.IMAGE_DISPLAY] = False
            elif change == "asset-revoked":
                catalog.records[FRONT].revoked = True
            else:
                path = catalog.root / catalog.records[FRONT].filename
                path.write_bytes(path.read_bytes() + b"mutated while processing")
            return findings

    report = asyncio.run(create_preview(request, provider, catalog, ChangingEngine(catalog)))
    assert report.outcome == "BLOCKED"
    assert not report.assets and not report.findings and report.provenance is None


@pytest.mark.parametrize("change", ["dangling-image", "safety-assertion", "too-many", "raw-secret-error"])
def test_untrusted_engine_output_is_validated_before_becoming_a_report(catalog, change):
    provider, _, request = setup_preview(catalog)

    class InvalidEngine(MockInspectionEngine):
        async def inspect(self, scenario, target, assets):
            if change == "raw-secret-error":
                raise RuntimeError("synthetic-private-error-marker")
            findings = await super().inspect(scenario, target, assets)
            if change == "dangling-image":
                findings[0] = findings[0].model_copy(update={"image_ids": ["image-from-another-event"]})
            elif change == "safety-assertion":
                findings[0] = InspectionFinding.model_construct(**{
                    **findings[0].model_dump(), "description": "This vehicle is safe to drive."})
            else:
                findings *= 10
            return findings

    report = asyncio.run(create_preview(request, provider, catalog, InvalidEngine(catalog)))
    assert report.outcome == "FAILED"
    assert not report.assets and not report.findings and report.provenance is None
    assert "synthetic-private-error-marker" not in report.model_dump_json()


def test_arbitrary_rehashed_valid_image_does_not_inherit_a_seeded_finding(catalog):
    provider, _, request = setup_preview(catalog)
    record = catalog.records[FRONT]
    path = catalog.root / record.filename
    replacement = BytesIO()
    Image.new("RGB", (record.width, record.height), "white").save(replacement, format="PNG")
    payload = replacement.getvalue()
    path.write_bytes(payload)
    record.sha256 = hashlib.sha256(payload).hexdigest()
    # A manifest checksum proves integrity relative to the manifest, not eligibility
    # for semantic annotations authored for different bytes.
    report = asyncio.run(create_preview(request, provider, catalog, MockInspectionEngine(catalog)))
    assert report.outcome in {"BLOCKED", "PARTIAL", "FAILED"}
    assert all(FRONT not in finding.image_ids for finding in report.findings)


def test_mock_engine_itself_rejects_an_unknown_scenario_and_unknown_asset_bytes(catalog):
    provider, result, _ = setup_preview(catalog)
    target = target_for(result)
    scenario = catalog.scenario_for(result)
    record, _ = catalog.validated_bytes(FRONT, now=datetime.now(timezone.utc))
    asset = public_asset(record, target)
    engine = MockInspectionEngine(catalog)
    altered = asset.model_copy(update={"content_sha256": "0" * 64})
    with pytest.raises(AssetUnavailable):
        asyncio.run(engine.inspect(scenario, target, [altered]))
    from dataclasses import replace
    with pytest.raises(AssetUnavailable):
        asyncio.run(engine.inspect(replace(scenario, scenario_id="invented-scenario"), target, [asset]))


def test_image_revocation_after_a_preview_cannot_be_bypassed_using_its_old_url(catalog):
    provider, _, request = setup_preview(catalog)
    report = asyncio.run(create_preview(request, provider, catalog, MockInspectionEngine(catalog)))
    assert report.outcome == "COMPLETED"
    catalog.records[FRONT].revoked = True
    with pytest.raises(AssetUnavailable):
        asyncio.run(asset_bytes(FRONT, request, provider, catalog))


def test_archived_scenario_cannot_directly_deliver_a_view_excluded_from_its_partial_report(catalog):
    provider, _, _ = setup_preview(catalog)
    url = "https://copart.com/lot/70000002"
    result = asyncio.run(resolve_auction(parse_auction_url(url), provider))
    request = PreviewRequest(url=url, expected_snapshot_fingerprint=stable_snapshot_fingerprint(result))
    report = asyncio.run(create_preview(request, provider, catalog, MockInspectionEngine(catalog)))
    assert report.outcome == "PARTIAL"
    assert any(exclusion.asset_id == "side-illustration-v1" for exclusion in report.exclusions)
    with pytest.raises(AssetUnavailable):
        asyncio.run(asset_bytes("side-illustration-v1", request, provider, catalog))


@pytest.mark.parametrize("field", ["event_id", "vehicle", "source-observation"])
def test_same_url_target_changes_while_engine_is_awaited_never_release_an_old_report(catalog, field):
    provider, _, request = setup_preview(catalog)

    class ChangingTargetEngine(MockInspectionEngine):
        async def inspect(self, scenario, target, assets):
            findings = await super().inspect(scenario, target, assets)
            record = provider.provider.records["copart-demo"]
            if field == "event_id":
                record.event_id = "another-sale-event"
            elif field == "vehicle":
                record.vehicle.trim = "A revised snapshot"
            else:
                from datetime import timedelta
                record.provenance.source_observed_at += timedelta(minutes=1)
            return findings

    report = asyncio.run(create_preview(request, provider, catalog, ChangingTargetEngine(catalog)))
    assert report.outcome == "BLOCKED" and report.reason_code == "TARGET_CHANGED"
    assert not report.assets and not report.findings and report.provenance is None
