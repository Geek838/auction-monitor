# Data access and the provider boundary

The resolver and Sprint 3 authored inspection preview remain local and synthetic. No Copart, IAAI, or Bid.Cars requests are made. The disabled Bid.Cars adapter is a placeholder, not a client or a claim of access. The supplied research links are background references and confer no reuse rights.

## Current offline contract

The closed registry accepts `AUCTION_PROVIDER=fixture` (default), `simulation` (explicitly synthetic), or `bidcars` (disabled). Selecting a name does not grant rights or supply credentials. Unknown names fail at startup. There is no external adapter that a feature flag can enable.

`provider_context` accompanies health and domain-resolution outcomes, including failures and empty results. It distinguishes provider mode, authorization and availability. Record provenance distinguishes MOCK, SIMULATED and the reserved LICENSED type. No existing runtime returns licensed vehicle data. Permission does not establish freshness: source observation time is distinct from retrieval time, archived events are historical, and absent age evidence/thresholds leave freshness unknown.

`GuardedProvider` checks a validated static policy before provider operations. Required purposes and capabilities are explicit; unknown uses are denied. Credential names are metadata, never values. IAAI mapping evidence must identify the exact submitted page/country and canonical stock, with source/channel/time evidence. Reference vehicle metadata has its own origin; deriving it from the candidate is not independent corroboration. Record and sale-event IDs are retained separately.

There is no persistent cache, database, retained external provider response, remote image fetch, or background task. The authored preview serves guarded local PNG illustrations with exact snapshot/hash/current-use checks; these are not auction photographs or AI output. A future storage implementation must respect both use rights and lifecycle limits; the current configuration fields are not a deletion service. See [provider contract and lifecycle decision](decisions/002-provider-contract.md) for policy semantics, compatibility and the boundary of implemented behavior.

## Adding an authorized provider later

1. Obtain written permission covering automated lookup, commercial metadata use, photograph display, AI processing if planned, caching, retention, and deletion. Confirm freshness guarantees and the meaning of each provider identifier.
2. Implement `AuctionSource` behind the existing domain types. Resolve listing references with the provider's documented authorized mechanism; an IAAI VehicleDetail page ID must be mapped explicitly to its actual stock number. A coincidentally equal string is not proof.
3. Return corroborated auction identity separately from the observed URL reference. Supply any independently known VIN/make/model/year for cross-checks. Preserve sale events and provider record IDs rather than collapsing by VIN.
4. Attach provider name, source URL, retrieval time, license scope, field evidence, event date/status, and non-live/historical flags. Never reuse fixture `MOCK` provenance for real records or imply a historical snapshot is live.
5. Translate permission failures into `NOT_AUTHORIZED` and connectivity/service failures into `SOURCE_UNAVAILABLE`. Neither means the vehicle is absent. Only an actual negative lookup supports `NOT_FOUND`.
6. Run the contract and regression tests, add provider-specific tests and authorized examples, and keep the fixture adapter available for offline development. Validate against the consented diverse-link feasibility set before making coverage claims.

The fixture adapter demonstrates mapping and conflict handling; it cannot establish what an unlicensed remote service knows. No network egress, secrets, or API keys are required to run the current offline application. Public-source research uses separately configured research domains; this does not enable any runtime provider. Credentials for a future authorized service must be supplied securely through deployment settings, never source code.

## Deliberately absent

No scraper, headless browsing bypass, unlicensed photo storage, live auction feed, VIN-history purchase, or commercial provider request is implemented. The UI provides identity resolution and an explicitly MOCK authored inspection preview; it does not assess a real vehicle or make financial recommendations.

## Current provider research

The [22 October public-source review](research/provider-selection-2026-10-22.md) recommends a commercial inquiry to Qopart, with Bid.Cars in parallel. No ready licensed channel has been selected. The [inquiries](research/provider-findings-2026-10-22.md) are drafted but unsent. Auto.dev has documented APIs but does not establish our exact auction-reference mapping or buyer-facing use scope in the reviewed material. No external adapter can be enabled merely by changing a flag.

## Zero-paid-API user review

The separate [manual-review workflow](sprint-4-delivery.md) compiles user-supplied facts and findings without provider calls. Photos remain browser-local; `/api/v1/manual-reviews` receives bounded text and client-declared metadata only. This does not grant a provider license, verify a VIN/listing, enable a real adapter or attach user images to the authored MOCK engine. No paid API was activated.
