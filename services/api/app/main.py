"""HTTP boundary; provider injection is explicit and fixture-only by default."""
import logging
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException

from app.domain.models import ResolveRequest, ResolutionResult
from app.providers.base import AuctionSource
from app.providers.fixture import FixtureProvider
from app.resolution.parser import InvalidAuctionURL, parse_auction_url
from app.resolution.resolver import resolve_auction

logger = logging.getLogger(__name__)
app = FastAPI(title="Auction Intelligence — fixture resolver", version="0.1.0")
fixture_provider = FixtureProvider()


def get_provider() -> AuctionSource:
    return fixture_provider


@app.get("/api/v1/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "provider": "FIXTURE", "data_type": "MOCK"}


@app.post("/api/v1/auction/resolve", response_model=ResolutionResult)
async def resolve(request: ResolveRequest, provider: Annotated[AuctionSource, Depends(get_provider)]) -> ResolutionResult:
    try:
        reference = parse_auction_url(request.url)
    except InvalidAuctionURL as exc:
        # Avoid logging raw user input, URL tokens, query strings, or VINs.
        logger.info("auction_resolution rejected_invalid_url")
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    result = await resolve_auction(reference, provider)
    logger.info("auction_resolution status=%s house=%s", result.status.value, reference.house.value)
    return result
