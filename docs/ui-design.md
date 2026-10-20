# Sprint 1 interface specification

Auction Intelligence helps buyers in Georgia establish the exact auction identity before making a purchase decision. This prototype resolves fixture records only. It must feel like a careful inspection worksheet: quiet, legible, and factual. The working name is temporary. English is the prototype language; Georgian localization remains an open product decision.

## Visual direction

Use warm paper, dark ink, fine rules, and generous typography. Avoid gradients, glossy glass, stock vehicle photos, ornamental dashboard charts, decorative AI symbols, pill navigation, and repeated elevated cards. There is one task, one form, and one evidence sheet. Do not imply that damage assessment or valuation is available.

Tokens:

| Token | Value | Use |
| --- | --- | --- |
| Paper | `#F4F1E9` | Page background |
| Sheet | `#FFFEF9` | Input and result background |
| Ink | `#202820` | Primary text |
| Muted | `#596153` | Supporting text |
| Rule | `#CBCDBF` | Dividers |
| Olive | `#40513B` | Main button and focus |
| Olive pale | `#E8EDDF` | Corroborated identity |
| Rust | `#A04826` | Mock indicator and errors |
| Rust pale | `#F8EADF` | Mock notice |
| Amber | `#805A16` | Ambiguous/unresolved text |

Use Georgia or another locally available serif for the main heading, a system sans-serif for interface text, and a system monospace for IDs/VINs. No external font fetch is required. Heading: `clamp(2.5rem, 5vw, 4.5rem)`, line-height 1.05, weight 400, letter-spacing -0.035em. Body: 16px/1.6. Labels: 13px/1.4, semibold. Metadata labels may use restrained uppercase with 0.08em tracking. Do not uppercase paragraphs. Border-radius 3–6px, no box shadows. Use a 4px spacing scale, primarily 8/16/24/32/48/64px.

## Layout

Desktop content width: 1120px with 32px horizontal padding. Mobile: 20px. Header is a thin ruled row: a small simple geometric mark and working name on the left, `Resolver / Sprint 1` on the right. No navigation links to future functionality.

Main introduction begins 64px below header. A small eyebrow reads `VEHICLE IDENTITY, FIRST`. Main heading: `Start with the exact vehicle.` A short description below: `Paste a Copart or IAAI listing link to check its auction identity before you go further.` A small side note on wide screens can read `Built for buyers importing to Georgia.` It must not promise cost analysis.

A full-width, high-contrast notice follows: **`Mock data environment`** — `Results use test fixtures. No live auction data or inspection advice is provided.` Keep this visible before and after every submission.

Form label: `Copart or IAAI listing URL`. Placeholder: `https://www.copart.com/lot/51374586`. Field and button are one horizontal row on desktop, stacked on mobile. Button: `Resolve listing` (more accurate than “Analyze vehicle” in Sprint 1). Input must be at least 48px high and have an explicit label. The user can press Enter. Under the field: `Supported sources: Copart and IAAI. Your link is parsed without opening the auction page.`

Present 2–4 actual fixture examples as understated text buttons. Examples must come from implemented fixtures, not invented IDs. Labels should expose the expected state, e.g. `Try a matched Copart fixture`, `Try an IAAI page reference`, `Try an ambiguous fixture`. Clicking populates the field; submission should be explicit unless the behavior is clearly labeled `Load … example`. Include a small supported-format explanation in a native `details` block only if needed.

Result uses the full available width under a horizontal rule. A small row reads `RESOLUTION RESULT` with status text. Use a definition list for data, not a dashboard grid. On desktop, use two columns of facts; on mobile, a single column. Allow long URLs and VINs to wrap without horizontal page overflow.

## Matched evidence sheet

Title: `[year] [make] [model]` with missing fields omitted. If make/model are both missing, use `Vehicle identity resolved` rather than fabricating a title. Header includes `Exact auction identity matched`, `MOCK`, and a separate `ARCHIVED` when applicable. Mock describes origin, archived describes auction state; they are independent.

