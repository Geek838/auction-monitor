"""Closed registry. Selecting an adapter does not create permission or API access."""
from functools import lru_cache
import os

from app.domain.models import AuctionHouse
from app.providers.bidcars import BidCarsProvider
from app.providers.fixture import FixtureProvider
from app.providers.policy import GuardedProvider, ProviderPolicy, Purpose
from app.providers.simulation import SimulationProvider
from app.providers.apibara import ApibaraProvider


def build_provider(name: str) -> GuardedProvider:
    if name == "fixture":
        return GuardedProvider(FixtureProvider(), ProviderPolicy(
            id="fixture", name="Local fixture dataset", mode="FIXTURE", enabled=True,
            houses=set(AuctionHouse), capabilities={"canonical_lookup", "page_mapping", "vehicle_lookup", "mock_inspection_preview"},
            permissions={Purpose.METADATA_LOOKUP: True, Purpose.METADATA_DISPLAY: True,
                         Purpose.IMAGE_RETRIEVAL: True, Purpose.IMAGE_DISPLAY: True},
        ))
    if name == "simulation":
        return GuardedProvider(SimulationProvider(), ProviderPolicy(
            id="simulation", name="Offline provider simulation", mode="SIMULATED", enabled=True,
            houses=set(AuctionHouse), capabilities={"canonical_lookup", "page_mapping", "vehicle_lookup", "mock_inspection_preview"},
            permissions={Purpose.METADATA_LOOKUP: True, Purpose.METADATA_DISPLAY: True,
                         Purpose.IMAGE_RETRIEVAL: True, Purpose.IMAGE_DISPLAY: True},
            freshness_threshold_seconds=86400,
            freshness_basis="Synthetic demonstration threshold (24 hours); not a provider freshness commitment.",
        ))
    if name == "bidcars":
        return GuardedProvider(BidCarsProvider(), ProviderPolicy(
            id="bidcars", name="Bid.Cars (not integrated)", mode="EXTERNAL", enabled=False,
        ))
    if name == "apibara":
        return GuardedProvider(ApibaraProvider(), ProviderPolicy(
            id="apibara", name="Apibara (third-party)", mode="EXTERNAL",
            enabled=os.environ.get("APIBARA_ENABLE") == "1", authorization_basis="USER_DECLARED",
            houses=set(AuctionHouse), capabilities={"canonical_lookup"},
            permissions={Purpose.METADATA_LOOKUP: True, Purpose.METADATA_DISPLAY: True},
            required_credentials=["APIBARA_API_KEY"],
        ))
    raise ValueError("Unsupported AUCTION_PROVIDER. Choose fixture, simulation, bidcars, or apibara.")


@lru_cache(maxsize=3)
def get_selected_provider() -> GuardedProvider:
    return build_provider(os.environ.get("AUCTION_PROVIDER", "fixture"))
