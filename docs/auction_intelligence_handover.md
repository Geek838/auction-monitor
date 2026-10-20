# Auction Intelligence — Product & Engineering Handover

**Working title:** Auction Intelligence (temporary; branding undecided)  
**Version:** 1.0  
**Date:** 19 October 2026  
**Status:** Product direction agreed; implementation not started  
**Initial market:** Georgia (country); expansion possible to other vehicle-import markets  
**Primary use case:** Evaluate damaged vehicles listed on Copart and IAAI **before bidding**.

> **North star:** A buyer pastes a Copart or IAAI link and receives an evidence-backed assessment of visible damage, likely repairs, hidden risks, Georgia-specific landed and repair costs, and — once price data is validated — a reasonable maximum bid.

---

## 1. Executive summary

Build a web application that helps Georgian individual buyers and professional vehicle importers decide whether an auction vehicle is worth purchasing. The user provides a **Copart or IAAI URL**. The backend identifies the original auction and lot/stock reference, searches for the corresponding vehicle using **Bid.Cars as a candidate secondary source**, verifies the match, and processes *lawfully available* vehicle data and photographs. An AI vision system produces structured damage observations and inspection risks. Deterministic financial modules estimate parts, labor, import costs, contingencies, and eventually maximum acceptable bids.

**Essential user-flow decision:** Users do **not** paste Bid.Cars links or manually find Bid.Cars records. Bid.Cars is an internal data-source candidate. The system must not depend on it being the only provider.

**Competitive edge hypothesis:** Actual Georgian repair costs and verified parts prices, measurable estimation accuracy, and clear uncertainty/evidence — not simply a generic LLM-generated damage report. Existing products already claim URL-based AI inspection and Georgian repair estimates, including CarXray.ai.

**Important:** There is no confirmed official, commercially licensed Bid.Cars API for this project. Technical access and legal permissions are separate questions. No production scraper, browser-automation bypass, or photo storage of unlicensed content should be assumed. Build against fixtures and a provider interface until permission and integration terms are clear.

## 2. Users and jobs to be done

### Primary personas

- **Individual buyer in Georgia:** Wants to avoid an unaffordable salvage purchase, understand repair risks, and compare all-in cost with a locally available vehicle.
- **Professional importer / reseller:** Reviews many listings, wants consistent reports, quick shortlists, repeatable profitability estimates, and saved vehicle comparisons.
- **Repair shop / parts partner (later):** Provides price quotes and earns new repair/parts leads.

### Core questions the product must answer

1. Is this the exact same vehicle as the auction listing I submitted?
2. What damage is *visibly supported* by auction photos?
3. Which components may need repair or replacement, and what cannot be determined visually?
4. What should be inspected for structural, airbag/SRS, ADAS, cooling, suspension, and mechanical problems?
5. How much might parts and repair labor cost in Georgia (range + evidence)?
6. What will the vehicle cost to acquire, transport, clear, and register in Georgia?
7. Is the deal attractive, and what maximum bid makes sense given uncertainty and desired margin?

## 3. Product positioning and business model

**Positioning:** “Know the real cost before you bid.”  
**Category:** Pre-purchase salvage-vehicle intelligence and cost estimation.  
**Initial geography:** Georgia; USD costs with GEL display, and localization in Georgian and English (Russian later).  
**Initial sources:** Copart and IAAI as user-supplied auction links; Bid.Cars as candidate metadata/history lookup subject to authorization.

**Possible monetization (hypotheses to validate, not committed prices):**

| Plan | User | Possible pricing test |
|---|---|---|
| Single inspection | Individual | US$5–10 per basic report |
| Verified estimate | Serious individual buyer | US$20–40 with supplier-sourced pricing |
| Dealer | Importer / reseller | US$99–299 per month with a report quota |
| Enterprise / white label | Large importer | Custom |

Other future channels: authorized supplier lead fees, repair referral fees, B2B data tools. Do not add these before proving core report accuracy and user willingness to pay.

## 4. Scope and priorities

### Phase 0 — prerequisite: data rights and provider feasibility

