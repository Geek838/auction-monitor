import asyncio
from datetime import datetime, timezone

import pytest

from app.domain.models import (
    AuctionHouse, ListingIdentity, ProviderResolution, Provenance, Vehicle, VehicleSnapshot,
)
from app.providers.base import NotAuthorized, SourceUnavailable
from app.resolution.parser import parse_auction_url
from app.resolution.resolver import resolve_auction

REFERENCE = parse_auction_url("https://copart.com/lot/51374586")
IDENTITY = ListingIdentity(house=AuctionHouse.COPART, lot_or_stock_number="51374586")


def snapshot(**updates):
    data = dict(
        record_id="event-one", identity=IDENTITY,
        vehicle=Vehicle(vin="SYNTHETIC-VIN-A", year=2021, make="Toyota", model="Camry"),
        provenance=Provenance(provider="FIXTURE", source_name="Synthetic fixture", source_url=REFERENCE.url,
                              retrieved_at=datetime(2026, 10, 19, tzinfo=timezone.utc),
                              license_scope="Synthetic test data only", data_type="MOCK"),
        event_date="2026-10-18",
    )
    data.update(updates)
    return VehicleSnapshot(**data)


class Provider:
    def __init__(self, result):
        self.result = result

    async def resolve(self, reference):
        if isinstance(self.result, Exception):
            raise self.result
        return self.result


def resolve(*candidates, expected=None, identity=IDENTITY):
    return asyncio.run(resolve_auction(REFERENCE, Provider(ProviderResolution(
        identity=identity, candidates=list(candidates), expected_vehicle=expected,
    ))))


def test_exact_identity_and_independent_vehicle_metadata_match():
    item = snapshot()
    result = resolve(item, expected=item.vehicle)
    assert result.status == "MATCHED"
    assert result.identity == IDENTITY
    assert result.vehicle == item.vehicle
    assert result.provenance.data_type == "MOCK"
    assert result.evidence


@pytest.mark.parametrize("field,value", [("vin", "SYNTHETIC-VIN-B"), ("year", 2022), ("make", "Honda"), ("model", "Accord")])
def test_independently_known_vehicle_conflicts_block_exact_match(field, value):
    item = snapshot()
    expected = item.vehicle.model_copy(update={field: value})
    result = resolve(item, expected=expected)
    assert result.status == "AMBIGUOUS"
    assert result.vehicle is None
    assert result.candidates and result.reasons


@pytest.mark.parametrize("identity", [
    ListingIdentity(house=AuctionHouse.IAAI, lot_or_stock_number="51374586"),
    ListingIdentity(house=AuctionHouse.COPART, lot_or_stock_number="051374586"),
])
def test_similar_identifier_or_vin_never_overrides_wrong_auction_identity(identity):
    result = resolve(snapshot(identity=identity))
    assert result.status == "AMBIGUOUS"
    assert result.vehicle is None


def test_same_vin_in_two_events_is_not_silently_collapsed():
    first = snapshot()
    second = snapshot(record_id="event-two", event_date="2026-09-01", event_status="ARCHIVED")
    result = resolve(first, second)
    assert result.status == "AMBIGUOUS"
    assert {item.record_id for item in result.candidates} == {"event-one", "event-two"}


def test_unknown_vin_and_partial_vehicle_data_remain_unknown():
    result = resolve(snapshot(vehicle=Vehicle(make="Toyota")))
    assert result.status == "MATCHED"
    assert result.vehicle.vin is None
    assert result.vehicle.year is None


def test_no_candidate_means_not_found():
    assert resolve().status == "NOT_FOUND"


@pytest.mark.parametrize("error,status", [(SourceUnavailable("offline"), "SOURCE_UNAVAILABLE"),
                                          (NotAuthorized("no license"), "NOT_AUTHORIZED")])
def test_provider_failure_is_not_misreported_as_absent_listing(error, status):
    result = asyncio.run(resolve_auction(REFERENCE, Provider(error)))
    assert result.status == status
    assert result.vehicle is None


def test_known_copart_lot_does_not_become_unresolved_when_provider_has_no_identity():
    result = asyncio.run(resolve_auction(REFERENCE, Provider(ProviderResolution())))
    assert result.status == "NOT_FOUND"
    assert result.identity == IDENTITY
    assert result.vehicle is None


def test_candidate_commercial_provider_stays_disabled_without_outbound_calls(monkeypatch):
    import socket
    from app.providers.bidcars import BidCarsProvider

    def forbidden(*args, **kwargs):
        pytest.fail("Disabled provider attempted outbound network access")

    monkeypatch.setattr(socket, "getaddrinfo", forbidden)
    monkeypatch.setattr(socket.socket, "connect", forbidden)
    provider = BidCarsProvider()
    result = asyncio.run(resolve_auction(REFERENCE, provider))
    assert result.status == "NOT_AUTHORIZED"
    assert result.vehicle is None
    with pytest.raises(NotAuthorized):
        asyncio.run(provider.get_vehicle("51374586"))
