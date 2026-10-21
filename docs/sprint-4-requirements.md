# Sprint 4 — private photo-evaluation intake

Status: **PO proposal for selection, not implementation or activation**, prepared 21 October 2026. The user called the next increment “Sprint 3”; Sprint 3 is already delivered at `a465e93`. This document provisionally names the next increment Sprint 4. Scope decisions below must be settled before the dependent work starts.

## Recommendation and evidence

The user has confirmed **neither an AI API nor permitted vehicle photos is available yet**. Build a small, runnable **local photo-evaluation intake tool** now: validate private cases, safely prepare permitted pixels, produce an inspectable readiness artifact and explicitly report missing rights/model inputs. Use the same boundary for a separately selected real-model adapter once actual inputs and access exist. This advances the ingestion prerequisite with executable behavior rather than another template-only sprint. Do not spend another sprint adding seeded findings or cosmetic demo scenarios, and do not jump to repair prices, taxes or maximum bids while their inputs remain unsupported.

This is a technical evaluation increment, not a production inspection feature. It deliberately has no public upload endpoint, account system, job queue, report database or new customer-facing workflow. An intake success means its selected local preparation steps completed; it does not mean a model ran. A later successful model call means valid experimental output was received; it does not establish vehicle condition, inspection accuracy, qualified review or readiness for buyers.

| Evidence reviewed | What it establishes |
| --- | --- |
| [Handover](auction_intelligence_handover.md), read in full, §§4–10 and 12–13 | Product direction: exact auction identity; authorized photos; evidence-linked M2 findings and uncertainty; evaluation before accuracy claims. M3 prices and M4 bids come later. Model/provider and image rights remain open decisions. |
| [Sprint 3 delivery](sprint-3-delivery.md) and [test report](sprint-3-test-report.md) | Authored MOCK preview is delivered; recorded 317 backend and 86 browser passes. These are inherited results, not rerun for this PO document. No real model, licensed provider or actual inspection exists. |
| [Vision readiness](vision-readiness.md) | Existing activation/evaluation specification already describes the gates. Sprint 4 should execute a selected slice rather than create another readiness-template pack. |
| Current `app/inspections/{engine,models,service}.py` and web `inspection-types.ts` | Engine is intentionally tied to registered authored scenarios. Provenance accepts MOCK only, model fields are null-only, images are self-authored PNG only. These contracts cannot truthfully represent a real model run merely by toggling an environment variable. |
| Current authored manifest and [provider contract](decisions/002-provider-contract.md) | Existing illustration permissions deny AI inference/training. Display permission and metadata permission do not authorize transmitting images to a model. |
| [Sprint 2 delivery](sprint-2-delivery.md) and [research pack](research/README.md) | No documented real provider agreement, executed identity study, accepted repair examples or completed interviews. Existing preparation does not establish those results. |
| User's Windows startup report | Startup failed because Pillow was missing; dependency-refresh commands were supplied, but a successful restart was not reported. The traceback used Python 3.14; the tested setup is Python 3.12. No claim that native Windows checks passed follows from that report. |

**Authority distinction:** The user's request authorizes PO planning and subsequent selected development. The handover supplies product requirements, not permission to scrape, contact businesses or spend money. The local evaluation route, limits and story breakdown here are PO proposals, not commitments already present in the handover. No external provider/model research, outreach, image collection or paid inference was performed for this document.

## Current recommendation and minimum next decisions

Proceed with the ready-to-code intake subset below without buying API access. For later real inference, resolve three concrete items; do not request secret values in chat or Git:

1. **Model route:** choose one actual vision provider/model with available API access, or choose an explicitly supported local model. For a remote model, identify current official API/model documentation and review input/output support, retention/training terms and permitted destinations. An API key alone does not settle image-use rights. No vendor or model is selected by this proposal.
2. **Input route:** identify at least one image set lawfully permitted for the selected processing/evaluation use, with an owner/reviewer and private evidence location. Prefer genuinely self-owned, permission-reviewed vehicle photos for the first technical run; do not download auction images or infer copyright from owning the car. If none exists, obtaining eligible material is a dependency, not an excuse to label seeded output real.
3. **Run bounds:** select private local execution and an explicit maximum pilot spend/call budget for a paid service, plus where private inputs/outputs may be kept and when they must be deleted. For a local model, agree compute/runtime limits and local storage instead. A qualified reviewer is needed before substantive damage-quality conclusions or any buyer pilot; the developer can assess technical transport/schema behavior only.

Recommended default operating mode is a single developer machine with no inbound service. **Immediate non-coding next step:** the product owner/user identifies one genuinely self-owned or expressly licensed vehicle photo set and a rights reviewer; record its allowed local preparation/evaluation uses privately. Do not buy or scrape an auction-image set as a shortcut. Once that set exists, compare current official documentation for a small number of actual model candidates and choose one, its retention terms and a bounded trial budget. No provider is selected or researched by this document. There is no inference activation while required rights/model/budget choices are unknown.

