"""Explicit offline simulation for provider-aware contracts; no licensed data or API."""
from datetime import timedelta

from app.domain.models import AuctionReference, ProviderResolution, VehicleSnapshot
from app.providers.fixture import FixtureProvider
from app.providers.policy import utc_now


class SimulationProvider(FixtureProvider):
    warnings = ["SIMULATED provider: hand-authored offline examples, no licensed data or live access."]

    def __init__(self):
        super().__init__()
        now = utc_now()
        for record in self.records.values():
            record.provenance.provider = "SIMULATION"
            record.provenance.source_name = "Offline provider simulation"
            record.provenance.source_url = f"simulation://records/{record.record_id}"
            record.provenance.data_type = "SIMULATED"
            record.provenance.license_scope = "Synthetic simulation only; no third-party metadata or image license asserted."
            record.provenance.retrieved_at = now
            # Deliberately old observation with recent retrieval proves those concepts differ.
            record.provenance.source_observed_at = now - timedelta(days=7)
        self.records["copart-leading-zero"].provenance.source_observed_at = None

    async def resolve(self, reference: AuctionReference) -> ProviderResolution:
        return await super().resolve(reference)

    async def get_vehicle(self, listing_id: str) -> VehicleSnapshot:
        return await super().get_vehicle(listing_id)
