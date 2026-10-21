# Georgian importer and repair-business discovery

Implements S2-08; sources: handover §§2–3, 11–13 and [Sprint 2 requirements](../sprint-2-requirements.md). Target: **at least five completed interviews** with Georgian importers and/or repair businesses. No interviews, recruitment or outreach have occurred in this work. This guide is not evidence of demand, willingness to pay, or usability success.

## Recruitment and consent preparation

Assign a research owner and approved recruitment channel before contact. Record business-role mix and selection limitations without inventing a quota split. Business interviews do not establish individual-buyer behavior. Ask language preference and arrange an agreed language; the English prototype is not proof of Georgian-localization readiness.

Before each interview, explain the identity-resolver prototype and research purpose, voluntary participation, note-taking use, storage/access/retention, and withdrawal route. Get consent for notes; obtain separate consent before recording. Do not collect recordings by default. Use a pseudonymous participant ID; keep names/contact/business identifiers in a separate restricted key outside Git.

Suggested opening: “We are learning how importers and repair businesses evaluate damaged auction vehicles before a purchase. There are no right answers. We will ask about real past work and show an optional clearly labeled test-data prototype. It does not inspect damage or estimate costs.”

## Neutral discussion guide

1. **Role and recent work:** What is your role in sourcing, importing or repairing vehicles? Walk through the most recent relevant purchase or repair from first listing to completion. What information did you have at each decision?
2. **Identity:** How did you verify the auction source, lot/stock, VIN and sale event? What happens if an IAAI page identifier differs from the stock number? Describe a case with conflicting, missing or historical data.
3. **A costly mistake:** Tell us about a purchase or repair that went differently from expected. What evidence was missing, and what could realistically have changed the decision? Avoid implying a tool could see hidden damage.
4. **Quotes and costs:** How do you obtain parts and labor quotes, check compatibility and date/currency, and handle uncertainty? What gets omitted from invoices? Ask about actual examples without requesting private documents during the interview unless a separate approved collection process exists.
5. **Georgia workflow:** Which steps differ for Georgian registration versus re-export? Who verifies transport/clearance assumptions? Where do stale prices or rule changes cause difficulty? Do not present unverified tax advice.
6. **Trust and action:** What evidence would make you trust or reject a listing identity or an estimate? Which unknowns require a specialist? What would make you stop a bid rather than accept an uncertain number?
7. **Optional fixture comprehension:** Explain that all shown vehicle records are synthetic. Ask the participant to resolve a supplied fixture, then explain MOCK, archived, matched, ambiguous and unresolved in their own words. Ask what they think the product has and has not verified. Do not coach the answer first. Do not paste private/live records or claim live access.
8. **Adoption and value:** What tools do you use now, and what would make switching worthwhile? What evidence or workflow improvement is missing? Explore willingness to pay only as an uncommitted hypothesis after understanding current spend and alternatives; do not anchor with handover example prices or promise payment features.
9. **Data sharing and close:** Under what conditions could a business lawfully share itemized repair evidence? Who owns the records/photo rights? Would a separate, consented follow-up be appropriate? Do not treat willingness to talk as permission to collect or reuse data.

Ask for concrete past behavior before hypothetical preferences. Preserve disagreement and negative feedback; do not lead participants to endorse AI analysis or a preselected provider.

## Private notes template

Copy into the approved restricted research location; do not commit completed participant records here.

| Field | Record |
| --- | --- |
| Session | Pseudonymous participant ID, date, role, recruitment/language context, researcher |
| Consent | Notes consent reference; recording consent/state separately; withdrawal/storage/retention policy references |
| Workflow evidence | Recent event and decision steps; current tools; identity verification; quote/clearance evidence; observed friction |
| Comprehension | Participant's own explanation of mock/historical/matched/unresolved; observed action versus researcher interpretation |
| Value and barriers | Current alternatives/spend where volunteered, adoption constraints, language/evidence needs, uncommitted pricing hypotheses |
| Contradictions | Counterexamples, uncertainty, missing context and interviewer influence |
| Follow-up | Separately agreed follow-up only; no unapproved contact/collection; evidence IDs rather than contact details |

Use quote IDs only if consent and sharing scope allow quotations. Summaries should omit identifying business and vehicle details unless essential and approved.

## Synthesis and completion

| Finding ID | Observed problem/behavior | Supporting session IDs and count | Contradictory evidence | Confidence/limits | Proposed backlog change | Owner/decision |
| --- | --- | --- | --- | --- | --- | --- |
| _blank template_ | | | | | | |

Record invited, consented, completed and withdrawn counts separately. A draft guide or five scheduled sessions does not meet the five-completed-interview target. Distinguish observed behavior from self-report and interpretation. Any proposed product change needs review against sprint scope; interview findings do not automatically authorize AI, financial or payment work.
