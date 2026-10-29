# Budget planning — requirements for the next release increment

PO/technical scope, **29 October 2026 (Asia/Tbilisi)**. The client authorizes work toward the finished product and requires **no spending on APIs**. The [handover](auction_intelligence_handover.md), especially §§4, 7–10, supplies the product direction; the specific calculator contract below is the implementation scope selected by the technical lead. It does not establish price evidence, a tax rule or completion of 1.0.

## Buyer outcome

A buyer can enter an assumed hammer bid and their dated repair/import quotes or explicit assumptions, see a reproducible low/base/high USD planning total, identify missing costs, and calculate a bid ceiling only within the supplied scenario's limits. No LLM performs arithmetic. No repair, fee, tax, exchange-rate or resale-price value is filled from an invented source.

The visible label is **USER-SUPPLIED PLANNING SCENARIO**. A quoted value means the user declares a quote; the server does not verify its supplier, vehicle compatibility, current market value or commercial validity. Results are not a professional repair estimate, an official customs assessment or a market-validated bid recommendation.

## Build-now contract

| Input | Required behavior |
| --- | --- |
| Currency | USD only in this increment. GEL conversion and currency mixing are not implemented or silently assumed. |
| Hammer bid | Non-negative decimal string in dollars, with at most two fraction digits; no JSON number, exponent, comma, currency symbol, infinity or NaN. |
| Cost rows | Bounded list with category, label, ordered `low <= base <= high`, source kind `QUOTE` or `ASSUMPTION`, source, `as_of` and optional expiry. Missing source/date makes either kind incomplete; QUOTE also needs an explicit validity end date. Every range uses exact decimal arithmetic. |
| Cost coverage | Account for `auction_broker`, `us_transport`, `ocean_port`, `georgia_clearance`, `registration`, `parts`, `labor`, `diagnostics`, `contingency`, and `other`, through rows or an explicit not-applicable reason. Unknown is not zero. |
| Auction fees | Separate user-supplied bid-dependent fee schedule with contiguous tiers from zero through an unbounded final tier; each tier supplies a flat amount and percentage. The `auction_broker` row covers broker/other fixed fees only and must not duplicate that schedule. |
| Market value | Optional user-supplied conservative USD value; it is not a looked-up comparable or authenticated resale valuation. Its assumed provenance remains visible. |
| Savings / reserve | Explicit required savings and extra risk reserve, shown separately; omission withholds the ceiling and zero must be deliberately entered. A zero setting does not establish that no risk exists. A contingency row and extra reserve are additive; avoid duplicate entry. |

Requests have bounded list/text/number sizes, strict extra-field rejection and a pre-parse JSON size limit. Responses preserve decimal strings, source classifications, missing/expired evidence, fee basis and the distinction between a subtotal and a complete total. Submitted source URLs are references only; the API never fetches them.

## Acceptance criteria

| ID | Behavior | Acceptance |
| --- | --- | --- |
| B1 | Exact arithmetic | Sum ranges with decimal-safe conventional code; round monetary fee results to cents using the documented rule. `0.10 + 0.20` produces `0.30`. |
| B2 | Known subtotal and completeness | Missing categories, absent fee schedule or unusable quoted evidence produces an explicit incomplete state. Known rows may have a subtotal, but an incomplete subtotal cannot be labelled all-in cost. |
| B3 | Evidence classification | Keep QUOTE and ASSUMPTION distinct. Missing quote source/date, future dates, expiry and stale evidence receive explicit validation/status behavior. No public-source or live-price claim follows from a client field. |
| B4 | Fee-dependent totals | Evaluate supplied fees at the hammer bid; disclose the fee and avoid adding it again as a fixed cost. Tier boundaries and rounding are deterministic. |
| B5 | Conservative ceiling | Use supplied conservative market value minus the high non-bid costs, required savings and extra risk reserve. Solve for the greatest cent-valued bid whose bid plus auction fee fits; do not subtract fees calculated at a different bid. |
| B6 | Abstention | Missing market value, critical costs, usable fee schedule or required evidence withholds a confident bid number. Assumption-only inputs may support explicitly indicative totals; they do not become a recommended maximum bid. No feasible positive budget has its own reason rather than an invented profitable deal. |
| B7 | Clear UI | Empty means unknown. Source/date fields and fee assumptions are editable. Show low/base/high with completeness reasons, stated input provenance and visible reserve/savings breakdown. Do not show a success badge merely because arithmetic ran. |
| B8 | Export / edits | Export the scenario and calculation with its declared evidence and assumptions. Editing any input clears the old result and rejects late responses. Preserve existing manual-photo and fixture workflows. |

The backend response contract uses `status=COMPLETE|INCOMPLETE`, `known_non_bid_totals`, `known_total_at_bid`, nullable `total_at_bid`, explicit issues/missing categories and `max_bid.status=INDICATIVE|WITHHELD|NO_FEASIBLE_BID`. COMPLETE only means the supplied scenario has covered categories and usable declared evidence. A computed ceiling is always INDICATIVE, including with QUOTE inputs, because market value and evidence remain user supplied. Missing market value, required savings or extra reserve withholds it. The execution report, not these requirements, establishes which checks actually passed.

## Fee and solver rules

- Tier starts are inclusive and ends exclusive. The selected tier fee is `flat + entire hammer bid × percent / 100`, rounded HALF_UP to cents; percentages are not marginal/progressive rates on portions of the bid. Coverage starts at zero, has no gaps/overlaps, and ends with an unbounded tier. Reject invalid bounds, negative rates and unsupported percentages.
- The total acquisition function must be monotonic, including flat/percentage transitions and cent rounding. Reject downward fee jumps rather than applying binary search to a non-monotonic schedule.
- The solver uses high-range non-bid costs for the conservative case and checks the resulting cent bid plus its own applicable fee. Verify the returned bid fits and the next cent does not, where within the search limit.
- Return no feasible bid when the fixed costs/reserve/savings already consume the supplied market value. Do not describe `0.00` as a profitable recommendation.
- Fees are user-supplied, not official Copart/IAAI schedules. Do not infer a house's fees from a website identifier, subscription tier or synthetic fixture.

## Evidence and tax boundaries

The calculator can record a user's sourced Georgian clearance amount or assumption. It does not implement current Revenue Service formulas, choose registration versus re-export rules automatically, authenticate quotes, select OEM parts or infer repairs from images. Do not hardcode percentages copied from import intermediaries. Parts compatibility, supplier/labor evidence, source freshness, official taxation and actual repair-outcome validation remain [1.0 readiness work](v1-release-readiness.md).

Amounts associated with different currencies are not accepted as USD by relabelling. No FX default is supplied; USD/GEL display requires a separately dated conversion source and tested conversion semantics in a later increment.

## Verification and completion

Required meaningful checks: strict money/range validation; missing versus explicit zero; duplicate/not-applicable coverage; quoted versus assumed/expired evidence; cent arithmetic; fee boundary/coverage/monotonicity; maximum feasible cent; absent value and no-feasible-budget states; bounded inputs and no outbound source fetching. Browser checks use the actual API and exercise incomplete and complete scenarios, editing, export, keyboard operation and mobile layout. Any demonstration prices are clearly synthetic engineering inputs.

Done means a runnable tested **user-supplied planning calculator** with accurate documentation and direct Windows commands. It does not mean supplier-backed Georgian estimation, validated bid intelligence, free live auction data or the full automatic 1.0 product is delivered. No paid API account, scraper, new tax table, external outreach, account system or payment flow is required for this increment.
