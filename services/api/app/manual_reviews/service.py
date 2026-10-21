"""Compile a user-reported document without external lookup, photo upload or AI."""
from datetime import datetime, timezone

from app.domain.models import AuctionHouse
from app.manual_reviews.models import (
    CanonicalClaim, DeclaredPhoto, ManualReviewReport, ManualReviewRequest, PhysicalCheck, ReportedFinding,
)
from app.resolution.parser import InvalidAuctionURL, parse_auction_url


PHYSICAL_CHECKS = (
    ("Structural integrity", "Ask a qualified collision specialist to inspect structural alignment and hidden load paths."),
    ("SRS and airbags", "Ask a qualified technician to inspect SRS components and diagnostic records."),
    ("ADAS", "Ask a qualified specialist to verify sensor condition, alignment and any required calibration."),
    ("Cooling", "Have the cooling system and concealed associated components physically inspected and tested."),
    ("Suspension", "Have suspension, steering and alignment inspected by a qualified technician."),
    ("Mechanical condition", "Arrange a qualified mechanical inspection and appropriate diagnostics."),
)


def compile_manual_review(request: ManualReviewRequest) -> ManualReviewReport:
    reference = parse_auction_url(request.url)
    if reference.house == AuctionHouse.COPART:
        if request.stock_number is not None and request.stock_number != reference.lot_number:
            raise InvalidAuctionURL("The manually supplied lot number conflicts with the Copart URL.")
        number = reference.lot_number
    else:
        # This is a user claim, not corroboration that the page maps to this stock.
        # Keep reference.stock_number null and the original page/country separate.
        number = request.stock_number
    return ManualReviewReport(
        reference=reference,
        canonical_claim=CanonicalClaim(house=reference.house, lot_or_stock_number=number),
        vehicle=request.vehicle,
        photos=[DeclaredPhoto(**photo.model_dump()) for photo in request.photos],
        findings=[ReportedFinding(**finding.model_dump()) for finding in request.findings],
        notes=request.notes,
        checks=[PhysicalCheck(system=system, recommendation=recommendation) for system, recommendation in PHYSICAL_CHECKS],
        warnings=[
            "User-supplied information is unverified. No provider lookup or independent auction/VIN match was performed.",
            "The URL was parsed locally; the auction page was not fetched. IAAI page IDs and claimed stock numbers remain distinct.",
            "Photo IDs, dimensions and hashes are client-supplied claims. This endpoint receives metadata only and does not receive or verify image bytes.",
            "Findings are user-reported text, not AI output or a professional assessment. No image analysis or model call occurred.",
            "Structural integrity, SRS/airbags, ADAS, cooling, suspension and mechanical function remain unknown. User reports do not establish safety or hidden condition.",
            "No repair costs, vehicle valuation or maximum bid were calculated. This report is not retained by the application server.",
        ],
        generated_at=datetime.now(timezone.utc),
    )
