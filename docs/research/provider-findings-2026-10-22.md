# Provider findings — Bid.Cars and Qopart

Reviewed **22 October 2026 (Asia/Tbilisi)** by the PO agent, with technical review by the root agent. This is current public-source research, not a supplier agreement or production integration. No account was created, business contacted, paid API called, auction inventory enumerated or photograph downloaded.

## Access and method

After the user published the environment's research-domain allowlist, ordinary HTTPS GETs succeeded for Bid.Cars and Qopart. This supersedes the earlier [zero-page access attempt](provider-research-2026-10-22.md) for these sites. Official navigation links led to the pages below; the linked English Bid.Cars PDF was downloaded and its text read with `pdftotext`. Requests were bounded and no hidden application API was reverse engineered.

The user-supplied Qopart example was read once to assess visible auction linkage. That is an individual research example, not authorization to ingest its inventory into our product. Public HTML/PDF evidence is cached locally under ignored `.cache/provider-research/`; no raw website inventory, photo bytes or private material is included in this report. The initial Qopart homepage read was capped at 1 MB; absence of a link in that partial snapshot is not proof of absence. Its reviewed about/terms/contact/partnership pages and the user-supplied example were smaller complete responses.

## Summary

| Candidate | Verified public offering | Automated data-access evidence | Rights evidence | Present recommendation |
| --- | --- | --- | --- | --- |
| Bid.Cars | Vehicle-import/broker platform; homepage offers Copart/IAAI filters, current/archive categories and VIN/lot search | No public API/feed/export documentation was found in the reviewed home/about/terms/contact navigation. This is a bounded finding, not proof no private API exists. | Official linked English terms §15.2 expressly say website use grants no rights/licenses to works or databases | Conditional commercial data-partnership candidate; keep adapter disabled pending actual documented channel and scope |
| Qopart | Import/bidding intermediary with Copart/IAAI browsing, Azerbaijan service and Georgian-facing pages | No public data API/feed/export specification was found in the reviewed pages; public agent program concerns import/referral commission | Both Azerbaijani and Georgian terms §9 require prior written permission for the stated automated commercial collection use | Conditional partnership candidate; do not implement a website scraper under current evidence |

These are supplier/product claims where indicated, not independently measured accuracy, coverage or freshness. Neither site has granted Auction Intelligence metadata, image or AI use through the reviewed material. Nothing here establishes that a separately negotiated integration is impossible.

## Bid.Cars evidence

