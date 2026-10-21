# Sprint 2 — authorized data feasibility and discovery

Status: proposed implementation backlog for review. This requirements document does not authorize provider contact, live auction access, data collection, or deployment. No such actions were taken to prepare it. Owners below are accountable roles to assign, not people already engaged.

## Goal and source of truth

Decide whether Auction Intelligence can lawfully and reliably resolve the exact Copart/IAAI listing through an authorized provider, while retaining a useful offline fixture product. Prepare the evidence and customer discovery needed for later inspection work.

**Sprint 2 is not M2.** The handover's §11 Sprint 2 is integration feasibility plus parallel business work. Its §4 M2 is a later visual-inspection milestone. This sprint does not implement AI/image analysis, damage findings, cost estimates, maximum bids, accounts, payments, live bidding, scrapers, photo ingestion, or an inspection dashboard. Planning future photo rights or a repair-validation dataset does not permit collecting or processing images now.

Source abbreviations used below:

| Source | Evidence and limits |
| --- | --- |
| H | [Handover v1.0](auction_intelligence_handover.md), read in full. §§1, 4–7, 10–14 govern rights, exact identity, provenance, feasibility and discovery. Appendix A describes the original Sprint 1 instruction; it does not replace §11's next-sprint backlog. |
| S1 | [Sprint 1 requirements](sprint-1-requirements.md), preserving identity and safety acceptance. |
| QA1 | [Sprint 1 test report](sprint-1-test-report.md): reports 75 pytest and 22 Playwright passes against synthetic fixtures, Chromium only; hosted CI and real-provider coverage were not validated. These results are inherited evidence, not checks rerun for this document. |
| INT | [Source integrations](source-integrations.md): licensed access must precede integration; offline fixtures remain available. |
| CODE | Existing `services/api/app/domain/models.py`, `providers/base.py`, `providers/bidcars.py`, `resolution/resolver.py`, `main.py`, frontend and setup commands. Current behavior is a fixture demonstration, not a commercial provider client. |

No current external research was conducted. H §14 contains historical research references, not licenses or verified present-day provider capabilities. Provider documentation, pricing, authorization, and regional coverage still require validation by the business owner through permitted channels.

## Existing baseline and invariant behavior

The existing `AuctionSource` boundary exposes `resolve` and `get_vehicle`; the Bid.Cars placeholder refuses both. Backend provider selection/health and frontend labels currently assume fixtures. `VehicleSnapshot.event_status` supports only `FIXTURE` and `ARCHIVED`; `license_scope` is narrative text, without enforceable use permissions. Vehicle attributes have field evidence; identity/mapping provenance is not yet a structured contract. There is no cache/retention enforcement or authorized adapter.

All next-phase stories preserve these invariants:

- Parse only exact allowlisted auction hosts without fetching the submitted URL. Users continue to paste Copart/IAAI URLs, not secondary-provider URLs. Retain SSRF controls if authorized outbound operations are introduced later.
- Keep raw IAAI internal page ID distinct from canonical stock. Require documented mapping evidence; equal strings, URL prefixes, and model similarity are insufficient. If the mapping cannot be corroborated, use `UNRESOLVED_ID`.
- Canonical listing identity is auction house plus exact string lot/stock. Preserve leading zeros. VIN can link vehicle history but cannot replace listing identity or merge separate auction events. Competing events remain `AMBIGUOUS` unless independent evidence selects an exact event.
- Cross-check independently supplied VIN/year/make/model when available. Conflicts are `AMBIGUOUS`; missing VIN stays null with a limitation. Never generate corroboration from the candidate being checked.
- Preserve all six outcomes: `MATCHED`, `AMBIGUOUS`, `NOT_FOUND`, `UNRESOLVED_ID`, `SOURCE_UNAVAILABLE`, `NOT_AUTHORIZED`. A successful authorized negative lookup alone supports `NOT_FOUND`; denied permission and service failure do not.
- Label MOCK, archived/historical, stale, and unknown freshness honestly. Licensing does not imply live data. Retrieval time does not prove source freshness. Never call a historical price a current bid.

