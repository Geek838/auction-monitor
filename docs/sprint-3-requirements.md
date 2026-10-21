# Sprint 3 — evidence-linked inspection preview

Status: PO recommendation for the next development increment, prepared 21 October 2026. This is a requirements package, not an implementation or a production-inspection claim. The handover defines M2 but no fixed Sprint 3; the scope below is a proposed first M2 increment, not an existing commitment to complete all of M2.

## Goal, evidence and recommendation

A buyer resolves a fixture Copart/IAAI listing, opens an unmistakably **MOCK inspection preview**, selects project-authored example images, and sees which seeded observations, uncertainties and physical checks relate to each image. The product demonstrates an evidence-linked report workflow without claiming it inspected an auction vehicle or ran AI.

Build now with an allowlisted set of self-authored raster illustrations/test images and a deterministic mock inspection adapter. Do not introduce arbitrary customer uploads, remote image ingestion, real vision calls or paid APIs in this slice. Those are conditional follow-ups with their own rights, security and operating decisions. Unknown asset bytes must lead to abstention, never canned damage findings.

| Reference | What it establishes |
| --- | --- |
| H: [handover v1.0](auction_intelligence_handover.md), read in full | §§4 M2, 7–10 require structured visual findings, photo references, uncertainty, verified optional localization and inspection guidance; §§5, 12 preserve exact identity and rights. §14 references are background, not current authorization. |
| S2: [requirements](sprint-2-requirements.md), [delivery](sprint-2-delivery.md), [test report](sprint-2-test-report.md) | Offline policy/evidence/UI slice delivered; recorded 190 pytest and 48 browser passes. These are inherited results, not rerun for this document. No commercial provider, image integration or model has been activated. |
| ADR: [provider contract](decisions/002-provider-contract.md) | Separate metadata/image/inference/training permissions, no synthetic fallback, exact page/country/stock, record/event separation and source-based freshness. |
| CODE: current domain models, `AuctionSource`, policy/registry and frontend `resolution-types.ts` | Resolver models exist; there is no photo, inspection finding, report or model-run implementation. Existing `FieldEvidence.kind` describes metadata origin and is not the damage-finding taxonomy. |
| Research: [preparation pack](research/README.md), [repair cohort](research/repair-cohort.md) | Templates only: 0 real identity-study cases, 0 accepted repair examples and 0 interviews recorded. No model accuracy evidence or rights agreement follows from those templates. |

The user has manually explored the app locally, including Windows startup, but no hosted CI result, formal native-Windows test run, licensed image collection or selected AI model has been supplied as new evidence. No external research, outreach, scraping, collection or application change was performed for this PO task.

## User flow and scope

1. Paste a supported Copart/IAAI URL and resolve it through the current provider mode. Keep existing identity, source-age and mock/simulation labels visible.
2. Only a corroborated, allowlisted fixture snapshot with an eligible authored image set offers **Open MOCK inspection preview**. Other matched records explain that no eligible preview images exist; a match does not imply image rights.
3. On the explicit action, the backend re-resolves/validates the reference and derives the approved scenario from the exact snapshot binding. If the current server snapshot differs from the one displayed, block attachment and require refresh/re-resolution. The browser cannot choose another vehicle's photos or submit arbitrary findings.
4. Display a small gallery and report. Selecting a finding focuses its referenced image; selecting an image reveals related findings. Show OBSERVED, SUSPECTED and UNKNOWN separately, alongside evidence and inspection recommendations.
5. Missing/invalid evidence produces a partial or blocked preview with reasons. Changing the URL, provider, record/event or failed lookup clears the previous report. The UI never presents a canned report as analysis of different bytes or a different vehicle.

**Build now:** authored-image manifest and rights metadata; typed inspection contracts; mock adapter and validators; one synchronous preview endpoint; gallery/report/checklist; denial/partial/error states; meaningful tests and review commands.

**Conditional later:** customer upload, authorized-provider photo ingestion, external vision adapter activation, persistent report history, background jobs and model evaluation. None is required to finish this bounded preview.

