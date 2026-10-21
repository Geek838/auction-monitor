# Provider recommendation — first live public-source review

Reviewed 22 October 2026 (Asia/Tbilisi). Owners: PO for commercial/product research; technical lead for integration feasibility. This follows the [earlier blocked attempt](provider-research-2026-10-22.md). The environment network update now permits ordinary reads. No contacts, accounts, paid calls, auction scraping or production integration were performed.

## Recommendation

**Prioritize a commercial data-access inquiry to Qopart, with Bid.Cars in parallel. Do not implement a scraper or select a production provider yet.** This is a contact priority based on the evidence below, not a claim either company sells a suitable API. Start with authorized exact-identity metadata if image/AI permissions cannot be established at the same time.

Qopart is the stronger first conversation because its verified Georgian-facing service and public partnership/contact path make the proposed product easy to explain, and the user-supplied example exposes an IAAI stock/lot reference and VIN. Its terms require prior written permission; that requirement is not an offer of an API or data partnership. Bid.Cars is the handover's established candidate, but public pages inspected do not establish an available licensed API. Neither supplies a documented exact IAAI internal-page-to-stock integration in the material reviewed. Actual availability, pricing and permitted product use require answers from the suppliers.

The PO prepares the inquiry and technical questions; the user is not assigned supplier research. Sending external messages needs separate authorization and an appropriate sending channel. Accepting an offer or spending money is a concrete business decision after terms exist. Nothing has been sent.

## Evidence-based comparison

| Candidate | Observed evidence | Product fit / unresolved issues | Decision now |
| --- | --- | --- | --- |
| Qopart | Homepage, Georgian terms and user-supplied listing retrieved; terms require permission for bulk commercial collection | Auction-oriented records; original IAAI page mapping, exact API/feed contract, freshness and image/inference rights unverified | First commercial inquiry; no collection/integration enabled |
| Bid.Cars | Official terms HTML and linked English PDF retrieved; database/works rights are not granted merely through website use | Relevant auction archive/import business; no documented authorized API or exact mapping established in reviewed material | Parallel commercial inquiry; existing adapter remains disabled |
| Auto.dev | Official API documentation and terms retrieved; VIN-based listings/photos endpoints documented | Documented API is useful evidence of technical access, but reviewed listing docs describe dealer inventory; no verified Copart lot/IAAI page mapping. Terms restrict internal/end-user usage | Do not choose for original URL resolver without a suitable documented operation and product-use agreement |
| Stat.vin | Homepage and terms-of-service retrieved; `/api` returned 404 | Published website license is personal/non-commercial and restricts reproduction, scraping and automated systems. A 404 at one guessed path does not prove no separate API exists | Not usable through ordinary website access for this product; separate agreement would be needed |
| motor.pl | Bare and www hosts returned HTTP 503 with an HTML temporarily-unavailable page | Exact service identity, offering, API and terms could not be verified | Unassessed; do not substitute a similarly named domain |
| westmotors.cz | HTTP 200 returned only a JavaScript cookie/browser-check page | Actual product, documentation and terms not retrieved; status 200 is not content verification | Unassessed; no browser-check bypass attempted |

Detailed Bid.Cars/Qopart evidence and the prepared inquiry are in [PO findings](provider-findings-2026-10-22.md). Auto.dev evidence is in [technical feasibility](auto-dev-feasibility-2026-10-22.md). These are published-source observations and technical recommendations, not a legal opinion or a license.

## Additional official-source evidence

- [Stat.vin Terms of Service](https://stat.vin/terms-of-service), HTTP 200, section 2.1.1: “a limited, non-exclusive, and non-transferable license to access the Website for personal and non-commercial use”. Section 2.3.1(a) prohibits reproducing images/descriptions on other websites; (c) includes “automated or non-automated scraping”; (d) prohibits “automated systems (such as robots, spiders, or offline readers)”. This does not establish the availability or scope of a separately negotiated feed.
- [Stat.vin homepage](https://stat.vin/), HTTP 200: the reviewed home/navigation links did not establish a developer API. `https://stat.vin/api` returned 404; that is a single-path observation, not an exhaustive search or nonexistence claim. A separate terms-and-conditions response exceeded the bounded read and is not used to support terms conclusions.
- [motor.pl](https://motor.pl/) and [www.motor.pl](https://www.motor.pl/) returned HTTP 503; the response says “The page you are looking for is temporarily unavailable.” No product capability can be inferred.
- [West Motors](https://westmotors.cz/), HTTP 200, returned a short page titled “Проверка браузера” (browser check), with a cookie-setting/reload script. We did not extract an approval cookie or circumvent the check.
- [Copart image/data agreement reference](https://www.copart.com/Content/US/EN/buyer/Sales/Image-and-Data-License-Agreement), HTTP 200 with only 212 bytes, did not yield readable agreement content. [IAAI homepage](https://www.iaai.com/) returned HTTP 200 with an Incapsula “Request unsuccessful” page. These are site-level content restrictions, distinct from the earlier environment CONNECT 403. Current official access/terms cannot be concluded from these responses.

Read-only retrieval used standard HTTPS clients with TLS verification, finite timeouts and bounded responses. Public text extracts are local ignored research artifacts; real photo bytes were not collected. No official auction-site controls were bypassed. Search engines and additional third-party hosts were outside the configured research-domain scope; this is a bounded shortlist review, not an exhaustive market survey.

## Concrete implementation gate

The existing `AuctionSource` protocol and `GuardedProvider` already provide the adapter/permission boundary. No new framework is needed. Before implementing one real adapter we need a documented operation and authorized response samples establishing:

1. Original house plus exact lot/stock lookup, including leading zeros and explicit IAAI page/country mapping if supported. Unsupported page mapping must remain `UNRESOLVED_ID`.
2. Provider record and sale-event identity, corroborating VIN/model evidence, and source observation/history semantics; retrieving historical data now must not label it live.
3. Actual authentication, fixed destination, schema, quotas/errors and finite request limits. Do not invent a web JSON endpoint from page scripts.
4. Commercial metadata lookup/display permission; independently establish any caching, photos, inference and derived-output use. Metadata-only scope can be implemented first.
5. Existing exact-match, policy, freshness and no-synthetic-fallback regression checks plus actual selected-provider contract tests. An authorized live smoke run is reported separately from test-double passes.

Without those facts, another disabled placeholder or a guessed API client does not advance this product. Existing fixture and mock inspection functionality remains available. No application code or test suite changed for this research slice; documentation checks are recorded separately.