## Prioritized stories and acceptance

Priorities describe the proposed sprint backlog. **Must** is required for a defensible feasibility decision; live-dependent acceptance remains explicitly blocked until its gate passes. **Should** strengthens execution; **Could** is optional carryover. A planning deliverable can be complete while external execution is pending, but the overall business targets must not then be marked achieved.

| ID | Priority | Deliverable | Primary owner | Start condition |
| --- | --- | --- | --- | --- |
| S2-01 | Must | Provider comparison and rights questions/evidence | Business lead | Draft now; outreach after G1 |
| S2-02 | Must | Static validated capabilities/authorization policy and tests | Technical lead | Offline design now; implementation separately scoped |
| S2-03 | Must | Mapping/reference evidence and event safeguards | Backend/QA | Contract review; synthetic examples |
| S2-04 | Must | Provider-aware labels and freshness semantics | Frontend/backend | Contract review; synthetic examples |
| S2-05 | Must | Lifecycle/outbound design and denial rules | Technical lead | Terms-independent safe defaults now |
| S2-06 | Must, gated | 50-link identity study plan and later authorized report | QA lead | Plan now; execution after G3 |
| S2-07 | Must, business | 20+ consented repair examples and readiness manifest | Research lead | Templates now; collection after permission |
| S2-08 | Must, business | Five+ Georgian business interviews and synthesis | PO/research lead | Guide now; interviews after G1 |
| S2-09 | Should | Updated offline regression evidence | QA/developer | When corresponding changes are implemented |
| S2-10 | Could | Reproduced Windows setup fix/guidance | Developer | Confirm supported target and reproduce |

### S2-01 — provider assessment and licensing evidence (Must, business)

**Story:** As the product owner, I need comparable evidence about Bid.Cars and alternatives so that we select a lawful, technically viable source rather than infer access from a public website. Source: H §§1, 4 Phase 0, 11 Sprint 2, 12–14; INT.

**Owners:** Business lead accountable for research/contact when separately authorized; rights/legal reviewer for scope; technical lead for capability assessment. **Dependencies:** an assigned business owner, authorized outreach for external execution, provider responses.

**Acceptance:**

1. Use the assessment template below for Bid.Cars and at least one alternative candidate/channel (the minimum comparison count is a planning proposal, not an H commitment). Unknowns remain unknown with an owner and next action; website availability is never evidence of automated commercial access.
2. Link each confirmed claim to dated written evidence, its scope, reviewer, and review/expiry date where supplied. Record denial, unsupported lookup, and unanswered questions explicitly.
3. Produce a recommendation with go/conditional/no-go and the precise unsupported houses, markets, identifiers, uses, or freshness claims. No provider is enabled by the assessment alone.
4. Prepare the licensing questions below without sending them in this task. A later authorized contact records the response as evidence, not presumed agreement.

**Deliverables:** candidate comparison, draft outreach/questions, rights evidence register, decision record. **Tests/review:** business and technical owners can trace every positive capability/right claim to evidence; missing proof fails the relevant gate.

### S2-02 — provider contract and fail-closed authorization (Must, development)

**Story:** As an integration developer, I need explicit capabilities and permissions so that a future adapter cannot use data for a purpose outside its agreement. Source: H §§4–7, 12; INT; CODE.

**Owners:** Technical lead and backend developer; rights reviewer approves semantics; QA verifies denial cases. **Dependencies:** S2-01 evidence for any real configuration; synthetic configuration permits independent development.

**Acceptance:**

