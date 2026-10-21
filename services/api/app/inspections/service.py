"""Server-owned identity, permission and asset checks around the mock preview."""
from datetime import datetime
from urllib.parse import urlencode
from uuid import uuid4

from app.domain.models import PreviewEligibility, ResolutionResult
from app.inspections.binding import content_projection, digest, stable_snapshot_fingerprint
from app.inspections.catalog import AssetCatalog, AssetUnavailable, Scenario
from app.inspections.engine import InspectionEngine, SAFETY_CHECKS
from app.inspections.models import (
    Exclusion, InspectionPreview, InspectionProvenance, InspectionTarget, PhotoAsset, PreviewRequest,
)
from app.providers.base import AuctionSource, NotAuthorized
from app.providers.policy import Purpose, utc_now
from app.resolution.parser import parse_auction_url
from app.resolution.resolver import resolve_auction

LIMITATIONS = [
    "MOCK INSPECTION PREVIEW — hand-authored example, no AI analysis.",
    "Images are project-authored illustrations, not photographs of the submitted auction vehicle.",
    "Exterior illustrations do not establish hidden condition, functional operation or roadworthiness.",
    "No underneath, interior, diagnostic or physical-inspection evidence is supplied.",
    "Report generation time is not image capture time or evidence of current vehicle condition.",
]


def check_image_use(provider: AuctionSource) -> None:
    context = getattr(provider, "context", None)
    authorize = getattr(provider, "authorize", None)
    policy = getattr(provider, "policy", None)
    if not callable(context) or not callable(authorize) or policy is None:
        raise NotAuthorized("No reviewed local image-preview policy is configured.")
    selected = context()
    if selected.mode not in {"FIXTURE", "SIMULATED"} or selected.id not in {"fixture", "simulation"}:
        raise NotAuthorized("Only explicitly registered authored preview modes are supported.")
    if "mock_inspection_preview" not in policy.capabilities:
        raise NotAuthorized("Authored inspection previews are not permitted.")
    for purpose in (Purpose.METADATA_LOOKUP, Purpose.METADATA_DISPLAY, Purpose.IMAGE_RETRIEVAL, Purpose.IMAGE_DISPLAY):
        authorize(purpose)


def eligible_assets(scenario: Scenario, catalog: AssetCatalog, now: datetime):
    valid: list[tuple] = []
    excluded: list[Exclusion] = []
    for asset_id in scenario.asset_ids:
        if asset_id in scenario.excluded_ids:
            excluded.append(Exclusion(asset_id=asset_id, reason="This authored scenario does not permit this view; partial-evidence demonstration."))
            continue
        try:
            valid.append(catalog.validated_bytes(asset_id, now=now))
        except AssetUnavailable as exc:
            excluded.append(Exclusion(asset_id=asset_id, reason=str(exc)))
    return valid, excluded


def preview_eligibility(result: ResolutionResult, provider: AuctionSource, catalog: AssetCatalog) -> PreviewEligibility:
    if result.status != "MATCHED":
        return PreviewEligibility(reason="Resolve one corroborated listing before requesting an inspection preview.")
    try:
        check_image_use(provider)
        scenario = catalog.scenario_for(result)
        if scenario is None:
            return PreviewEligibility(reason="No eligible authored preview images are registered for this exact snapshot.")
        valid, _ = eligible_assets(scenario, catalog, utc_now())
        if not valid:
            return PreviewEligibility(reason="No currently permitted, intact authored preview images are available.")
        return PreviewEligibility(available=True, reason="An explicitly MOCK inspection preview is available for this authored example.", scenario_id=scenario.scenario_id)
    except Exception:
        # Asset/policy failure must never make metadata resolution unusable.
        return PreviewEligibility(reason="Authored preview images or their current permissions are unavailable.")


def attach_preview_context(result: ResolutionResult, provider: AuctionSource, catalog: AssetCatalog) -> ResolutionResult:
    result.snapshot_fingerprint = stable_snapshot_fingerprint(result)
    result.preview_eligibility = preview_eligibility(result, provider, catalog)
    return result


def target_for(result: ResolutionResult) -> InspectionTarget:
    return InspectionTarget(reference=result.reference, provider_context=result.provider_context,
        identity=result.identity, record_id=result.record_id, event_id=result.event_id,
        event_status=result.event_status, event_date=result.event_date,
        snapshot_fingerprint=stable_snapshot_fingerprint(result), vin=result.vehicle.vin,
        content_fingerprint=digest(content_projection(result)),
        source_observed_at=result.provenance.source_observed_at,
        retrieved_at=result.provenance.retrieved_at, freshness=result.freshness)


def public_asset(record, target: InspectionTarget) -> PhotoAsset:
    query = urlencode({"url": target.reference.url, "expected_snapshot_fingerprint": target.snapshot_fingerprint})
    return PhotoAsset(asset_id=record.asset_id, title=record.title or record.view_label,
        alt_text=record.alt_text, view_label=record.view_label,
        content_sha256=record.sha256, width=record.width, height=record.height,
        source_kind=record.source_kind, author=record.author, rights_reference=record.rights_reference,
        asset_url=f"/api/v1/inspection-assets/{record.asset_id}?{query}")


