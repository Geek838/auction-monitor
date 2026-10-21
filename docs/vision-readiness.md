# Real vision activation and evaluation readiness

This specification satisfies Sprint 3's preparation story S3-08. It is based on the [handover](auction_intelligence_handover.md) M2 direction, [Sprint 3 requirements](sprint-3-requirements.md), and [provider contract](decisions/002-provider-contract.md). It does not choose a vendor/model, activate an API, grant image rights, or claim that any evaluation has run.

## Model-independent boundary

A future vision adapter receives only a server-validated exact inspection target and a bounded, use-permitted image set. The target includes canonical listing identity, provider record/event, source snapshot fingerprint and asset hashes. The adapter must not resolve or rewrite auction identity, select a similar vehicle, grant rights, execute tools or fetch arbitrary URLs. A changed target/image set invalidates the run's binding rather than silently reusing a report.

Output follows the typed inspection schema: supported visible observations, evidence-linked suspicions with confirmation steps, explicit unknowns, image references, limitations and qualified physical checks. Existing metadata `FieldEvidence.kind` is not the damage taxonomy. Metadata such as “Front End” does not by itself prove a visual observation. Model output is untrusted data and cannot bypass validation or introduce HTML, executable instructions, tools, financial calculations or authorization changes.

Localization is optional and independently validated. Numerically valid coordinates are not proof that a component was localized correctly. Uncertain localization falls back to the image reference and text; no fabricated full-image box or confident overlay is substituted.

For actual runs, record the real model/provider and model version, adapter version, prompt/template revision, output-schema revision, actual input asset hashes, target fingerprint, operation timestamps and validation outcomes. Preserve available source/photograph dates separately from report generation time. Mock provenance must remain MOCK, with actual model/prompt/provider fields null, and must never be rewritten as a real run.

## Separate activation gates

| Gate | Evidence required before activation |
| --- | --- |
| Input use and linkage | Authorized source; exact listing/image relationship; asset-specific retrieval/display/storage uses; source and observed/capture dates or explicit unknowns; current review/effective/expiry/revocation state |
| Inference rights | Explicit permission for transmission to the selected processor/subprocessors, inference and retention of inputs/outputs, applicable territory/audience and derived-data restrictions; unknown rights deny that use |
| Processor/model review | Current official API/model documentation, supported input/output limits, data retention/deletion and training terms, permitted destinations and appropriate technical/rights review; no guessed API or commercial availability |
| Secure operation | Required credential names and secure bindings if needed, approved service destinations, TLS verification, bounded input/decoded size, finite timeouts/retries and resource/cost budget, safe logs, sanitized errors and rollback owner |
| Evidence and quality | Rights-reviewed consented evaluation material, independent adjudication plan, outcome taxonomy and measured acceptance decisions; no production quality claim from synthetic output |
| Separately scoped rollout | Documented adapter implementation decision, supported subset, observed results, domain-reviewed safety wording, operating monitoring and disable/revocation process |

Inference and model training are separate uses. Neither photo-display permission, vehicle ownership nor a contributor checkbox establishes auction-photo copyright, processor transmission permission or training permission. Do not request secret values through a repository, report or chat; use secure environment settings.

## Failure and abstention behavior

Schema-invalid, conflicting, unsupported or unsafe outputs must not become a confident completed report. Fail the run or return only validated partial evidence with explicit exclusions. An absent photo or unknown condition does not mean no damage. A denied or failed real adapter must not silently return seeded mock findings; mock demonstrations remain an explicit independent mode.

Images, captions, EXIF/metadata and instructions appearing within them remain untrusted content. They cannot change the system's instructions, identity, permission checks or tool access. Test such hostile content as boundary/validation tests; do not call a synthetic hostile-caption test proof of resistance by an untested real model.

Structural integrity, SRS/airbags, ADAS, cooling, suspension and mechanical condition cannot be established from cosmetic appearance alone. Require uncertainty and appropriate professional inspection/diagnostics. Do not provide a safe-to-drive verdict, hidden structural certainty, exact invented OEM parts, unsupported repair/replacement conclusions or financial projections.

## Evaluation plan before accuracy claims

Use the separately consented, rights-reviewed completed-repair cohort with original auction evidence and itemized repair outcomes. The handover's 20+ examples are a collection/readiness target, not a statistically sufficient benchmark or a promised accuracy level. Preserve private evidence outside Git and apply the agreed retention, withdrawal and access rules.

Freeze a blinded holdout design before model/prompt tuning. Independent reviewers adjudicate findings against the permitted photo evidence and repair records, retaining disagreements, exclusions and cases that cannot be resolved. Distinguish truly invisible damage, incomplete invoices, repair quality and pre-existing defects from errors that visible evidence could have supported. Record cohort selection bias and the supported vehicle/damage/source subset.

Measure visible-finding precision/recall and critical missed categories; evidence-link correctness; unsupported-assertion and abstention rates; uncertainty calibration only where score meaning supports it; source/image completeness; latency and actual per-run resource/cost. Define denominators and report partial/failed/unrun cases separately. Choose thresholds only after the data and candidate model are reviewed; no launch percentage or provider choice is invented here. Repair/cost accuracy belongs to later separately scoped M3 work.

Seeded fixture tests establish contract, gallery and safety-gate behavior. They cannot establish real visual accuracy, calibrated confidence, mechanical reliability or production coverage. A real-user pilot needs observed results, qualified domain review and an explicit supported-scope decision.

## Customer-upload follow-up

Customer images require a separate agreed ingestion path: rights/consent and listing-linkage evidence, supported raster formats, malicious-file/decoded-size limits, safe decoding and metadata stripping, restricted access, storage/retention/deletion, abuse controls and deployment isolation. Unverified photos cannot inherit a resolved VIN/event merely because a user selected that listing. Training, public redisplay and external inference remain separately denied until granted and scoped. This specification does not implement that path or a storage/deletion service.