**Excluded:** costs/parts pricing, landed-cost/tax engines, maximum bids, model training, live auction integration, accounts/login, payments, marketplace, public deployment, fabricated diagnoses, a new design-system project, and Georgian localization by assumption. English is the proposed preview language; localization remains an explicit decision.

## Prioritized backlog

Must stories define the buildable slice. Should stories improve evaluation preparation without implying a live model. Conditional stories are specified boundaries, not permission to implement/activate them now. Owners are roles to assign, not people already engaged.

| ID | Priority | Deliverable | Owners / dependencies |
| --- | --- | --- | --- |
| S3-01 | Must | Authored asset manifest and exact snapshot binding | Developer + PO/rights reviewer; S2 identity/policy contract |
| S3-02 | Must | Typed inspection/evidence contract and validators | Backend + QA; S3-01 |
| S3-03 | Must | Deterministic mock adapter and synchronous preview operation | Backend; S3-01–02 |
| S3-04 | Must | Evidence-linked gallery and report | Frontend + designer; S3-02–03 |
| S3-05 | Must | Unknowns, coverage gaps and physical-inspection checklist | PO + backend + qualified domain reviewer; S3-02 |
| S3-06 | Must | Use guards, safe asset serving and transient lifecycle | Backend + QA; S3-01–03, existing policy |
| S3-07 | Must | Regression, adversarial and user-demo validation | QA + developers; all build-now stories |
| S3-08 | Should | Future vision-adapter/evaluation readiness specification | Technical lead + PO/QA; no vendor/model presumed |
| S3-09 | Conditional, not this slice | Customer-upload or authorized-photo path | Rights/privacy + technical lead; explicit source/storage/security decision |
| S3-10 | Carryover, business | Provider, study, cohort and interview evidence | Business/research owners; existing Sprint 2 gates |

### S3-01 — rights-cleared assets tied to the exact snapshot

**Story:** As a buyer reviewing the preview, I need to know which image belongs to this exact example so that evidence cannot be borrowed from a similar vehicle. Trace: H §§4–5, 7, 9; S2/ADR.

Acceptance:

- Register only project-authored raster assets with an asset ID, cryptographic content digest, decoded dimensions/MIME, view label or UNKNOWN, author/provenance, explicit permitted display/demo uses and rights review reference. Label diagrams/illustrations as such; do not imply they are auction photos.
- Bind each scenario to provider/data mode, canonical house + exact string lot/stock, provider record ID, sale-event ID/context and snapshot/version fingerprint. Preserve IAAI page/country/stock evidence separately. VIN alone cannot select images or findings.
- Include at least one eligible example for each auction house as a proposed demo target, plus missing-photo and incomplete-evidence cases. Exact fixture keys/assets are chosen and documented during implementation, not claimed to exist yet.
- Keep provider metadata mode, asset origin and inspection-engine mode distinct. A SIMULATED listing may have a MOCK preview only when that combination is explicitly registered and visibly labeled; this never licenses attaching mock photos to a real external listing.
- A wrong binding, changed hash, unavailable asset, expired/revoked use or unknown scenario cannot yield seeded observations for that asset. No bytes from Copart/IAAI/Bid.Cars are fetched or committed to satisfy the image requirement.

### S3-02 — structured findings with honest evidence

**Story:** As a buyer, I need supported observations and uncertainty to be distinguishable so that an inspection suggestion does not look like a diagnosis. Trace: H §§4 M2, 7–10.

Acceptance:

