# Apibara auction-data feasibility — 31 October 2026

This read-only review identifies a materially closer source for the original auction-URL flow. It does **not** establish a provider agreement or enable an integration. Ordinary public documentation and terms were retrieved; no auction record, API request, registration, provider message, purchase or image download was performed.

## What the provider documents

- [Product page](https://apibara.tech/en/products/vehicle-auction-data-api) and [homepage](https://apibara.tech/en) returned HTTP 200. They explicitly advertise Copart and IAAI normalized data, API-backed customer-facing applications and **100 recurring requests per month without a payment card**. The free quota is publicly advertised; plan entitlements and billing at account creation still need checking. The provider says production access uses subscription plans; free testing is not a promise of free production usage.
- The official [OpenAPI specification](https://apibara.tech/openapi/v1.json) returned HTTP 200, 280,610 bytes. It defines `GET https://apibara.tech/api/v1/vehicle-auction/vehicles/urltodetails?url=...` with an `X-API-Key` header. It describes resolving Copart or IAAI URLs to a `VehicleDetailsResponse` with a `data` record. The published vehicle schema includes `platform`, **string** `lot_number`, `vin`, `year`, `make`, `model`, auction fields and media. The schema does not mark these properties required, and the contract does not by itself validate their population or correctness for an actual lot.
- The official [complete developer reference](https://apibara.tech/llms-full.txt) says this endpoint imports a vehicle from a pasted Copart or IAAI link and describes 404 for missing records, 422 for validation failures and 429 for rate or quota limits. It explicitly warns that fields, coverage, real-time timing and complete history are not guaranteed. No authenticated source request was made and no credentials exist in this repository.
- The [terms](https://apibara.tech/en/terms), last updated 12 June 2026, include a vehicle-data commercial/media clarification updated **27 October 2026**. They say server-side commercial integration is supported within plan limits, but **before public redistribution the intended audience, fields and applicable source rights must be agreed with support**. Storage/refresh/reuse and post-subscription use need agreement where applicable. The provider states that it does **not** currently offer a verified blanket Copart/IAA photo sublicense; photo URLs and a technical proxy do not establish permission to republish, download, resize, store or sublicense photographs. Attribution is suggested, not a substitute for permission. The terms do not explicitly establish AI inference rights for auction photographs.
- The API's URL endpoint is a single provider result. Its public schema does not demonstrate independently corroborated **IAAI internal VehicleDetail page ID to stock number** mapping or prove it handles the country's `~US` suffix. A stock number returned by the same provider cannot independently corroborate its own page mapping. Do not turn this into `MATCHED` or equate an IAAI page ID with its stock number merely because numbers look similar.

## Recommendation and next gate

Prioritize Apibara ahead of the earlier [MarketCheck lead](free-auction-provider-review-2026-10-30.md) for a free-tier, metadata-first feasibility evaluation: its **documented original-URL operation** and stated Copart/IAAI coverage directly match the user journey. Actual coverage, current event semantics, data accuracy, free production entitlement, downstream commercial-display rights and photo/inference rights remain unverified. Its data is not an official auction feed and must not be described as one.

The existing provider guard should stay closed until the intended use is authorized with current evidence; no verified credential, signed permission, source response or live-match validation has been supplied. Do not invent an API key, accept terms on a client's behalf, scrape the public demo, derive private endpoints, or substitute a static result. If appropriately authorized, validate a narrow Copart and IAAI sample, preserve source/event identity and freshness, cross-check VIN when independent evidence is available, and report coverage and false matches separately. If independent page-to-stock evidence is absent, IAAI remains `UNRESOLVED_ID` under the current matching policy. Leave images and image inference disabled unless those distinct rights are established.

## Draft provider inquiry — unsent

**Subject:** Free-tier API scope and original Copart / IAAI listing resolution

Hello Apibara team,

We are evaluating your Vehicle Auction Data API for Auction Intelligence, a buyer-facing Georgia vehicle-import research application. Our user starts with an original Copart or IAAI lot URL and needs a correctly identified listing before reviewing vehicle evidence.

1. Does the 100-requests-per-month, no-card plan permit a public application to look up and display metadata for end users, including commercial use? Are calls to `/vehicles/urltodetails` included, and are overages hard-blocked without an automatic charge or paid-plan activation?
2. May we display and temporarily cache auction house, lot/stock number, VIN, vehicle specifications, source observation time, auction status and event date to the submitting user? What refresh, retention, attribution, deletion and country restrictions apply?
3. For IAAI URLs such as `VehicleDetail/{internal_page_id}~US`, what response fields and evidence independently establish the mapping to the actual stock number? Are page ID, country, stock number, VIN and distinct sale-event identifiers exposed separately? How are relisted VINs, missing fields and conflicts represented?
4. What rights, if any, cover access, display, download, resize, temporary storage and local AI inference on auction photographs, and derived inspection reports? The public terms state there is no verified blanket Copart/IAA photo sublicense; please identify what rights you can grant and what separate permissions are required.
5. Can you provide documentation of authentication, source observation time versus retrieval time, quota exhaustion, freshness and permitted technical handling, plus an authorized sample response with sensitive values removed?

We plan no bulk historical archive, model training, automatic bidding, or raw-feed resale. Please specify any limitations or terms applicable to this use.

Thank you.

**Status:** Draft only. No message has been sent and no account has been created.
