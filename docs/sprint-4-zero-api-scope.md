# Sprint 4 — usable review without paid APIs

PO scope update, **22 October 2026 (Asia/Tbilisi)**. The user requires no spending on APIs and wants development to proceed. This supersedes the paid-access assumption in the provider-discovery recommendation; it does not establish free commercial source access. The [handover](auction_intelligence_handover.md) remains the long-term product direction.

## Decision

Build an integrated **user-supplied vehicle review** now: accept a supported auction reference, manually supplied vehicle details, browser-local photos and the user's own evidence-linked notes; produce a clearly unverified review that can be exported and printed. This gives the application useful behavior with real user inputs without buying API access or inventing an auction record. Keep existing fixture resolution and authored MOCK previews available and clearly separate.

This is a practical fallback, **not completion of the original automatic URL-to-AI inspection product**. The app must not advertise that it fetched the auction listing, verified the vehicle or analyzed photographs. Entering review details is ordinary product use; the client is not assigned provider research, integration design or development.

## Zero-cost access evidence

The PO re-read these official pages on 22 October using bounded HTTPS GETs; no account, API call, auction search, photograph collection, outreach or payment was made. Earlier detailed [provider findings](research/provider-findings-2026-10-22.md) and [Auto.dev feasibility](research/auto-dev-feasibility-2026-10-22.md) remain relevant.

