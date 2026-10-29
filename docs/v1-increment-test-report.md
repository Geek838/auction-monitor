# 1.0 development increment — execution evidence

Execution date: **29 October 2026 (Asia/Tbilisi)**. This report covers the user-supplied budget planner, optional loopback-only vision adapter and free NHTSA manufacturer VIN enrichment. These checks do not establish automatic auction identity coverage, model damage-detection quality, independently verified repair pricing or completion of the full 1.0 handover.

## Executed results

| Check | Actual result |
| --- | --- |
| Complete backend suite | **520 passed**: inherited 371 plus 149 new cases |
| New budget API/solver checks | **62 passed** |
| New local-vision API/transport checks | **55 passed** |
| New VIN API/transport checks | **32 passed** |
| Fixture browser suite | **92 passed**, desktop/mobile Chromium |
| Simulation browser suite | **64 passed**, desktop/mobile Chromium |
| Disabled Bid.Cars browser suite | **38 passed**, desktop/mobile Chromium |
| Browser total | **194 distinct passing cases**: inherited 142 plus 52 new cases |
| Frontend TypeScript / production build | **Passed**, executed by the parent agent after VIN integration |
| Whitespace | `git diff --check` passed |

All three complete browser suites passed on their first execution; no browser assertion or implementation correction was needed during these runs. Servers were stopped afterward and ports 3000/8000 were verified closed. One inherited Starlette/httpx deprecation warning remains. This execution uses Linux; native Windows, hosted CI, other browser engines and screen-reader sessions have not been observed.

## Backend evidence

Budget tests use the actual HTTP boundary and service. They verify decimal-string arithmetic, low/base/high totals, fee rounding at half-cent boundaries, missing categories/fees/sources, quote expiry and explicit not-applicable decisions. A fee discontinuity makes 4999.99 the final feasible bid in a controlled case. Separate tests prove that the computed ceiling fits and one more cent exceeds the supplied bound. An independent exhaustive cent oracle checks the binary search against several fee/reserve/cost scenarios. Aggregating sixty maximum-sized inputs remains cent-exact and does not reuse per-input size limits for the sum. Quote validity is inclusive and rechecked at evaluation, using Georgia calendar dates. No tax or supplier price is generated.

Local-vision tests call the actual API while replacing only `OllamaRuntime.request_json`. Real generated PNG/JPEG bytes are decoded, checked, stripped of original metadata and re-encoded; their actual sent-byte SHA-256 values match provenance. JPEG EXIF orientation is applied. Hash mismatch, corrupt/animated/oversized images, missing permission, wrong model inventory, remote-model claims, invalid output references, confidence/financial fields, tool calls and known unsafe assertions fail without mock findings. Model replacement invalidates results. Disabled configuration and concurrent-request blocking perform no transport calls. Transport tests establish fixed loopback destinations, direct no-proxy behavior, redirect denial, timeouts, response limits and sanitized malformed data. These transport doubles are not evidence that a real model made any observation.

VIN tests call the actual API with a `VpicClient.request_json` double. They verify uppercase normalization, strict 17-character syntax, exact returned-VIN matching, single-source-row/count requirements, decoded versus partial versus invalid/unavailable outcomes and no auction-verification promotion. Empty facts with a clean source code remain partial, not a falsely invalid VIN. Fixed official HTTPS URL, redirect denial, no API authentication, finite timeout, response cap and sanitized failures are tested independently. Routine tests do not call the live government service.

Pre-parse body boundaries are checked for the new routes: budget 64 KiB, local analysis 9 MiB and VIN 4 KiB. Existing route limits and inherited provider/identity/MOCK/manual-review regressions remain in the full suite.

## Browser interpretation