- Determine whether Bid.Cars grants explicit commercial permission for automated lookup, use of metadata/photos, AI processing, caching, display, and retention.
- Evaluate official/authorized data channels for Copart, IAAI and other providers as alternatives.
- Build local fixture data and mock adapters immediately, *without waiting for a production data contract*.
- Document freshness limits: historical Bid.Cars snapshots are **not** a guaranteed real-time live auction feed.

### Phase 1 — first coding milestone (M1): auction URL resolver + exact vehicle identity

**IN scope:**

- Simple web UI with one input: “Paste Copart or IAAI URL.”
- Recognize permitted Copart and IAAI hostname variants; reject all other hosts.
- Extract auction house and apparent listing/page ID where the URL format allows it.
- Support IAAI cases where a URL's internal VehicleDetail ID may not equal the displayed stock number; represent that as **unresolved** rather than pretending they match.
- Define `AuctionSource` provider interface and `BidCarsProvider` placeholder/adapter behind it; implement **FixtureProvider** first.
- Search by auction house + lot/stock where the provider legally supports it; fall back to VIN only when actually available.
- Validate exact match using auction source and identifier, with VIN/model cross-checks when available.
- Return explicit `MATCHED`, `AMBIGUOUS`, `NOT_FOUND`, `UNRESOLVED_ID`, `SOURCE_UNAVAILABLE`, `NOT_AUTHORIZED` outcomes.
- Show matched vehicle information, provenance, fetched-at timestamp, and any licensed images.
- Unit and API tests, typed schemas, sample data fixtures, logging and basic error handling.

**OUT of scope for M1:** LLM calls, damage estimation, shipping calculations, custom scrapers, live bidding, payments, accounts, paid plans, marketplace, VIN-history purchase, advanced design system.

### Phase 2 — M2: evidence-based visual damage inspection

- Ingest authorized photos through the provider adapter or customer-supplied images where permitted.
- Structured AI extraction: visible damaged region, possible component, severity, observation text, image reference, confidence/uncertainty.
- Separate **OBSERVED**, **SUSPECTED**, and **UNKNOWN** findings.
- Image highlighting via verified normalized boxes/polygons; if localization is uncertain, show image reference and textual finding rather than fabricated bounding boxes.
- Mechanical/structural inspection checklist contextualized to collision area, not definitive diagnosis.
- Generate readable report in English first, Georgian next.

### Phase 3 — M3: repair and landed-cost estimates

- Deterministic cost engine backed by dated part quotes and labor-rate records.
- Parts alternatives: used OEM, aftermarket, new OEM where compatibility is verified.
- Low / expected / high estimates for each repair operation and total.
- Import-cost breakdown: winning bid, auction/broker fees, US inland transport, ocean freight/port charges, Georgian customs/excise, registration, incidental costs.
- Configurable defaults with clear editable assumptions; link tax calculations to current Revenue Service requirements.
- Historic/comparable sale analysis **only** when comparable records are properly licensed and normalized.

### Phase 4 — M4: bid intelligence and user accounts

- Risk-adjusted maximum-bid calculator (individual savings or dealer resale margin).
- Saved vehicles, comparison tables, batch processing, report history, payment plans, and dealer dashboard.
- Confidence bands and explicit “insufficient evidence” abstention when estimates cannot be supported.

## 5. Critical vehicle matching logic

**Canonical identity:** `(auction_house, auction_lot_or_stock_number)` identifies an auction listing, not necessarily the lifetime identity of a physical vehicle. **VIN** identifies the vehicle (where known); the same VIN may appear in multiple auction events or later re-listings.

Observed Bid.Cars URL convention (reference only, **not guaranteed contract**): `1-<lot>` for Copart and `0-<stock>` for IAAI. This convention must not be the sole verification criterion. Their site advertises VIN/lot lookup and historical auction records.

**Matching algorithm (proposed):**

