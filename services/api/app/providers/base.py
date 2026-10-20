from typing import Protocol

from app.domain.models import AuctionReference, ProviderResolution, VehicleSnapshot


class SourceUnavailable(Exception):
    """Provider could not complete lookup; never equivalent to not found."""


class NotAuthorized(Exception):
    """No licensed access for this operation."""


class AuctionSource(Protocol):
    async def resolve(self, reference: AuctionReference) -> ProviderResolution: ...
    async def get_vehicle(self, listing_id: str) -> VehicleSnapshot: ...