Budget normal flows use actual API calculations and user-entered engineering quote/fee inputs, not substituted totals. The local-analysis positive consumer fixtures replace runtime availability and the report only at the browser boundary; the underlying API's parsed reference is retained. Manufacturer consumer fixtures return a clearly controlled decode response without a live government dependency. Those intercepts must not be described as installed-model or external-provider validation. The parent/integration agents separately record actual runtime and public-source smoke evidence in [local model smoke](local-model-smoke.md) and [free VIN data](free-vin-data.md); those are distinct from these routine test-double checks.

The new actual-API budget flows verify a complete declared quote/fee scenario and its 7409.09 indicative ceiling, missing-cost withholding, JSON download, print visibility, clearing/edit invalidation, forged-input response rejection and literal supplier text escaping. The normal manual-review and fixture workflows retain their inherited coverage.

The local-analysis default-disabled check runs in all provider modes and proves selecting/consenting photos does not silently dispatch inference. Three fixture-only consumer cases explicitly replace status/report responses: they check prepared-byte hashing, explicit dispatch consent, literal hostile text, photo-digest binding, export and stale-response rejection. These are not live model UI tests. Two fixture-only VIN consumer cases likewise replace the government response: no lookup occurs while typing, applying returned details requires a second explicit action, an edited VIN discards an old response, and applied manufacturer facts still compile an unverified manual review.

Ignored `.cache/qa/v1/` holds all three execution logs and desktop/mobile budget screenshots. `budget-mobile.png` was visually inspected at 320 CSS pixels: totals, the bid ceiling and its INDICATIVE / USER INPUTS label remain readable without horizontal overflow. Local-analysis screenshots contain clearly controlled engineering-pattern data, not a vehicle assessment. No physical printer or saved PDF behavior, actual free-source coverage, automotive quality or calibrated confidence is established by these browser checks.

## Reproduce

With the existing pinned dependencies installed, from the repository root:

```bash
.venv/bin/python -m pytest services/api/tests
npm --prefix apps/web run typecheck
npm --prefix apps/web run build
```

Browser suites own FastAPI/Next.js processes and require free configured ports. Run each mode sequentially, separately from production builds:

```bash
PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH=/usr/bin/chromium E2E_PROVIDER_MODE=fixture npm --prefix apps/web run test:e2e -- --workers=2
PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH=/usr/bin/chromium E2E_PROVIDER_MODE=simulation npm --prefix apps/web run test:e2e -- --workers=2
PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH=/usr/bin/chromium E2E_PROVIDER_MODE=bidcars npm --prefix apps/web run test:e2e -- --workers=2
```

Omit the executable override for Playwright-managed Chromium. PowerShell equivalents are in the Windows setup guide. No real photos, supplier credentials or paid service is needed for the routine test suite.

## Final actual-runtime follow-up

After the initial suites, the model smoke exposed a 60-second CPU inference timeout and inspection of Next.js revealed a separate 30-second default rewrite timeout. The backend model deadline is now 180 seconds with a 1,000-token concise prompt revision (`visible-evidence-v2`), and the Next.js proxy is finite at 210 seconds. The focused transport/API suite passed after this correction; the parent reran the full backend suite after the correction: **520 passed**, with the same inherited framework warning. These changes do not enable hosted inference.

A real production-proxy request through Next.js -> FastAPI -> local Qwen3-VL 2B completed in 46.325 seconds, exceeding the old proxy cutoff. It returned zero findings and correctly identified the owned image as non-vehicle evidence, with six UNKNOWN physical checks, exact model/image digests and actual token counts. Earlier Moondream semantic weakness and the earlier Qwen timeout are preserved in [the model evidence](local-model-smoke.md). This is not a vehicle-damage benchmark or readiness claim. A final real VIN HTTP smoke also succeeded; routine UI/transport fixtures remain clearly separate.

The parent also reran the eight local-analysis desktop/mobile browser checks after the timeout/proxy changes: **8 passed**. These are targeted reruns of cases already in the 194-case total, not additional unique cases. Production TypeScript/build checks passed with the final 210-second proxy configuration. All owned API/web/model servers were stopped after the actual smoke; ports 3000, 8000 and 11434 were verified closed.
