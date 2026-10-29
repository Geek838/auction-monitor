# Georgian clearance — official-source evidence

Reviewed **29 October 2026 (Asia/Tbilisi)** by the PO agent. Bounded, ordinary HTTPS reads only: no login, vehicle submission, calculator result, unpublished tax API, supplier contact or payment. This is source research, not a legal opinion, implemented tax engine or current quote for a particular car.

## Retrieved sources

| Official source | Access and relevant evidence |
| --- | --- |
| [Revenue Service Auto/Moto Levy Calculator](https://rs.ge/CarClearance-en) | HTTP 200, 50,099 bytes. The page says the service provides payable clearance fees after the user selects the relevant fields and clicks Calculate. Much of the input UI is dynamic and Georgian despite the English route. No calculation was submitted. |
| [Revenue Service legislation](https://rs.ge/Legislation-en?cat=1&tab=1) | HTTP 200, 35,489 bytes. Official navigation separates tax, customs, legislative acts and resolutions and links the RS information hub. The page itself does not provide a complete vehicle formula. |
| [Matsne Tax Code, English publication 247](https://matsne.gov.ge/en/document/view/1043717?publication=247) | HTTP 200, complete 3,112,321-byte HTML. Document No. 3591, issuer Parliament of Georgia. The retrieved English publication selector identifies **15 October 2026**, publication 247. The first bounded general-page read was partial; this explicit-publication read was complete. Relevant clauses were read, not every provision independently adjudicated. |
| [Interior Ministry Service Agency](https://www.sa.gov.ge/) | HTTP 200; official vehicle-registration/service navigation is readable. It is a separate source for registration procedures and charges. No actual registration service or complete fee table was executed/validated. |

## What is established

- The RS calculator exposes separate hybrid, electric, right/converted-steering, sport and classic selections, plus year/engine fields. A simple percentage of purchase price is not a demonstrated substitute for these inputs.
- In the retrieved Tax Code, **Article 188(12–18)** provides motor-car excise rules for commodity item 8703, including age/engine-displacement rates, hybrid and steering variants, an electric/right-or-converted-steering case and an age definition. Article 188(9–10) has separate sports/classic provisions.
- For example, Article 188(12–13) states GEL 1.5/cm³ for age 0–6 and GEL 4.5/cm³ above six years, subject to that article's other rules. These are observed statutory clauses, **not a universal clearance estimate** or a copied application default.
- Article 188(18) bases import age on customs-declaration registration year minus **production year**. A VIN decoder's model year must not silently become verified production year.
- **Article 197(6)** provides an engine-displacement/years-of-operation import-duty rule for qualifying 8703 cars. Applicability and exemptions must be checked before calculation; the general 12% list in the same article is not automatically the car's rate.
- **Articles 189(8) and 198(3)** describe conditional refunds after release for free circulation and subsequent export/departure within 180 calendar days. They do not make every vehicle marked “re-export” automatically tax-free or turn a conditional refund into immediate zero cash outlay.
- The RS page warns about additional Service Agency charges and names declaration, export-inspection, transit-plate, registration-certificate, state-plate and inspection-act services. These must not disappear from an all-in budget because excise was computed.

## Implementation decision for this release

**Keep the current budget's clearance and registration amounts user-declared and sourced.** Official rules are available, so “no official formula exists” would be false. However, this research has not validated the complete classification, exemptions, effective-date, import-purpose, VAT and agency-charge matrix against official calculator outcomes. No automatic Georgian tax result is implemented or verified by this document.

The blank RS page's displayed zero amounts are placeholders, not a vehicle-specific zero-tax result. Do not infer a flat VAT/duty rate from an import intermediary or apply a general statutory rate without checking the vehicle/procedure exclusions. The English publication was retrieved; primary Georgian text and language equivalence were not separately compared.

## Next owned engineering work

1. PO/technical lead freeze a supported tax subset with the relevant official clauses and effective versions; cover registration versus re-export, classification and exemptions explicitly. Preserve unknowns outside that subset.
2. Add actual required inputs, including production/declaration year, displacement, drivetrain/steering and procedure; a decoded VIN alone does not establish them all. Specify GEL arithmetic and dated USD conversion separately.
3. Validate boundary cases and total cash outlay against permitted official calculator/manual outcomes and the Service Agency fee source before enabling an automatic tax estimate. Document refunds separately from upfront payments.
4. Keep all such work with the team; no tax research task is assigned to the client. A reviewed sourced amount can still be used in the current planning budget without pretending the application independently verified it.

The new free NHTSA VIN flow is a separate metadata capability under technical validation. It neither establishes original auction identity nor supplies the complete Georgian tax facts or a customs assessment.