Prominent facts:

- Auction: `Copart` or `IAAI`.
- Canonical ID: `Lot number` for Copart, `Stock number` for IAAI.
- Submitted reference: show raw listing/page identifier separately from canonical ID.
- VIN: actual value or `Not supplied`.
- Auction status: supplied value or `Not supplied`.
- Auction event date, when supplied.

Below facts, include `Why this record matched` and a short list of actual backend evidence. Never invent a VIN verification if VIN was absent. List provider name, retrieval timestamp with timezone, data license scope, and source link when supplied and validated. Use `Retrieved … UTC`; retrieval time does not establish freshness of the auction event.

If archived: prominent copy `Historical auction record. This does not show a current listing or current bid.` Do not render a monetary field as “current bid.” If photos are absent: a small `No licensed photos supplied` line; do not use a generic car photo. The absence of photos should not overwhelm identity information.

## States and precise copy

| State | Heading | Supporting copy / action |
| --- | --- | --- |
| Empty | No result panel | Form and fixture notice are sufficient; avoid empty decorative panels. |
| Loading | `Checking the listing identity…` | Button says `Resolving…`; prevent duplicate submissions and announce progress. Retain submitted URL. |
| Invalid URL | `This link cannot be resolved` | Display specific parser reason. Hint: `Use a direct Copart or IAAI listing URL.` Input has `aria-invalid` and message association. |
| MATCHED | `Exact auction identity matched` | Present evidence sheet. Add no safety or buying recommendation. |
| AMBIGUOUS | `We could not confirm one exact match` | `Conflicting or multiple records need verification. No vehicle has been selected.` Present candidates as a static list with source/lot/stock/VIN/conflict evidence. No “select nearest” control. |
| NOT_FOUND | `No fixture record found` | In fixture mode: `This link was parsed, but our test dataset has no matching record. It does not tell us whether the auction listing exists.` |
| UNRESOLVED_ID | `The IAAI stock number is not confirmed` | `This link contains an internal page ID. We cannot treat it as a stock number without provider evidence.` Show page ID labeled explicitly. |
| SOURCE_UNAVAILABLE | `The data provider is unavailable` | `We could not complete verification. Try again later.` Do not classify as no record. |
| NOT_AUTHORIZED | `Authorized data access is not available` | `This provider is disabled until commercial access is agreed. You can continue with fixture examples.` |
| Transport failure | `We could not reach the resolver` | `Check that the API is running and try again.` Preserve field and allow retry. |

Use actual backend reasons after mapping them to readable text; do not show Python exceptions or stack traces. When a new submission begins, clear the previous result so it cannot be mistaken for the new URL. Retain user input after error. Separate URL validation from provider outcomes.

## Accessibility and interaction

Use `header`, `main`, `form`, semantic headings, labels, and definition lists. Announce loading and completion with a persistent `aria-live="polite"` region; use `role="alert"` for submission errors. Move keyboard focus to the result heading after completion only when it improves navigation and does not disrupt typing. Never rely on green/amber/rust alone: every state has visible words.

Buttons and links have at least 44px usable target areas; keyboard focus has a 3px olive outline with 3px offset. Support 200% zoom and a 320px viewport. Keep body lines under roughly 75 characters. Respect `prefers-reduced-motion`; no animation is necessary. External source links must have clear accessible labels, no tracking additions, and `rel="noopener noreferrer"` when opened in a new tab. All content from providers is rendered as text, never HTML.

## Acceptance review

Review at 390px and 1440px widths and with keyboard-only use. Confirm the mock notice remains unmistakable in screenshots of every outcome. Confirm IAAI page ID and stock number have different labels even when strings happen to coincide. Confirm historical records never imply live freshness, no absent data is guessed, and no repair/cost/login/payment affordances appear.