- Define a new finding classification `OBSERVED | SUSPECTED | UNKNOWN`, separate from existing metadata `SUPPLIED | OBSERVED | INFERRED | MISSING` origin fields. Do not convert `primary_damage` metadata automatically into a photo OBSERVED finding.
- OBSERVED requires a valid authorized image reference and a concrete visible-feature description. In this slice it is a hand-authored observation about the synthetic image, labeled MOCK. SUSPECTED requires its evidence-linked rationale and a confirmation step; UNKNOWN states what is not assessable and the missing evidence/physical check.
- Every image reference points to an eligible asset in the same report snapshot; dangling IDs and mismatched hashes are invalid. No free-text assertion can override identity, rights or schema validation.
- Severity is bounded and may be UNKNOWN. Confidence may be null; the mock adapter supplies no fabricated calibrated percentage or model score. A future raw model score must disclose its meaning/uncalibrated status rather than imply measured correctness.
- Localization is optional. The normal fallback is image reference plus text, with no overlay. Only author-reviewed coordinates bound to the exact fixture bytes/dimensions may render; validate finite normalized values, nonempty geometry and bounds. Unknown localization must not generate a full-image placeholder box or guessed highlight.
- Findings contain no repair price, exact invented OEM part number, hidden structural certainty, overall safe-to-drive verdict or unsupported airbag/mechanical diagnosis.

### S3-03 — mock engine and server-owned preview orchestration

**Story:** As a developer, I need an inspection boundary that exercises the report workflow without pretending an AI provider exists. Trace: H §§4, 6–7, 10; ADR.

Acceptance:

- Introduce an `InspectionEngine` protocol and deterministic `MockInspectionEngine`. The mock accepts only approved scenario/asset hashes, returns versioned seeded findings and makes no network/model call. Arbitrary bytes or scenarios abstain with no damage assertions.
- Propose `POST /api/v1/inspections` for a synchronous preview, aligned with H's draft direction; its exact wire schema is an implementation ADR decision. Input supplies the auction reference and an expected snapshot fingerprint/opaque binding reference from the displayed resolution, not trusted client status/snapshots, raw image URLs, arbitrary filesystem paths, model names, rights/provider overrides or findings.
- Resolve and validate the current target server-side using existing guards. Non-MATCHED outcomes block preview and preserve the resolver status/reason; no images from the nearest vehicle and no silent fixture substitution.
- Expose narrow server-derived preview eligibility through an additive resolver field or reviewed availability contract. The UI must not infer eligibility from a vehicle title, VIN, provider label or client-supplied `MATCHED` value.
- Independently recompute and compare the expected snapshot binding server-side. A changed provider/record/event/content version returns a distinct target-changed block; do not attach a new report to an old displayed card. The UI also rejects responses whose target differs from its currently displayed resolution. An additive server-derived fingerprint/opaque reference can supply this precondition without a database; it is a comparison hint, not proof of permission or identity.
- On an eligible scenario return a complete typed preview response. A valid subset may produce PARTIAL with explicit exclusions; no usable eligible images produces BLOCKED, not a fabricated all-clear report. A contract/engine failure produces FAILED without invented findings or raw exception disclosure.
- Keep work synchronous and bounded for fixed local assets. Do not invent queued/running jobs, polling endpoints, workers, a database or job completion timing merely for a deterministic mock. A future asynchronous model run gets a separate reviewed state contract.
- Record engine name/version, scenario/fixture revision, schema version, generation timestamp and image/target digests. For MOCK, model and prompt identifiers are null/not applicable; never fabricate an OpenAI/other vendor run or charge.

### S3-04 — readable gallery and report

**Story:** As a buyer, I need to inspect the evidence behind each finding rather than trust an unexplained result. Trace: H §9 M2; current worksheet design.

Acceptance:

