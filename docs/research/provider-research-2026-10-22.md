# Provider research — attempted access and next actions

Review date: **22 October 2026 (Asia/Tbilisi)**. Research owner: PO agent. Technical reviewer: root coding agent. This records an actual public-documentation access attempt, not a completed API/terms assessment. No provider was contacted, account created, auction record/photo collected or paid service used.

**Follow-up:** the network configuration was subsequently published and ordinary provider reads succeeded. See the [live findings](provider-findings-2026-10-22.md) and [current recommendation](provider-selection-2026-10-22.md). The access failures below are the earlier attempt, not current blanket network status.

## Finding and recommendation

**Zero current website pages were retrieved.** All ordinary HTTPS reads below failed before content delivery with `Tunnel connection failed: 403 Forbidden`. Search and official auction-site requests failed the same way. Root separately obtained network permission and retried outside the sandbox; the tunnel failure persisted. This is an environment access failure, not evidence that a candidate forbids automation, has no API, or is unavailable to normal users.

Recommend replacing the photo-intake-first sprint proposal with **provider discovery followed by the first supported integration**. PO owns website/business-model/access/terms research and recommendation; the technical lead owns identity/schema/operation validation. The user is not assigned website investigation, supplier comparison or collection of their own photographs to substitute for this work.

Bid.Cars is first investigation priority because the [handover](../auction_intelligence_handover.md) already identifies it as a metadata/history candidate. West Motors and Qopart are parallel user-nominated candidates. Establish the exact `motor.pl` business/domain before substituting a similarly named service. Investigate official Copart/IAAI channels as primary-source alternatives. This is a provisional research order, not a ranking of verified capabilities.

## Access evidence

Method: bounded ordinary GET requests using Python standard HTTPS client; no authentication, hidden-endpoint reverse engineering, auction-record enumeration, browser bypass or photo downloading. All returned the tunnel failure above; no API/terms conclusions follow.

| Purpose | Exact URL attempted | Outcome |
| --- | --- | --- |
| Bid.Cars homepage | https://bid.cars/en/ | HTTPS tunnel 403; no content |
| Bid.Cars terms from handover | https://bid.cars/en/terms | HTTPS tunnel 403; no content |
| Bid.Cars hostname variant | https://www.bid.cars/en/terms | Same failure |
| User-nominated domain | https://motor.pl/ | Same failure; service identity unverified |
| Domain hostname variant | https://www.motor.pl/ | Same failure |
| West Motors homepage | https://westmotors.cz/ | Same failure |
| West Motors hostname variant | https://www.westmotors.cz/ | Same failure |
| Official Copart agreement URL from handover | https://www.copart.com/Content/US/EN/buyer/Sales/Image-and-Data-License-Agreement | Same failure; current clauses unread |
| Official IAAI homepage | https://www.iaai.com/ | Same failure |
| Qopart homepage (root follow-up) | https://qopart.az/ | Same failure; no content |
| User-supplied Qopart example (root follow-up) | https://qopart.az/ge/vehicles/2021-audi-q5-premium-plus-45-tfsi-quattro-s-tronic-wa1baafy1m2015300-cms6ihx2t1s61uu3q18ayw1k7 | Same failure; no listing content retrieved |
| Public search | https://www.google.com/search?q=Bid.Cars+API+terms | Same failure; no results |
| Public search | https://www.bing.com/search?q=Bid.Cars+API | Same failure; no results |

Additional guessed discovery URLs (`https://api.bid.cars/`, `https://developer.iaai.com/`, `https://www.iaai.com/marketing/our-services/vehicle-data-services`) failed at the same tunnel. These probes **do not establish that such APIs, hosts or services exist**. Future discovery must follow actual official links; no integration should use guessed endpoints.

The handover's references were recorded on 19 October 2026. They remain background information, not reverified commercial permissions or guarantees. No current pricing, quotas, freshness, coverage, metadata reuse, image/AI rights or IAAI mapping semantics were established here. Unverified does not mean prohibited.

The user supplied the Qopart example as another candidate. Its URL text contains a VIN-shaped identifier and a site-specific record suffix; those strings alone do not establish the original auction house, lot/stock, sale event, data freshness, image provenance or access permissions. Prioritize checking independent auction linkage and any official feed/API/partnership offering once public-source access works. No claim about the page contents or the site's service has been verified.

## PO and technical lead work queue

| Order | Owner | Concrete deliverable |
| --- | --- | --- |
| 1 | Technical lead | Resolve permitted public-documentation access, then retry normal reads; distinguish infrastructure failure from site-level access restrictions. No further probes or bypass attempts in this execution. |
| 2 | PO | Establish each candidate's exact entity/domain, public API/feed/export/partnership offering, documentation and published price/quotas. Cite official pages and dates; advertised features remain distinct from a contract. |
| 3 | PO + technical lead | Compare automated commercial metadata lookup/display separately from image retrieval/display, processor inference, retention and derived reports. Unknown published scope becomes a precise question, not assumed permission or prohibition. |
| 4 | Technical lead | Validate exact Copart lot and IAAI page/country-to-stock linkage, independently evidenced VIN/model, separate records/events/relistings, timestamps and historical/live semantics against actual documentation and authorized samples. |
| 5 | PO | Draft one concrete commercial inquiry if public material cannot settle scope: proposed product/uses, expected volume and unanswered fields. No message is sent by this report; the user need not write or research the inquiry. |
| 6 | PO + technical lead | Recommend one evidenced route, actual costs where known, allowed subset and integration backlog. Metadata-only integration can advance the product while photos/AI remain unresolved. |

## Minimum unresolved supplier questions

- Which documented channel can you authorize for automated commercial Copart/IAAI lookup for this Georgian pre-purchase product?
- How are IAAI internal page/country, stock, VIN and separate sale events linked and corroborated?
- Which metadata and photo uses are included? Separately: AI-processor transmission, display, caching, storage, derived reports, deletion and revocation?
- Is the feed historical or live, what do timestamps mean, and what freshness/coverage commitments exist?
- What authentication, authorized samples/sandbox, price, quotas, support and schema-change policy apply?

PO prepares and consolidates these questions. Sending outreach, contractual acceptance and spending require applicable user authorization; the research and technical evaluation themselves stay with the agents. No unknown recipient or guessed contact address is supplied here.

## Development consequence

The next step remains blocked on research access, with ownership above. This is **not a completed provider study** and selects no real provider. Keep the working offline application; do not create a scraper or adapter from guessed URLs or quietly replace the auction-URL product with more seeded reports. Follow the first documented, permitted integration route and report unsupported uses separately. Requirements/report writing only: no application code or tests changed or executed for this report.
