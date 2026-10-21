"""HTTP boundary; explicit closed provider selection defaults to offline fixtures."""
import logging
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query, Response

from app.domain.models import ResolveRequest, ResolutionResult
from app.providers.base import AuctionSource
from app.providers.policy import provider_context
from app.providers.registry import get_selected_provider
from app.resolution.parser import InvalidAuctionURL, parse_auction_url
from app.resolution.resolver import resolve_auction
from app.inspections.catalog import AssetCatalog, AssetUnavailable
from app.inspections.engine import InspectionEngine, MockInspectionEngine
from app.inspections.models import InspectionPreview, PreviewRequest
from app.inspections.service import asset_bytes, attach_preview_context, create_preview
from app.inspections.body_limit import PreviewBodyLimit
from app.providers.base import NotAuthorized
from app.manual_reviews.models import ManualReviewReport, ManualReviewRequest
from app.manual_reviews.service import compile_manual_review

logger = logging.getLogger(__name__)
app = FastAPI(title="Auction Intelligence — identity and user-supplied reviews", version="0.4.0")
app.add_middleware(PreviewBodyLimit)
# Fail startup on unsupported configuration; never silently switch into mock mode.
get_selected_provider()


def get_provider() -> AuctionSource:
    return get_selected_provider()


def get_catalog() -> AssetCatalog:
    # A new request reads current manifest permissions; per-use hash checks also
    # invalidate approvals on in-flight changes and reused catalog test contexts.
    return AssetCatalog()


def get_inspection_engine(catalog: Annotated[AssetCatalog, Depends(get_catalog)]) -> InspectionEngine:
    return MockInspectionEngine(catalog)


@app.get("/api/v1/health")
async def health(provider: Annotated[AuctionSource, Depends(get_provider)]) -> dict:
    context = provider_context(provider)
    data_type = {"FIXTURE": "MOCK", "SIMULATED": "SIMULATED"}.get(context.mode, "UNAVAILABLE")
    return {"status": "ok", "provider": context.id.upper(), "data_type": data_type,
            "provider_context": context.model_dump(mode="json")}


@app.post("/api/v1/manual-reviews", response_model=ManualReviewReport)
async def manual_review(request: ManualReviewRequest, response: Response) -> ManualReviewReport:
    response.headers["Cache-Control"] = "no-store, max-age=0"
    response.headers["X-Content-Type-Options"] = "nosniff"
    try:
        return compile_manual_review(request)
    except InvalidAuctionURL as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.post("/api/v1/auction/resolve", response_model=ResolutionResult)
async def resolve(request: ResolveRequest, provider: Annotated[AuctionSource, Depends(get_provider)],
                  catalog: Annotated[AssetCatalog, Depends(get_catalog)]) -> ResolutionResult:
    try:
        reference = parse_auction_url(request.url)
    except InvalidAuctionURL as exc:
        logger.info("auction_resolution rejected_invalid_url")
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    result = await resolve_auction(reference, provider)
    logger.info("auction_resolution status=%s house=%s", result.status.value, reference.house.value)
    return attach_preview_context(result, provider, catalog)


@app.post("/api/v1/inspections", response_model=InspectionPreview)
async def inspect(request: PreviewRequest, provider: Annotated[AuctionSource, Depends(get_provider)],
                  catalog: Annotated[AssetCatalog, Depends(get_catalog)],
                  engine: Annotated[InspectionEngine, Depends(get_inspection_engine)], response: Response) -> InspectionPreview:
    response.headers["Cache-Control"] = "no-store, max-age=0"
    response.headers["X-Content-Type-Options"] = "nosniff"
    try:
        return await create_preview(request, provider, catalog, engine)
    except InvalidAuctionURL as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.get("/api/v1/inspection-assets/{asset_id}")
async def inspection_asset(asset_id: str, provider: Annotated[AuctionSource, Depends(get_provider)],
                           catalog: Annotated[AssetCatalog, Depends(get_catalog)],
                           url: Annotated[str, Query(min_length=1, max_length=2048)],
                           expected_snapshot_fingerprint: Annotated[str, Query(pattern=r"^[a-f0-9]{64}$")]) -> Response:
    try:
        payload, mime_type = await asset_bytes(asset_id, PreviewRequest(url=url,
            expected_snapshot_fingerprint=expected_snapshot_fingerprint), provider, catalog)
    except InvalidAuctionURL as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except NotAuthorized as exc:
        raise HTTPException(status_code=403, detail="Current image access is not authorized.") from exc
    except AssetUnavailable as exc:
        if str(exc) == "TARGET_CHANGED":
            raise HTTPException(status_code=409, detail="Listing target changed; resolve again.") from exc
        raise HTTPException(status_code=404, detail="No eligible authored image is available for this target.") from exc
    except Exception as exc:
        raise HTTPException(status_code=503, detail="The authored image could not be validated.") from exc
    return Response(content=payload, media_type=mime_type, headers={
        "Cache-Control": "no-store, max-age=0", "X-Content-Type-Options": "nosniff",
        "Content-Security-Policy": "default-src 'none'", "Cross-Origin-Resource-Policy": "same-origin",
    })