1. Agree an internal contract proposal covering the fields/policies below and document compatibility with the current API and `AuctionSource`. Do not invent a provider endpoint, auth scheme, payload, SDK, or official API. Provider-specific mapping waits for authoritative documentation.
2. Default runtime remains fixtures. A real adapter stays disabled until reviewed authorization evidence, documented capabilities, valid securely supplied required credentials (if any), and an explicit allowed-use configuration all exist. A configured credential alone cannot enable it; a switch alone cannot override missing rights. Do not assume every authorized channel requires an API key.
3. Denied/missing/expired authorization returns `NOT_AUTHORIZED` without making the prohibited call. Unsupported IAAI mapping remains unresolved rather than guessed. Service/schema/rate-limit failures become `SOURCE_UNAVAILABLE` with a safe explanation, not false absence. Proposed unsupported-operation mappings are documented and tested before use.
4. Secrets live only in secure environment settings, never repository files, UI payloads, logs, or evidence exports. Record variable names/presence requirements only. Revocation disables new access immediately under the agreed policy.
5. Deterministic contract tests cover fixture and simulated authorized/unauthorized configurations without external traffic. Existing disabled Bid.Cars behavior remains testable. Do not implement a speculative production adapter.

**Deliverables:** internal contract ADR, typed policy/capability design and implementation tasks, fixture-based contract tests, configuration guide. **Proposed version:** `provider-contract-v1` is a recommendation for review, not a committed API version or vendor contract.

Keep this slice small: validated static configuration and deterministic tests are sufficient. No permission administration UI, new database, legal workflow platform, or retention service is required. This turn delivers requirements only; these are acceptance criteria for later implementation.

### S2-03 — independently evidenced identity and event resolution (Must, development)

**Story:** As a buyer, I need proof that the record belongs to the submitted listing so that a plausible vehicle cannot be falsely matched. Source: H §§5, 7, 10; S1; CODE.

**Owners:** Backend developer; technical lead approves identity semantics; QA owns adverse cases. **Dependencies:** S2-02; real evidence depends on S2-01.

**Acceptance:**

1. Extend the internal proposal to carry IAAI page-to-stock mapping origin, reference, corroborated house/identifier, and evidence timestamp independently of candidate vehicle metadata. Missing or unusable mapping evidence cannot produce an IAAI `MATCHED` response.
2. Reference metadata states origin and observation/retrieval times. Tests prove that candidate-derived expectations cannot masquerade as an independent VIN/year/make/model check.
3. Preserve provider record and event identifiers/date/status through results. Same VIN across different lots or events does not collapse records; repeated lot/stock with competing event records remains ambiguous unless event selection is independently supported.
4. Preserve current conservative outcomes for wrong source, wrong exact identifier, VIN/model conflict, partial metadata, leading zeros, alphanumeric page IDs, multiple candidates, and no mapping. Do not broaden a parser format without documented examples and tests.
5. Field evidence identifies missing values and distinguishes supplied/observed/inferred evidence; expand identity/event evidence deliberately rather than claim the existing vehicle-only dictionary already covers it.

**Deliverables:** contract mapping/evidence extension, adverse fixtures, regression tests, provider conformance checklist. **Tests:** unit and API conflict matrix plus browser page/stock separation and clear ambiguity/unresolved copy.

### S2-04 — provider-aware labels and freshness (Must, development)

**Story:** As a buyer, I need truthful source and age information even on an empty or failed lookup so that I do not confuse fixtures, licensed snapshots, and live auctions. Source: H §§5, 7, 9–10, 12; S1; CODE.

**Owners:** Frontend/backend developers; designer reviews copy; QA verifies states. **Dependencies:** S2-02 contract and S2-03 evidence semantics. Simulated non-mock tests require no real access.

**Acceptance:**