1. Parse and normalize a user URL **without fetching it**; determine provider from an exact hostname allowlist.
2. Extract URL listing/page ID as a **string** (preserve leading zeros). For IAAI, treat a page ID as distinct from stock number unless proven equivalent.
3. Ask authorized provider adapter for records matching source + actual lot/stock number; if not available, resolve reference using a permitted primary provider/metadata source.
4. If a VIN is available, cross-check it. Also verify make, model, year and auction house when provided.
5. Return `MATCHED` only when source and exact lot/stock identity are corroborated. If data conflict, return `AMBIGUOUS` with candidate records and reasons. Never silently choose the nearest-looking model.
6. Link historical events by VIN but keep their auction identities separate; retain event date, status, fetched-at time and data provenance.
7. Expose stale data prominently. Do not call a historical price a “current bid.”

**Edge cases:** mobile URLs, extra query parameters, trailing slashes, redirects, URL shorteners (do not follow arbitrary redirects), unsupported domains, HTML-encoded ampersands, alphanumeric IAAI IDs, multiple sales, duplicate VIN events, unknown VIN, expired listings, no photos, VIN/title inconsistency, archived-only data, blocked/unauthorized API.

**Security:** URL parsing must never fetch arbitrary user URLs. If the app later fetches permitted URLs, use strict hostname allowlists, DNS/IP restrictions, redirect checks, timeouts, size limits, and rate limits to prevent SSRF. Treat retrieved page content and LLM outputs as untrusted.

## 6. System design (preferred starting architecture)

The implementation may adapt frameworks, but the boundaries below should remain.

```text
Browser (Next.js / TypeScript)
   | POST /api/resolve { auctionUrl }
   v
Backend (Python FastAPI + Pydantic)
   | URL Parser / Auction Identity Resolver
   | Provider Registry
   |-- FixtureProvider  [M1]
   |-- BidCarsProvider [disabled until access permitted]
   |-- OtherAuthorizedProvider [optional]
   |
   v
Vehicle Match Validator ---> PostgreSQL (records, sources, matching status)
   |
   +---> Inspection Job Queue [M2]
           | Vision model adapter -> structured findings
           | Evidence/image annotations
           | Repair pricing engine [M3]
           | Shipping/customs engine [M3]
           ` Report assembly [M3/M4]
```

**Recommended starting stack:** Next.js App Router + TypeScript + Tailwind; FastAPI + Pydantic + pytest; PostgreSQL (can start with SQLite for isolated prototype but use a migration path); SQLAlchemy/Alembic as needed; Docker Compose for development. Playwright for E2E. No orchestration framework or background queue required for M1; add a job worker when AI requests become slow.

**Design rule:** LLMs extract structured observations; arithmetic, currency conversion, fee schedules, vehicle matching, and safety gates use validated conventional code. Store model/version/prompt/version and quote timestamps for auditability.

### Suggested repository layout

```text
auction-intelligence/
  apps/
    web/                       # Next.js interface
  services/
    api/
      app/
        api/                   # FastAPI routes
        domain/                # Pydantic schemas + enums
        resolution/            # URL parser and matcher
        providers/             # Source interfaces, fixture adapter
        inspections/           # M2 vision + findings
        pricing/               # M3 cost engines
        persistence/           # DB access
      tests/
        unit/
        integration/
        fixtures/
  docs/
    decisions/                 # Architecture and licensing decisions
    source-integrations.md
    estimation-methodology.md
  .env.example
  docker-compose.yml
  README.md
```

## 7. Suggested data contracts

### Provider abstraction (conceptual)

```python
class AuctionSource(Protocol):
    async def resolve(self, reference: AuctionReference) -> ResolutionResult: ...
    async def get_vehicle(self, listing_id: str) -> VehicleSnapshot: ...
