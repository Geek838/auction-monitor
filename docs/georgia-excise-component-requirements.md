# Georgia excise component — supported planning subset

PO freeze: **30 October 2026 (Asia/Tbilisi)**. This extends the [official-source research](georgia-cost-evidence.md) with actual Revenue Service calculator UI results and primary Georgian statutory clauses. It authorizes implementation of one sourced component estimate. It does not establish total clearance, final customs liability, vehicle classification or full 1.0 readiness.

## Supported inputs and result

Only calculate when all eligibility facts are explicitly supplied and supported:

- Ordinary passenger car classified under NCNFEA **8703**, conventional petrol or diesel, non-hybrid and non-electric.
- Original left-hand steering, not converted; not sport, classic or special-purpose, and no exemption/special treatment claimed.
- Intended release for free circulation and registration in Georgia. Re-export, temporary admission, refund claims and unknown purpose are outside this subset.
- Actual **production year**, with an explicit known-production-year declaration. VIN model year must not populate this as verified production year. Production year is no later than declaration year; restrict age to 0–30 years to exclude classic vehicles over 30.
- Actual integer engine displacement in **cm³**, bounded 100–7,000 for this product subset. Litres rounded to a marketing engine size are insufficient. The source UI examples below use exact nominal litre selections corresponding to the stated cc; no compatibility or actual vehicle specification is inferred.
- Planned customs-declaration registration date within **30 October–31 December 2026**, under the current rules reviewed on 30 October. Do not offer historical January–September 2026 assessments: the current text contains 2026 amendments and those historical effective/transitional rules were not validated. Dates outside the reviewed planning window are withheld until a new rule review. A date window is an application support limit, not a claim that tax law expires then or that amendments cannot occur inside it.

Unknown facts and valid but unsupported selections return an explicit `WITHHELD` outcome and reasons, with no amount/rate substituted. Reject malformed numerical/date input separately. Do not default eligibility to yes. Store the submitted facts, actual calculation timestamp, source edition, review date and supported-policy version in the response.

For eligible inputs:

`age_years = declaration_registration_year − production_year`

| Age | Excise rate | Statutory basis |
| --- | --- | --- |
| 0–6 inclusive | GEL 1.50 per cm³ | Tax Code Article 188(12) |
| Over 6 within supported subset | GEL 4.50 per cm³ | Tax Code Article 188(13) |

`excise_component_gel = engine_displacement_cc × rate_gel_per_cc`

Use exact decimal arithmetic, return amount/rate as decimal strings and format the component to two decimal places. Article 188(18) supplies the production/declaration year definition. A user declaration is not independently verified by this calculation. Label the result **Excise component estimate** with its reviewed-rule date. Show a clear warning that a later law change or corrected vehicle facts can change the amount.

There is no import duty, VAT, clearance-service fee, registration charge, used-days/storage charge, shipping, repair cost, currency conversion or conditional refund in this result. Do not return a full clearance total or automatically fill/mark complete an existing budget category. The budget's Georgia-clearance category covers more than this component. Re-export refunds are not an up-front reduction.

## Primary law and date evidence

Read both official editions:

