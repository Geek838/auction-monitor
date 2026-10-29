# Version 1.0 readiness

Working release assessment, **29 October 2026 (Asia/Tbilisi)**. The client asks the team to proceed toward 1.0 without paid APIs. The [handover](auction_intelligence_handover.md) is the source of product direction; its own “Version 1.0” identifies the document, not a claim that software 1.0 exists.

## Release outcome

The intended buyer outcome remains: paste an original Copart/IAAI URL, establish the exact auction listing and vehicle, inspect permitted photo evidence with explicit uncertainty, assess supported Georgia-specific acquisition/repair costs and derive a defensible bid limit where evidence permits. A manual review or a mathematically correct planning calculator is useful progress toward this outcome, but does not silently replace it.

No numeric completion percentage is used here: code coverage, mock scenarios and passed transport tests do not measure commercial access, visual accuracy or cost-estimation reliability. Statuses distinguish delivered baseline, work in progress and missing external/product evidence.

## Evidence-based status

| Capability / release evidence | Current verified state | Remaining evidence or completion boundary |
| --- | --- | --- |
| Safe original URL parsing and conservative identity engine | Delivered for local synthetic fixtures | Existing parser/provider/IAAI-page/stock/event regressions remain passing; no change weakens MATCHED semantics |
| Real exact auction lookup | Not delivered | A documented free/permitted channel, actual supported lookup/mapping, independently corroborated identity and an authorized live validation set |
| Auction-source and photo use scope | Narrow authored-demo permission only; user photo permission is a declaration | Actual source rights for commercial metadata/photo display, any processing, storage and lifecycle uses; user selection cannot manufacture rights |
| Manufacturer VIN enrichment | Real free [NHTSA vPIC integration](free-vin-data.md) implemented and live-smoked | Source metadata is not auction/history/physical identity verification; partial errors and explicit application remain visible |
| Authored inspection preview | Delivered MOCK workflow | Maintain accurate labels; no seeded findings for unknown or real user photo bytes |
| Manual vehicle evidence review | Delivered as USER-SUPPLIED / UNVERIFIED | Originally delivered with [371 backend and 142 browser passes](sprint-4-test-report.md); inherited checks were rerun within the current 520/194 suite. Browser-only manual photos and unverified reports remain unchanged. |
| Actual image analysis | Optional local adapter implemented and executed on owned engineering images; not a vehicle-quality benchmark | Installed/documented supported model, permitted inputs, actual run provenance and response validation; no fixture fallback or tool/URL execution from image content |
| Local-only vision option | Implemented; real CPU runtime/model smoke recorded in [model evidence](local-model-smoke.md) | Actual model/license and hardware limits, bounded local transport, permitted input handling, executed smoke evidence and honest availability/error behavior |
| Damage quality and safety | No real model benchmark or qualified mechanical review | Domain-reviewed fixed wording and blinded real evidence evaluation, visible-finding correctness, unsupported assertions, critical misses, abstention and supported subset |
| Deterministic budget planning | Implemented; [520 backend / 194 browser checks](v1-increment-test-report.md) pass across this increment and inherited functionality | [Budget requirements](v1-budget-requirements.md), decimal-safe ranges, coverage/evidence states and meaningful executed backend/browser tests |
| Georgian repair-price estimation | Not delivered | Dated compatible part quotes, labor records and repair outcomes; calibrated ranges and measured error, not merely user-entered totals |
| Official landed-cost calculation | Relevant [official rules retrieved](georgia-cost-evidence.md), but automatic tax calculation is not implemented/validated | Current authoritative Revenue Service/fee evidence, vehicle-specific registration/re-export treatment, validated schedules and explicit assumptions |
| Bid intelligence | Conservative fee-aware indicative planning ceiling implemented; market/pricing evidence remains user-declared | Fee-dependent solver plus reliable local value/non-bid evidence and missing-data abstention; an unverified planning ceiling is labelled accordingly |
| USD/GEL conversion | Not delivered | Dated rate source, exact conversion/rounding semantics and source-age handling; no invented rate |
| Packaging and platform operation | Local Linux prototype checks recorded | Repeatable installation/start, current full checks, documented limits, observed native Windows/CI results and the actual chosen release channel |
| Real-user/pilot readiness | Not established | Permitted data, domain-reviewed safety wording, evidence of supported accuracy/coverage and actual user workflow validation |

Record newly executed results in the increment's delivery/test report and then update these rows. Do not mark model execution complete from a test double, record current provider access from historical research, or infer native Windows success from cross-platform-looking code.

## Work delivered and owned next steps

1. Delivered the user-supplied budget scenario and conservative fee-aware ceiling without buying a source or inventing pricing.
2. Implemented and exercised a bounded optional local vision path, with actual model documentation, weight licensing and CPU runtime evidence. Output quality remains experimental, separately from transport success. Explicit opt-in must distinguish any image transmission to a local analyzer from the existing browser-only manual workflow.
3. Preserve user-supplied/fixture/model/provider provenance separately, keep old results invalidated after edits and retain safe failure states.
4. Keep the source-access work with the PO and technical lead. The [22 October review](research/provider-selection-2026-10-22.md) found no ready free authorized auction provider in its bounded shortlist; it does not prove none exists. Contact drafts remain unsent and no contract/account is assumed.
5. Publish code, current execution evidence and runnable commands, with release claims matching what actually ran. No paid API, silent trial charge or unauthorized scraping is a fallback.

Local inference has no paid API bill, but still uses device/storage/compute resources and depends on a model's actual terms and quality. A working local model does not independently identify which auction a photo belongs to or establish structural/mechanical condition. A user-entered quote or VIN does not become independently verified because the application stores or calculates it.

## What still prevents a full 1.0 claim

- No established zero-cost authorized original-auction lookup and photo channel has been demonstrated. The core pasted-URL flow cannot be advertised as live until one works with exact identity evidence.
- No validated real visual-inspection/repair-outcome cohort or automotive-domain quality assessment exists. Local transport/schema tests alone cannot supply this.
- No authenticated Georgian parts/labor/market-value cohort supports automatic repair/value estimates. Official import rules are now sourced, but their full classification, exemptions, effective-date, currency and fee matrix has not been implemented and validated. The calculator states only what follows from declared inputs.
- Real release operations and user validation must be observed, including the supported Windows installation/run path and any actual public deployment. This file does not deploy a service or establish a user pilot.

The team owns research, implementation, test execution and packaging. External agreements, third-party replies, missing runtime access and qualified review are dependencies to report concretely, not research assignments to the client or reasons to substitute fabricated data. No message, purchase or contract acceptance is authorized by this checklist itself.

## Scope choices

English first is consistent with the handover's M2 sequence. Georgian localization, saved comparisons/history, dealer batch work, accounts, payments and monetization are later product increments unless specifically selected; their absence must be disclosed rather than automatically equating every handover idea with a first-release blocker. None compensates for missing exact identity, meaningful evidence or truthful financial output.

Until the core evidence and validation gates are met, describe deliveries by their actual capability (manual review, budget planning, optional experimental local analysis). Do not rename a constrained fallback “finished automatic Auction Intelligence 1.0”.

## Delivered increment evidence

The [execution report](v1-increment-test-report.md) records 520 passing backend tests and 194 browser checks, plus production build/typecheck. Actual [free VIN service](free-vin-data.md) and [local inference](local-model-smoke.md) runs are separate from routine transport doubles. No API purchase, subscription or secret key was required. No real auction-source or qualified automotive benchmark claim follows from these results.
