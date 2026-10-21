"""HTTP boundary; explicit closed provider selection defaults to offline fixtures."""
import logging
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException

from app.domain.models import ResolveRequest, ResolutionResult
from app.providers.base import AuctionSource
from app.providers.policy import provider_context
from app.providers.registry import get_selected_provider
from app.resolution.parser import InvalidAuctionURL, parse_auction_url
from app.resolution.resolver import resolve_auction

logger = logging.getLogger(__name__)
app = FastAPI(title="Auction Intelligence — identity resolver", version="0.2.0")
# Fail startup on unsupported configuration; never silently switch into mock mode.
get_selected_provider()


def get_provider() -> AuctionSource:
    return get_selected_provider()


@app.get("/api/v1/health")
async def health(provider: Annotated[AuctionSource, Depends(get_provider)]) -> dict:
    context = provider_context(provider)
    data_type = {"FIXTURE": "MOCK", "SIMULATED": "SIMULATED"}.get(context.mode, "UNAVAILABLE")
    return {"status": "ok", "provider": context.id.upper(), "data_type": data_type,
            "provider_context": context.model_dump(mode="json")}


@app.post("/api/v1/auction/resolve", response_model=ResolutionResult)
async def resolve(request: ResolveRequest, provider: Annotated[AuctionSource, Depends(get_provider)]) -> ResolutionResult:
    try:
        reference = parse_auction_url(request.url)
    except InvalidAuctionURL as exc:
        logger.info("auction_resolution rejected_invalid_url")
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    result = await resolve_auction(reference, provider)
    logger.info("auction_resolution status=%s house=%s", result.status.value, reference.house.value)
    return result
