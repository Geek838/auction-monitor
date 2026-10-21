"""Adverse authorization checks use spies: denial must precede provider I/O."""
import asyncio
from datetime import datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from app.domain.models import AuctionHouse, ListingIdentity, ProviderResolution, Provenance, Vehicle, VehicleSnapshot
from app.providers.base import NotAuthorized, SourceUnavailable
from app.providers.policy import AuthorizationEvidence, GuardedProvider, ProviderPolicy, Purpose
from app.resolution.parser import parse_auction_url

NOW = datetime(2026, 10, 21, 12, tzinfo=timezone.utc)
REFERENCE = parse_auction_url("https://copart.com/lot/00012345")


def authorization(**updates):
    data = dict(reference="test-only://authorization", reviewer="Synthetic reviewer",
                reviewed_at=NOW - timedelta(days=2), effective_at=NOW - timedelta(days=1),
                expires_at=NOW + timedelta(days=1),
                purposes={Purpose.METADATA_LOOKUP, Purpose.METADATA_DISPLAY})
    data.update(updates)
    return AuthorizationEvidence(**data)


def policy(**updates):
    data = dict(id="test-external", name="Synthetic policy test", mode="EXTERNAL", enabled=True,
                houses={AuctionHouse.COPART, AuctionHouse.IAAI},
                capabilities={"canonical_lookup", "page_mapping", "vehicle_lookup"},
                permissions={Purpose.METADATA_LOOKUP: True, Purpose.METADATA_DISPLAY: True},
                authorization=authorization())
    data.update(updates)
    return ProviderPolicy(**data)


class SpyProvider:
    def __init__(self):
        self.calls = []

    async def resolve(self, reference):
        self.calls.append(("resolve", reference))
        return ProviderResolution()

    async def get_vehicle(self, listing_id):
        self.calls.append(("get_vehicle", listing_id))
        return VehicleSnapshot(record_id=listing_id,
            identity=ListingIdentity(house=AuctionHouse.COPART, lot_or_stock_number="00012345"),
            vehicle=Vehicle(), provenance=Provenance(provider="TEST", source_name="Synthetic test",
                source_url="test-only://snapshot", retrieved_at=NOW, license_scope="Synthetic testing only",
                data_type="LICENSED"))


def invoke(guard, operation):
    return asyncio.run(guard.resolve(REFERENCE) if operation == "resolve" else guard.get_vehicle("record-1"))


@pytest.mark.parametrize("operation", ["resolve", "get_vehicle"])
@pytest.mark.parametrize("failure", ["disabled", "missing-evidence", "revoked", "expired", "not-effective", "future-review", "missing-purpose", "missing-display", "missing-credential"])
def test_denied_operations_never_reach_provider(operation, failure):
    config = policy()
    if failure == "disabled":
        config.enabled = False
    elif failure == "missing-evidence":
        config.authorization = None
    elif failure == "revoked":
        config.authorization.revoked = True
    elif failure == "expired":
        config.authorization.expires_at = NOW
    elif failure == "not-effective":
        config.authorization.effective_at = NOW + timedelta(minutes=1)
    elif failure == "future-review":
        config.authorization.reviewed_at = NOW + timedelta(minutes=1)
    elif failure == "missing-purpose":
        config.authorization.purposes.remove(Purpose.METADATA_LOOKUP)
    elif failure == "missing-display":
        config.permissions.pop(Purpose.METADATA_DISPLAY)
    elif failure == "missing-credential":
        config.required_credentials = ["TEST_PROVIDER_KEY"]
    spy = SpyProvider()
    guard = GuardedProvider(spy, config, clock=lambda: NOW, credential_present=lambda _: False)
    with pytest.raises(NotAuthorized):
        invoke(guard, operation)
    assert spy.calls == []
    assert guard.context().authorization == "DENIED"
    assert guard.context().available is False


