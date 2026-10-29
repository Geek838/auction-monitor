# Free manufacturer VIN metadata — NHTSA vPIC

Reviewed and exercised **29 October 2026 (Asia/Tbilisi)**. This is a real public API integration with no account, key or paid subscription. It enriches a user-entered VIN with manufacturer specifications. It is not an auction data provider, VIN-history purchase, vehicle-condition assessment or physical VIN verification.

## Official evidence

- [NHTSA vPIC API documentation](https://vpic.nhtsa.dot.gov/api/), HTTP 200: documents `GET /vehicles/DecodeVinValues/{VIN}?format=json`, a flat JSON result. vPIC is populated from manufacturer submissions through the Part 565 process. The docs describe automated traffic rate controls; no guaranteed quota or SLA is invented here.
- [Official FAQ](https://vpic.nhtsa.dot.gov/api/home/index/faq), HTTP 200, asks “Is there a licensing requirement or registration requirement to use the APIs?” Its answer says the API services are “free for use by the public” as part of NHTSA's Open Data initiatives and there is “no need to register your application”. This supports this public metadata operation; it grants no third-party auction photographs or commercial auction records.
- The FAQ explains that foreign vehicles are covered when manufacturers registered them for US import/use/sale. It describes lower historical coverage before 1995 and no standardized pre-1980 VIN data. Do not advertise universal vehicle coverage or use its broad marketing/coverage percentages as this app's measured accuracy.
- The API supports partial VINs, but this application intentionally accepts only complete 17-character VINs without I, O, Q, wildcards or URL syntax. Syntax validation does not prove that a physical vehicle bears that VIN.

## Delivered boundary

`POST /api/v1/vehicles/decode-vin` accepts only `{ "vin": "..." }`. The frontend sends it only after the user selects a lookup action and discloses the NHTSA destination. Photo bytes, auction URLs and manual notes are not included. Results can be explicitly applied to the user's editable review fields; applying them does not promote the review to `MATCHED` or independently corroborate an auction listing.

The backend uses one fixed HTTPS host/path, default certificate verification and the configured network proxy, a 10-second timeout, a 1 MiB response cap, no redirect following and no automatic retry. Two concurrent requests per process are allowed; additional requests return an honest busy result. No durable cache, account or server history is added.

The response records `source=NHTSA_VPIC`, actual returned VIN, retrieval timestamp, fixed official source URL, make/model/model-year, source error codes and warnings, with `identity_status=NOT_AUCTION_VERIFIED`. It requires a single response row that echoes the requested VIN. Unexpected/mismatched responses and service failures produce `UNAVAILABLE` with cleared vehicle fields. Source-reported errors or missing facts cannot become a clean decode. Even `DECODED` means manufacturer metadata was returned without the source's decode error—not that an auction record, ownership, title, accident history, condition or physical identity was verified.

The source message explicitly says missing values mean NHTSA lacks that information, not that a feature is absent. Source errors and partial results remain visible. The user can review any returned facts rather than silently overwriting their input.

## Actual smoke evidence

An ordinary unauthenticated GET and the application service were both executed successfully against:

`https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVinValues/1HGCM82633A004352?format=json`

This engineering/test VIN returned one row: VIN `1HGCM82633A004352`, make `HONDA`, model `Accord`, model year `2003`, `ErrorCode=0`. The application service returned `DECODED`, `NOT_AUCTION_VERIFIED` and the same three facts. This is actual public-service behavior for one test input, not an auction match, source SLA or broad coverage benchmark. No photo was sent or downloaded and no paid call was made.

Routine tests replace the transport with declared deterministic fixtures and exercise strict VIN input, source response binding, errors/partials and bounded transport behavior. They do not call the live service or claim live access from a passing test double. Final execution counts belong to the increment test report.

A final live in-process FastAPI HTTP smoke also returned HTTP 200, `DECODED`, HONDA/Accord/2003 and `NOT_AUCTION_VERIFIED`, with `Cache-Control: no-store`. This used the actual NHTSA service, separately from routine test doubles.
