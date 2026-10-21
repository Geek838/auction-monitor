# Exact-listing identity feasibility study

Implements S2-06 and handover §10. This is a prepared protocol, not an executed study. **No real links have been evaluated in this work.** [The synthetic rows](identity-synthetic-examples.csv) are unrun examples of manifest use and count as zero real observations.

## Cohort and entry gate

After written rights, documented authorized access, safe-operation checks and permitted evidence handling are confirmed, evaluate **50 diverse real links: at least 20 Copart and 20 IAAI**. Assign the remaining ten explicitly based on gaps; do not invent a quota split. Cover active, sold, archived and relisted cases for each source where authorized examples are available. Report unavailable strata or recruitment bias rather than claim full diversity.

This cohort assesses identity resolution, not image inspection or repair cost. Repair examples can overlap only if separately eligible for each purpose. Synthetic fixtures, rejected unsafe URLs and repeated retries do not count toward the fifty distinct study cases.

## Manifest and execution

Use a private working copy of [the header-only manifest](identity-study-template.csv). Real URLs, identifiers, provider records and rights evidence stay outside Git. Identifiers are text: configure spreadsheet import as text so `00012345` is not converted to a number. Store timestamps as ISO 8601 with offsets/UTC; blank means unknown, never an invented observation time.

For each approved case:

1. Record sample identity, rights/ground-truth evidence references, expected auction house, exact lot/stock and distinct IAAI page ID if applicable, expected event, auction-state stratum and independent reviewer. Establish ground truth before viewing the resolver outcome where practicable. Unknown truth is inconclusive, not success.
2. Run only the documented authorized resolver operation. Record provider/adapter/contract version, selected data mode, timestamps, actual status, corroborated listing/event, candidate IDs, mapping/reference evidence IDs, reasons, source age/freshness, latency and error class. Do not fetch user URLs or scrape to fill missing evidence.
3. Have an independent reviewer adjudicate every `MATCHED` assertion against source, exact identifier, event and available VIN/model corroboration. Preserve separate events even when VINs repeat. Record disagreements and exclusion reasons; do not silently remove difficult cases.
4. Classify the case as verified exact match, false exact match, correct/uncertain abstention, service/permission failure, inconclusive truth, or unrun. `NOT_FOUND`, `UNRESOLVED_ID`, `AMBIGUOUS`, `SOURCE_UNAVAILABLE` and `NOT_AUTHORIZED` remain distinct.
5. A false exact assertion stops pilot activation. Diagnose, add a regression, fix and rerun affected cases; retain original and rerun results instead of replacing the failed record. Keep the permitted sample and evidence under its reviewed retention policy.

The manifest's evidence fields hold opaque private references, not raw documents. Store detailed permitted payloads only in approved restricted storage. Do not enter credentials, participant details or unnecessary personal data in a manifest.

## Required report

| Measure | Report definition |
| --- | --- |
| Enrollment | Planned, enrolled, executed, unrun, excluded and inconclusive counts, with reasons; distinct real cases versus synthetic examples |
| Coverage | Counts/denominators by house, provider, auction state, supported mapping capability and observed outcome |
| Exact assertions | Total `MATCHED`, independently verified exact assertions, false assertions and cases lacking adjudicable truth; zero observed false assertions is a sample target, not universal assurance |
| Abstention | Separate `AMBIGUOUS`, `UNRESOLVED_ID` and completed `NOT_FOUND` rates using explicit executed-case denominators; do not hide them in success coverage |
| Service behavior | Permission/service/schema/rate errors and retries; do not count provider failure as record absence |
| Freshness/latency | Source-age availability, archived/stale/unknown labels, measured latency distribution and measurement method; no unsupported SLA or coverage target |
| Decision | Supported subset, unresolved gaps, false-match regressions, evidence limitations, reviewer and conditional/no-go/limited-pilot recommendation |

If rights or access are unavailable, report **real study pending**, the precise missing gate and owner. A template or synthetic walkthrough does not complete the study. Publish only rights-reviewed aggregate information.

## Synthetic manifest walkthrough

`identity-synthetic-examples.csv` contains two local fixture URL keys and expected outcomes. `actual_status` and adjudication remain blank with `execution_state=UNRUN`; no runtime assertion was made while preparing these files. They demonstrate leading-zero preservation and IAAI page/stock separation. Running them later is an offline dry run only, never evidence about real auction inventory or the fifty-link target.
