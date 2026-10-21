"""Deterministic authored examples only; no image recognition or model calls."""
from typing import Protocol

from app.domain.models import ResolutionResult, ResolutionStatus
from app.inspections.binding import content_projection, digest
from app.inspections.catalog import AssetCatalog, AssetUnavailable, Scenario
from app.inspections.models import InspectionFinding, InspectionTarget, PhotoAsset
from app.providers.fixture import FixtureProvider
from app.providers.policy import utc_now
from app.providers.simulation import SimulationProvider

SAFETY_CHECKS = {
    "Structural integrity": "Have a qualified collision specialist inspect structural alignment and hidden load paths.",
    "SRS and airbags": "Have a qualified technician inspect SRS components and diagnostic records; an illustration cannot establish operation.",
    "ADAS": "Ask a qualified specialist to verify sensor condition, alignment and any required calibration.",
    "Cooling": "Have the cooling system and associated concealed components physically inspected and tested.",
    "Suspension": "Have suspension, steering and alignment physically inspected by a qualified technician.",
    "Mechanical condition": "Arrange a qualified mechanical inspection and appropriate diagnostics before a purchase decision.",
}


class InspectionEngine(Protocol):
    async def inspect(self, scenario: Scenario, target: InspectionTarget, assets: list[PhotoAsset]) -> list[InspectionFinding]: ...


class MockInspectionEngine:
    def __init__(self, catalog: AssetCatalog):
        self.catalog = catalog

    async def inspect(self, scenario: Scenario, target: InspectionTarget, assets: list[PhotoAsset]) -> list[InspectionFinding]:
        registered = self.catalog.scenarios.get(target.record_id)
        if registered != scenario or target.provider_context.id not in {"fixture", "simulation"}:
            raise AssetUnavailable("Unknown target or authored inspection scenario.")
        trusted = FixtureProvider() if target.provider_context.id == "fixture" else SimulationProvider()
        snapshot = trusted.records.get(target.record_id)
        if snapshot is None:
            raise AssetUnavailable("Unknown authored listing snapshot.")
        expected = ResolutionResult(status=ResolutionStatus.MATCHED, reference=target.reference,
            provider_context=target.provider_context, identity=snapshot.identity, vehicle=snapshot.vehicle,
            record_id=snapshot.record_id, event_id=snapshot.event_id, event_status=snapshot.event_status,
            event_date=snapshot.event_date, provenance=snapshot.provenance)
        if (digest(content_projection(expected)) != target.content_fingerprint
                or target.identity != snapshot.identity or target.event_id != snapshot.event_id
                or target.vin != snapshot.vehicle.vin):
            raise AssetUnavailable("Target does not match the authored image scenario.")
        if not assets or len(assets) > 6 or len({a.asset_id for a in assets}) != len(assets):
            raise AssetUnavailable("No usable authored image set.")
        for asset in assets:
            if asset.asset_id not in scenario.asset_ids or asset.asset_id in scenario.excluded_ids:
                raise AssetUnavailable("Image does not belong to this authored scenario.")
            record, _ = self.catalog.validated_bytes(asset.asset_id, now=utc_now())
            if asset.content_sha256 != record.sha256:
                raise AssetUnavailable("Image content is not the registered authored example.")
        if scenario.fail_engine:
            raise RuntimeError("Authored failure scenario")
        findings: list[InspectionFinding] = []
        asset_ids = {asset.asset_id for asset in assets}
        if not scenario.no_visible_marks:
            if "front-illustration-v1" in asset_ids:
                findings.append(InspectionFinding(finding_id="drawn-front-mark", classification="OBSERVED",
                    region="Front bumper area", component="Illustrated bumper surface",
                    description="The authored front-view illustration contains a highlighted irregular mark on the drawn bumper.",
                    rationale="This is a manually annotated feature of the project illustration, not an observation of a real auction vehicle.",
                    image_ids=["front-illustration-v1"],
                    confirmation="For an actual vehicle, have a qualified body specialist inspect the corresponding surface and nearby attachments."))
                findings.append(InspectionFinding(finding_id="attachment-check", classification="SUSPECTED",
                    region="Front bumper area", component="Nearby attachments",
                    description="A comparable mark on a real vehicle could warrant checking nearby bumper attachments; their condition is not established here.",
                    rationale="The drawn bumper mark is an example trigger for an inspection question, not evidence that concealed attachments are damaged.",
                    image_ids=["front-illustration-v1"],
                    confirmation="Have a qualified specialist physically inspect the attachments before drawing a repair conclusion."))
            if "side-illustration-v1" in asset_ids:
                findings.append(InspectionFinding(finding_id="drawn-side-mark", classification="OBSERVED",
                    region="Side panel area", component="Illustrated side panel",
                    description="The authored side-view illustration contains short contrasting strokes across the drawn panel.",
                    rationale="The visible strokes are deliberately drawn fixture features; depth, material damage and real vehicle condition are not measured.",
                    image_ids=["side-illustration-v1"],
                    confirmation="For a real vehicle, ask a qualified body specialist to inspect surface condition and panel alignment."))
        for index, (system, recommendation) in enumerate(SAFETY_CHECKS.items()):
            findings.append(InspectionFinding(finding_id=f"unknown-system-{index}", classification="UNKNOWN",
                region="Not assessable from authored exterior illustrations", component=system,
                description=f"{system} cannot be established from this synthetic exterior image set.",
                rationale="No physical examination, functional testing or relevant diagnostic evidence has been supplied.",
                confirmation=recommendation))
        return findings
