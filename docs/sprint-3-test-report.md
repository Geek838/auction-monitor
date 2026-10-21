# Sprint 3 test execution report

Executed on 21 October 2026 in the Linux cloud workspace against the delivered [Sprint 3 requirements](sprint-3-requirements.md). This verifies a deterministic, evidence-linked MOCK preview built from project-authored illustrations. It does not evaluate damage detection, an AI model, real vehicle condition or commercial provider access.

## Executed results

| Check | Actual result |
| --- | --- |
| Backend unit/API suite | **317 passed**; includes the inherited Sprint 1/2 regressions |
| Fresh isolated Python environment | Pinned dependency installation, `pip check` and the same **317 tests passed**, independently run by the root agent |
| Fixture-mode browser suite | **48 passed**, desktop Chromium and mobile Chromium |
| Simulation-mode browser suite | **32 passed**, desktop Chromium and mobile Chromium |
| Disabled Bid.Cars-mode browser suite | **6 passed**, desktop Chromium and mobile Chromium |
| Browser total | **86 distinct passing cases**; the inherited 48 cases remain included |
| Frontend TypeScript / production build | Passed, executed by the root agent |
| Dependency audit | Python audit clean after the certifi patch update, executed by the root agent |
| Whitespace check | `git diff --check` passed |

Browser suites started their own actual FastAPI and Next.js servers sequentially. Fixture and simulation tests assert the server's selected mode through the health endpoint. Normal preview flows use real resolver, preview and guarded image endpoints, rather than substituting report responses. Image checks include decoded browser `naturalWidth`; API tests separately verify PNG bytes, dimensions and SHA-256 digests with Pillow.

An initial fixture run had two failures in an inherited keyboard test: its global exact `MOCK` locator became ambiguous after a separate inspection badge was added. The locator was scoped to the listing badge. Both targeted reruns and the final complete fixture suite passed; no production change was required. The new hostile-caption cases also passed before the complete final run. One existing pytest Starlette/httpx deprecation warning remains; there were no pytest skips in this Linux execution.

## Coverage and evidence

| Requirement | Verified behavior |
| --- | --- |
| S3-01 | Copart and IAAI exact binding; IAAI page/country/stock remain distinct; provider, mode, record, event, VIN and content changes cannot inherit an old preview. Genuine source-observation and evidence revisions affect the fingerprint; request-only retrieval/evaluation timing does not. Unknown scenarios and arbitrary replacement PNGs cannot inherit authored findings, including after a manifest rehash. |
| S3-02 | Strict finding taxonomy; image references and hashes belong to the same report; duplicate/dangling references fail. Confidence and actual model/provider/prompt fields remain null. Optional geometry rejects invalid bounds, non-finite values and unreviewed references; normal output has no fabricated overlays. Unsupported fields and known unsafe assertions fail validation. |
| S3-03 | Completed, partial, blocked and failed outcomes; missing/forged preconditions; same-URL record/event/content/source-evidence changes before and during awaited inspection; malformed engine output cannot become a successful report. |
| S3-04 | Both auction houses, gallery selection, keyboard activation, finding-to-image navigation, persistent MOCK/no-AI labels, provenance, archived context, missing images, partial output, engine failure and unknown-only output. Editing the URL clears the previous report immediately; a delayed old response cannot attach beneath a new listing. |
| S3-05 | Observed, suspected and unknown sections remain distinct; physical checks and coverage limitations stay visible. Missing photos and no drawn mark do not produce an all-clear conclusion. |
| S3-06 | Preview and direct asset requests recheck current permissions, expiry, revocation, scenario/target binding and exact bytes. Filesystem manifest revocation is observed after an earlier successful request. Metadata resolution remains available when image permissions are denied. Known-but-unbound asset IDs, arbitrary paths/URLs, corrupt/truncated files, mismatched dimensions/MIME, symlinks, excess catalog entries and oversized PNGs fail closed. Socket/DNS-denial tests exercise preview plus image delivery without external calls. Both POST endpoints enforce a 16 KiB pre-parse body limit, including chunked bodies without Content-Length; normal chunked and malformed-small JSON behavior is checked. |
| S3-07 | Inherited parser/provider/policy/freshness coverage, strict request/output validation, hostile caption escaping, failed image delivery and late-response tests. Screenshots and platform limits are recorded below. |

Four browser scenarios use deliberately controlled interception and should be interpreted accordingly:

- The precondition test changes the outgoing snapshot fingerprint; the actual API returns `TARGET_CHANGED` and the UI requires fresh resolution.
- The unavailable-image test aborts one PNG transport request; related observed/suspected text is withheld.
- The stale-response test holds a response generated by the actual API until the input changes, then releases it.
- The hostile-caption test changes a returned asset title and finding description at the browser consumer boundary. The markup renders literally, creates no injected image and executes no injected handler. Backend output-validation and no-network tests cover the server boundary separately. This is output escaping coverage, not adversarial-model evaluation.

## Visual evidence

Local screenshots are generated under `.cache/qa/sprint3/` (ignored build/test artifacts):

- `fixture-desktop-chromium.png` and `fixture-mobile-chromium.png`: full fixture report.
- `simulation-desktop-chromium.png` and `simulation-mobile-chromium.png`: full simulation report.
- `gallery-mobile.png`: viewport screenshot at **320 CSS px**, including the MOCK warning, gallery controls, actual authored illustration and caption. Mobile device pixel ratio makes the PNG wider in physical pixels. The image was visually inspected; text and controls wrap and the browser assertion confirms no horizontal page overflow.

## Reproduce

From the repository root after installation:

```bash
make test-api
npm --prefix apps/web run typecheck
npm --prefix apps/web run build
```

Run the three browser suites from `apps/web`, one mode at a time:

```bash
E2E_PROVIDER_MODE=fixture npm run test:e2e -- --workers=2
E2E_PROVIDER_MODE=simulation npm run test:e2e -- --workers=2
E2E_PROVIDER_MODE=bidcars npm run test:e2e -- --workers=2
```

This cloud run used `PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH=/usr/bin/chromium` and disabled Next.js telemetry. A normal local setup can use Playwright-managed Chromium; see the README and Windows setup guide for installation and PowerShell equivalents. Browser tests start the API/web servers themselves and require their configured ports to be free.

## Limits and remaining gates

This execution used Linux and Chromium only. Hosted CI, native Windows, other browsers, screen-reader use and real-user sessions were not observed. A symlink-defense test may skip on operating systems that prohibit creating symlinks; it ran here. Production build/typecheck and fresh-install/audit evidence above were supplied by the collaborating root agent, while browser suites were executed by QA.

All imagery and findings are authored fixtures. There are no customer uploads, licensed auction photographs, live auction data requests, actual model runs, measured visual accuracy or calibrated confidence. Schema and known-token safety validation cannot prove every possible unsafe natural-language claim is recognized. Qualified automotive wording review, real-image rights, external-provider authorization, model evaluation and real-user pilot readiness remain separate gates documented in the delivery record.