1. Health/provider context and UI receive the selected provider's actual mode, including empty/error responses; remove unconditional fixture labeling only as part of this deliberate change. Do not claim a selected but disabled provider is operationally ready.
2. Offline fixtures always display MOCK. A denied non-mock simulation cannot be labeled as a completed licensed lookup. Never silently substitute a synthetic matched vehicle after a real-provider failure; an explicit return to fixture mode must remain visible.
3. `LICENSED` describes permission, not freshness. Archived is historical. Missing source update time means freshness unknown; recent retrieval of an old snapshot cannot earn a live label.
4. Display provider, retrieval time, source observation/update time when available, event state/date, match evidence and limitations. Separate legal access, record age, and source availability. Explain `NOT_FOUND` without fixture-only wording when the selected provider is not fixtures.
5. Choose any staleness thresholds from measured/provider-supported guarantees and product review; thresholds and latency budgets remain proposals until agreed. Use deterministic clocks to test fresh/stale/unknown cases. Extend event states only through documented compatibility review; do not fabricate vendor statuses.

**Deliverables:** provider-aware API/UI contract, accessible status copy, deterministic freshness tests. **Tests:** browser cases for all six outcomes in fixture and simulated non-mock modes, unknown age, archived recent retrieval, and no stale prior result after failure.

### S2-05 — cache, retention, deletion and outbound policy (Must, development design)

**Story:** As the data-rights owner, I need enforceable use and lifecycle limits so that approved metadata access does not accidentally authorize storage or image reuse. Source: H §§4–7, 12; INT.

**Owners:** Technical lead/backend developer; rights reviewer; QA. **Dependencies:** S2-02; production values depend on written terms from S2-01.

**Acceptance:**

1. Record metadata and image permissions separately, including cache TTL, maximum retention, display scope, deletion/revocation obligations, derived-data rules, and restrictions by field/asset. Unknown permissions deny that use. No image fetch/display/storage/AI processing occurs under metadata-only access.
2. Produce an enforceable lifecycle design with cache keys that include provider, canonical listing and event/reference context; VIN alone is never a key for listing reuse. Distinguish source freshness from local cache age.
3. No cache is required for this feasibility stage: default to no persistent provider-data storage while terms are unknown. Any later cache implementation must test TTL expiry, maximum retention, invalidation and verified deletion, including derived records/backups as required by agreement, before being enabled.
4. Before any permitted adapter is enabled, document allowlisted service destinations from official documentation, TLS verification, timeouts, response-size/schema limits, bounded retry/rate-limit behavior, and redirect/DNS/IP controls. Never fetch user URLs or forward credentials across redirects. Avoid raw URL/VIN/secret logging.
5. Use synthetic records to test policy denial and lifecycle semantics. An uncertain permission, expiry or revocation cannot be bypassed by a previously cached record.

**Deliverables:** lifecycle/security ADR, permission matrix, denial/lifecycle test plan; runtime guards when implementing S2-02. Persistence technology and production TTLs remain explicit decisions rather than arbitrary defaults.

### S2-06 — authorized 50-link identity feasibility study (Must, conditional research)

**Story:** As the product owner, I need measured exact-match reliability and coverage so that pilot claims reflect evidence. Source: H §10 feasibility targets; §§5, 11; QA1; INT.

**Owners:** QA lead and technical lead; business lead secures permitted examples. **Dependencies:** S2-01 rights and documented provider access, S2-02–05 readiness, consent/rights for stored validation evidence, authorized execution.

**Acceptance:**

1. Prepare a manifest/results template now. Once access is permitted, test 50 diverse real listing links: at least 20 Copart and 20 IAAI, with the remaining 10 distributed explicitly. Cover active, sold, archived and relisted records; log unavailable strata rather than invent results. Fixture records do not count toward 50.
2. Record expected auction identity/event and independent ground-truth evidence, provider, timestamps, mapping evidence, actual status, match reason, limitations, latency/error class and reviewer. Do not retain third-party content beyond granted scope.
3. Review each `MATCHED` assertion against ground truth. Target zero false exact matches in the studied sample; any false match stops pilot activation until fixed and regression-tested. Unknown ground truth is not a verified match. Report adjudication disagreements and inconclusive cases.
4. Publish counts and denominators by house, auction state, provider and outcome. Separate false matches, abstention/unresolved rate, service failures, sample coverage, and correctness of asserted matches. Fifty links do not establish universal reliability. Set coverage goals only after capability evidence, without promising a fabricated success percentage.
5. If access is absent, deliver the manifest design and synthetic dry run clearly marked pending real validation. Do not mark the feasibility study complete or make production coverage claims.

