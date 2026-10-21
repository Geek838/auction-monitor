from datetime import datetime, timedelta, timezone

import pytest

from app.domain.models import AuctionHouse, ListingIdentity, Provenance, Vehicle, VehicleSnapshot
from app.resolution.freshness import assess_freshness

NOW = datetime(2026, 10, 21, 12, tzinfo=timezone.utc)


def snapshot(source_time=None, *, retrieved_at=NOW, status="ACTIVE", realtime=False):
    return VehicleSnapshot(record_id="synthetic-source-record", event_id="synthetic-sale-event",
        identity=ListingIdentity(house=AuctionHouse.COPART, lot_or_stock_number="00012345"),
        vehicle=Vehicle(), event_status=status,
        provenance=Provenance(provider="TEST", source_name="Synthetic source",
            source_url="test-only://snapshot", retrieved_at=retrieved_at,
            source_observed_at=source_time, data_type="LICENSED", realtime=realtime,
            license_scope="Synthetic test of licensed-data semantics; no actual licensed data"))


@pytest.mark.parametrize("source_time", [None, NOW + timedelta(seconds=1)])
def test_missing_or_future_observation_is_unknown_even_with_recent_retrieval(source_time):
    result = assess_freshness(snapshot(source_time), now=NOW, threshold_seconds=60, basis="Synthetic policy")
    assert result.status == "UNKNOWN"


@pytest.mark.parametrize("kwargs", [{}, {"threshold_seconds": 60}, {"basis": "Synthetic policy"}])
def test_licensing_realtime_claim_or_current_retrieval_cannot_supply_missing_freshness_policy(kwargs):
    result = assess_freshness(snapshot(NOW, realtime=True), now=NOW, **kwargs)
    assert result.status == "UNKNOWN"


@pytest.mark.parametrize("age,expected", [(0, "FRESH"), (60, "FRESH"), (61, "STALE")])
def test_source_age_uses_explicit_threshold_and_deterministic_clock(age, expected):
    observed = NOW - timedelta(seconds=age)
    result = assess_freshness(snapshot(observed), now=NOW, threshold_seconds=60, basis="Synthetic test boundary")
    assert result.status == expected
    assert result.source_observed_at == observed
    assert result.evaluated_at == NOW
    assert result.threshold_seconds == 60 and result.basis == "Synthetic test boundary"


def test_recent_retrieval_does_not_refresh_an_old_source_snapshot():
    result = assess_freshness(snapshot(NOW - timedelta(days=10), retrieved_at=NOW), now=NOW,
                              threshold_seconds=3600, basis="Synthetic policy")
    assert result.status == "STALE"


@pytest.mark.parametrize("source_time", [None, NOW, NOW - timedelta(days=500)])
@pytest.mark.parametrize("event_status", ["ARCHIVED", "SOLD"])
def test_completed_event_is_historical_even_when_retrieved_or_observed_now(source_time, event_status):
    result = assess_freshness(snapshot(source_time, status=event_status), now=NOW,
                              threshold_seconds=60, basis="Synthetic policy")
    assert result.status == "HISTORICAL"