## User job and evaluation flow

The immediate user is the product/development evaluator: “Can a real model produce useful, image-supported observations, and where does it abstain or fail?” The buyer's original URL-to-exact-vehicle job remains the eventual integration target.

**Ready to code now:** steps 1–2, safe preparation under local-use permission, and a local readiness report. Steps 3–5 are conditional follow-up; missing model selection must not prevent local validation, and missing inference rights must block dispatch while permitting only separately granted local uses.

1. Prepare a private local case manifest and bounded local raster images with actual permission/review evidence. The operator invokes a CLI, initially in **validate-only** mode.
2. Validation reports accepted/excluded inputs, actual prepared-byte counts, current use permissions, configured limits and the model-selection state (explicitly not selected today). It does not estimate model cost or imply a dispatch occurred. No validation step makes a network call or creates model findings.
3. A separate explicit run command sends only the accepted image pixels and the fixed task to the chosen adapter. No URL fetching, general tool execution or instructions from image captions/EXIF are allowed.
4. Validate the actual response and record success, partial output, blocked input or failed call distinctly. Never fall back to seeded findings. The report is **EXPERIMENTAL / UNREVIEWED** until a qualified human separately assesses its claims.
5. Review evidence links, unsupported claims, missed visible features, uncertainty, latency and actual reported resource use. Produce a private machine-readable result and readable local report. Publish only permitted synthetic examples or reviewed aggregates to Git.

A standalone evaluation case is **not an exact-matched auction listing**. A filename, pasted auction URL, operator-entered VIN, photo caption or manifest checkbox cannot create `MATCHED` status. If listing linkage is unavailable, label it **UNVERIFIED / standalone photos** and omit verified listing identity. Never display real photos under a fictional fixture listing. Future integration into URL resolution requires a separate authorized metadata/image channel and independent listing/event linkage; it is not part of this sprint.

## Selected-slice backlog

| ID | Priority | Deliverable | Dependencies / owner |
| --- | --- | --- | --- |
| S4-01 | Must | Explicit readiness/status contract, current missing-input state and concrete next owner actions | Product + technical lead; no model or access invented |
| S4-02 | Must | Private case manifest, local validation and safe image preparation | Backend; per-use rights/storage supplied at execution |
| S4-03 | Must / conditional | Separate experimental output contract now; one real adapter only after selection | Backend; real adapter needs model/limits decision |
| S4-04 | Must | Explicit validate/prepare commands and private readiness report; real run command remains disabled | Backend + UX/copy; S4-02 |
| S4-05 | Conditional | Actual real-image/model smoke run and honest evaluation findings | QA + technical lead; eligible inputs and selected model access |
| S4-06 | Must | Regression, adverse-condition tests and Windows instructions | QA + developers; all technical stories |
| S4-07 | Conditional follow-up | Connect authorized real listing/photo data to the buyer UI | Actual provider/image contract, independent linkage, domain review and separately selected scope |
| S4-08 | Carryover business | Real provider decision, 50-link identity study, 20+ repair examples, five+ interviews | Business/research owners; existing protocols, not this coding slice |

### S4-01 — explicit readiness and later selection

- The runnable local workflow distinguishes local validation/preparation permission from inference readiness. Its report lists missing photo/use evidence, model selection, credentials and budget independently, without requesting secret values or displaying a usable analysis action. Do not require nonexistent model credentials just to validate a local manifest.
- Conditional adapter selection record: record the actual chosen model identifier/version semantics, provider, official documentation URLs and review date; supported image formats, structured-output mechanism, request/response limits and known operational restrictions.
- Record what permissions cover local processing, external inference if used, private evaluation/report retention and allowed reviewers. Training remains separately denied unless explicitly granted and separately scoped. Do not copy private contracts or personal data into Git; use opaque evidence references.
- Before real activation: record maximum calls/spend or local compute bounds, timeout/retry policy, deletion/retention owner and stop/disable mechanism. Paid activation stays disabled without explicit budget and credentials securely supplied through environment settings/local ignored configuration.
- In the conditional real-model increment, choose exactly one adapter. Do not build multiple vendors, a generic orchestration framework or an arbitrary caller-controlled API base URL. Local-model support is not implemented automatically if the user selects a remote service, or vice versa.

### S4-02 — reviewed local inputs without an upload service

