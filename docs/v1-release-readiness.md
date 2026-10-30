# Version 1.0 readiness

Working release assessment, **30 October 2026 (Asia/Tbilisi)**. The client asks the team to proceed toward 1.0 without paid APIs. The [handover](auction_intelligence_handover.md) is the source of product direction; its own “Version 1.0” identifies the document, not a claim that software 1.0 exists.

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
| Damage quality and safety | No real model benchmark or qualified mechanical review; an [offline evaluation-accounting tool](vision-evaluation.md) and synthetic self-tests are implemented | Domain-reviewed fixed wording and blinded real evidence evaluation, visible-finding correctness, unsupported assertions, critical misses, abstention and supported subset. Accounting/hash validation is not an automotive quality score. |
| Deterministic budget planning | Implemented; [520 backend / 194 browser checks](v1-increment-test-report.md) pass across this increment and inherited functionality | [Budget requirements](v1-budget-requirements.md), decimal-safe ranges, coverage/evidence states and meaningful executed backend/browser tests |
| Georgian repair-price estimation | Not delivered | Dated compatible part quotes, labor records and repair outcomes; calibrated ranges and measured error, not merely user-entered totals |
| Official landed-cost calculation | A restricted current-2026 [excise component](georgia-excise-component-requirements.md) is implemented from primary law and seven actual official calculator cases; total clearance is withheld | Remaining import duty/VAT treatment, exemptions/procedures, agency fees, registration and full landed-cost coverage require separate validation. Excise does not complete the clearance budget. |
| Bid intelligence | Conservative fee-aware indicative planning ceiling implemented; market/pricing evidence remains user-declared | Fee-dependent solver plus reliable local value/non-bid evidence and missing-data abstention; an unverified planning ceiling is labelled accordingly |
| USD/GEL conversion | Official NBG reference adapter and `/exchange` UI implemented. On 31 October 2026, a strict no-redirect live API smoke converted USD 100 to GEL 259.92 using the official 2.5992 rate effective that day. Earlier source denial/redirect responses remain evidence of intermittent availability. | The official feed is requested for the current Georgia calendar day; previous effective days are labeled and stale/future rates withheld. Preserve indicative-rate meaning and explicit availability limits. |
| Packaging and platform operation | [PowerShell launchers and bounded checks](release-operations.md) pushed in `0c4d88c` and `41b50a2`; clean Linux installation and checks passed. Hosted Windows setup/parsing passed, but hosted test execution/reporting remains unresolved | Record completed Linux/Windows job results, actual Windows startup and public deployment separately. A requested cancellation or configured workflow is not a passing run. |
| Real-user/pilot readiness | Not established | Permitted data, domain-reviewed safety wording, evidence of supported accuracy/coverage and actual user workflow validation |

Record newly executed results in the increment's delivery/test report and then update these rows. Do not mark model execution complete from a test double, record current provider access from historical research, or infer native Windows success from cross-platform-looking code.

## Work delivered and owned next steps

1. Delivered the user-supplied budget scenario and conservative fee-aware ceiling without buying a source or inventing pricing.
2. Implemented and exercised a bounded optional local vision path, with actual model documentation, weight licensing and CPU runtime evidence. Output quality remains experimental, separately from transport success. Explicit opt-in must distinguish any image transmission to a local analyzer from the existing browser-only manual workflow.
3. Preserve user-supplied/fixture/model/provider provenance separately, keep old results invalidated after edits and retain safe failure states.
4. Keep the source-access work with the PO and technical lead. The [30 October review](research/free-auction-provider-review-2026-10-30.md) adds MarketCheck as a documented auction-API/free-tier candidate beyond the [earlier shortlist](research/provider-selection-2026-10-22.md). Exact Copart/IAAI coverage, page-to-stock mapping, endpoint billing and this product's allowed commercial/photo/inference use remain unestablished; no account, query or integration is claimed. This bounded review does not prove no suitable supplier exists. Contact drafts remain unsent and no contract/account is assumed.
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

The [earlier execution report](v1-increment-test-report.md) records 520 backend and 194 browser passes. The [current report](v1-next-test-report.md) records the additional connected workflow, exchange, excise, evaluation and operation checks. Actual [free VIN service](free-vin-data.md), [local inference](local-model-smoke.md) and [official RS calculator observations](georgia-excise-component-requirements.md) remain separate from transport doubles. No API purchase, subscription or secret key was required. No real auction-source or qualified automotive benchmark claim follows from these results.
