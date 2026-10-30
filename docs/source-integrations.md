# Data access and the provider boundary

The default resolver and Sprint 3 authored inspection preview remain local and synthetic. No direct Copart, IAAI, or Bid.Cars requests are made. The disabled Bid.Cars adapter is a placeholder, not a client or a claim of access. The optional Apibara adapter uses that provider's documented endpoint for metadata only, and requires an enable flag and API key. It has not been exercised with an authenticated live response; fixture mode remains the default.

## Provider contract

The closed registry accepts `AUCTION_PROVIDER=fixture` (default), `simulation` (explicitly synthetic), `bidcars` (disabled), or `apibara` (opt-in external metadata). Selecting a name does not supply credentials. Unknown names fail at startup. The Apibara adapter additionally requires `APIBARA_ENABLE=1` and `APIBARA_API_KEY` in the API process.

`provider_context` accompanies health and domain-resolution outcomes, including failures and empty results. It distinguishes provider mode, authorization and availability. Record provenance distinguishes MOCK, SIMULATED and the reserved LICENSED type. The optional adapter has not yet been live-validated. Permission does not establish freshness: source observation time is distinct from retrieval time, archived events are historical, and absent age evidence/thresholds leave freshness unknown.

`GuardedProvider` checks a validated static policy before provider operations. Required purposes and capabilities are explicit; unknown uses are denied. Credential names are metadata, never values. IAAI mapping evidence must identify the exact submitted page/country and canonical stock, with source/channel/time evidence. Reference vehicle metadata has its own origin; deriving it from the candidate is not independent corroboration. Record and sale-event IDs are retained separately.

There is no persistent cache, database, retained external provider response, remote image fetch, or background task. The authored preview serves guarded local PNG illustrations with exact snapshot/hash/current-use checks; these are not auction photographs or AI output. A future storage implementation must respect both use rights and lifecycle limits; the current configuration fields are not a deletion service. See [provider contract and lifecycle decision](decisions/002-provider-contract.md) for policy semantics, compatibility and the boundary of implemented behavior.

## Adding an authorized provider later

1. Obtain written permission covering automated lookup, commercial metadata use, photograph display, AI processing if planned, caching, retention, and deletion. Confirm freshness guarantees and the meaning of each provider identifier.
2. Implement `AuctionSource` behind the existing domain types. Resolve listing references with the provider's documented authorized mechanism; an IAAI VehicleDetail page ID must be mapped explicitly to its actual stock number. A coincidentally equal string is not proof.
3. Return corroborated auction identity separately from the observed URL reference. Supply any independently known VIN/make/model/year for cross-checks. Preserve sale events and provider record IDs rather than collapsing by VIN.
4. Attach provider name, source URL, retrieval time, license scope, field evidence, event date/status, and non-live/historical flags. Never reuse fixture `MOCK` provenance for real records or imply a historical snapshot is live.
5. Translate permission failures into `NOT_AUTHORIZED` and connectivity/service failures into `SOURCE_UNAVAILABLE`. Neither means the vehicle is absent. Only an actual negative lookup supports `NOT_FOUND`.
6. Run the contract and regression tests, add provider-specific tests and authorized examples, and keep the fixture adapter available for offline development. Validate against the consented diverse-link feasibility set before making coverage claims.

The fixture adapter demonstrates mapping and conflict handling; it cannot establish what a remote service knows. No network egress, secrets, or API keys are required to run offline fixture mode. The opt-in Apibara adapter needs a server-side credential; never put it in source code. Its IAAI VehicleDetail page identifier is not treated as a stock number and unresolved page mappings are withheld.

## Deliberately absent

No scraper, headless browsing bypass, unlicensed photo storage, live auction feed, VIN-history purchase, or commercial provider request is implemented. The UI provides identity resolution and an explicitly MOCK authored inspection preview; it does not assess a real vehicle or make financial recommendations.

## Current provider research

The [22 October public-source review](research/provider-selection-2026-10-22.md) recommends a commercial inquiry to Qopart, with Bid.Cars in parallel. No ready licensed channel has been selected. The [inquiries](research/provider-findings-2026-10-22.md) are drafted but unsent. Auto.dev has documented APIs but does not establish our exact auction-reference mapping or buyer-facing use scope in the reviewed material. No external adapter can be enabled merely by changing a flag.

## Zero-paid-API user review

The separate [manual-review workflow](sprint-4-delivery.md) compiles user-supplied facts and findings without provider calls. Photos remain browser-local; `/api/v1/manual-reviews` receives bounded text and client-declared metadata only. This does not grant a provider license, verify a VIN/listing, enable a real adapter or attach user images to the authored MOCK engine. No paid API was activated.

## Free manufacturer metadata and local inference

The optional [NHTSA vPIC integration](free-vin-data.md) is a real free public metadata service, invoked only by an explicit VIN lookup. It has no original auction lot/page mapping and is not registered as an `AuctionSource`. The review remains unverified after manufacturer fields are applied.

The separate [local-model experiment](local-vision.md) sends permitted prepared image bytes to a fixed loopback Ollama endpoint, not a commercial auction source or hosted AI provider. Runtime/model provenance and user consent are independent of metadata/image rights on third-party websites. Existing browser-only manual photo handling is unchanged. Neither feature enables Bid.Cars or removes an authorization gate.