- [Georgian Tax Code publication 247](https://matsne.gov.ge/ka/document/view/1043717?publication=247): HTTP 200 on 30 October; the active publication selector explicitly shows **15/10/2026**. The bounded 4,000,001-byte HTML read is a **partial whole-document capture**, but contains the complete relevant Article 188 text. Do not claim the whole Georgian code was downloaded or reviewed. Local exact article excerpt: `.cache/georgia-evidence/2026-10-30/taxcode-247-ka-article188.txt`, SHA-256 `383461247e4d0f8143ff7ebe8fdf6cce5f98f3a0b0ff0ca3dfb58cdf2a964504`.
- [English Tax Code publication 247](https://matsne.gov.ge/en/document/view/1043717?publication=247): the relevant clauses were read in the earlier complete capture and reread on 30 October. The dates, age boundary, displacement rates and production/declaration-year wording agree with the primary Georgian clauses for this narrow rule. This is an engineering comparison, not a certified legal translation or review of every exemption.

Primary Georgian Article 188(12) says **“0-დან 6 წლის ასაკის ჩათვლით”** and **“1.50 ლარი ძრავის მოცულობის 1 სმ³-ზე”**: age zero through six inclusive and GEL 1.50 per cubic centimetre, unless otherwise established by the article. Paragraph 13 says **“6 წელზე მეტი ასაკის”** and **“4.50 ლარი”**: over six years and GEL 4.50. Paragraph 18 determines import age from **“საბაჟო დეკლარაციის რეგისტრაციის წელსა და მსუბუქი ავტომობილის გამოშვების წელს შორის”**: declaration-registration year versus production year.

Paragraphs 14–17 contain hybrid, right/converted steering and electric variants. Separate sport/classic and exemption provisions also exist. Excluding these cases is deliberate product scope; do not claim they pay the ordinary rate or zero tax.

## Actual official calculator UI validation

The PO exercised [RS Auto/Moto Levy Calculator](https://rs.ge/CarClearance-en) on **30 October 2026**. These are real UI calculations, not mocked responses, copied intermediary estimates or model-generated answers. The page's current manufacture-year default was 2026; there is no user-selectable declaration year. Results validate the **current 2026 context**, not every future or historical declaration date.

For every case the **Vehicle** tab was active; Hybrid, Electric, Right Wheel/Moved, Sport and Classic were unchecked; Used days was left blank. The visible **Manufacture Year** and **Engine** dropdowns were operated, then the visible **Calculate** button clicked. The page does not expose a separate petrol/diesel selector; conventional non-hybrid/non-electric cases are the evidenced UI branch, consistent with the statutory ordinary-car wording.

| Manufacture year | Engine UI (litres) | Equivalent cc | Age in 2026 | Observed excise GEL | Observed customs tax GEL | Observed page total GEL |
| --- | --- | --- | --- | --- | --- | --- |
| 2021 | 2.0 | 2,000 | 5 | 3,000 | 125 | 3,605 |
| 2020 | 2.0 | 2,000 | 6 | 3,000 | 130 | 3,610 |
| 2019 | 2.0 | 2,000 | 7 | 9,000 | 135 | 9,615 |
| 2026 | 2.0 | 2,000 | 0 | 3,000 | 105 | 3,585 |
| 2021 | 1.0 | 1,000 | 5 | 1,500 | 62.5 | 2,042.5 |
| 2021 | 1.5 | 1,500 | 5 | 2,250 | 93.75 | 2,823.75 |
| 2019 | 3.5 | 3,500 | 7 | 15,750 | 236.25 | 16,466.25 |

The customs-tax and total columns are **observed comparison context only**, not supported component outputs. For example the manufacture-2026 case returns customs tax 105 rather than a naïve 100, so copying a displacement-only duty formula would be unjustified. The page separately displays a 150 GEL vehicle-clearance charge and agency-service amounts. Their full applicability, time semantics and totals are not frozen by this excise work.

Screenshots and visible-text artifacts are under ignored `.cache/georgia-evidence/2026-10-30/rs-conventional-*.png`/`.txt`. The four age cases are in `rs-calculator-results.json`; the three displacement cases are in `rs-calculator-displacement-results.json`. Screenshots were visually inspected, including the age-seven output. The site's styled dropdowns update visible/custom selection state while the hidden native `<select>` retains its original default. Therefore the evidence is the operated visible controls and screenshot/result, not the stale hidden-select value.

Reviewable copies are retained with this repository: [age-six screenshot](evidence/rs-2026-10-30/rs-conventional-2020.png), [age-seven screenshot](evidence/rs-2026-10-30/rs-conventional-2019.png), [current-production-year screenshot](evidence/rs-2026-10-30/rs-conventional-2026.png), [captured age-case results](evidence/rs-2026-10-30/rs-calculator-results.json) and [captured displacement-case results](evidence/rs-2026-10-30/rs-calculator-displacement-results.json). These are dated observations of the official public calculator for engineering verification, not a tax assessment or permission to collect auction photographs. The screenshots are copied unchanged from the observed browser captures.

### Browser transport limitations and workaround

Unmodified Chromium initially showed `NET::ERR_CERT_AUTHORITY_INVALID` because its browser trust did not include the environment proxy CA. We did **not** ignore TLS warnings or disable certificate verification. A standard Node/Playwright request context used the configured HTTPS proxy and existing `NODE_EXTRA_CA_CERTS` trust, with `ignoreHTTPSErrors:false`, to relay actual browser requests/responses into the UI. The calculator runs used only `rs.ge`/`www.rs.ge`; third-party fonts/resources were blocked. The first ordinary page-load inspection allowed page-requested assets; no vehicle photos were requested. A direct no-proxy Node attempt failed `ECONNREFUSED`, then was configured to use the existing environment proxy.

No endpoint was invented, replayed or reverse-engineered; only the page's own requests after visible UI actions were relayed. No login, captcha, fiscal declaration, external message or purchase occurred. The calculation is an informational public UI operation, not submission of a tax declaration. Its font fallback may render warning-icon names as “error”/“exclamation”; those visible labels are not interpreted as a calculation failure when actual numeric result fields are populated. If an official request is denied, stop rather than bypass its response.

## Engineering acceptance

1. Encode the seven observed excise results as source-backed regression cases, separately from generated unit boundaries; rate transition age six to seven is mandatory.
2. Cover missing facts, contradictory/unsupported classification, hybrid/electric, right/converted steering, special vehicles, exemptions, re-export/unknown purpose, outside-review date, future/unknown production year, cc units/bounds, strict integers and string money.
3. Browser tests must require explicit eligibility choices and actual production-year declaration; no VIN model-year shortcut or silent budget mutation. Editing facts invalidates the result and late responses cannot restore stale output.
4. Always show component-only meaning, versioned official sources and incomplete wider costs. No numerical “full clearance” or “safe to bid” implication follows.
5. Record actual executed API/browser validation separately from authored tests and these live official UI cases. Keep broader release gates in [readiness](v1-release-readiness.md).