- Preserve the paper-and-ink layout, keyboard navigation, visible focus and responsive behavior. Give authored images meaningful view/illustration alt text and accessible selected-image controls. Add a small gallery and report within the resolved-listing flow, not an unrelated dashboard or account/history area.
- Persistently show **MOCK INSPECTION PREVIEW — hand-authored example, no AI analysis**. Label each synthetic illustration and retain the original MOCK/SIMULATED provider and historical/stale/unknown-source notices.
- Show observed/suspected/unknown groups, referenced images, limitations, severity/uncertainty and recommended checks. Selecting a finding/image maintains a clear accessible relationship; metadata-only evidence is labeled separately from image evidence.
- Expose useful provenance details without dumping private policy documents or internal paths. Display listing, record/event and relevant source/image dates; report generation time is not an image capture date or proof of current vehicle condition.
- Handle loading, partial images, missing photos, blocked permissions/identity, unknown asset, engine error and retry accessibly. Clear previous images/findings on changed reference, new resolution or failure, and discard late responses for an earlier listing/request. Never keep an old Camry report beside a newly submitted listing.
- Do not call the action “AI analysis,” a mock result a real inspection, or absent findings “no damage.” No preview button is offered as usable for ambiguous/unresolved/disabled-source cases; server-side denial is required even if a client bypasses the UI.

### S3-05 — physical checks and abstention

**Story:** As a buyer, I need explicit inspection limits so that visible cosmetic evidence is not mistaken for a safety assessment. Trace: H §§4 M2, 8–10, 12.

Acceptance:

- Include a coverage/limitations section identifying available views, missing/obscured areas and what cannot be inferred from the example. No useful finding must not be translated into proof of absence of damage.
- Structural integrity, SRS/airbags, ADAS, cooling, suspension and mechanical condition remain UNKNOWN unless a narrowly supported visible observation is described. Even an observed damaged part does not establish hidden condition, functionality or roadworthiness.
- Recommend relevant qualified physical inspection/diagnostics, tied to the scenario's visible area or a stated coverage gap. Recommendations are checks, not diagnoses or mandatory repair/replacement conclusions. A domain reviewer approves wording before any future real-user pilot.
- A no-visible-damage synthetic case still includes safety-critical unknowns. Unsupported safety assertions are rejected/removed with a reason; they cannot be promoted to a confident summary.

### S3-06 — use permissions, asset delivery and lifecycle

**Story:** As the data owner, I need the preview to use only the intended authored material and to stop using revoked evidence. Trace: H §§5–7, 12; ADR.

Acceptance:

- Add only the narrow local-fixture permissions/capabilities needed for preview display. Metadata permission alone does not enable image display; image display does not enable inference, training, redistribution or external storage. Unknown rights deny the affected use, without breaking the existing metadata-only resolver.
- Check target binding, asset hash and current permitted use before report generation and asset delivery; recheck relevant rights before releasing awaited results. A previous preview or cached possession is not a permission bypass.
- Serve allowlisted asset IDs through a controlled local route or equivalent reviewed mechanism, never an arbitrary file/URL fetch. Reject path traversal, unknown IDs and client-provided data URLs/filesystem paths. Use actual verified raster MIME, safe response headers and no executable image content.
- Proposed minimum storage design: immutable authored assets/manifest in the repository, report computed per request and held only in the current browser view; no server report history, uploaded bytes or response cache. Use non-cacheable preview responses/guarded asset responses where needed to preserve current-use checks. Document that static Git assets and downloaded client copies are not a deletable private upload store.
- Bound asset count/decoded dimensions/bytes and request/output sizes through the reviewed manifest/configuration. Any numeric caps are engineering proposals with resource rationale, not handover limits; there is no unbounded upload or paid-operation budget in this slice.
- Treat image text, metadata, EXIF/captions and all future model output as untrusted data. No instruction embedded in an asset changes authorization, identity or tool behavior. Do not add EXIF/GPS collection, arbitrary rendering HTML, external scripts or secrets to reports/logs. Offline tests fail if inspection triggers outbound network access.

### S3-07 — proof of the delivered workflow

**Story:** As a reviewer, I need repeatable failures and evidence navigation so that a polished mock does not conceal unsafe matching or inference. Trace: H §10; S2 test baseline.

Acceptance:

