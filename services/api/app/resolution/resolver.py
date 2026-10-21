"""Conservative identity validation. VIN and credentials never replace evidence."""
import logging
from datetime import datetime

from app.domain.models import (
    AuctionHouse, AuctionReference, EvidenceOrigin, ListingIdentity, ResolutionResult, ResolutionStatus,
)
from app.providers.base import AuctionSource, NotAuthorized, SourceUnavailable
from app.providers.fixture import MOCK_WARNING
from app.providers.policy import provider_context, utc_now
from app.resolution.freshness import assess_freshness

logger = logging.getLogger(__name__)


def independent_origin(origin: EvidenceOrigin, candidates, now: datetime) -> bool:
    candidate_refs = {c.provenance.source_url for c in candidates} | {c.record_id for c in candidates}
    return (origin.kind in {"SUPPLIED", "OBSERVED"} and origin.observed_at <= now
            and "candidate" not in origin.channel.casefold() and origin.reference not in candidate_refs)


async def resolve_auction(reference: AuctionReference, provider: AuctionSource, *, now: datetime | None = None) -> ResolutionResult:
    now = now or utc_now()
    result = ResolutionResult(
        status=ResolutionStatus.NOT_FOUND, reference=reference, provider_context=provider_context(provider),
        warnings=list(getattr(provider, "warnings", [])),
    )
    try:
        lookup = await provider.resolve(reference)
        # A malformed result is a source failure, never absence of a listing.
        from app.domain.models import ProviderResolution
        if not isinstance(lookup, ProviderResolution):
            raise SourceUnavailable("Invalid provider result.")
    except NotAuthorized:
        result.status = ResolutionStatus.NOT_AUTHORIZED
        result.provider_context.authorization = "DENIED"
        result.provider_context.available = False
        result.reasons = ["Provider access is not authorized for this operation. No permitted lookup was completed."]
        return result
    except Exception:
        # Never log provider exception text: it may contain URLs, credentials or response bodies.
        logger.warning("auction_resolution provider_unavailable house=%s", reference.house.value)
        result.status = ResolutionStatus.SOURCE_UNAVAILABLE
        result.provider_context.available = False
        result.reasons = ["The data provider could not complete this lookup. This does not mean the listing is missing."]
        return result
    if lookup.identity is None and reference.house == AuctionHouse.COPART and reference.lot_number:
        lookup.identity = ListingIdentity(house=reference.house, lot_or_stock_number=reference.lot_number)
    result.identity = lookup.identity
    result.candidates = lookup.candidates
    result.mapping_evidence = lookup.mapping_evidence
    result.reference_evidence = lookup.reference_evidence
    if MOCK_WARNING not in result.warnings and any(c.provenance.data_type == "MOCK" for c in lookup.candidates):
        result.warnings.append(MOCK_WARNING)
    if lookup.identity is None:
        result.status = ResolutionStatus.UNRESOLVED_ID
        result.reasons = ["The internal page ID could not be mapped to a verified auction stock number."]
        return result
    identity = lookup.identity
    if reference.page_id:
        mapping = lookup.mapping_evidence
        if (mapping is None or mapping.page_id != reference.page_id or mapping.country != reference.country or mapping.identity != identity
                or mapping.identity.house != AuctionHouse.IAAI
                or not independent_origin(mapping.origin, lookup.candidates, now)):
            result.status = ResolutionStatus.UNRESOLVED_ID
            result.identity = None
            result.reasons = ["Independent page-to-stock mapping evidence is missing, conflicting or unusable. The page ID is not a stock number."]
            return result
    conflicts: list[str] = []
    if identity.house != reference.house:
        conflicts.append("Resolved auction house conflicts with the submitted reference.")
    if reference.house == AuctionHouse.COPART and identity.lot_or_stock_number != reference.lot_number:
        conflicts.append("Resolved lot number conflicts with the submitted lot number.")
    if reference.stock_number and identity.lot_or_stock_number != reference.stock_number:
        conflicts.append("Resolved stock number conflicts with the submitted stock number.")
    reference_evidence = lookup.reference_evidence
    corroborated = reference_evidence is not None and independent_origin(reference_evidence.origin, lookup.candidates, now)
    if reference_evidence and not corroborated:
        conflicts.append("Reference metadata is not independently evidenced; candidate-derived or invalid corroboration cannot prove identity.")
    expected = reference_evidence.vehicle if reference_evidence else lookup.expected_vehicle
    for candidate in lookup.candidates:
        if candidate.identity != identity:
            conflicts.append("Candidate auction house or exact lot/stock identity does not match.")
        if expected:
            for field in ("vin", "year", "make", "model"):
                expected_value = getattr(expected, field)
                actual = getattr(candidate.vehicle, field)
                if expected_value is not None and actual is not None and str(expected_value).casefold() != str(actual).casefold():
                    conflicts.append(f"Candidate {field.upper()} conflicts with reference metadata.")
    if len(lookup.candidates) > 1:
        conflicts.append("Multiple source records or auction events remain; an exact event cannot be selected safely.")
    if conflicts:
        result.status = ResolutionStatus.AMBIGUOUS
        result.reasons = list(dict.fromkeys(conflicts))
        return result
    if not lookup.candidates:
        result.reasons = ["No provider record matches this exact auction identity."]
        return result
    candidate = lookup.candidates[0]
    result.status = ResolutionStatus.MATCHED
    result.vehicle = candidate.vehicle
    result.provenance = candidate.provenance
    result.field_evidence = candidate.field_evidence
    result.record_id = candidate.record_id
    result.event_id = candidate.event_id
    result.event_status = candidate.event_status
    result.event_date = candidate.event_date
    policy = getattr(provider, "policy", None)
    result.freshness = assess_freshness(candidate, now=now,
        threshold_seconds=getattr(policy, "freshness_threshold_seconds", None),
        basis=getattr(policy, "freshness_basis", None))
    result.evidence = ["Auction house matches exactly.", "Lot/stock identifier matches exactly, preserving all characters."]
    if reference.page_id:
        result.evidence.append("Independent page mapping corroborates the IAAI stock number; page ID is kept separate.")
    if corroborated:
        for field in ("vin", "year", "make", "model"):
            if getattr(expected, field) is not None and getattr(candidate.vehicle, field) is not None:
                result.evidence.append(f"{field.upper()} agrees with independently sourced reference metadata.")
    else:
        result.warnings.append("Independent vehicle reference metadata is unavailable; no VIN/model corroboration is asserted.")
    if candidate.vehicle.vin is None:
        result.warnings.append("VIN is unavailable; vehicle identity could not be cross-checked by VIN.")
    if candidate.event_status in {"ARCHIVED", "SOLD"}:
        result.warnings.append("Historical sold/archived event — this record is not a live auction feed.")
    if result.freshness.status == "STALE":
        result.warnings.append("Source observation is stale under the configured age policy, regardless of retrieval time.")
    if result.freshness.status == "UNKNOWN":
        result.warnings.append("Source freshness is unknown; retrieval time alone does not prove current data.")
    if not candidate.provenance.realtime:
        result.warnings.append("Provider snapshot is not real-time. No current bid or availability is asserted.")
    return result