| Route | Current official evidence | Decision |
| --- | --- | --- |
| Auto.dev Free | [Pricing](https://auto.dev/pricing) offers $0 and 1,000 monthly calls; [terms §4.4](https://auto.dev/terms) explicitly exclude production systems serving end users. Reviewed endpoints do not establish exact Copart-lot or IAAI-page mapping. | Real evaluation allowance, not a demonstrated free production resolver; no registration or activation |
| Auto.dev paid trial | Current terms describe a $1 trial plus standard metered API fees | Excluded by zero-paid-API requirement |
| Qopart free VIN UI | [FAQ](https://qopart.az/faq) says technical VIN information can be viewed free through its linked [VIN Decoder](https://qopart.az/vin-decoder) | A free consumer page does not establish an automated-data license, listing/event match or photo rights; no VIN submitted |
| Qopart agent program | [Agent page](https://qopart.az/become-agent) describes earning commission; [Georgian terms §9](https://qopart.az/ge/terms) require prior permission for the specified commercial bulk collection | Referral program is not an offered free data feed |
| Bid.Cars / Stat.vin | Reviewed terms do not grant this product ordinary website-data reuse; Stat.vin limits the website license to personal/non-commercial use | No free authorized production feed established by reviewed sources |
| motor.pl / West Motors | Earlier responses were unavailable/browser-check content | Still unassessed; do not treat inaccessible pages as evidence of no free service |

**Bounded conclusion:** no reviewed route establishes a zero-cost, authorized exact-auction URL resolver for this product. This is not proof no such route exists. Provider research stays with the PO and technical lead; commercial contact drafts remain unsent. No new network-setting task is assigned to the client in order to ship this fallback.

## Build-now stories and acceptance criteria

| ID | Deliverable | Acceptance |
| --- | --- | --- |
| Z4-01 | Clear independent entry to user-supplied review | Available without a provider match or API key; never silently replaces a failed lookup; persistent **USER-SUPPLIED / UNVERIFIED** provenance |
| Z4-02 | Supported URL and vehicle inputs | Existing safe parser validates Copart/IAAI URLs without fetching; identifiers remain strings; VIN syntax validation is not identity verification; conflicting typed Copart lot/reference is rejected or explicitly flagged |
| Z4-03 | Browser-local photos | Bounded JPEG/PNG selection, actual browser decoding and useful failure messages; gallery and note/image navigation; no photo bytes or base64 sent to the backend or external service |
| Z4-04 | User-written evidence notes | Explicitly authored by the user; any OBSERVED/SUSPECTED wording describes what the user reported, not an application/model observation; no automatic visible findings or invented severity/confidence |
| Z4-05 | Honest report and physical checks | Show reference, user details, user notes, evidence identifiers and limitations; generic physical checks are identified as checks, never a diagnosis; no roadworthiness/all-clear statement |
| Z4-06 | Export and print | Download readable machine-readable review data and provide a readable print view with unverified/source labels retained; explain whether photo pixels are included or only referenced; do not imply JSON retains images if it does not |
| Z4-07 | Tests and reproducible delivery | Backend contract tests, actual API-backed desktop/mobile browser flows, relevant regression suite and direct PowerShell commands; report executed results and remaining limits |

### Identity boundary

- A parsed Copart lot is a URL reference, not a provider-confirmed listing. User-entered lot, VIN, make/model/year and event details remain claims even when mutually consistent.
- For IAAI, preserve original page ID and country independently of any user-supplied stock. A typed stock number is not independent mapping evidence. Equal-looking numbers must not become a verified mapping.
- Use a separate manual-review contract/status; do not relax resolver `MATCHED` semantics, overwrite provider evidence, fabricate record/event IDs or mark manual data `LICENSED`/`MOCK`.
- Never attach real user photos to the existing authored-fixture inspection scenario or release seeded findings for them.

### Photos, notes and lifecycle

- Explain before selection that photos stay in the current browser view. No model, external image fetch, OCR or photo upload runs. The user should select photos they are entitled to process; the product does not grant copyright or inference rights.
- File count/bytes and decoded dimensions must be bounded in implementation and documented. Reject unsupported, invalid and over-limit files. Do not accept arbitrary image URLs, HTML or executable image content.
- If preparation changes pixels or strips metadata, record the prepared image's actual digest separately from any original digest; make the recorded hash meaning explicit. Do not imply the server verified bytes it never received. A declared digest is integrity metadata, not independent proof of vehicle identity.
- Notes and captions are untrusted text. Render/print/export them safely; no generated HTML or pasted instructions may execute scripts, alter permissions or trigger network fetches.
- Changing relevant vehicle, photo or note inputs invalidates a prior report; discard late responses for the old input. Provide a clear reset that removes the review and releases app-owned object URLs. Do not promise secure deletion of browser caches or downloaded copies.
- No shared server history, automatic persistence, public photo publication or report database is required. The browser's metadata request may contain only the bounded declared review fields; do not log unrestricted vehicle notes or photo payloads.

### Safety and honesty

The report records a user's review, not a qualified inspection. Structure, SRS/airbags, ADAS, cooling, suspension and mechanical function cannot be established by this workflow. Relevant professional examination remains recommended. No costs, parts quotes, taxes, maximum bid, false confidence percentage or unsupported hidden-damage conclusion is generated. User-entered safety claims must not become application-endorsed conclusions.

## Verification required

- Valid Copart and IAAI manual workflows; missing optional fields, distinct page/stock identifiers and leading-zero preservation. Invalid URLs and conflicting claims cannot become a verified match.
- Strict bounded API input/output and extra-field rejection; no arbitrary path/URL/image-payload fields; API tests deny outbound network access.
- Photo bytes stay browser-local: inspect requests, decoded preview behavior and failure states; linked notes refer only to the selected review's images. Test duplicate/dangling references and declared-hash labeling at the metadata boundary.
- Editing/resetting clears old report content; delayed old responses never appear under changed details. Exercise download content, print visibility, keyboard operation and mobile wrapping.
- Hostile notes/captions render literally; unsupported file types, corrupt/over-limit inputs and image replacement fail safely. No expected error silently produces fixture content.
- Preserve Sprint 1–3 parser/provider/freshness/MOCK-preview checks. Any controlled browser interception is identified as a test double, not evidence of real data access or AI quality.

## Completion and future direction

Done means the manual review works end to end with real user inputs, documented limits, meaningful executed tests and runnable local commands. Report it as **user-supplied review delivered; automatic live-data lookup and AI analysis remain unavailable**. Do not count requirements writing or example screenshots as implementation.

No paid API usage does not mean zero hosting, storage or compute cost. An optional local vision model needs an actual model/license choice, installed weights, hardware bounds, secure invocation and quality evaluation; none is implied installed by this scope. Local inference and any free authorized data source are later concrete engineering decisions, not flags that turn the current manual workflow into AI.
