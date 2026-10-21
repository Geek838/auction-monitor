# Provider assessment and licensing preparation

Implements S2-01; see [Sprint 2](../sprint-2-requirements.md) and handover §§1, 4 Phase 0, 11–14. No current external research or provider contact has been performed. Public availability and the handover's research references do not establish permission, a commercial API, or current capabilities.

## Initial comparison

All evidence-dependent cells intentionally remain Unknown. The alternative rows describe channels to investigate, not services claimed to be available to this project.

| Candidate/channel | Automated commercial metadata access | Copart exact lot lookup | IAAI stock/page mapping | Freshness and history | Image/AI rights | Pricing/quotas | Decision |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Bid.Cars candidate | Unknown | Unknown | Unknown | Unknown | Unknown | Unknown | Pending evidence; adapter disabled |
| Official or expressly authorized Copart channel | Unknown | Unknown | Unknown/not assumed | Unknown | Unknown | Unknown | Investigate eligible access |
| Official or expressly authorized IAAI channel | Unknown | Unknown/not assumed | Unknown | Unknown | Unknown | Unknown | Investigate eligible access |
| Other authorized provider, to identify | Unknown | Unknown | Unknown | Unknown | Unknown | Unknown | No selection made |

Business owner: **unassigned**. Rights reviewer: **unassigned**. Technical reviewer: **unassigned**. No recommendation to enable a provider can be made from this blank comparison.

## Assessment and evidence record

Complete a restricted working copy per candidate. Use evidence IDs in any shareable report, not contracts or credentials.

| Field | Required record |
| --- | --- |
| Assessment | Candidate/legal entity, assessor, review date, evidence IDs, status and confidence |
| Authority | Rights holder/authorization chain; written permission for this product's exact commercial use; effective/expiry dates; revocation/change mechanism |
| Lookup semantics | Supported houses/regions; exact lot/stock lookup; IAAI internal page-to-stock mechanism and evidence; permitted VIN search; leading-zero behavior; provider record/event identifiers |
| Fields and history | Available/null fields; active/sold/archived/relisted coverage; separate sale events; independent VIN/model corroboration; meaning of source/retrieval times |
| Separate uses | Automated metadata lookup/display; caching/retention; redistribution/derived outputs; photo retrieval/display/storage; AI inference/evaluation/training, each independently allowed/denied/unknown |
| Operation | Documented integration/auth method; credentials required if any; service destinations; sandbox; quotas/retries; schema changes; support; costs, with evidence |
| Lifecycle | TTL/retention ceiling if permitted; deletion/withdrawal/revocation and backup/derived-data handling; attribution and audience/territory limits |
| Decision | Go/conditional/no-go; unsupported use/house/region; remaining questions and owners; evidence review date; exact next action |

Use the following rights-evidence register in the approved private location:

| Evidence ID | Candidate | Claim or exact purpose | Allowed/denied/unknown | Authoritative document/reference | Scope/limitations | Effective/expiry/review dates | Reviewer | Next action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| _blank template_ | | | Unknown | | | | | |

Do not infer permission from a narrative `license_scope` string. A positive decision requires reviewable evidence and the implemented operation's checks. A metadata-only agreement may support a metadata pilot while images remain disabled; image rights never follow automatically from metadata rights, and inference rights never imply training rights.

## Draft questions for authorized future outreach

The business owner can adapt these after the outreach activity is authorized. This document sends nothing and names no actual recipient.

1. Which documented automated channel, if any, can you authorize for a commercial pre-purchase application serving buyers in Georgia? Which entity grants the rights? Can we obtain the permitted scope in writing?
2. Which auction houses, regions, states and historical periods are covered? Define lot, stock, internal page, provider-record and sale-event identifiers. Can IAAI VehicleDetail page references be explicitly mapped to stock numbers, with provenance?
3. Which documented operations support auction house plus exact lot/stock and permitted VIN lookup? How are missing, conflicting, duplicate-event and partial records represented? Request official documentation rather than suggest invented endpoints or prefixes.
4. Which metadata fields may be retrieved, displayed commercially, cached, retained, shared or used in derived outputs? What territory, audience, attribution and onward-use limits apply? Is metadata-only access possible?
5. Separately for each photograph: who has authority to license it, and may we retrieve, thumbnail/display, store, archive, evaluate, transmit for named AI-subprocessor inference, retain outputs or train models? Which uses are prohibited or separately licensed?
6. What cache TTLs, maximum retention periods, deletion/revocation obligations, backup/derived-data rules and audit conditions apply? How are removed assets and rights changes communicated?
7. What does each timestamp and auction state mean? Is the feed historical or live, with what evidenced freshness/completeness guarantees? Can relistings and multiple sale events be distinguished?
8. What authentication, credentials if required, sandbox, service destinations, rate limits, supported retries, availability/support, pricing and change notification are documented? How are permission denial, absent data, throttling and service failures distinguished?
9. Can authorized samples and independent ground truth be retained for the 50-link identity study? What publication/redaction limits apply to case details versus aggregate results? No image or AI rights are presumed by that study.

## Decision review

Recommend only the supported subset with evidence. Reject guessed identifiers and technically accessible but unlicensed sources. If identity or rights remain unknown, record a conditional/no-go and keep the affected real-provider operation disabled. A credential or configuration switch is not authorization. A provider decision does not authorize a public pilot; the identity study, safe-operation checks and rollout decision remain separate.
