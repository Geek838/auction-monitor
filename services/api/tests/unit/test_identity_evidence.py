import asyncio
from datetime import datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from app.domain.models import (
    AuctionHouse, EvidenceOrigin, ListingIdentity, MappingEvidence, ProviderResolution,
    Provenance, ReferenceEvidence, Vehicle, VehicleSnapshot,
)
from app.resolution.parser import parse_auction_url
from app.resolution.resolver import resolve_auction

NOW = datetime(2026, 10, 21, 12, tzinfo=timezone.utc)
IAAI = parse_auction_url("https://iaai.com/VehicleDetail/AB-41000001~US")
IDENTITY = ListingIdentity(house=AuctionHouse.IAAI, lot_or_stock_number="0045371195")


def origin(**updates):
    data = dict(source="Synthetic mapping register", reference="test-only://independent/lookup",
                channel="independent-reference", observed_at=NOW - timedelta(hours=1))
    data.update(updates)
    return EvidenceOrigin(**data)


def candidate():
    return VehicleSnapshot(record_id="source-record-one", event_id="sale-event-one", identity=IDENTITY,
        vehicle=Vehicle(vin="SYNTHETIC-VIN-A", make="Toyota", model="Camry", year=2021),
        provenance=Provenance(provider="SIMULATION", source_name="Synthetic provider record",
            source_url="test-only://candidate/source-record-one", retrieved_at=NOW,
            source_observed_at=NOW - timedelta(days=2), license_scope="Synthetic testing only",
            data_type="SIMULATED"), event_status="SOLD", event_date="2026-10-01")


class Provider:
    def __init__(self, lookup):
        self.lookup = lookup

    async def resolve(self, reference):
        return self.lookup


def lookup(**updates):
    item = candidate()
    data = dict(identity=IDENTITY, candidates=[item], mapping_evidence=MappingEvidence(
        page_id=IAAI.page_id, country="US", identity=IDENTITY, origin=origin()),
        reference_evidence=ReferenceEvidence(vehicle=item.vehicle.model_copy(deep=True),
            origin=origin(reference="test-only://independent/vehicle-reference")))
    data.update(updates)
    return ProviderResolution(**data)


def resolve(data, reference=IAAI):
    return asyncio.run(resolve_auction(reference, Provider(data), now=NOW))


def test_explicit_mapping_keeps_alphanumeric_page_and_zero_padded_stock_separate():
    result = resolve(lookup())
    assert result.status == "MATCHED"
    assert result.reference.page_id == "AB-41000001"
    assert result.reference.stock_number is None
    assert result.identity.lot_or_stock_number == "0045371195"
    assert result.mapping_evidence.page_id == result.reference.page_id
    assert result.record_id == "source-record-one" and result.event_id == "sale-event-one"
    assert result.event_status == "SOLD"
    assert any("VIN" in item and "independent" in item for item in result.evidence)


@pytest.mark.parametrize("case", ["absent", "different-page", "different-stock", "different-house", "inferred", "missing", "future", "same-candidate-reference", "candidate-channel"])
def test_unusable_page_mapping_cannot_produce_an_exact_match(case):
    data = lookup()
    if case == "absent":
        data.mapping_evidence = None
    elif case == "different-page":
        data.mapping_evidence.page_id = "41000001"
    elif case == "different-stock":
        data.mapping_evidence.identity = ListingIdentity(house=AuctionHouse.IAAI, lot_or_stock_number="45371195")
    elif case == "different-house":
        data.mapping_evidence.identity = ListingIdentity(house=AuctionHouse.COPART, lot_or_stock_number="0045371195")
    elif case in {"inferred", "missing"}:
        data.mapping_evidence.origin.kind = case.upper()
    elif case == "future":
        data.mapping_evidence.origin.observed_at = NOW + timedelta(seconds=1)
    elif case == "same-candidate-reference":
        data.mapping_evidence.origin.reference = data.candidates[0].provenance.source_url
    elif case == "candidate-channel":
        data.mapping_evidence.origin.channel = "candidate-metadata"
    result = resolve(data)
    assert result.status == "UNRESOLVED_ID"
    assert result.vehicle is None and result.identity is None
    assert result.reasons


@pytest.mark.parametrize("case", ["inferred", "missing", "future", "same-candidate-reference", "same-record-id", "candidate-channel"])
def test_candidate_derived_or_unusable_reference_metadata_is_not_corroboration(case):
    data = lookup()
    if case in {"inferred", "missing"}:
        data.reference_evidence.origin.kind = case.upper()
    elif case == "future":
        data.reference_evidence.origin.observed_at = NOW + timedelta(seconds=1)
    elif case == "same-candidate-reference":
        data.reference_evidence.origin.reference = data.candidates[0].provenance.source_url
    elif case == "same-record-id":
        data.reference_evidence.origin.reference = data.candidates[0].record_id
    elif case == "candidate-channel":
        data.reference_evidence.origin.channel = "candidate"
    result = resolve(data)
    assert result.status == "AMBIGUOUS"
    assert result.vehicle is None
    assert not any("VIN agrees" in item for item in result.evidence)


def test_matching_legacy_expected_vehicle_does_not_claim_independent_corroboration():
    data = lookup(reference_evidence=None)
    data.expected_vehicle = data.candidates[0].vehicle.model_copy(deep=True)
    result = resolve(data)
    assert result.status == "MATCHED"
    assert not any("VIN agrees" in item for item in result.evidence)
    assert any("unavailable" in warning and "reference" in warning for warning in result.warnings)


def test_country_reference_cannot_reuse_another_markets_page_mapping():
    result = resolve(lookup(), parse_auction_url("https://iaai.com/VehicleDetail/AB-41000001~CA"))
    assert result.status == "UNRESOLVED_ID"
    assert result.vehicle is None


@pytest.mark.parametrize("field", ["source", "reference", "channel"])
def test_whitespace_only_evidence_is_invalid(field):
    with pytest.raises(ValidationError):
        origin(**{field: " \t "})


def test_naive_mapping_observation_is_invalid():
    with pytest.raises(ValidationError):
        origin(observed_at=datetime(2026, 10, 20))