- Preserve relevant Sprint 1/2 parser, matching, policy, mode and freshness regressions. Add unit/API checks for exact target/asset binding, altered bytes, missing/revoked rights, all three finding classes, dangling references, invalid geometry, safety wording and deterministic versioned mock output.
- Assert unknown/customer-supplied asset bytes cannot receive an existing scenario's canned observations. Mock output is selected only by the server's allowlisted snapshot/scenario, never user text or VIN similarity. Test a same-URL record/event/content change between resolve and preview, and a forged/missing snapshot precondition; neither may place a report beneath the wrong snapshot.
- Browser checks against the actual API cover Copart and IAAI preview, image/finding navigation, persistent MOCK/no-AI labels, archived/stale context, missing/partial images, blocked/failed preview, clearing a previous report and rejecting late cross-listing responses. Include desktop/mobile and keyboard behavior; report what actually ran.
- Verify a hostile asset caption or future-output fixture cannot alter permissions or cause network/tool execution. Test request ID/path abuse, UI text escaping and output validation; do not describe those fixtures as adversarial-model evaluation.
- Record actual test counts, build/typecheck results and platform limits. The inherited 190/48 counts are a regression baseline, not Sprint 3 execution evidence. Verify native Windows via an observed CI/user run before claiming that platform's full suite passes.

### S3-08 — real vision and evaluation readiness (Should, specification only)

Prepare a pluggable future vision-adapter contract, rights/processor checklist and evaluation protocol. Do not implement/activate a paid or remote adapter without a separately scoped development decision, documented provider/model capabilities, image inference rights, secure required credentials, retention/subprocessor terms and bounded cost/timeout behavior.

Future runs record actual model/provider, model version, prompt/template revision, schema version, source image hashes, timestamps, validation outcomes and limitations. Future output is schema-validated and cannot set auction identity, grant rights, execute tools, calculate finances or override safety gates. Training is separately denied unless explicitly licensed and scoped.

Use the consented repair cohort and blinded independent human adjudication for later visual accuracy, missed safety-critical findings and uncertainty evaluation. The 20+ cohort target is readiness evidence, not statistical sufficiency or an accuracy guarantee. Fixture/schema/UI tests prove plumbing only; they cannot prove damage-detection precision, calibrated confidence, real cost accuracy or market coverage. Choose metrics and thresholds after dataset/model review, without an invented launch percentage.

### S3-09 — customer/authorized photo ingestion (conditional follow-up)

Do not build this path merely because file upload is technically easy. A later scope must decide ownership/rights evidence, explicit image-to-listing binding, upload formats and decoded-size limits, metadata stripping, safe decoding, malicious files, storage access, retention/deletion, abuse limits and deployment isolation. A checkbox or vehicle ownership does not grant auction-photo copyright, AI transmission or training rights. Uploaded photos with unverified listing linkage remain unverified and cannot silently inherit a resolved VIN/event. Real authorized-provider ingestion also needs documented endpoints, destinations and per-use rights; existing disabled adapters stay disabled.

### S3-10 — business carryover, not completed by a preview

Track existing provider/licensing assessment, the authorized 50-link identity study, 20+ consented repair examples and five+ Georgian business interviews independently. Keep actual agreements, licensed datasets/photos, invoices, contact details and private linkage keys outside Git. Use the existing research templates; do not replace those activities with another synthetic report or invent current external findings.

## Proposed typed contracts and API decisions

Names below are internal recommendations to finalize in an implementation ADR, not a vendor SDK or a finalized public API. Keep existing resolver fields/outcomes compatible.