**Deliverables:** rights-approved manifest, run report, errors/regressions and provider recommendation. This study tests listing identity, not damage recognition or repair accuracy.

### S2-07 — consented completed-repair validation cohort (Must, business)

**Story:** As a future inspection evaluator, I need consented before/after evidence so that later M2/M3 evaluation can be blinded and checked against real repairs. Source: H §§10–11, 12.

**Owners:** Business/research lead recruits when authorized; rights/privacy reviewer validates permissions; QA/data steward owns manifest quality. **Dependencies:** authorized outreach, consenting contributors and image/invoice rights, secure storage and access policy. No model implementation dependency.

**Acceptance:**

1. Prepare consent and eligibility templates; later assemble at least 20 completed-repair vehicle examples with original auction photos and itemized post-repair invoices. This cohort is distinct from the 50-link resolver sample; overlap is allowed only with separate purpose/rights documentation.
2. Each accepted example has a stable pseudonymous ID, vehicle/listing/event linkage with confidence, photo provenance, documented permitted uses, invoice dates/currency and line items, known damage/repair outcomes, evidence gaps and reviewer. Redact contributor/customer contact and unnecessary personal or financial details. Keep invoices, personal data, restricted VINs/identity keys, credentials and licensed datasets outside Git. Only synthetic examples or rights-reviewed redacted manifest templates belong in the repository; pseudonymization alone does not confer publication rights.
3. Separate consent to interview/share an invoice from rights to auction photographs, display, archive, or AI processing. Contributor consent cannot grant rights they do not hold. Missing photo rights makes the example ineligible for image evaluation until resolved; record exclusions rather than imply a full set.
4. Define restricted access, retention, withdrawal/deletion and a blinded holdout plan. Do not train, benchmark or upload images to a model in this sprint. Document selection bias, incomplete invoices and invisible damage limitations.
5. Record accepted/awaiting/excluded counts and reasons. A collection plan is not 20 collected examples. Missing rights/participants remain owner-assigned blockers to the business target.

**Deliverables:** cohort schema, consent/rights checklist, private evidence manifest and readiness report. Detailed accuracy metrics/benchmarks are future M2/M3 work, not claimed results.

### S2-08 — Georgian importer and repair discovery (Must, business)

**Story:** As the product owner, I need actual local workflow and pricing-evidence needs so that later work solves purchasing decisions. Source: H §§2–3, 11–13.

**Owners:** PO/research lead and business lead; designer observes when consented. **Dependencies:** authorized recruitment and participant consent; no provider contract required for a synthetic demo.

**Acceptance:**

1. Draft a neutral guide now; later complete at least five interviews with Georgian importers and/or repair businesses, documenting participant-role mix and recruitment limitations. Do not invent a quota split or claim individual-buyer validation from business interviews.
2. Ask participants to describe their most recent purchase and a costly mistake; how they verify lot/stock/VIN; when stale/archive data hurts; what proof would change a bid decision; repair/parts quote sourcing and dates; invoice availability; Georgian registration versus re-export workflows; and how they handle uncertainty and specialist inspection.
3. Show only the clearly labeled synthetic resolver if testing comprehension. Ask participants to explain MOCK, archived, exact match and unresolved states in their own words. Do not promise an AI inspection or financial recommendation is available.
4. Explore willingness to pay as a hypothesis without asserting the handover's sample prices are agreed. Ask about adoption barriers, language preference, preferred evidence and data-sharing conditions; do not introduce payment functionality.
5. Obtain consent for notes and separately for recording, minimize identifying information, store notes privately, synthesize recurring findings and contradictory evidence. Each proposed backlog change cites supporting observations, confidence and owner; interviews do not silently expand this sprint.