- Accept a versioned private case manifest and local files only, through the operator CLI. Validate opaque case/image IDs, nonblank provenance/rights references, review/effective/expiry/revocation state and use-specific permissions before preparation and again before any later dispatch. Explicit local preparation/private-display permission is required for those uses; inference may remain denied independently. Unknown or revoked inference use blocks transmission.
- Reject remote URLs, data URLs, arbitrary filesystem traversal, symlink escapes, duplicate IDs, unlisted files and archives. Resolve all inputs under the selected case root; do not scan unrelated folders. A manifest is an operator review record, not a license generator or independent identity proof.
- Decode actual JPEG/PNG pixels with the maintained image library, not extensions/MIME claims; reject executable formats, animation, corrupt/truncated files and over-limit inputs. Remove EXIF/GPS and embedded metadata from transmitted copies; do not send original filenames, case notes, VINs, source URLs or repair invoices unless a separately reviewed model task requires them (none is proposed here).
- Proposed engineering bounds: six images per case, 64 KiB manifest, 8 MiB per original file, 24 MiB total input and 20 million decoded pixels per image; normalize to at most 2048 pixels on the longest side and respect any smaller selected-model limit. These are product engineering proposals, not invented provider limits. Record original and normalized hashes, dimensions and transformation revision; bind findings to the actual normalized bytes sent.
- No public HTTP ingestion, persistent shared upload store, automatic photo harvesting or customer consent UI is added. Private originals and generated artifacts remain outside Git. The operator specifies a private output root and reviewed retention policy. The tool records expiry where applicable and provides scoped cleanup for its generated files; it never deletes originals or promises deletion of externally copied files. No default retention period is invented.

### S4-03 — separate experimental contract now; real adapter after selection

- Ready now: introduce an experimental contract separate from `InspectionPreview`/`MockInspectionEngine`. Reuse validated taxonomy concepts where sensible, but do not weaken MOCK literals, change fixture permissions or retrofit fabricated model provenance into existing seeded reports.
- Conditional on a selected model: the adapter receives validated prepared pixels/IDs and a fixed versioned task. It cannot resolve auction identity, grant permissions, invoke tools, browse or fetch URLs. Image text/captions remain untrusted content. Prompt-only resistance is not treated as a guarantee.
- Validate strict bounded output: at most 30 findings; OBSERVED/SUSPECTED require existing image references and supporting rationale; UNKNOWN has explicit gaps/confirmation. Reject extra financial, OEM-part, safety-verdict or invented verified-identity fields. Confidence remains null unless a later evaluated meaning is agreed; do not rename a model's self-rating “calibrated confidence.”
- No localization overlays in this increment: retain image references and textual regions. A model box is not verified localization. Structural integrity, SRS, ADAS, cooling, suspension and mechanical function remain explicitly unknown without relevant physical/diagnostic evidence.
- Actual provenance records provider/model as reported, adapter/prompt/schema revisions, actual input digests, timestamps, validation outcome and usage where genuinely supplied. Unknown usage stays unknown; do not invent dollar amounts or API return fields.
- Known unsafe assertions and invalid references fail validation, with sanitized reasons. A narrow phrase filter cannot establish natural-language safety: every accepted run remains experimental/unreviewed and requires human evaluation. Never supply an all-clear summary or claim absence of hidden damage.
- One bounded request per invocation by default; no automatic retry unless the selected budget explicitly covers it. Enforce finite provider timeout and response-byte/output limits, TLS verification for remote APIs and cancellation/termination where the chosen runtime supports it. Failures do not silently select a different model or return mock findings.

### S4-04 — inspectable local artifacts

- Provide separate validate/prepare commands now, documented for PowerShell and Linux; a real run command is enabled only in the conditional adapter increment. A run attempt with no selected adapter returns a clear blocked reason and makes zero network calls. Missing credentials, invalid case, denied use, timeout, unavailable model, invalid output and empty findings have distinct exit/status reasons; logs contain no secret values, photo payloads or unrestricted source/model content.
- Write machine-readable intake results and a readable local report showing permitted prepared images, provenance, exclusions, actual bytes/digests and readiness blockers. Do not show seeded findings in this report. The conditional model increment additionally shows validated evidence-linked findings and physical-check unknowns. Use escaping and local asset references; no external scripts/fonts/requests or executable returned HTML. The artifact cannot send photos to a third party on opening.
- Clearly separate run status from review status: e.g. `VALID_OUTPUT` is not `DOMAIN_REVIEWED`. Partial/excluded images and failed runs remain visible. No fake latency, quality or success counters. Do not claim reliable cancellation or remote deletion if the API provides no such guarantee.
- Keep all generated output under the explicitly selected private output root; refuse accidental output into tracked source locations by default. Do not overwrite original inputs. Do not publish or add real artifacts to Git as a convenience.

### S4-05 — first actual evidence and evaluation