@pytest.mark.parametrize("operation", ["resolve", "get_vehicle"])
def test_metadata_only_access_works_without_image_ai_or_cache_rights(operation):
    spy = SpyProvider()
    guard = GuardedProvider(spy, policy(), clock=lambda: NOW)
    invoke(guard, operation)
    assert len(spy.calls) == 1
    assert guard.context().authorization == "APPROVED"
    for purpose in [Purpose.IMAGE_RETRIEVAL, Purpose.IMAGE_DISPLAY, Purpose.IMAGE_STORAGE,
                    Purpose.AI_INFERENCE, Purpose.MODEL_TRAINING, Purpose.METADATA_CACHE]:
        with pytest.raises(NotAuthorized):
            guard.authorize(purpose)


def test_credential_presence_is_checked_only_when_documented_as_required():
    spy = SpyProvider()
    guard = GuardedProvider(spy, policy(), clock=lambda: NOW,
                            credential_present=lambda _: pytest.fail("No credentials were required"))
    asyncio.run(guard.resolve(REFERENCE))
    assert len(spy.calls) == 1


def test_required_credential_allows_use_without_exposing_its_value():
    spy = SpyProvider()
    checked = []
    guard = GuardedProvider(spy, policy(required_credentials=["TEST_PROVIDER_KEY"]), clock=lambda: NOW,
                            credential_present=lambda name: checked.append(name) or True)
    asyncio.run(guard.resolve(REFERENCE))
    assert checked and set(checked) == {"TEST_PROVIDER_KEY"}
    assert len(spy.calls) == 1
    assert "TEST_PROVIDER_KEY" not in guard.context().model_dump_json()


def test_revocation_and_expiry_are_checked_again_on_later_operations():
    config = policy()
    spy = SpyProvider()
    current = [NOW]
    guard = GuardedProvider(spy, config, clock=lambda: current[0])
    asyncio.run(guard.resolve(REFERENCE))
    config.authorization.revoked = True
    with pytest.raises(NotAuthorized):
        asyncio.run(guard.get_vehicle("previous-record"))
    config.authorization.revoked = False
    current[0] = config.authorization.expires_at
    with pytest.raises(NotAuthorized):
        asyncio.run(guard.resolve(REFERENCE))
    assert len(spy.calls) == 1


@pytest.mark.parametrize("changes", [
    {"houses": {AuctionHouse.IAAI}}, {"capabilities": {"page_mapping"}},
])
def test_unsupported_house_or_lookup_capability_never_calls_provider(changes):
    spy = SpyProvider()
    guard = GuardedProvider(spy, policy(**changes), clock=lambda: NOW)
    with pytest.raises(SourceUnavailable):
        asyncio.run(guard.resolve(REFERENCE))
    assert spy.calls == []


def test_missing_page_mapping_capability_abstains_without_calling_provider():
    spy = SpyProvider()
    guard = GuardedProvider(spy, policy(capabilities={"canonical_lookup"}), clock=lambda: NOW)
    result = asyncio.run(guard.resolve(parse_auction_url("https://iaai.com/VehicleDetail/AB-41000001~US")))
    assert result.identity is None and result.candidates == []
    assert spy.calls == []


def test_missing_vehicle_lookup_capability_denies_before_provider_call():
    spy = SpyProvider()
    guard = GuardedProvider(spy, policy(capabilities={"canonical_lookup", "page_mapping"}), clock=lambda: NOW)
    with pytest.raises(SourceUnavailable):
        asyncio.run(guard.get_vehicle("record-one"))
    assert spy.calls == []


@pytest.mark.parametrize("operation", ["resolve", "get_vehicle"])
@pytest.mark.parametrize("change", ["revoked", "expired", "display-denied"])
def test_permission_changes_during_provider_operation_prevent_releasing_its_result(operation, change):
    config = policy()
    current = [NOW]

    class ChangingProvider(SpyProvider):
        def change_policy(self):
            if change == "revoked":
                config.authorization.revoked = True
            elif change == "expired":
                current[0] = config.authorization.expires_at
            else:
                config.permissions[Purpose.METADATA_DISPLAY] = False

        async def resolve(self, reference):
            result = await super().resolve(reference)
            self.change_policy()
            return result

        async def get_vehicle(self, listing_id):
            result = await super().get_vehicle(listing_id)
            self.change_policy()
            return result

    spy = ChangingProvider()
    guard = GuardedProvider(spy, config, clock=lambda: current[0])
    with pytest.raises(NotAuthorized):
        invoke(guard, operation)
    assert len(spy.calls) == 1