| Type | Minimum fields and invariants |
| --- | --- |
| `InspectionTarget` | Original reference; provider ID/mode; canonical identity; record/event IDs; stable content/version-based source snapshot fingerprint; nullable VIN; source timestamps/freshness. Server-derived from a corroborated snapshot, not a trusted browser object; request-only timing must not make an unchanged snapshot appear changed. |
| `PhotoAsset` | Asset ID, content hash, dimensions/MIME, view label/UNKNOWN, source kind `SELF_AUTHORED_FIXTURE`, origin/review reference, per-use permissions, target/scenario binding; capture time nullable. No arbitrary remote URL or local path from input. |
| `InspectionFinding` | Stable finding ID; `OBSERVED/SUSPECTED/UNKNOWN`; region/component when supported; description/rationale; severity including UNKNOWN; nullable confidence with basis; image IDs; optional verified localization; confirmation recommendation. Evidence must belong to this report. |
| `Localization` | Exact asset/hash and reviewed geometry; normalized finite box or polygon with bounded nonzero extent; `verified_by`/review basis. Null means show text/image reference only. Being numerically in bounds does not itself prove localization. |
| `InspectionProvenance` | Engine ID/version, mode `MOCK`, fixture/scenario revision, schema revision, generated-at, target/image digests; model/provider/prompt fields null for mock. Future AI fields describe actual runs, never invented placeholders. |
| `InspectionPreview` | Ephemeral request/report ID; target; eligible assets; findings; recommended checks; coverage/limitations; exclusions/reasons; provenance; outcome `COMPLETED/PARTIAL/BLOCKED/FAILED`. COMPLETED means mock workflow completed, never vehicle passed inspection or AI completed. |

Suggested synchronous operation: `POST /api/v1/inspections` with the reference URL and expected snapshot binding, returning `InspectionPreview` directly. Invalid/malformed input remains a clear 4xx; domain blocking preserves the original resolver outcome and distinct target-changed/rights/no-images/unsupported-scenario reasons. No GET/polling/job queue is required without persistent/asynchronous work; H's later endpoint sketches remain future options. Final status codes, response bounds and version-compatibility decisions belong in the ADR and tests.

## Demonstration and release checks

Before calling the slice done, a new reviewer can follow documented Linux and PowerShell commands, resolve the chosen Copart and IAAI examples, open the MOCK preview, select an image-linked observation, distinguish a suspicion from an unknown, and see the recommended physical check. They can then trigger at least missing images, wrong event/asset binding, unknown bytes and denied access, with no copied report or fake all-clear outcome.

| Gate | Required evidence / consequence |
| --- | --- |
| G3-A — offline story ready | Proposed contracts/scope reviewed, authored asset ownership/demo rights recorded, scenario/expected findings independently reviewed, testable examples and resource bounds chosen. PO/technical lead can resolve routine offline choices; unknown commercial rights do not block this path. |
| G3-B — offline slice done | Must stories implemented/reviewed; new and relevant regressions actually pass; report/image links and labels work; no unexpected network/model calls; safe failure/partial states and user commands verified; actual limits recorded. |
| G3-C — customer/remote images | Separate source/use rights, identity linkage, security, storage/lifecycle and user-experience scope accepted. Without them no upload, arbitrary URL fetch or licensed image integration is enabled. |
| G3-D — actual AI evaluation | Separately scoped adapter, selected model/docs, inference/processor rights, required secure credentials, operating bounds and consented evaluation evidence. Without them remain deterministic MOCK; no hidden AI fallback or claims. |
| G3-E — real-user pilot | Domain-reviewed safety wording, observed evaluation evidence/limitations, supported-source subset, rights/current operating checks and rollout/rollback owner. No production or safe-to-drive claim follows from mock completion. |

On a binding/hash/rights failure, block the affected asset/report or return an explicitly partial report from the remaining valid evidence. On an engine/contract failure, do not promote partial unvalidated findings to completed output. Re-enable affected use only after correction and relevant regression checks; do not switch engines or vehicles silently.

## Decisions and sequencing

Recommended sequence: agree S3-01/02 contracts and authored fixtures → implement the guarded mock preview → build the gallery/report/checklist → exercise failure states and regressions → record delivery separately from business/real-AI readiness.

PO and technical lead can choose the initial authored scenarios, synchronous wire details and bounded resource settings during development. The user/business owner still needs to assign the licensing/research/rights owners, choose a restricted evidence location, and decide when to scope real-image/AI evaluation. Brand, commercial model/vendor, localization timing, production storage and deployment are not silently selected here. There is no need for a paid API key or actual auction-photo license to build this authored MOCK preview.
