"""Conservative identity matching. VIN never replaces an auction identity."""
import logging

from app.domain.models import AuctionHouse, AuctionReference, ListingIdentity, ResolutionResult, ResolutionStatus
from app.providers.base import AuctionSource, NotAuthorized, SourceUnavailable
from app.providers.fixture import MOCK_WARNING

logger = logging.getLogger(__name__)


async def resolve_auction(reference: AuctionReference, provider: AuctionSource) -> ResolutionResult:
    result = ResolutionResult(
        status=ResolutionStatus.NOT_FOUND, reference=reference,
        warnings=list(getattr(provider, "warnings", [])),
    )
    try:
        lookup = await provider.resolve(reference)
    except NotAuthorized:
        result.status = ResolutionStatus.NOT_AUTHORIZED
        result.reasons = ["Provider access is not authorized. No live lookup was performed."]
        return result
    except (SourceUnavailable, ConnectionError, TimeoutError):
        logger.warning("auction_resolution provider_unavailable house=%s", reference.house.value)
        result.status = ResolutionStatus.SOURCE_UNAVAILABLE
        result.reasons = ["The data provider is unavailable. Retry later; this does not mean the listing is missing."]
        return result
    if lookup.identity is None and reference.house == AuctionHouse.COPART and reference.lot_number:
        # Copart URLs already provide a canonical lot; an empty provider result
        # is not an unresolved IAAI internal page mapping.
        lookup.identity = ListingIdentity(house=reference.house, lot_or_stock_number=reference.lot_number)
    result.identity = lookup.identity
    result.candidates = lookup.candidates
    if MOCK_WARNING not in result.warnings and any(c.provenance.data_type == "MOCK" for c in lookup.candidates):
        result.warnings.append(MOCK_WARNING)
    if lookup.identity is None:
        result.status = ResolutionStatus.UNRESOLVED_ID
        result.reasons = ["The internal page ID could not be mapped to a verified auction stock number."]
        return result
    identity = lookup.identity
    conflicts: list[str] = []
    if identity.house != reference.house:
        conflicts.append("Resolved auction house conflicts with the submitted reference.")
    if reference.house == AuctionHouse.COPART and identity.lot_or_stock_number != reference.lot_number:
        conflicts.append("Resolved lot number conflicts with the submitted lot number.")
    if reference.stock_number and identity.lot_or_stock_number != reference.stock_number:
        conflicts.append("Resolved stock number conflicts with the submitted stock number.")
    for candidate in lookup.candidates:
        if candidate.identity != identity:
            conflicts.append("Candidate auction house or exact lot/stock identity does not match.")
        if lookup.expected_vehicle:
            for field in ("vin", "year", "make", "model"):
                expected = getattr(lookup.expected_vehicle, field)
                actual = getattr(candidate.vehicle, field)
                if expected is not None and actual is not None and str(expected).casefold() != str(actual).casefold():
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
    result.event_status = candidate.event_status
    result.event_date = candidate.event_date
    result.evidence = ["Auction house matches exactly.", "Lot/stock identifier matches exactly, preserving all characters."]
    if reference.page_id:
        result.evidence.append("Provider's explicit page mapping corroborates the IAAI stock number; page ID is kept separate.")
    if lookup.expected_vehicle:
        for field in ("vin", "year", "make", "model"):
            if getattr(lookup.expected_vehicle, field) is not None and getattr(candidate.vehicle, field) is not None:
                result.evidence.append(f"{field.upper()} agrees with provider reference metadata.")
    if candidate.vehicle.vin is None:
        result.warnings.append("VIN is unavailable; vehicle identity could not be cross-checked by VIN.")
    if candidate.event_status == "ARCHIVED":
        result.warnings.append("Historical archived event — this record is not a live auction feed.")
    if not candidate.provenance.realtime:
        result.warnings.append("Provider snapshot is not real-time. No current bid or availability is asserted.")
    return result