**Deliverables:** guide, consent template, five+ anonymized interview summaries and prioritized discovery synthesis. A guide alone does not satisfy the interview-count target.

### S2-09 — reproducible offline review and regression evidence (Should, development/QA)

**Story:** As a reviewer, I need a repeatable fixture demonstration while external work proceeds. Source: H §§10–11; QA1; S1; CODE.

**Owners:** QA and developer; PO verifies claims. **Dependencies:** S2-02–05 for any corresponding code changes.

**Acceptance:** all existing meaningful regression checks continue passing; new guard/mapping/freshness tests fail on the unsafe behavior they target; offline tests deny unexpected socket/DNS access. Report actual pytest/browser/build/typecheck results and environment limits without copying prior counts as a new run. Verify the existing POST resolve and health contracts, fixture UI and disabled adapter. Hosted CI and additional browser coverage are claimed only when executed.

**Deliverables:** updated test report and runnable commands, fixture conformance demonstrations, unresolved-risk register. No real data, secrets, or unlicensed photos are added to fixtures.

### S2-10 — bounded Windows setup carryover (Could, developer experience)

**Story:** As a Windows contributor, I need explicit supported startup commands so that shell assumptions do not prevent the offline demo. Source: reported setup friction in the development session plus CODE `Makefile`/README's `python3`, `.venv/bin/python`, and `make` assumptions; this document has not reproduced a Windows failure.

**Owners:** Developer with Windows validation access; QA. **Dependencies:** confirm target shell/runtime and reproduce the reported issue. **Acceptance:** document/test either an agreed WSL path or native PowerShell equivalents for venv, install, API, web and checks; record what was actually executed. Do not label Windows supported without verification. Keep this to setup guidance/helper scripts, with no application-scope expansion or platform promise.

## Proposed provider authorization/capability contract

The following are **internal design recommendations**, not a vendor API, a finalized wire schema, or evidence that these capabilities exist. Keep stable public fields compatible where possible; record any migration before changing them. Numeric TTLs, latency budgets, request limits, and supported markets come from reviewed terms/measurements, not invented defaults.

| Area | Proposed data/behavior | Evidence needed before real use |
| --- | --- | --- |
| Contract identity | Internal contract version, provider identity, adapter version, agreement/policy evidence reference and review status | Technical review plus signed/written authorized terms and effective dates |
| Allowed purposes | Separate states for automated lookup, commercial metadata use/display, metadata caching, photo retrieval/display/storage, AI inference, model training, derived-data sharing and redistribution; default denied/unknown | Explicit per-purpose scope, territory, audience and subcontractor restrictions; inference permission never implies training permission |
| Capabilities | Supported houses/regions, canonical lot/stock lookup, permitted VIN lookup, explicit page mapping, event history, field availability and freshness semantics | Authoritative provider documentation and approved examples; no guessed endpoints or `1-`/`0-` assumptions |
| Mapping evidence | Submitted page reference, corroborated canonical identity, origin/reference and observation/retrieval time, reviewable evidence scope | Authorized mapping mechanism; no derivation from page digits alone |
| Candidate evidence | Independent reference metadata origin/time; provider record/event identifiers; field evidence and missingness; normalized statuses with raw permitted status mapping | Provider contract and tested normalization; unavailable VIN remains null |
| Provenance/freshness | Source name/reference, retrieval time, source observation/update time if known, event time/status, data mode, historical/unknown/stale flags | Defined meaning of timestamps and any freshness guarantee; `LICENSED` does not mean `LIVE` |
| Images | Per-asset rights reference, permitted uses, attribution, expiry, storage/redisplay limits, deletion obligations | Rights for the exact use and assets; absent scope means no image action |
| Lifecycle | Cache enabled/disabled, TTL, retention ceiling, expiry/revocation checks, derived-data and backup rules, deletion verification | Agreed policies; no persistent provider-data cache until terms are known |
| Operations | Enabled state, required credential names if any, documented service hosts, failure mapping, bounded timeouts/retries and rate limits, safe logs | Valid securely supplied credentials when documented as required, approved network destinations and provider terms; never expose values |

