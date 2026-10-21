"""Hand-authored fictional records; no data or photos fetched from auction sites."""
from datetime import datetime, timezone

from app.domain.models import (
    AuctionHouse, AuctionReference, FieldEvidence, ListingIdentity,
    Provenance, ProviderResolution, Vehicle, VehicleSnapshot,
    EvidenceOrigin, MappingEvidence, ReferenceEvidence,
)
from app.providers.base import NotAuthorized, SourceUnavailable

MOCK_WARNING = "Illustrative MOCK fixture — not live auction data. Vehicle details and VINs are synthetic."
FIXTURE_TIME = datetime(2026, 10, 19, 12, 0, tzinfo=timezone.utc)


def snapshot(record_id: str, house: AuctionHouse, number: str, *,
             archived: bool = False, partial: bool = False) -> VehicleSnapshot:
    vehicle = Vehicle(
        vin=None if partial else "FIXTUREVIN0000001", year=None if partial else 2021,
        make="Toyota", model="Camry", trim=None if partial else "SE",
        primary_damage=None if partial else "Front End",
    )
    return VehicleSnapshot(
        record_id=record_id, event_id=f"event-{record_id}",
        identity=ListingIdentity(house=house, lot_or_stock_number=number),
        vehicle=vehicle,
        provenance=Provenance(
            provider="FIXTURE", source_name="Local synthetic fixture dataset",
            source_url=f"fixture://auction-intelligence/{record_id}",
            retrieved_at=FIXTURE_TIME, source_observed_at=datetime(2026, 10, 1, 12, tzinfo=timezone.utc), license_scope="Synthetic local demonstration and testing only; no auction data or photo rights implied.",
            data_type="MOCK", realtime=False,
        ),
        event_status="ARCHIVED" if archived else "FIXTURE",
        event_date="2025-06-12" if archived else "2026-10-01",
        field_evidence={field: FieldEvidence(
            kind="MISSING" if value is None else "SUPPLIED", source=record_id,
            note="Not available in fixture." if value is None else "Hand-authored synthetic fixture value.",
        ) for field, value in vehicle.model_dump().items()},
    )


class FixtureProvider:
    """Exact local lookups. Page mapping is explicit, never inferred from digits."""
    warnings = [MOCK_WARNING]

    def __init__(self) -> None:
        copart = AuctionHouse.COPART
        iaai = AuctionHouse.IAAI
        records = [
            snapshot("copart-demo", copart, "51374586"),
            snapshot("copart-leading-zero", copart, "00012345", partial=True),
            snapshot("copart-event-a", copart, "70000001"),
            snapshot("copart-event-b", copart, "70000001", archived=True),
            snapshot("copart-archive", copart, "70000002", archived=True),
            snapshot("iaai-demo", iaai, "45371195"),
            snapshot("copart-conflict-a", copart, "70000005"),
            snapshot("copart-conflict-b", copart, "70000005"),
            snapshot("copart-single-conflict", copart, "70000006"),
        ]
        records[-2].vehicle.vin = "FIXTUREVIN0000002"
        records[-1].vehicle.vin = "FIXTUREVIN0000002"
        self.records = {record.record_id: record for record in records}
        # Separate, explicitly authored reference-channel metadata. Never derive
        # corroborating expectations from a candidate being validated.
        self.reference_metadata = {
            (copart, number): Vehicle(vin="FIXTUREVIN0000001", year=2021, make="Toyota", model="Camry")
            for number in ("51374586", "70000001", "70000002", "70000005", "70000006")
        }
        self.reference_metadata[(copart, "00012345")] = Vehicle(make="Toyota", model="Camry")
        self.reference_metadata[(iaai, "45371195")] = Vehicle(
            vin="FIXTUREVIN0000001", year=2021, make="Toyota", model="Camry",
        )
        self.page_identities = {
            "41000001": ListingIdentity(house=iaai, lot_or_stock_number="45371195"),
            "AB-41000001": ListingIdentity(house=iaai, lot_or_stock_number="45371195"),
        }

    async def resolve(self, reference: AuctionReference) -> ProviderResolution:
        if reference.house == AuctionHouse.COPART:
            number = reference.lot_number
            if number == "70000003":
                raise SourceUnavailable("The fixture simulates a provider connection failure.")
            if number == "70000004":
                raise NotAuthorized("The fixture simulates missing provider permission.")
            identity = ListingIdentity(house=reference.house, lot_or_stock_number=number) if number else None
        else:
            identity = self.page_identities.get(reference.page_id or "") if reference.country in {None, "US"} else None
        if identity is None:
            return ProviderResolution()
        candidates = [r.model_copy(deep=True) for r in self.records.values() if r.identity == identity]
        reference_metadata = self.reference_metadata.get((identity.house, identity.lot_or_stock_number))
        expected = reference_metadata.model_copy(deep=True) if reference_metadata else None
        origin = EvidenceOrigin(
            source="Synthetic independent reference channel", reference=f"fixture://reference/{identity.house}/{identity.lot_or_stock_number}",
            channel="reference-metadata", observed_at=FIXTURE_TIME,
        )
        mapping = MappingEvidence(page_id=reference.page_id, country=reference.country, identity=identity, origin=EvidenceOrigin(
            source="Synthetic page mapping register", reference=f"fixture://page-mapping/{reference.page_id}",
            channel="page-mapping", observed_at=FIXTURE_TIME,
        )) if reference.page_id else None
        for candidate in candidates:
            for field, value in {"identity.house": candidate.identity.house, "identity.lot_or_stock_number": candidate.identity.lot_or_stock_number,
                                 "event_id": candidate.event_id, "event_date": candidate.event_date, "event_status": candidate.event_status}.items():
                candidate.field_evidence[field] = FieldEvidence(kind="MISSING" if value is None else "SUPPLIED", source=candidate.record_id,
                                                               note="Hand-authored synthetic listing/event value.")
        return ProviderResolution(identity=identity, expected_vehicle=expected,
                                  reference_evidence=ReferenceEvidence(vehicle=expected, origin=origin) if expected else None,
                                  mapping_evidence=mapping, candidates=candidates)

    async def get_vehicle(self, listing_id: str) -> VehicleSnapshot:
        return self.records[listing_id].model_copy(deep=True)
