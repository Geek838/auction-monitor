# Sprint 1 requirements and acceptance

Source: supplied *Auction Intelligence — Product & Engineering Handover*, v1.0, 19 October 2026, especially §§4–7 and 9–13. The user's request limits implementation to Sprint 1. This document translates that scope into reviewable acceptance criteria; it does not establish commercial access or additional commitments.

## Product goal

A buyer pastes a Copart or IAAI URL and learns whether the configured fixture provider can corroborate the exact auction listing. The interface explains the evidence, uncertainty, provenance, and historical status. A matching model name or VIN alone never proves listing identity.

## Requirements traceability

| ID | Handover | Requirement and acceptance |
|---|---|---|
| S1-01 | §§6, 11 | A new engineer can run the Next.js/TypeScript frontend and FastAPI/Pydantic backend using documented commands. Dependencies are reproducible and pytest plus Playwright checks are documented. |
| S1-02 | §§4–5, 10 | Parse user input locally, without requesting its URL. Accept only documented exact Copart/IAAI hosts and recognized listing paths. Reject malformed URLs, credentials, unsupported schemes/hosts, host suffix tricks, redirect wrappers, and localhost/private-network targets. Preserve identifiers as strings, including leading zeros. |
| S1-03 | §§4–5, 7 | Represent the auction house, URL page reference, and canonical lot/stock identity separately. An IAAI VehicleDetail page ID is not a stock number. Without a corroborated mapping, return `UNRESOLVED_ID`. |
| S1-04 | §§4, 6–7 | Define a typed `AuctionSource` boundary and fixture implementation. A Bid.Cars adapter remains disabled pending permission. No scraper, arbitrary fetch, or implied commercial API access is introduced. |
| S1-05 | §§5, 10 | Return `MATCHED` only for corroborated auction house and exact lot/stock identity. Cross-check supplied VIN and vehicle attributes when available. Conflicting evidence or competing exact candidates yields `AMBIGUOUS`, with reasons; never select a similar-looking vehicle. |
| S1-06 | §§5, 7, 10 | Preserve separate auction events even when VINs repeat. VIN may be null; unavailable metadata must not be fabricated. A canonical listing identity is not a lifetime vehicle identity. |
| S1-07 | §§4, 7, 9 | Implement `POST /api/v1/auction/resolve` and `GET /api/v1/health`. Expose `MATCHED`, `AMBIGUOUS`, `NOT_FOUND`, `UNRESOLVED_ID`, `SOURCE_UNAVAILABLE`, and `NOT_AUTHORIZED` as distinct outcomes. Provider failures must not become false not-found results. Invalid input gets a clear client error. |
| S1-08 | §§7, 9 | Render one URL input and clear loading/result/error states. Matched results show source, canonical lot/stock, available vehicle details, match evidence, provider, retrieval timestamp, source reference, and an unmistakable MOCK warning. Historical records are visibly archived and never called a current bid. |
| S1-09 | §§1, 4, 7 | Every fixture response carries mock provenance and a non-live designation. Record source name/URL, retrieval time, license scope, and field evidence classification (supplied, observed, inferred, or missing). Show photos only with demonstrated rights; omission is valid. |
| S1-10 | §§10–11 | Unit/API tests exercise parser safety, identity and failure outcomes. Browser tests cover a successful fixture resolution and a failure, including visible mock labeling. Missing photos and partial metadata render gracefully. Basic diagnostic logging avoids unnecessary user-input disclosure. |

## Fixture scenario matrix

These are synthetic scenarios, not claims about live auction inventory. Implemented fixture URLs and identifiers are listed in the project README or fixture source. Tests should assert the evidence rules as well as status codes.

| Scenario | Expected behavior |
|---|---|
| Copart numeric lot | `MATCHED` for the same house and exact lot; explicit MOCK label. |
| Tracking parameters, trailing slash, permitted mobile hostname | Normalize recognized forms without network access; do not change identity. |
| Leading-zero lot or stock | Preserve original identifier text through parsing and matching. |
| IAAI page with proven mapping | Preserve internal page ID separately; match only the mapped stock with supporting evidence. |
| IAAI page without mapping, including alphanumeric reference | `UNRESOLVED_ID`; no guessed stock number. |
| Matching auction identity and available VIN | `MATCHED` when all supplied cross-checks agree. |
| Matching lot but conflicting VIN or vehicle evidence | `AMBIGUOUS`, with a conflict reason. |
| More than one competing exact record | `AMBIGUOUS`; no silent first-result selection. |
| Same VIN in two distinct sale events | Keep events distinct; one event cannot satisfy the other's lot/stock identity. |
| Provider has no record | `NOT_FOUND`, without invented vehicle details. |
| Provider connection/service failure | `SOURCE_UNAVAILABLE`, distinct from absence of a listing. |
| Provider permission missing | `NOT_AUTHORIZED`, explaining that access is unavailable. |
| Archived record | Explicit historical status and retrieval timestamp, never a live-price claim. |
| Missing VIN, photos, or optional attributes | Null/absent values render honestly and gracefully. |
| Unsupported/malformed/malicious URL | Reject before provider lookup; no outgoing fetch. |
| HTML-encoded query separators or extra parameters | Handle only documented URL syntax; never interpret query text as instructions or follow redirects. |

## Scope boundaries and decisions

Sprint 1 contains no LLM calls, image analysis, repair or landed-cost estimates, maximum-bid recommendations, accounts, payments, live bidding, scraping, or purchased VIN history. The 50-link feasibility study requires authorized data and is not a claim that the fixture resolver has production coverage. Georgia pricing research and user interviews belong to later work.

The following remain open: contracted data provider and its access terms; photo display, AI-processing, cache and retention rights; production identity mapping for IAAI; freshness guarantees; brand/domain; Georgian localization timing; vision model; pricing partners; resale-data sources; and monetization. Do not make these prerequisites for a runnable fixture prototype.

Storage may remain in memory for this deterministic fixture milestone. Document that snapshots and provenance need a persistence/migration decision before production integration. A narrow, documented parser allowlist is preferable to pretending to support every regional or legacy URL format; unsupported formats must fail clearly.

## Definition of done

The documented local commands start both applications. A fixture link for each auction house displays corroborated identity and mock provenance. Invalid, unresolved, ambiguous, absent, unavailable, and unauthorized cases are distinguishable. Unit, API, and required browser checks pass, and the product makes no live-data or licensed-access claim.
