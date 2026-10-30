# Additional Georgia excise cases — 31 October 2026

The team checked the official [Georgian Tax Code publication 247](https://matsne.gov.ge/ka/document/view/1043717?publication=247) and its [English edition](https://matsne.gov.ge/en/document/view/1043717?publication=247), Article 188(14–16), against actual selected inputs in the official [Revenue Service calculator](https://rs.ge/CarClearance-en). This is a planning component from user declarations, not a customs assessment or a complete clearance calculation.

Article 188(14) reduces the age 0–6 rate for left-hand-drive hybrids by 60%. Articles 188(15–16) triple the base rate for right-hand drive or converted steering. Supported combinations are deliberately narrow: ordinary 8703 passenger petrol/diesel cars, or original-left-drive hybrids aged 0–6, with all other previously required eligibility facts. A hybrid over six years old or with right/converted steering remains withheld, as do electric, special/exempt, re-export and otherwise unsupported cases.

On 31 October 2026, the current-year official calculator produced the following results with 2,000 cm³ and the corresponding option checked. The observed older hybrid result is recorded for completeness, but remains excluded from the application subset.

| Production year | Option | Observed excise GEL |
| --- | --- | --- |
| 2021 | Hybrid | 1,200 |
| 2020 | Hybrid | 1,200 |
| 2019 | Hybrid | 9,000 |
| 2021 | Right wheel/moved | 9,000 |
| 2019 | Right wheel/moved | 27,000 |
| 2021 | Neither | 3,000 |

[Captured UI results](evidence/rs-2026-10-31/calculator-results.json) and [actual checkbox states](evidence/rs-2026-10-31/selected-controls.txt) document these observations. The checkbox state array follows the page's hybrid, electric, right/moved, sport, classic and additional order. Inputs were operated through the public browser UI, using the environment's trusted proxy CA and without ignoring TLS errors. No login, fiscal submission, third-party price collection, undocumented endpoint or bypass was used. One initial attempt clicked only the visible text rather than the control; its results are excluded. Exact production year and engine displacement remain user-supplied and unverified. The 31 December 2026 application review horizon, the unknown remaining duties/fees, and no automatic budget insertion remain unchanged.
