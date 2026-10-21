# Sprint 4 zero-paid-API test execution

Executed **22 October 2026 (Asia/Tbilisi)** in the Linux cloud workspace. This validates the [zero-API manual review slice](sprint-4-zero-api-scope.md): user-entered facts, browser-local photos, user-reported findings and an exportable/printable document. It does not validate a live auction integration, image analysis, model accuracy or vehicle condition.

## Results

| Check | Executed result |
| --- | --- |
| Complete backend unit/API suite | **371 passed**, including all inherited regressions and **54 new manual-review cases** |
| Fixture browser suite | **68 passed**, desktop and mobile Chromium, including PNG and JPEG/EXIF cases |
| Explicit IAAI HTTPS port/consumer checks | **6 targeted reruns passed** after the supported `:443` UI detection correction; included in the unique cases above |
| Simulation browser suite | **50 passed**, desktop and mobile Chromium |
| Disabled-provider browser suite | **24 passed**, desktop and mobile Chromium |
| Unique browser total | **142 distinct cases passed**; includes the inherited 86 cases plus 56 new manual-review cases |
| Frontend TypeScript / production build | **TypeScript and production build passed**, including final revalidation after the `:443` UI correction, executed by the root agent |
| Documentation/whitespace | `git diff --check` passed; root also checked local documentation links |

No runtime dependencies or lockfiles changed. No real provider account, paid API request, photo transmission to an external service, model call or data-access agreement was used. One inherited Starlette/httpx deprecation warning remains in pytest. Native Windows and hosted CI were not observed.

## What the new checks establish

The backend tests exercise the actual FastAPI route, parser, contracts and compiler:

- Copart lot strings retain leading zeros; metadata remains `USER_SUPPLIED_UNVERIFIED`, not `MATCHED` or licensed-provider output.
- IAAI page/country and manually claimed stock remain separate, even if the claim happens to equal the page string. No mapping evidence is invented.
- Vehicle fields are syntactically validated; invalid VIN characters/length, unreasonable years and coerced integer/boolean claims are rejected. A normalized VIN is still user supplied, not independently verified.
- Observed/suspected user findings require linked photo metadata; dangling references, duplicate IDs, bad digests/dimensions and excessive lists fail validation.
- Image bytes/data URLs/remote photo URLs, verification overrides, model/confidence and financial/part fields are rejected as unsupported inputs. Hashes/dimensions accepted by this metadata-only endpoint are explicitly **client declared, not server verified**.
- Empty-evidence reports contain no canned findings. All six physical-check systems remain UNKNOWN. Known unsupported safety-verdict phrases are rejected; this narrow wording check is not a general natural-language safety classifier.
- Socket/DNS-denial checks confirm report compilation needs no outbound connection, including while the selected auction provider is disabled.
- The manual route enforces an exact 32 KiB pre-parse JSON boundary, including streamed bodies with no Content-Length. The original resolver retains its smaller 16 KiB bound. Successful reports are non-cacheable.

Browser checks use real FastAPI and Next.js servers. Normal review requests are not substituted:

- The home-page entry leads to `/review`; the local PNG is decoded/prepared in the browser, rendered from a blob URL and linked to a user-entered finding.
- A generated PNG carries a private ancillary text marker. Its normalized browser copy loses that marker, its SHA-256 matches the submitted metadata, and the actual POST has no pixels, base64 image, original filename or marker. The flow triggers no external HTTP request.
- A separate generated JPEG has EXIF orientation 6 and a private description marker. Chromium correctly prepares a 60×80 PNG from the 80×60 original, strips the marker and submits only its matching hash/dimensions. These are solid-color engineering images, not vehicle photographs or damage-analysis examples.
- Facts-only reports, distinct IAAI page/stock with explicit HTTPS port 443, literal hostile notes, invalid image bytes, JSON download and the browser print action are exercised. Print media hides the editor and retains the report; no physical printer/PDF output is claimed.
- Editing invalidates the old report. Clear review resets fields/findings and revokes the local photo URL. A response delayed until after an edit cannot reappear beneath changed evidence.
- Consumer-boundary tests mutate only the returned Copart lot or IAAI page from an actual API response; the UI rejects that report. These controlled interceptions test response binding, not a real provider or model.

## Corrections during execution

The initial fixture execution passed 62 cases and failed four assertions because a global `role=alert` locator also matched Next.js's route announcer. Scoping the assertions inside the application main region fixed the tests; the product's image-error and response-rejection behavior was already correct. The final complete fixture suite passed.

Implementation review separately identified that the manual stock-field visibility check omitted the parser-supported explicit HTTPS port `:443`. The frontend check was corrected; targeted desktop/mobile IAAI and forged-reference flows passed, and subsequent provider-mode suites use that URL form. This is a supported-URL UI correction, not evidence of auction mapping.

## Reproduce

After installing the existing pinned dependencies, from the repository root:

```bash
.venv/bin/python -m pytest services/api/tests
npm --prefix apps/web run typecheck
npm --prefix apps/web run build
```

Run browser modes sequentially with their configured ports free:

```bash
E2E_PROVIDER_MODE=fixture npm --prefix apps/web run test:e2e -- --workers=2
E2E_PROVIDER_MODE=simulation npm --prefix apps/web run test:e2e -- --workers=2
E2E_PROVIDER_MODE=bidcars npm --prefix apps/web run test:e2e -- --workers=2
```

This cloud execution used `PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH=/usr/bin/chromium` and disabled Next.js telemetry. PowerShell invocations without `make` are in [Windows setup](windows-setup.md). Browser suites own their API/web server lifetimes; a running unrelated service is not silently reused.

## Visual evidence and limits

Ignored `.cache/qa/sprint4/` contains full report screenshots for each executed mode and desktop/mobile profile, plus `gallery-mobile.png`, a viewport at **320 CSS pixels**. The viewport was visually reviewed: facts, local-evidence notice, engineering image and hash wrap remain readable without horizontal overflow. Local fixture/target/simulation logs are also retained there.

The reported browser count is unique test cases across desktop/mobile profiles and modes, excluding targeted reruns. All photos used for this execution are generated engineering fixtures. No automotive-domain assessment, real source coverage, external AI robustness, calibrated confidence, screen-reader session or native Windows behavior is established. The complete API/backend result and browser report must not be described as a finished automatic inspection product.