| Source | Retrieved evidence and product consequence |
| --- | --- |
| [Homepage](https://bid.cars/en/) — HTTP 200 | Search input says **“Search by VIN or lot number”**; Copart and IAAI filters and Current/Archived views are present. This supports product fit for lookup research, not API semantics, permission or lookup accuracy. No search was submitted. |
| [About](https://bid.cars/en/about-us) — HTTP 200 | Describes sourcing/importing and shipping vehicles; says **“We serve both individual clients and dealers as well as wholesale customers.”** Dealer/wholesale service is not automatically data redistribution access. |
| [Terms landing page](https://bid.cars/en/terms) — HTTP 200 | Links [English terms PDF](https://bid.cars/terms_en.pdf), retrieved HTTP 200, 180,212 bytes. The available English document identifies itself as dated **8 June 2019**. It is a currently linked document, not proof that every commercial scope or language version is current/equivalent. |
| English PDF §15.1–2 | §15.1 states text/multimedia and database protection. §15.2: **“By using works or databases made available on the WEBSITE, USERS do not acquire any rights or licenses to these works or databases.”** A public page or paid consumer account does not supply our commercial data license. |
| English PDF §5.1 | Disclaims responsibility for auction validity and vehicle data. Do not treat a new retrieval as a guarantee that a sale is live or record details remain accurate. |
| [Contact](https://bid.cars/en/contact) — HTTP 200 | Identifies **BidCars Patryk Szwałek**, VAT-EU PL4990650123, Poznań. Describes chat/phone/helpdesk and notes support availability for active users with paid deposit or bid history. This is an official contact route, not an API onboarding promise. The terms PDF lists `support@bid.cars`; no message has been sent. |

The English PDF's consumer-account price is not an API quote and is deliberately not used as an integration budget. No API authentication scheme, quota, endpoint, exact IAAI page-to-stock mapping, service-level freshness, event versioning, retention permission or image/inference license was established. The site's `1-`/`0-` URL patterns mentioned in the handover are not an independent identity contract.

**Bid.Cars next owned action:** PO prepares a commercial data-access inquiry; technical lead requests the documented lookup contract and authorized sample format if the provider offers one. Keep metadata display, photo display/storage and processor inference as separate requested uses. Do not purchase a consumer membership assuming it enables our integration.

## Qopart evidence

| Source | Retrieved evidence and product consequence |
| --- | --- |
| [About](https://qopart.az/about) — HTTP 200 | Describes an Azerbaijan vehicle-import intermediary for Copart/IAAI/Manheim. Claims **“180,000+”** vehicles with daily updates and uses “real time” marketing language. This was not independently verified and is not a freshness guarantee for each record. |
| [Azerbaijani terms](https://qopart.az/terms) — HTTP 200 | Page states last update **1 August 2026**. §1 describes search, estimates and intermediary/agent service. §5 says damage/VIN/photos come from auction sources and disclaims accuracy guarantees. It does not establish a sublicensing chain for our use. |
| [Georgian terms](https://qopart.az/ge/terms) — HTTP 200 | Page states last update **27 September 2026**. §1 describes the Georgia-facing auction/import service. §5 disclaims completeness/accuracy of auction-source price, VIN, damage and photos. |
| Georgian terms §9 | Heading **“ბოტები და ავტომატური წვდომა”** (bots and automated access). Relevant text: **“ჩვენი წინასწარი წერილობითი ნებართვის გარეშე აკრძალულია ამ მონაცემების მასობრივი შეგროვება ბოტით, crawler-ით ან scraper-ით კომერციული მიზნით.”** Informal translation: without prior written permission, bulk collection of these data using bots/crawlers/scrapers for commercial purposes is prohibited. The clause exempts ordinary search-engine indexing; that exemption does not describe our product. |
| Azerbaijani terms §9 | Likewise addresses bots/automated access and prior written permission for the specified collection/copying/redistribution/commercial-use activities. The two language versions should not be assumed word-for-word equivalent. The proposed ongoing commercial ingestion needs an explicit agreement. |
| [Agent program](https://qopart.az/become-agent) — HTTP 200 | Offers a partner route for finding import customers, routing bidding/import through Qopart, and earning agreed agent commission. This is an import/referral partnership, not published authorization or documentation for a software data feed. |
| [Contact](https://qopart.az/contact) — HTTP 200 | Official contact page offers phone **+994 77 500 81 71**, email/Instagram/Facebook, and Baku location. The contact page publishes **support@qopart.az** through its protected email display; that address was recovered from the page's public display encoding, not guessed. No message was sent. |

### User-supplied identity example

[2021 Audi Q5 example](https://qopart.az/ge/vehicles/2021-audi-q5-premium-plus-45-tfsi-quattro-s-tronic-wa1baafy1m2015300-cms6ihx2t1s61uu3q18ayw1k7) returned HTTP 200. The visible page identifies **IAAI**, displayed lot **45942937**, VIN **WA1BAAFY1M2015300**, Boston–Shirley location and 11 photo slots. We did not download those photos, submit a bid, or validate the record with IAAI.

This is materially better evidence than the URL slug alone: the page actually presents an auction house plus listing number and VIN. It still does **not** prove an internal IAAI `VehicleDetail` page-ID/country → stock mapping, independent corroboration, sale-event identity, currentness or lawful onward photo use. The Qopart record suffix is its own site ID; it cannot become an IAAI internal page ID. Its displayed price/status is not imported into our app or claimed live here.

The Georgian terms also distinguish claimed official excise calculation from estimated customs/VAT formula components. These are supplier statements, not verified Georgian tax rules; do not copy those percentages into Auction Intelligence. Costs remain outside this integration slice.

**Qopart next owned action:** PO prepares a software/data partnership inquiry, explicitly different from the referral-agent program. Technical lead asks for exact source/stock/page/event identifiers, timestamps and a documented supported export/feed if available. No API endpoint is guessed or browser request replayed.

## Decision and development consequence

For these two candidates, the useful next step is a **specific data-access offer**, not a scraper implementation. Prioritize a documented data API alternative if the broader research finds one with suitable supported use; retain Bid.Cars and Qopart as parallel negotiation candidates. A metadata-only authorized pilot is useful before photos or AI are permitted.

PO owns the comparison and inquiry drafting. Technical lead owns schema/identity/operational review. The user is needed only for a concrete contractual/spend decision or explicit outreach authorization once recipient, message and requested scope are reviewable. No message has been sent and no spending has occurred.

**First contact recommendation (PO judgment): Qopart**, because the verified Georgian-facing product and public partnership/contact path make the proposed use easy to explain. This is a negotiation priority, not evidence it can legally sublicense data or offers an API. Ask Bid.Cars in parallel if outreach is authorized; its broader visible archive/lookup fit is useful, but its support page describes existing-customer access restrictions. Neither ranks as a ready integration today.

Questions already prepared for an authorized inquiry:

1. Do you offer a supported API/feed/export and permit commercial metadata lookup/display in an independent pre-purchase app for Georgian buyers?
2. Can original Copart lots and IAAI internal page/country references be mapped to exact source stock, VIN and separate sale events? Provide documented semantics and an authorized sample.
3. Separately, can photographs be retrieved, displayed, retained and transmitted to an identified AI processor? What source authorization, retention/deletion and derived-output conditions apply?
4. What auth, pricing, quotas, freshness/history semantics, support and change/deprecation policy apply?

Until a documented permitted channel is established, existing real-provider adapters remain disabled, and no real records inherit authored mock previews. This research is complete for the bounded public pages reviewed; commercial eligibility and live integration remain unresolved.

## Reviewable outreach drafts — not sent

**Qopart recipient:** `support@qopart.az`, from the public [contact page](https://qopart.az/contact); phone +994 77 500 81 71 is an alternative official channel. **Subject:** Commercial auction-data partnership for Auction Intelligence.

> Hello Qopart team, we are developing Auction Intelligence, a pre-purchase vehicle assessment application for buyers in Georgia. Buyers would paste a Copart or IAAI URL; we need to resolve the exact original listing, VIN and sale event through an authorized source. Your Georgian-facing service looks relevant. Do you offer a supported API, feed or export with permission to display metadata in an independent commercial application? We are asking about a software/data partnership, rather than the import-referral agent program. Please share the documented lookup/IAAI page-to-stock mapping, timestamps/history semantics, auth, pilot access, pricing and quotas. Separately, can your agreement cover photo display, storage and processing by an identified AI provider, and what source-rights and retention/deletion restrictions apply? A metadata-only pilot would also be useful. We have not integrated or bulk-collected your data and will agree scope before activation. Please direct us to the appropriate commercial/data contact.

**Bid.Cars recipient:** `support@bid.cars`, published in the English terms PDF; [official contact page](https://bid.cars/en/contact) also lists supported channels and existing-customer limitations. **Subject:** Authorized data-access inquiry for Georgian pre-purchase application.

> Hello BidCars team, we are developing Auction Intelligence for buyers importing damaged vehicles into Georgia. The user supplies an original Copart or IAAI URL, and our backend must resolve the exact source lot/stock, VIN and sale event. Do you offer a commercially licensed API, feed or export for this use? We understand website access or consumer membership does not itself license the database. Please provide supported lookup and IAAI internal page-to-stock semantics, record/event and source timestamps, authorized samples, auth, pricing, quotas, and permitted display/retention/derived-output scope. Separately, are auction photographs available for licensed display/storage and inference through an identified AI processor? We can begin with metadata only. We have not enabled a Bid.Cars data integration and are requesting a documented authorized route before doing so. Please route this inquiry to the appropriate data/commercial contact.

These are complete draft messages for review, not contact authorization. A recipient's reply would still need technical/use-scope review and any necessary contract/budget decision; a general positive response is not automatically an image or AI license.