`license_scope` text remains useful human provenance but is insufficient as the only runtime permission check. An adapter must not activate because a string contains “licensed.” Revocation and missing evidence fail closed for the affected operation; allowed metadata use does not require disabling independent offline fixtures.

## Candidate assessment template

Create one record per candidate/channel; initially label all unverified items **Unknown**. Bid.Cars is a candidate; official/authorized Copart, IAAI and other channels are alternatives to investigate, not integrations claimed to exist.

| Category | Record for each candidate |
| --- | --- |
| Identity | Candidate, responsible contact/channel when authorized, assessor, last reviewed, evidence links, status |
| Legal | Rights holder/authorization chain; commercial use; territories; permitted audience; metadata and each image use; retention/deletion; redistribution and derived data; agreement effective/expiry/revocation |
| Lookup | Copart lot and IAAI stock coverage; explicit IAAI page mapping; permitted VIN search; leading zeros/alphanumeric IDs; event and regional identifier semantics |
| Data | Available fields/nulls; history versus active snapshots; source timestamps; event segregation; photo licensing; freshness guarantee or explicit absence |
| Operations | Documented integration method and authentication; sandbox availability; quotas/rate limits; availability/support; schema/version changes; costs and restrictions, all with evidence |
| Evaluation | Authorized examples, unresolved risks, assessment confidence, fit/gaps, go/conditional/no-go recommendation, next action and owner |

Commercial feasibility considers both integration cost and rights limitations. A cheap source without dependable listing identity or permitted commercial use is not a viable replacement. Coverage and latency thresholds remain open until measured and reviewed.

## Draft licensing and technical questions — do not send yet

1. Do you provide an authorized automated channel for this commercial pre-purchase product? Which entity can grant the rights, and can the intended uses be documented in writing? A public archive or technical accessibility is insufficient.
2. Which auction houses, countries/markets, listing states and historical periods are covered? How are lot, stock, page, provider-record and sale-event IDs defined? Is explicit IAAI VehicleDetail-page mapping supported, and what proves it?
3. What documented lookup operations exist for source plus exact lot/stock and, if known, VIN? Can reference metadata be independently corroborated? What are null/conflict/duplicate-event semantics? Request official docs rather than propose guessed endpoints.
4. Which metadata fields may be used commercially, displayed, cached, retained, exported or shared? What attribution, territorial/audience limits and source updates apply?
5. For photographs separately: may we retrieve, thumbnail/display, store, archive, transmit to named AI subprocessors for inference, retain outputs, or use in evaluation? Is model training forbidden or separately licensed? Who warrants the rights for each asset? Can metadata-only access be licensed independently?
6. What TTLs, retention ceilings, deletion/revocation requirements, derived-data restrictions, backup treatment and audit obligations apply? How are removed listings/photos and rights changes communicated?
7. What does each timestamp/status mean? Is the service historical or real time; what freshness, availability and completeness commitments are actually offered? Can expired or relisted records be distinguished?
8. What supported auth, sandbox, quotas/rate limits, cost model, permitted retry behavior, versioning/change notification and support exist? How are denied/expired access, absent data, throttling and service errors distinguished?
9. May authorized samples be retained for the identity feasibility study, and under what redaction/security/publication conditions? May only aggregate results be published? Confirm no photo collection/AI rights are assumed by this request.

Business owner can adapt this draft and initiate contact only under a separately authorized outreach action. This requirements task sends no messages and makes no commercial requests.

## Decision gates and definition of ready

