# Consented repair-cohort preparation

Implements S2-07 and handover §§10–11. Goal: **20+ eligible completed-repair vehicle examples**, with original auction photos and itemized post-repair invoices, for a later separately scoped evaluation. This work has collected **zero** examples. It performs no photo ingestion, model inference/training, damage analysis or cost estimation.

## Eligibility and private manifest

Use [the header-only manifest](repair-cohort-template.csv) in approved restricted storage. Keep original invoices, images, identity/VIN keys and consents outside Git. Separate the identity key from pseudonymous case data. Document who can access each location; minimize fields and redact contributor/customer identifiers and unrelated financial details before evaluator access.

An accepted case needs all of the following:

- A stable pseudonymous case ID and rights-reviewed listing/vehicle/event linkage. Keep IAAI page and stock distinct; record linkage confidence and independently reviewed evidence. Do not assert linkage when it is uncertain.
- Original auction-photo provenance, asset-specific rights evidence, exact allowed evaluation uses, and any attribution/retention restrictions. A contributor who owns a vehicle may not own its auction photographs.
- Itemized completed-repair evidence: invoice date/currency, parts/labor/operations and known gaps, completion evidence and reviewer. An incomplete bill cannot prove every repair or hidden defect; record gaps and potential selection bias.
- Separate consent/authority for sharing the invoice, storing the supplied material, note-taking/contact, and any future evaluation use. Photo display, archive, transmission to an AI processor, inference and training are distinct rights. Unknown rights deny that use.
- An owner, permitted access list, withdrawal/deletion route, applicable expiry/retention policy and review date. No invented default retention duration.

Use `AWAITING_EVIDENCE`, `ACCEPTED`, `EXCLUDED` or `WITHDRAWN` with reasons. Cases missing photo rights are not eligible for image evaluation; record them as awaiting/excluded rather than inflate the accepted cohort. A case accepted for one purpose is not automatically cleared for another.

## Draft contributor explanation and consent checklist

This is a preparation checklist for rights/privacy review, not a finalized consent form or a substitute for the actual asset owner's permission. Complete organization/owner, purpose, storage location, access, retention and withdrawal details before recruitment. No outreach or signatures have occurred here.

Suggested plain-language explanation: “We are preparing research on how auction evidence compares with completed vehicle repairs. Participation is voluntary. We would like to understand which records you can lawfully share and for what specific uses. The prototype currently resolves listing identity; it does not perform an AI inspection or give a repair estimate.”

Record decisions separately, with evidence and date:

| Item | Capture before use |
| --- | --- |
| Contributor authority | What the contributor owns or is authorized to share; restrictions; evidence reviewer |
| Invoice/material sharing | Specific records/purpose, redactions, permitted viewers and storage; no blanket reuse assumption |
| Photo rights | Rights holder/chain, specific assets and permitted uses; do not rely on vehicle ownership or invoice consent |
| Future AI/evaluation | Distinct inference/evaluation/training and subprocessor permissions; these activities are not executed in Sprint 2 |
| Privacy and withdrawal | Voluntary nature, contact route, access and retention policy, withdrawal consequences, deletion/retention obligations and verification |
| Publication | Separate explicit scope, if any; no raw case/invoice/photo publication assumed; aggregate reporting still reviewed |

Any collection should use the minimum evidence needed and the agreed transfer channel. Do not request credentials or ask contributors to send sensitive records through a public repository or issue.

## Future evaluation readiness and holdout plan

Reserve evaluation roles and a blinded holdout design before later model tuning. Keep outcome invoices/repair labels hidden from any future first-pass inspection when assessing generalization; the exact split is an explicit future evaluation decision, not an invented quota here. Record vehicle/model/damage selection bias, repair quality, missing operations, unknown pre-existing defects and invoice completeness. No accuracy metrics are produced from this preparation.

Report cohort counts by accepted/awaiting/excluded/withdrawn and rights/quality reason. Twenty rows without eligibility review are not twenty accepted examples. The distinct 50-link identity study cannot replace this cohort.
