# Free auction-source review — 30 October 2026

PO-owned public-source research for the client's no-paid-API requirement, **Asia/Tbilisi**. This extends the [22 October shortlist](provider-selection-2026-10-22.md). Ordinary bounded HTTPS reads only; no account, key, API-data query, photograph download, provider message, purchase, collection script or access-control bypass.

## Decision

**MarketCheck is a concrete new API candidate worth a narrow coverage/use-scope validation; it is not a selected live provider.** Unlike generic VIN decoder sites, its official documentation describes actual auction-search and auction-listing operations, an advertised free tier, and user-driven application display/AI usage. The reviewed evidence still does not establish Copart/IAAI coverage, exact submitted-lot semantics, an IAAI internal-page-to-stock mapping, all photo/inference uses or that commercial deployment of this product is included in the free allowance. Do not convert those unknowns into a working-auction-access claim or integrate a guessed adapter.

No reviewed source yet proves a zero-cost permitted complete original-auction flow. This is a bounded research result, not proof that no supplier can offer one.

## MarketCheck — actual official documents retrieved

All pages below returned HTTP 200 on 30 October. API examples were read as documentation; the query examples were **not executed**.

| Source | Established evidence | Product implication |
| --- | --- | --- |
| [Auction Search](https://docs.marketcheck.com/docs/api/cars/inventory/auction-search) | Documents `GET https://api.marketcheck.com/v2/search/car/auction/active`; US auction inventory, `seller_type=auction`; `source`, `stock_no`, `vdp_url`, VIN and other filters. Explicitly says to try it with a free API key after account creation. Claims daily refresh by 11:00 UTC. | Much closer to our lookup need than VIN-only retail APIs. Generic stock and VDP filters do not establish exact original-auction identity semantics. Daily refreshed inventory is not live bidding. Documentation marketing counts are not our measured coverage. |
| [Auction Listing Details](https://docs.marketcheck.com/docs/api/cars/vehicle-listing/auction-listing) | Documents `GET https://api.marketcheck.com/v2/listing/car/auction/{listing_id}`; the identifier is a case-sensitive provider listing ID, not an auction lot or VIN alone. Schema refers to Car Listing Details; includes specifications, seller/media/marketplace context. | Preserve provider record identity separately. Do not pass a Copart lot or IAAI page ID into this path and pretend it is the provider ID. |
| [Pricing](https://www.marketcheck.com/apis/pricing/) | Advertises Free `$0/mo`, 500 calls/month, 5/second, 100-mile radius restriction, 500-row free pagination. Lists auction search and auction details at `$0.008` per call in endpoint pricing, paid Basic `$299/mo + data fees` and Standard `$749/mo + data fees`. | A free plan exists, but plan subscription price and endpoint usage price must not be conflated. The docs invite a free-key auction try; whether all intended auction calls incur no data fees needs confirmation from actual account terms/entitlement before activation. No payment instrument/account was supplied. |
| [Quota and Rate Limits](https://docs.marketcheck.com/docs/get-started/api/quota-and-rate-limits) | Free 500/month, 5/second; monthly quota shared by account keys and resets at calendar-month start. Exceeding quota blocks requests with 429. | Supports a bounded no-overage hypothesis, not a contractual no-charge guarantee for every endpoint. No multi-account quota evasion. |
| [Terms of Service](https://www.marketcheck.com/terms_of_service/) | §3 permits real-time/user-driven apps, tools and workflows, including AI/natural-language interfaces, and application display. §5 restricts substantial persistence/extraction, competitive replication, model training and collection targeting; real-time AI use without independent datasets is distinguished from training. §6 says commercial products/scale may require a separate written enterprise agreement, at MarketCheck's discretion. | This is stronger app-use evidence than a personal-only website licence. It does not resolve this product's commercial deployment, exported/persistent reports, caching, photo rights, model inputs/derived output retention or competing-product interpretation. |
| [Access Control](https://docs.marketcheck.com/docs/get-started/api/access-control) | Documents key-level endpoint restrictions and account IP allowlisting; new keys have full endpoint permissions by default, subject to account entitlements. | Useful technical controls if selected; no key was created. Keep eventual keys server-side and exclude from URL/access logs even if examples show query-key auth. |

The public auction pages reviewed did not explicitly name Copart or IAAI, guarantee original lot/stock coverage, show IAAI page/country mapping or independently corroborate source-event linkage. A URL equality search could retrieve a record, but equality asserted by that same record alone is not independent evidence of the vehicle. The existing conservative resolver/permission rules remain the integration boundary.

### Team-owned next validation

1. Establish free auction-endpoint entitlement, no automatic charge/overage, and product-display/inference/export/retention scope from actual supplier terms or written clarification. Keep the prepared question with the PO; no outreach is implied or sent.
2. Establish that `source` plus `stock_no` or `vdp_url` supports the actual Copart/IAAI domains and preserves leading zeros. Demand separate IAAI internal page, country and stock fields/mapping evidence; unsupported mapping remains `UNRESOLVED_ID`.
3. If useful access is legitimately available, run a narrow authorized sample set, cross-check actual identity/event/freshness and permission fields, and record match coverage separately from false-match rate. Do not download photos to establish metadata coverage.
4. Only then implement a bounded fixed-destination adapter reusing `AuctionSource`/`GuardedProvider`. No synthetic fallback for real misses or source errors, and no vin-only matching/relisting collapse.

The team owns these steps. The client is not assigned provider research, and the existence of a sign-up form is not authorization for us to invent an email identity, accept a paid plan or send messages.

## Other public-source observations

- [Carfast homepage](https://carfast.express/en) and its [partner page](https://carfast.express/en/partners) were retrieved. The reviewed partner page did not establish an API/data-feed contract. Its [Website Terms of Service](https://carfast.express/en/terms-of-service), HTTP 200, §2.1 grants personal/non-commercial access; §2.3 restricts copying/automated or non-automated scraping and automated website access. Its free consumer calculator is not a licence to reproduce a data feed, customs formula or photos. No listing or image collection followed.
- AutoBidMaster and Salvagebid public homepages returned HTTP 403. VehicleDatabases' auction-history product route and Carstat's public routes also returned HTTP 403. These observations do not establish capabilities, prices, nonexistence or permission. No challenge was bypassed.
- `auctionapi.com` returned HTTP 503. A single guessed AutoAuctionSpot API page was inaccessible at the network tunnel; Bidinfo's `/api` returned 404 and its homepage returned 403. These are unverified leads rather than documented products, and are not recommended based on a suggestive name.
- Direct exploratory Copart/IAAI developer/marketing paths produced denial, empty content or 404. They yielded no official API documentation. A guessed route is not evidence an official developer product exists or does not exist. No private web endpoint was reverse-engineered.
- A Google search returned only a script/redirect shell; a Bing query returned unrelated Microsoft results. Neither supplied reliable provider evidence, and no search snippet is used to support a vendor conclusion.

This review adds a useful documented candidate and excludes a newly read personal-only site as an immediate collection source. It does not purchase access, establish a provider relationship or complete the original 1.0 auction-access gate.