| Gate | Required evidence | Owner and consequence if missing |
| --- | --- | --- |
| G0 — offline development ready | Story scope/acceptance reviewed, synthetic fixtures identified, API compatibility risks noted, no secrets/live data required | PO/technical lead: S2-02–05 design and offline tests can proceed independently |
| G1 — external work authorized | Assigned business/research owners, approved outreach/recruitment activity and participant/data handling plan | Business lead: prepare templates only; do not contact providers or participants |
| G2 — authorized integration ready | Written use-specific rights, documented operation/identifier semantics, approved destinations, valid securely supplied required credentials if any, policy review | Rights/technical leads: keep real adapter disabled; no speculative provider implementation or calls |
| G3 — controlled evaluation ready | S2-02–05 guards and identity tests pass, rights-approved manifests, independent ground truth, retention/deletion plan and permitted execution | QA/technical leads: no real-link run until evidence exists; synthetic dry run is explicitly separate |
| G4 — limited resolver pilot | Reviewed study with zero observed false exact matches, documented house/status coverage and limitations, owner-approved rollout and rollback | PO/QA/business: no pilot on false-match failures or unsupported claims; scope may remain fixtures or a proven supported subset |
| G-image — image use, separately gated | Written per-use/per-asset rights, approved attribution/retention/deletion, and separately scoped implementation | Rights/technical leads: absent image rights blocks images, not an otherwise authorized metadata-only resolver; image implementation remains outside this sprint |
| G5 — later M2 ready | Independently scoped vision requirements, image/AI-processing rights, consented evaluation cohort readiness and explicit implementation decision | PO/rights/technical leads: passing Sprint 2 never automatically starts image analysis |

A development story is ready when its proposed contract choices are reviewed, dependencies have a permitted offline path, measurable acceptance and test data exist, and blockers have owners. Live/provider-specific work is not ready merely because an empty adapter can be scaffolded. Business execution is ready only after G1 and the rights needed for its exact collection/use.

## Definition of done and release/no-go

**Requirements package done:** this source-traced backlog, templates, gates and owners are reviewable; proposals are distinguishable from handover requirements. It does not mean interviews, licenses, data collection or the feasibility study have occurred.

**Development slice done:** agreed internal contract and offline guard/mapping/label changes are implemented, reviewed and tested; existing resolver regressions pass; reproducible commands and actual test evidence are recorded; fixture mode remains truthful and usable; no live adapter is enabled without G2/G3.

**Business Sprint 2 targets done:** provider rights/capabilities receive an evidence-based decision (including a documented no-go); the handover's 20+ consented repair examples and five+ interviews are genuinely collected and reviewed, or explicitly recorded as incomplete with owner/dependency. Do not convert missing external evidence into a claim of full sprint completion. The 50-link study has its own conditional completion status and cannot be substituted by those activities.

Rollout is phased: offline fixture release → separately authorized controlled evaluation → explicitly approved limited resolver pilot. Keep fixture mode available and visibly separate. No production publication is requested here. On permission expiry/revocation, false exact matches, unsafe outbound access, misleading freshness labels or unmet deletion requirements, disable affected provider operations and return truthful unavailable/unauthorized states. Do not silently serve mock matches as real fallback. Re-enable only after evidence, fixes and relevant checks are reviewed.

## Minimal decisions and actionable planning summary

The user/business owner needs to assign: (1) the accountable licensing/outreach owner and authority/budget for future contact; (2) a rights reviewer and secure evidence location; (3) a research owner and consented recruitment/storage process; and (4) who can approve the internal contract and eventual pilot subset. Exact provider choice, production TTLs/freshness promises and any live rollout remain evidence-dependent. Brand, monetization, model selection and localization do not block offline feasibility preparation.

Proceed now with review of S2-02–05 contract proposals and synthetic acceptance cases; prepare S2-01, S2-06, S2-07 and S2-08 templates without contact or collection. Assign business actions separately, then gather written rights and capability evidence through authorized channels. When gates permit, implement only the documented provider integration, run the distinct identity study, and review results before a limited resolver pilot. Keep M2 inspection and financial features in a separately approved future backlog. S2-10 Windows work is bounded optional carryover after reproduction, not a reason to expand product scope.