```

Provider results must carry `source_name`, `source_url`, `retrieved_at`, `license_scope`, and whether each field is observed, supplied, inferred, or missing. Never present fixture/mock data as live auction data.

### M1 API (draft)

- `POST /api/v1/auction/resolve` — input `{ "url": "https://www.copart.com/lot/51374586" }`; output resolution and normalized vehicle when matched.
- `GET /api/v1/health` — basic service status.
- Later: `POST /api/v1/inspections`, `GET /api/v1/inspections/{id}`, `GET /api/v1/reports/{id}`.

Example *illustrative response* (not proof this current lot exists):

```json
{
  "status": "MATCHED",
  "input": { "url": "https://www.copart.com/lot/51374586" },
  "auction": { "house": "COPART", "listing_ref": "51374586" },
  "vehicle": {
    "vin": "EXAMPLE_ONLY",
    "year": 2021,
    "make": "Toyota",
    "model": "Camry",
    "primary_damage": "Front End"
  },
  "provenance": {
    "provider": "FIXTURE",
    "retrieved_at": "2026-10-19T12:00:00Z",
    "data_type": "MOCK",
    "realtime": false
  },
  "warnings": ["Illustrative test fixture — not live auction data"]
}
```

**Schema detail:** VIN should be `null` when unavailable; never substitute placeholder values in real responses. Example uses an explicit fixture-only placeholder to avoid exposing a purported real VIN. All monetary fields later use decimal-safe representation (`amount`, `currency`, `source`, `as_of`), not floating point.

### Initial storage entities

| Entity | Important fields |
|---|---|
| `auction_listing` | provider, source lot/stock, source URL, event status, event date, VIN, snapshot timestamp |
| `vehicle` | VIN (nullable), make, model, year, trim, engine, odometer, title |
| `source_record` | provider, external id, raw permitted metadata, retrieval time, license scope |
| `photo` | authorized source reference or storage key, angle, rights/retention metadata |
| `resolution_attempt` | input URL, parsing result, candidate ids, status, match reasons, error |
| `inspection_report` (M2) | vehicle/listing, model+prompt versions, findings, evidence, timestamps |
| `damage_finding` (M2) | image id, region, component, OBSERVED/SUSPECTED/UNKNOWN, severity, evidence |
| `part_quote` (M3) | compatible part, condition, supplier, currency, amount range, timestamp |
| `cost_estimate` (M3) | version, line items, assumptions, low/base/high, provenance |

## 8. Repair estimation methodology

A repair report must not claim to see through body panels. Use three evidence types:

- **OBSERVED:** directly supported by photograph or auction metadata, with explicit provenance.
- **SUSPECTED:** possible secondary consequence of the observed damage, with reason and recommended confirmation.
- **UNKNOWN / NEEDS INSPECTION:** safety-critical or mechanical condition cannot be established from supplied data.

A cost line item needs: component or operation, action (`inspect`, `repair`, `replace`), compatible part/part number if verified, quantity, supplier quote or assumed range, labor hours, rate, paint/materials, possible scans/calibration, and confidence/quote date. Offer **low / base / high** scenarios and a separate hidden-damage contingency. Never invent an exact OEM part number. Significant SRS/ADAS/structural risks should trigger specialist-inspection recommendations, not an automated “safe to drive” label.

**Total acquisition + repair cost** = hammer bid + auction/broker fees + inland transport + ocean shipping/port fees + Georgian duties/excise/registration + parts + labor + diagnostics/calibration + risk contingency + other known fees.

**Max bid (later)** = conservative local market value (or resale proceeds) - all non-bid costs - uncertainty allowance - buyer's required savings or dealer margin. Because auction fees can depend on bid size, solve numerically using the fee schedule; don't simply subtract a fixed fee from the price. If crucial costs lack evidence, withhold a single confident max-bid number.

Georgia clearance must be checked using current official RS guidance and vehicle-specific information; do not hardcode 2026 tax rules from blog posts. Also ensure the model distinguishes a car intended for **registration in Georgia** from one intended for **re-export**.

## 9. Initial UI specification

**Landing:** single text field and `Analyze vehicle` action. Supported sources: Copart and IAAI. On submit show clear processing/resolution status.

**Resolved vehicle card (M1):** source logo/name, vehicle title, VIN where available, year/make/model/trim, lot/stock, auction status, retrieval timestamp, source link, photo thumbnail only if rights permit, badges for `LIVE DATA / ARCHIVED / MOCK`. Show exact-match evidence.

**Inspection view (M2):** multi-photo gallery with selectable evidence-linked findings, parts checklist, “needs physical inspection” section, confidence and limitations. Do not overlay a highlighted region unless actually localized to that image.

**Budget view (M3):** purchase and transport line items; parts and local labor low/base/high; total cost; editable bid assumption; value compared with Georgia market when supported.

**Errors:** unsupported URL, ID unresolved, listing not found, ambiguous match, data permission unavailable, missing photographs, stale listing, analysis failed. Avoid a generic failure page. Never show made-up records just to fill a UI.

## 10. Quality engineering and acceptance criteria

### Required test cases for M1

1. Valid Copart desktop URL containing a numeric lot ID.
2. Copart link with trailing slash / tracking parameters.
3. Valid IAAI `VehicleDetail` link with an internal ID **not assumed** to be its stock number.
4. Matching VIN and source lot/stock resolves exactly.
5. Same VIN with multiple sale events does not collapse records.
6. Wrong VIN for apparently matching lot is treated as `AMBIGUOUS`, not matched.
7. Provider lacks the listing -> `NOT_FOUND` (not 500).
8. Provider connection fails -> `SOURCE_UNAVAILABLE` (not false not-found).
9. Unlicensed provider -> `NOT_AUTHORIZED` with clear UI message.
10. Unsupported domain, malformed URL, malicious hostname, open redirect, embedded credentials, localhost/private-network URL -> rejected.
11. Preserve identifiers as strings (including leading zeros).
12. Archived listing is labeled historical, never live.
13. No photo or partial vehicle metadata renders gracefully.
14. User-provided URL cannot trigger arbitrary fetch or prompt-injection instructions.
15. Fixture results display an unmistakable MOCK label.

**Targets for feasibility study, not launch claims:** Test 50 diverse real links (at least 20 Copart + 20 IAAI; active, sold, archived, relisted), subject to authorized access. Aim for **zero false exact-match assertions** in validation. Report match coverage separately by auction house, status, and data source. Coverage targets should be set only after assessing what licensed data is available.

### Required tests for M2–M3

- Model evaluation against a blinded set of repaired vehicles with original auction photos and itemized post-repair invoices.
- Per-part precision and recall; critical missed damage categories; confidence calibration; cost absolute percentage error and low/high interval coverage.
- Distinguish genuinely unseen damage from errors the model could have detected.
- Verify safety-critical unknowns, missing evidence behavior, stale quotes, currency conversion, tax schedules, non-numeric money and negative values.
- Track model cost, latency, and report completeness on each change.

## 11. Implementation backlog and definition of done

### Sprint 1 — build only the resolver

- [ ] Scaffold API/web monorepo with clear setup commands.
- [ ] Add robust URL parser (Copart + IAAI) with exact host allowlist.
- [ ] Add typed enums/schemas for identity and resolution statuses.
- [ ] Implement `AuctionSource` protocol + in-memory `FixtureProvider`.
- [ ] Add exact-match validation with conflicts/ambiguity handling.
- [ ] Implement `POST /api/v1/auction/resolve` and `GET /api/v1/health`.
- [ ] Add browser URL form, resolved vehicle card, mock-data warning, and error states.
- [ ] Write pytest unit/API tests and at least one Playwright happy-path + failure-path flow.
- [ ] Add seed fixtures for both auction houses and ambiguous, missing, archived, error cases.
- [ ] Document environmental setup and how a licensed provider can be plugged in later.

**Sprint 1 definition of done:** A new engineer can clone/run the project locally; entering fixture Copart/IAAI links displays the correct matched identity; invalid and ambiguous cases are correctly rejected; tests pass; no live unauthorized scraping, false data claims, LLM calls, payments, or financial projections are present.

### Sprint 2 — integration feasibility (parallel business work)

- [ ] Contact Bid.Cars for commercial data licensing / partnership and written scope.
- [ ] Review eligible alternative authorized data sources.
- [ ] Define provider integration contract and caching/retention rules.
- [ ] Assemble a consented validation set with 20+ completed-repair examples and invoices.
- [ ] Interview 5+ Georgian importers/repair businesses about workflows and pricing data.

## 12. Known risks and mitigation

| Risk | Mitigation |
|---|---|
| Bid.Cars commercial data use not permitted | Keep adapter disabled, build on fixtures, negotiate rights or switch authorized source |
| IAAI URL ID does not equal stock number | Keep raw page id and canonical stock distinct; explicit resolution stage |
| Stale archive data mistaken for live auction | Timestamp all fields, display archived/current labels, never infer live bid |
| AI hallucinates hidden damage or exact parts | Evidence taxonomy; human review; low/base/high ranges; abstain if uncertain |
| False-positive VIN/lot matching | Exact auction identity checks, conflict gating, audit log, regression tests |
| Repair prices differ dramatically locally | Date-stamped real supplier/garage quotes; per-region rates; measure errors |
| Customs and auction fees change | Versioned fee/rule tables and official sources, quote dates |
| Photo copyrights, licensing and retention | Written provider agreement; data-minimization and deletion controls |
| Competitors already support similar feature | Differentiate on measured Georgian cost accuracy and provenance |
| AI API cost / latency | Cached authorized structured records; bounded photos/tokens; background jobs later |

## 13. Open decisions (do not silently assume)

- Brand name and domain.
- Exact contracted auction data provider (Bid.Cars is a candidate, **not confirmed**).
- Production permission to process/archive/show third-party listing images.
- Whether to ship Georgian localization alongside first functional prototype.
- AI vision provider/model; choose after benchmark against fixture photos.
- First set of high-frequency vehicle makes/models for pricing research.
- Local garages/parts suppliers as pilot partners.
- How to source authenticated Georgian resale-value data.
- Whether final pricing is per-report, subscription, or both.

## 14. Current research references (verified 19 Oct 2026)

1. Bid.Cars auction archive describes VIN/lot/stock lookup and sale history: https://bid.cars/en/bidfax
2. Sample Bid.Cars IAAI record showing `0-` source prefix, stock and VIN: https://bid.cars/en/lot/0-45371195/2011-Toyota-Camry-4T1BF3EK1BU656377
3. Sample Bid.Cars Copart record showing `1-` prefix and vehicle details: https://bid.cars/en/lot/1-73431655/2017-BMW-3-Series-WBA8B9G33HNU53543
4. Bid.Cars published terms: https://bid.cars/en/terms (English PDF linked there)
5. Copart's Image and Data License Agreement limits scraping and derivative use: https://www.copart.com/Content/US/EN/buyer/Sales/Image-and-Data-License-Agreement
6. Georgian Revenue Service official vehicle levy calculator: https://rs.ge/CarClearance-en
7. Existing competitor with Copart/IAAI analysis and Georgia-cost claims: https://www.carxray.ai/

All above are **research references**, not partner endorsements, API agreements, or permission to reuse copyrighted content.

---

# Appendix A — Copy/paste prompt for a new coding chat

> You are my senior software architect and hands-on coding agent. I want to build **Auction Intelligence**, an AI pre-purchase inspection application for buyers of damaged vehicles imported into Georgia. Read the attached `auction_intelligence_handover.md` as the source of truth.
>
> **Core user flow:** The user pastes a Copart or IAAI lot URL. Our backend extracts the auction source and lot/page identifier, then uses a pluggable authorized data provider (Bid.Cars is a candidate, not yet licensed) to resolve the exact vehicle. It checks auction identity and VIN rather than guessing. Later phases analyze photos, estimate repairs in Georgia, calculate full landed cost, and recommend a maximum bid.
>
> **Start with Sprint 1 only:** scaffold a Next.js + TypeScript frontend and FastAPI + Pydantic backend, implement a safe Copart/IAAI URL parser, canonical listing identity, `AuctionSource` provider interface, fixture/mock provider, exact-match/ambiguous/not-found logic, API and minimal UI, plus pytest/Playwright tests. Keep IAAI internal page ID distinct from stock number. Clearly label mock data. Do not scrape Copart, IAAI or Bid.Cars or pretend commercial API access exists; use fixtures while we evaluate authorized data access.
>
> First give me a concise implementation plan and repository structure, then begin writing the actual project code with runnable commands and tests. Do not build AI image analysis, cost estimates, login or payments in Sprint 1. Explain any architectural tradeoffs briefly and favor simple, well-tested code. If you cannot access the attached handover file, ask me to upload it rather than inventing its content.
