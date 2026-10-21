# Sprint 4 — provider discovery and first authorized integration

Status: revised PO/technical recommendation, 22 October 2026 (Asia/Tbilisi). **Research attempted; current public-source verification is blocked. No provider has been selected or integrated.**

## Why the scope changed

The user correctly challenged the earlier private-photo intake proposal: Auction Intelligence should resolve a pasted Copart/IAAI URL using an existing authorized data source. Lack of an existing account or agreement is a research task for the PO and technical lead, not a reason to assign provider discovery to the user or make a standalone photo tool the default next sprint. This revision supersedes the earlier recommendation in this file; Git history preserves it.

The [handover](auction_intelligence_handover.md) remains the product direction. Sprint 3 delivered only an authored MOCK inspection preview. Its [317 backend / 86 browser results](sprint-3-test-report.md) are inherited evidence, not new execution for this planning revision. No production data access, real photographs or AI model is available in the existing application.

The user authorizes provider research and planning. This does not authorize contacting businesses, accepting contracts, purchasing access, collecting auction records/photos, or bypassing access controls. Public technical/terms research is read-only work we own and can perform without asking the user to do it.

## Research status and ownership

The named research targets are **bid.cars, motor.pl, westmotors.cz and qopart.az**, with official auction channels and documented alternative data services considered where relevant. Exact domains, operating entities and offerings must be established from retrieved sources, not guessed from names. A candidate is not a verified supplier.

Ordinary HTTPS reads on 22 October returned environment-proxy CONNECT 403 responses before any site content was obtained. A network permission grant and an outside-sandbox retry did not resolve the restriction. This is **not evidence of a provider ban, missing API, restrictive terms, or site bot protection**. See the [attempted-research evidence record](research/provider-research-2026-10-22.md). No current provider ranking, rights determination or API specification can honestly be established from these attempts.

| Work | Accountable role | Expected result |
| --- | --- | --- |
| Current official-source provider research | PO | Verified shortlist, cited evidence, unresolved questions and recommendation |
| API/schema/identity feasibility | Technical lead | Integration approach, exact lookup/mapping semantics, constraints and effort |
| Use-scope evidence review | PO + appropriate business/rights reviewer | Supported metadata/image/inference uses and unresolved commercial questions |
| Implementation and validation | Developers + QA | Authorized adapter and executed contract/identity/UI tests |
| Business commitment, only if needed | User/business owner | Decision on a concrete shortlisted offer, actual terms and budget |

The user should receive a recommendation and specific decisions, not an empty questionnaire or a request to research websites. Credentials are supplied securely only if the selected integration needs them; never ask for keys in chat or Git. If commercial questions remain after public research, prepare a targeted inquiry and identify the recipient from a verified official source. Sending it requires separate outreach authorization.

## Prioritized backlog and acceptance criteria

### S4-01 — actual provider research (PO, must)

- Retrieve official product, developer/API/feed/export, pricing if published, terms and image/data-use documentation for the named sites and a small relevant alternative set. Use normal public access; do not scrape auction listings or bypass blocks.
- Cite exact source URLs, retrieval/review dates and brief supporting text for each material claim. Distinguish verified publication, supplier claim, unavailable page and unresolved question. Published API availability alone is not a project license.
- Establish product fit: supported auction houses/regions, exact lot/stock lookup, explicit IAAI page-to-stock mapping, VIN cross-checks, event/history identifiers and freshness semantics. A VIN-only service may be useful but cannot silently satisfy the URL-to-exact-listing job.
- Review uses separately: commercial automated metadata lookup/display, photo retrieval/display, inference, storage/retention and derived output. Unknown scope remains unknown; public visibility is neither blanket permission nor proof of prohibition.
- Deliver a ranked recommendation with reasons and unresolved dependencies. If network access remains blocked, report that blocker; do not mark research complete or replace findings with templates.

### S4-02 — concrete integration decision (PO + technical lead, must)

- Select one provider/channel using S4-01 evidence, or make a justified no-selection decision with the next owned action. An authorized metadata-only integration is a valid first slice if photo/inference use is unavailable.
- Record the actual documented operations, identity/mapping contract, auth method, destination, quotas, costs if established, freshness, retention and use scope. Do not invent endpoints, response fields or package prices.
- Present only necessary business choices: concrete spend/contract/access decisions. Keep research, technical comparison and implementation planning with the team.

### S4-03 — first authorized adapter (developers, conditional on S4-02)

- Implement the selected documented channel behind `AuctionSource`. Keep fixtures explicitly available for offline development; real lookup failures must not fall back to fixture success.
- Preserve exact auction house and lot/stock strings, IAAI page/country separately from stock, independent VIN/model corroboration and distinct record/sale-event identity. Missing IAAI mapping returns unresolved, not a guess.
- Return truthful matched/ambiguous/not-found/unresolved/unavailable/unauthorized outcomes and actual provenance. Label historical data as historical; a fresh request does not make an old snapshot live.
- Enable only the established use scope. Metadata access must not enable photos, AI or training automatically. Do not attach real provider records to existing authored mock-image scenarios.
- Use fixed documented destinations, bounded requests/responses, finite timeouts/retries, secure credentials and sanitized logs. No arbitrary user-URL fetch, scraper or access-control workaround.

### S4-04 — end-to-end product behavior (frontend + backend, conditional)

- A permitted, supported original auction URL resolves through the selected provider and shows its exact identity, provenance, source age and limitations.
- Unavailable/denied data explains the cause without fabricated records. Ambiguous and unresolved identities remain actionable failures.
- Show images only if that separate use and exact linkage are established. Keep Sprint 3 authored examples visibly MOCK; no implication that licensed metadata authorizes its photographs for inference.
- Defer real AI selection/activation until permitted inputs and processing terms exist. No standalone upload UI is required to finish a metadata integration.

### S4-05 — verification and reproducibility (QA, must for selected implementation)

- Preserve existing parser, identity, provider-policy, freshness and mock-preview regressions. Add selected-adapter request/response contract tests with clearly identified test doubles; routine CI needs no paid access.
- Test exact identity conflicts, duplicate/relisted events, leading zeros, missing mapping, denied uses, unavailable source, malformed/oversized responses and no synthetic fallback. Add browser checks for delivered states on desktop/mobile.
- Any actual provider smoke test uses authorized access and records what really ran. It does not establish broad coverage; use the existing identity-study protocol before wider coverage claims.
- Update stale source-integration wording and provide tested setup instructions, including direct PowerShell commands and the supported Python version. Record actual results; do not claim native Windows/hosted CI or real-provider success without observed evidence.

## Sequencing and completion

First restore ordinary public-source access and complete S4-01. Then deliver the recommendation and concrete integration choice, implement the supported slice, execute its tests and record the result. If a contract/account decision is needed, complete the public research and concrete integration plan first; ask only for that specific business decision.

A research report is not an integration, an adapter test double is not live access, and a permission string in configuration is not a license. Sprint delivery must state which of research, selection, implementation and authorized live validation actually completed. Current state: **public-source research blocked; no provider selected; no new application code written**.

The existing consented repair cohort and Georgian workflow interviews remain parallel business work with their own owners, not proof supplied by this sprint. Excluded here: unlicensed scraping, production deployment, paid calls without an agreed budget, external outreach without authorization, repair/landed-cost estimates, taxes, maximum bids, login and payments.
