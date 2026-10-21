# Sprint 2 delivery and outstanding evidence

Delivery tracker for [Sprint 2 requirements](sprint-2-requirements.md). The offline development slice is implemented and verified; broader business targets remain incomplete. This tracker separates those results from preparation artifacts and real-world execution. See the [executed test report](sprint-2-test-report.md).

| Requirement | Prepared/implemented deliverable | Current completion claim | Remaining evidence/action |
| --- | --- | --- | --- |
| S2-01 provider feasibility | [Assessment, rights register and question templates](research/provider-assessment.md) | Preparation complete; candidates remain unverified | Assign business/rights owners; separately authorized outreach; obtain and assess written capabilities/rights; record recommendation |
| S2-02 provider policy | [Static policy and closed registry](../services/api/app/providers/policy.py), [contract ADR](decisions/002-provider-contract.md) | Implemented and verified offline | Written terms, provider documentation and required credentials still absent; real adapter remains disabled |
| S2-03 identity evidence | Typed mapping/reference origins, exact country/page/stock checks, record/event IDs | Implemented and verified with synthetic evidence | Actual provider channel independence and real coverage remain unverified |
| S2-04 provider/freshness UI | Selected context across outcomes; distinct data/authorization/age labels | Implemented and verified in three actual offline configurations | No claim of licensed data or live feed; future integration needs real metadata semantics |
| S2-05 lifecycle/outbound | Validated use/TTL/retention policy, no persistent cache; [lifecycle/security ADR](decisions/002-provider-contract.md) | Guard checks implemented; lifecycle/outbound design documented | No network client or storage/deletion service implemented; provider-specific terms/destinations remain unknown |
| S2-06 identity feasibility | [Protocol and manifest templates](research/identity-study.md) | Preparation complete; **0 real cases executed** | Approved access and ground truth; 50 real diverse links (20+ Copart, 20+ IAAI); adjudication/report |
| S2-07 repair cohort | [Consent/eligibility and manifest templates](research/repair-cohort.md) | Preparation complete; **0 accepted examples** | Authorized recruitment and per-use rights; 20+ accepted completed repairs/invoices; restricted evidence review |
| S2-08 local discovery | [Interview guide, notes and synthesis templates](research/interview-guide.md) | Preparation complete; **0 completed interviews** | Assign research owner/consent plan; five+ Georgian business interviews and synthesis |
| S2-09 regressions | 190 pytest tests; 48 desktop/mobile browser checks; TypeScript and production build | Passed locally on Linux; includes all existing Sprint 1 regressions | Hosted CI not observed; browser coverage is Chromium only |
| S2-10 Windows carryover | [PowerShell guide](windows-setup.md), cross-platform Playwright path, Windows CI job | Documentation/configuration delivered; native execution pending | Windows environment was unavailable locally; verify hosted Windows job and actual user workflow |

## Next owner actions

Assign the business licensing lead, rights reviewer and research/data steward; choose restricted evidence storage and a lawful retention/withdrawal process before external activity. Decide which provider capabilities and uses are actually documented; metadata, image display/storage and future AI use have separate gates. No agreement or credential has been supplied by this research pack.

The offline configuration, policy, identity-evidence and truthful-label slice has been verified. A test passing with a simulated provider does not establish commercial rights or live coverage. Bid.Cars and other real-provider operations remain disabled until their gates pass; never silently replace a failed real lookup with synthetic success.

Keep real study data, contracts, invoice/photo files, personal information, contact keys, credentials and restricted manifests outside Git. The committed CSVs are header-only templates or explicitly synthetic unrun examples, not enrollment or study results. See [research handling guidance](research/README.md).

## Release boundary

This sprint's offline coding slice is complete within the verified scope above. The broader sprint retains incomplete business targets until written provider decisions, the consented repair cohort and interviews genuinely exist. Any controlled real-link run or limited pilot requires the separate gates described in the requirements. AI photo inspection (M2), repair/landed-cost estimation, bid recommendations, login and payments remain outside this delivery.
