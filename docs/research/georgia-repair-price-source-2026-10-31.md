# Georgian repair-price source research — 31 October 2026

The buyer needs compatible, current Georgian parts and labor evidence. This is a bounded public-source research finding, not a live price provider, retail quote or validated estimate. No paid access, accounts, provider outreach, scraping of auction sites or access-control bypass was used.

## Current official procurement example

The [Georgian State Procurement Agency](https://procurement.gov.ge/) links to a public guest search at [tenders.procurement.gov.ge](https://tenders.procurement.gov.ge/public/?lang=en). On 31 October, the visible guest UI returned current records for category `50100000` (vehicle repair and maintenance). Selecting fulfilled contracts with a price list returned thousands of records; these are institutional procurements and not automatically applicable to private buyers. Ordinary Chromium could not validate this environment's proxy certificate, so the UI was exercised through a Playwright request context using the configured proxy and existing trusted CA with TLS verification enabled. Third-party assets were blocked. Searches and document navigation used the site's visible UI; no unpublished API was reverse-engineered.

A concrete public example is tender **NAT260014199**, announced 9 July 2026 for Borjomi municipal light-vehicle parts, repair and maintenance. The portal provides a [procurement link](https://tenders.procurement.gov.ge/public/?go=693545&lang=en) and shows an awarded and fulfilled contract. It identifies a 2026 fleet-service period and a contractual procurement ceiling of 35,000 GEL. The tender says bids exclude VAT; this does **not** independently establish the VAT treatment of each eventual payment.

The tender's public Documentation tab links an authority XLSX price table with per-model parts and service columns. Its figures are maximum permitted unit values, not actual customer quotes; the original bidder-offer columns are blank. The Offers tab separately links the successful bidder's signed price sheet and a total price-list bid of 80,984.01 GEL. The spreadsheet's total ceiling is 101,230 GEL. Some signed sheet values match the stated maximums; it is not safe to assume the auction's aggregate change applies proportionally to every item without checking the signed contract's line-level terms.

The portal's Agreement tab also links a signed 15 September 2026 acceptance act for a 5,568 GEL transaction. It itemizes, for that specific public fleet contract, two front headlamps at 144 GEL each and two shock-absorber kits at 144 GEL each, among other items. The act does not establish which exact make/model each of those lines fits; it does not explicitly establish VAT treatment per line or any present-day retail availability. These observations are not inputs to the application's repair calculator.

Documents contain VINs, personal identifiers and bank details. The source documents and unredacted extracts were kept only in ignored local research storage and must not be committed, uploaded to a model, exposed in reports or copied into a dataset. The aggregate prices above omit such identifiers. Public website accessibility is not evidence of permission to republish or commercially redistribute supplier documents; reuse terms and any personal-data obligations remain unverified.

## Older open-data portal

The agency homepage also links [Georgian Public Procurement Open Data](http://opendata.spa.ge/#/tenders). Its visible UI describes Open Contracting Data Standard records but explicitly covers 2011 through the first quarter of 2019. The HTTPS host returned 503 during this check. Historical tenders are useful for methodology research, not current Georgian repair quotes. No historical values were promoted into application defaults.

## Decision and remaining evidence

This is a real, dated institutional source lead. It does not yet support automatic product estimates: the observed act has no per-line vehicle compatibility, no stated parts condition or availability for this buyer, and unresolved VAT and redistribution scope. A defensible estimate needs matched part or operation and vehicle fit, current price/expiry and currency, clear labor scope, independently sourced VAT treatment, and permission for the intended use. It also requires coverage from multiple comparable cases, uncertainty ranges and measured errors. Keep the evidence separate from real-time retail quotes and do not convert procurement ceilings into customer prices.