@pytest.mark.parametrize("updates", [
    {"mode": "LIVE"}, {"cache_ttl_seconds": 3600},
    {"permissions": {Purpose.METADATA_CACHE: True}},
    {"permissions": {Purpose.METADATA_CACHE: True}, "cache_ttl_seconds": 3600, "max_retention_seconds": 60},
    {"freshness_threshold_seconds": 60}, {"required_credentials": ["not a variable"]},
    {"unsupported_override": True},
])
def test_inconsistent_or_unknown_policy_configuration_is_rejected(updates):
    with pytest.raises(ValidationError):
        policy(**updates)


def test_cache_permission_needs_explicit_limits_and_current_purpose_authorization():
    config = policy(permissions={Purpose.METADATA_LOOKUP: True, Purpose.METADATA_DISPLAY: True,
                                Purpose.METADATA_CACHE: True}, cache_ttl_seconds=30, max_retention_seconds=60)
    guard = GuardedProvider(SpyProvider(), config, clock=lambda: NOW)
    with pytest.raises(NotAuthorized):
        guard.authorize(Purpose.METADATA_CACHE)
    config.authorization.purposes.add(Purpose.METADATA_CACHE)
    guard.authorize(Purpose.METADATA_CACHE)
    config.authorization.revoked = True
    with pytest.raises(NotAuthorized):
        guard.authorize(Purpose.METADATA_CACHE)


def test_image_inference_permission_does_not_implicitly_grant_model_training():
    config = policy(permissions={Purpose.METADATA_LOOKUP: True, Purpose.METADATA_DISPLAY: True,
                                Purpose.AI_INFERENCE: True})
    config.authorization.purposes.add(Purpose.AI_INFERENCE)
    guard = GuardedProvider(SpyProvider(), config, clock=lambda: NOW)
    guard.authorize(Purpose.AI_INFERENCE)
    with pytest.raises(NotAuthorized):
        guard.authorize(Purpose.MODEL_TRAINING)


@pytest.mark.parametrize("operation", ["resolve", "get_vehicle"])
def test_wrong_provider_return_schema_is_unavailable(operation):
    class InvalidProvider(SpyProvider):
        async def resolve(self, reference):
            return {"status": "found", "vehicle": "invented"}

        async def get_vehicle(self, listing_id):
            return {"vehicle": "invented"}

    guard = GuardedProvider(InvalidProvider(), policy(), clock=lambda: NOW)
    with pytest.raises(SourceUnavailable):
        invoke(guard, operation)


def test_naive_authorization_timestamps_are_rejected():
    with pytest.raises(ValidationError):
        authorization(reviewed_at=datetime(2026, 10, 20))


@pytest.mark.parametrize("operation", ["resolve", "get_vehicle"])
@pytest.mark.parametrize("mode,returned_type", [("EXTERNAL", "MOCK"), ("EXTERNAL", "SIMULATED"),
                                                ("FIXTURE", "LICENSED"), ("SIMULATED", "MOCK")])
def test_provider_mode_cannot_be_replaced_by_mislabeled_or_synthetic_fallback(operation, mode, returned_type):
    class WrongModeProvider(SpyProvider):
        async def get_vehicle(self, listing_id):
            item = await super().get_vehicle(listing_id)
            item.provenance.data_type = returned_type
            return item

        async def resolve(self, reference):
            item = await self.get_vehicle("record-one")
            return ProviderResolution(identity=item.identity, candidates=[item])

    guard = GuardedProvider(WrongModeProvider(), policy(mode=mode), clock=lambda: NOW)
    with pytest.raises(SourceUnavailable):
        invoke(guard, operation)
