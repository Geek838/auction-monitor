"""Deliberately disabled: no commercial access or rights are assumed."""
from app.domain.models import AuctionReference, ProviderResolution, VehicleSnapshot
from app.providers.base import NotAuthorized


class BidCarsProvider:
    async def resolve(self, reference: AuctionReference) -> ProviderResolution:
        raise NotAuthorized("Bid.Cars integration is disabled pending written licensing and authorized API access.")

    async def get_vehicle(self, listing_id: str) -> VehicleSnapshot:
        raise NotAuthorized("Bid.Cars integration is disabled pending written licensing and authorized API access.")