async def create_preview(request: PreviewRequest, provider: AuctionSource, catalog: AssetCatalog,
                         engine: InspectionEngine) -> InspectionPreview:
    result = await resolve_auction(parse_auction_url(request.url), provider)
    base = dict(request_id=str(uuid4()), resolver_status=result.status.value)
    if result.status != "MATCHED":
        return InspectionPreview(**base, outcome="BLOCKED", reason_code="IDENTITY_NOT_MATCHED", reasons=result.reasons or ["A corroborated listing is required."])
    fingerprint = stable_snapshot_fingerprint(result)
    if fingerprint != request.expected_snapshot_fingerprint:
        return InspectionPreview(**base, outcome="BLOCKED", reason_code="TARGET_CHANGED",
            reasons=["The listing snapshot changed. Resolve it again before opening a preview."])
    target = target_for(result)
    try:
        check_image_use(provider)
    except NotAuthorized:
        return InspectionPreview(**base, target=target, outcome="BLOCKED", reason_code="NOT_AUTHORIZED", reasons=["Current image-display or authored-preview permission is unavailable."])
    try:
        scenario = catalog.scenario_for(result)
        if scenario is None:
            return InspectionPreview(**base, target=target, outcome="BLOCKED", reason_code="NO_IMAGES", reasons=["No authored image scenario belongs to this exact listing snapshot."])
        valid, excluded = eligible_assets(scenario, catalog, utc_now())
    except Exception:
        return InspectionPreview(**base, target=target, outcome="FAILED", reason_code="CATALOG_FAILURE", reasons=["The authored preview catalog could not be validated. No report was released."])
    if not valid:
        return InspectionPreview(**base, target=target, outcome="BLOCKED", reason_code="NO_IMAGES",
            reasons=["No intact, currently permitted authored images are available."], exclusions=excluded)
    assets = [public_asset(record, target) for record, _ in valid]
    try:
        findings = await engine.inspect(scenario, target, assets)
        if not isinstance(findings, list) or not 0 < len(findings) <= 30:
            raise ValueError("Invalid finding count.")
        # Revalidate serialized output; an adapter cannot bypass contracts via model_construct.
        from app.inspections.models import InspectionFinding
        findings = [InspectionFinding.model_validate(item.model_dump() if isinstance(item, InspectionFinding) else item) for item in findings]
        check_image_use(provider)
        current = await resolve_auction(parse_auction_url(request.url), provider)
        if current.status != "MATCHED" or stable_snapshot_fingerprint(current) != fingerprint:
            return InspectionPreview(request_id=base["request_id"], resolver_status=current.status.value,
                outcome="BLOCKED", reason_code="TARGET_CHANGED",
                reasons=["The listing changed while the preview was being prepared. Resolve it again; no report was released."])
        check_image_use(provider)
        for asset in assets:
            record, _ = catalog.validated_bytes(asset.asset_id, now=utc_now())
            if record.sha256 != asset.content_sha256 or asset.asset_id in scenario.excluded_ids:
                raise AssetUnavailable("Image changed during preview generation.")
        provenance = InspectionProvenance(scenario_id=scenario.scenario_id, generated_at=utc_now(),
            target_digest=fingerprint, image_digests={a.asset_id: a.content_sha256 for a in assets})
        return InspectionPreview(**base, target=target, outcome="PARTIAL" if excluded else "COMPLETED",
            reason_code="PARTIAL_EVIDENCE" if excluded else "MOCK_COMPLETE", assets=assets,
            findings=findings, checks=list(SAFETY_CHECKS.values()), limitations=LIMITATIONS,
            exclusions=excluded, provenance=provenance)
    except NotAuthorized:
        return InspectionPreview(**base, target=target, outcome="BLOCKED", reason_code="NOT_AUTHORIZED", reasons=["Image or preview permission changed. No report was released."])
    except AssetUnavailable:
        return InspectionPreview(**base, target=target, outcome="BLOCKED", reason_code="ASSET_UNAVAILABLE", reasons=["The authored image set is no longer eligible. No report was released."])
    except Exception:
        return InspectionPreview(**base, target=target, outcome="FAILED", reason_code="ENGINE_FAILURE", reasons=["The mock preview could not be validated. No findings were released; retry or resolve again."])


async def asset_bytes(asset_id: str, request: PreviewRequest, provider: AuctionSource, catalog: AssetCatalog) -> tuple[bytes, str]:
    result = await resolve_auction(parse_auction_url(request.url), provider)
    if result.status != "MATCHED":
        raise NotAuthorized("A corroborated listing is required for this image.")
    if stable_snapshot_fingerprint(result) != request.expected_snapshot_fingerprint:
        raise AssetUnavailable("TARGET_CHANGED")
    check_image_use(provider)
    scenario = catalog.scenario_for(result)
    if scenario is None or asset_id not in scenario.asset_ids or asset_id in scenario.excluded_ids:
        raise AssetUnavailable("Unknown or unpermitted authored image for this target.")
    record, payload = catalog.validated_bytes(asset_id, now=utc_now())
    check_image_use(provider)
    return payload, record.mime_type
