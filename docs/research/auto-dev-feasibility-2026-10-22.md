# Auto.dev — public API and Auction Intelligence feasibility

Reviewed **22 October 2026 (Asia/Tbilisi)** by the integration engineer. Ordinary bounded reads of the official homepage and documentation succeeded with HTTP 200. This is a documentation assessment, not an executed API integration, rights opinion or provider recommendation to activate. No account, key, API request, photo download, purchase or supplier contact was made. Public HTML/text evidence is retained locally under ignored `.cache/provider-research/autodev*` files.

## Recommendation

**Do not select Auto.dev as the primary auction-URL resolver on the evidence reviewed.** It has a real, documented developer API and a no-card evaluation plan, but the reviewed public operations are VIN-based dealer/market listings and photographs. They do not establish exact Copart-lot lookup, IAAI VehicleDetail-page-to-stock mapping or sale-event-specific image binding. This makes it a possible later enrichment/evaluation candidate, not a demonstrated substitute for an auction data provider.

The account/key is not the only missing item. First obtain documented exact auction-reference support, event linkage and a use scope covering this buyer-facing product. Do not build a guessed auction adapter merely because other vehicle APIs are well documented.

## Verified public documentation

| Topic | Retrieved official evidence | Finding and practical implication |
| --- | --- | --- |
| Product orientation | [Vehicle Listings API](https://docs.auto.dev/v2/products/vehicle-listings) | “Get comprehensive vehicle listings from U.S. physical & online dealers.” It documents `GET https://api.auto.dev/listings` and `GET https://api.auto.dev/listings/{vin}`. A VIN is required for the latter; a Copart lot is not a VIN. |
| Search and shape | Same listing documentation | Collection search supports vehicle/dealer/retail filters, pagination and geographic filters. `data` is an array for the collection and an object for the VIN operation. `?select=` changes objects to flat dot-keyed properties. The documented wholesale filters concern buy-now price, state and miles; reviewed pages do not document a Copart lot or IAAI page/stock lookup parameter. |
| History/freshness | Same listing documentation | With no current listing, the VIN operation returns “its most recent stored listing,” with `removedAt`, described as the last time a source saw it listed; disappearance was within 48 hours after. This historical fallback must not be presented as a live auction event. `createdAt`/`updatedAt` describe listing creation/update, not a verified auction observation or guaranteed freshness SLA. |
| Photos | [Vehicle Photos API](https://docs.auto.dev/v2/products/vehicle-photos) | Documents `GET https://api.auto.dev/photos/{vin}` and describes “retail images” from dealer listings and auction sources. The response includes `data.retail` image URLs; documentation also shows `wholesale` potentially empty and historical `removedAt`. A VIN-only photo collection does not establish which auction listing or sale event each image belongs to. No images were fetched. |
| Authentication | [Getting Started](https://docs.auto.dev/v2/getting-started) | Signup/email verification and a dashboard API key are required. The recommended server-to-server method is `Authorization: Bearer YOUR_API_KEY`. Browser-session and query-key approaches are also documented; our eventual backend should use the header and avoid keys in URLs/logs. |
| Evaluation allowance | [Pricing](https://auto.dev/pricing), [Terms §4.4](https://auto.dev/terms) | Free: 1,000 calls/month, no card, capped at the limit; published rate is 5 requests/second. Terms state the included free allowance is for “evaluation, development, and small-scale applications” and “not for production systems serving end users.” No free-plan account was created. |
| Paid options | [Pricing](https://auto.dev/pricing) | Published monthly Growth is $299/month **plus data fees**, Scale $599/month **plus data fees**. Growth lists 10 requests/second and per-call listing/photo fees of $0.0015/$0.0009; Scale 50 requests/second and $0.001/$0.0007. These are retrieved price snapshots, not a quote, recommendation to purchase or an agreed trial budget. “Unlimited API request volume” does not mean zero usage fees. |
| Enterprise | Same pricing page | Advertises custom data fees/licensing, bulk feeds and custom limits. No enterprise scope or offer has been obtained. |

The documentation's examples and marketing are provider claims; they do not prove actual coverage, accuracy, availability for any particular vehicle, or the chain of rights from original photo owners. No reviewed page identifies guaranteed Copart/IAAI coverage or an IAAI internal-page mapping operation. This is a bounded “not established by reviewed material” finding, not proof that a separately negotiated service cannot exist.

## Use-scope findings

The [published terms](https://auto.dev/terms) identify Drivly, Inc. and show an effective date of January 2026 and last-updated date of September 16, 2026.

- §4.1 permits integrating automotive data into applications and building automotive-related products. However, §4.2 prohibits reselling, redistributing or sublicensing Automotive Data, and §4.3 limits the license to “internal business purposes” and prohibits derivative databases/competing data products. The interaction of these clauses with a buyer-facing paid inspection report needs explicit clarification; a technical API key must not be treated as unlimited display/redistribution permission.
- §6.1 says data comes from publicly available internet sources, disclaims accuracy/completeness/timeliness, and permits removing datasets when source terms or legal conditions change. This statement does not establish original auction-photo rights or authorization for external-model processing.
- The reviewed terms do not establish a specific grant for our external AI inference, caching/retention duration, image redistribution, or derived damage reports. Treat each as unresolved, not automatically allowed or universally prohibited. Source changes/removal must be reflected in any eventual use controls.
- Free-plan evaluation permission does not resolve the product-fit and exact-identity gaps above. Do not request a key or create a paid trial until there is a concrete useful experiment and any required business decision.

## Fit against the current code

The review covered `AuctionSource`, `GuardedProvider`, `AuctionReference`, `ProviderResolution`, `VehicleSnapshot`, the URL parser and conservative resolver.

| Existing requirement | Evidence available from Auto.dev docs | Integration consequence |
| --- | --- | --- |
| Start from Copart URL's exact string lot | VIN and generic listing search documented | No demonstrated conversion from the submitted lot to a VIN or exact auction record. Never substitute a similar vehicle or silently ask a VIN API to interpret a lot. |
| Keep IAAI page/country distinct from stock | No reviewed documented page-to-stock operation | Without independent mapping evidence the existing resolver must remain `UNRESOLVED_ID`; the adapter cannot invent equality or derive mapping from its own candidate. |
| Preserve provider record, sale event and canonical auction identity | Retail listing objects; no verified auction-event linkage established | Do not use VIN alone as an auction record/event ID or collapse relistings. A generic dealer listing cannot satisfy canonical auction identity by assertion. |
| `LICENSED` external snapshots and current use checks | API exists; this project's allowed use scope is not established | Keep any new provider disabled until actual reviewed authorization covers the operation, and keep metadata/photo/inference uses independent. |
| Source-based freshness | Creation/update/removal timestamps documented | Map only documented semantics; preserve unknown observation/freshness where unsupported. `retrieved_at=now` must not imply source freshness or live bidding. |
| Exact authored preview binding | Existing mock images and findings are fixture-only | No real Auto.dev metadata or VIN photo collection may inherit the current mock inspection scenario. |

If suitable auction documentation and use terms are later obtained, a narrow async HTTP adapter can reuse the existing policy wrapper and resolver. It needs bounded fixed-destination requests, header auth, strict response normalization, explicit status translation, no synthetic fallback and selected-provider contract tests. That is manageable conventional work; the unresolved source-to-identity evidence is the blocker, not the HTTP client. Engineering effort should be estimated against the actual supported operation and schema, not guessed auction endpoints.

## Owned next actions

1. PO consolidates this candidate with Bid.Cars, Qopart and other source findings. Rank exact auction-data fit and allowed product use ahead of API polish or an inexpensive evaluation plan.
2. If Auto.dev remains relevant, PO prepares a targeted inquiry asking whether an authorized operation/feed supports Copart lot and IAAI page/stock lookup, event-specific photos and commercial report display/AI use. Preparing the inquiry is our work; sending requires separately authorized outreach.
3. Technical lead evaluates any actual documented response/sample and independent linkage evidence before designing an adapter. No implementation or live API smoke result is claimed in this report.