- Execute at least one permitted real-image run only after the agreed model/input/budget decisions are met. Record what actually ran, any excluded images, exact model/provenance and technical behavior. If it cannot run, retain a blocked status with the concrete reason.
- Compare outputs with the permitted visible evidence: evidence-link correctness, unsupported visible/hidden claims, useful abstention, missed plainly visible features and failure handling. A developer checks technical behavior; damage-quality adjudication needs a qualified reviewer, with disagreements and unknown ground truth preserved.
- Add varied cases as eligible material exists: limited/occluded views, no clear visible damage and different damage regions. Do not fabricate cohort size or treat one smoke case as a benchmark. Repair invoices/ground truth stay withheld from the model when evaluating first-pass image findings.
- For future model comparison, use the same rights-reviewed cases/preprocessing and blinded human reference judgments; compare visible-finding precision/recall, critical misses, evidence correctness, unsupported claims, abstention, latency and actual usage. Define denominators and supported subset before claiming results. No vendor ranking or launch threshold is invented before real evidence exists.
- Record a concrete recommendation: continue, revise or stop, with observed defects and missing evidence. The handover's 20+ repair examples remain a future collection target, not an achievement of this smoke run. A buyer pilot and accuracy claim remain out of scope.

### S4-06 — tests and reproducible review

- Preserve the existing parser, exact identity, mode/permission, freshness, authored preview and browser regressions. No real inference or network dependency is added to routine CI; use a deterministic transport test double only to test the selected adapter's request/response contract, clearly labeled as such.
- For the ready-to-code slice, test valid/denied/expired/revoked cases, traversal/symlink escapes, invalid/corrupt/oversized images, metadata stripping, original-versus-prepared hashes, readiness blockers, hostile text escaping and safe cleanup. Verify validate-only makes no network call and blocked cases cannot dispatch. Experimental-contract tests cover strict output/dangling references and known unsafe assertions; no generated model findings are implied.
- In the conditional adapter increment, additionally test bounded timeouts/responses, credential errors and no seeded fallback. Verify the remote adapter sends only to the reviewed fixed destination, or that the selected local runner has no network tool path. An unexpected URL/image field cannot change destination. Tests must not include real secrets/private photos.
- Verify changing original or prepared pixels/permissions after validation invalidates preparation/dispatch or requires revalidation. Intake artifacts retain the prepared-image digest they actually describe; later model reports must retain the digest of the actual request, never a replacement image.
- Update stale `docs/source-integrations.md` wording to distinguish the delivered local authored preview from absent remote photo access. Document fresh Python 3.12 dependency install, startup/check commands and the tool's Windows invocation without `make`. Claim native Windows support only after an observed Windows run/CI result, not merely cross-platform-looking paths. Report actual test counts and build/typecheck results, not inherited Sprint 3 totals.

## Architecture and sequencing

Prefer a small `services/api/app/vision_evaluation/` module with case validation, preparation, selected adapter, output validation and CLI/report writer, plus focused tests and one decision record. This path is provisional; developers can choose a simpler equivalent. Do not add a server, database, queue or upload API solely for the evaluator. Keep real adapter dependencies optional if they are unnecessary for the existing offline application.

Sequence now: implement readiness/case/preparation/report contracts → test successful local preparation, exclusions and blocked inference with explicitly synthetic engineering fixtures → document actual local results and missing input/model evidence. Conditional next: obtain permitted real inputs → select model/terms/budget → implement exactly one real adapter with transport doubles → execute adverse tests → perform the explicitly budgeted smoke run → record S4-05 evidence and any qualified review. Synthetic engineering fixtures test plumbing; they are not an accepted real vehicle cohort and their local-use permission must not silently become inference permission. An independent QA review should challenge the identity boundary and untrusted-output behavior before external inference is activated.

Source integration remains a parallel prerequisite to the eventual buyer feature. A real-photo evaluator does not make the existing URL resolver live. It is preferable to prove the vision contract on a small lawful standalone set than to attach real findings to fictional metadata or quietly build an unauthorized scraper.

## Definition of done and exclusions

The proposed ready-to-code Sprint 4 slice is complete when the local validate/prepare/report tool runs, success/exclusion/denial paths are reproducible, tests pass and Windows commands are documented, with inference explicitly blocked when no selected adapter/input rights exist. Reviewers can inspect normalized images and their actual digests without any network call or fabricated findings. Report this as **photo intake/preparation delivered; real vision not implemented or executed**. The conditional real-vision objective is complete only after a selected real adapter and an authorized actual run exist; test-double output is never a successful inspection.

No buyer launch, real-data coverage/accuracy claim or qualified vehicle verdict follows from technical completion. Connecting into the product UI needs independent listing/event evidence, source/image-use authorization, domain-reviewed output and separately selected rollout scope. Existing MOCK and SIMULATED labeling stays intact.

Excluded: public uploads, arbitrary remote image fetching, scraping, auction/provider integrations without documented access, new seeded demo scenarios, production deployment, accounts, payments, saved reports, repair/landed-cost estimates, Georgian tax rules, price quotes, maximum bids, automatic localization, model training and external business outreach. Georgian localization is a future explicit choice, not assumed here.
