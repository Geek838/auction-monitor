# Sprint 2 development slice verification

The executed scope is offline provider-policy, identity-evidence and provider-aware UI development. No authorized external provider, real auction inventory, licensed photographs, AI processing or production deployment was exercised.

## Executed results

| Check | Actual result | Environment and scope |
| --- | --- | --- |
| Python unit/API suite | **190 passed**, one framework deprecation warning | Python 3.12, Linux cloud workspace; includes the Sprint 1 regression suite and new policy, evidence, freshness and provider-mode cases |
| Python suite with ambient `AUCTION_PROVIDER=simulation` | **190 passed**, same warning | Test fixtures explicitly select their own baseline and clear registry state; developer demo configuration cannot silently change test expectations |
| Fixture browser suite | **26 passed** | 13 flows on desktop Chromium and mobile Chromium, using actual fixture API through Next.js |
| Simulation browser suite | **18 passed** | Nine flows on both browser profiles, using actual offline simulation API through Next.js |
| Disabled Bid.Cars browser suite | **4 passed** | Two flows on both browser profiles, using the actual disabled external-provider configuration |
| TypeScript / route types | **Passed** | `make check` on the final frontend |
| Production build | **Passed** | `NEXT_TELEMETRY_DISABLED=1 make build`, after browser servers stopped |
| Dependency consistency | **Passed** | `pip check`; no runtime or dependency declaration changes required |

The **48 browser checks** completed without skipped or expected-failure cases in the selected mode-specific suites. Modes ran sequentially with separate service lifetimes. The browser configuration does not reuse an existing server unless explicitly requested, and each mode checks the API's actual provider context before asserting UI behavior.

All browser resolution requests use the real local API. One fixture flow deliberately aborts only the health request in the browser to verify `SOURCE UNKNOWN`, hidden fixture shortcuts, and recovery after a real resolution supplies context. This is a controlled transport-failure test, not a claim that an external provider was tested.

The existing warning is `StarletteDeprecationWarning` for TestClient's `httpx` compatibility. It does not change test outcomes. Chromium also prints environment color-variable warnings; those are distinct from application failures.

## Acceptance evidence

| Story | Verified behavior |
| --- | --- |
| S2-02 — static policy and permission checks | Both `resolve` and `get_vehicle` deny before provider calls when disabled or when evidence, purposes, current authorization or required credentials are absent. Tests cover future review/effective dates, expiry, revocation, metadata display denial, missing operation capabilities and unsupported houses. Credentials are checked only when documented as required. |
| S2-02 — permission changes during a lookup | Spy adapters change revocation, expiry or display permission while awaited; the guard rechecks and does not release the result. Provider failures are unavailable outcomes without exposing exception text or secret markers. |
| S2-03 — independent identity evidence | Mapping tests bind IAAI page, country, source house and exact stock string. Missing, conflicting, inferred, future, whitespace-only and candidate-derived evidence cannot corroborate a match. Legacy comparison metadata cannot claim independent VIN corroboration. Sale-event IDs remain distinct from provider-record IDs. |
| S2-03 — existing match protections | Leading zeros, alphanumeric IAAI page IDs, source/identifier conflicts, VIN/model/year conflicts, duplicate events and unknown VIN remain covered by regression checks. A Canadian page reference cannot use the US fixture mapping. |
| S2-04 — actual provider context | Health and all six domain outcomes preserve the selected mode. Fixture results remain MOCK; simulation remains SIMULATED; disabled external access never produces a licensed result or matched fixture fallback. Denials and unavailable sources retain distinct outcomes and clear previous vehicle data. |
| S2-04 — freshness | Deterministic unit checks use source observation time and an explicit threshold/basis. Missing/future observations or missing policy remain UNKNOWN. Recent retrieval cannot refresh an old source snapshot. SOLD/ARCHIVED events remain HISTORICAL. Browser checks verify unknown fixture freshness, stale simulation data, unknown observation time and archived copy. Licensing and real-time flags alone do not establish freshness. |
| S2-05 — use separation and lifecycle defaults | Metadata-only authorization works without image, inference, training or cache permissions. Inference permission does not grant training. Cache policy requires explicit TTL/retention limits and purpose authorization; revocation denies reuse. No persistent provider-data cache or image processing is implemented, so storage/deletion execution is not claimed. |
| S2-05 — no synthetic substitution | Guard tests reject mismatched provenance types for fixture, simulation and external policies before returning results. Registry and disabled-provider tests deny outbound socket/DNS operations; unknown provider configuration fails instead of falling back. |
| S2-09 — reproducible regression checks | Actual backend and browser results above, strict mode/port selection, isolated test provider state and preserved original resolver cases. |
| S2-10 — Windows carryover | Playwright now chooses `.venv/Scripts/python.exe` on Windows and `.venv/bin/python` elsewhere, using a quoted absolute path. Native Windows execution was not available in this Linux run; Windows CI execution remains pending. |

## Reproduce locally

From repository root, after installing the pinned dependencies:

```bash
.venv/bin/python -m pytest services/api/tests -q
AUCTION_PROVIDER=simulation .venv/bin/python -m pytest services/api/tests -q
cd apps/web
PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH=/usr/bin/chromium E2E_PROVIDER_MODE=fixture npm run test:e2e -- --workers=2
PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH=/usr/bin/chromium E2E_PROVIDER_MODE=simulation npm run test:e2e -- --workers=2
PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH=/usr/bin/chromium E2E_PROVIDER_MODE=bidcars npm run test:e2e -- --workers=2
```

`PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH` is the current cloud-image override. With a Playwright-managed Chromium installed, omit it. `E2E_API_PORT` and `E2E_WEB_PORT` can select free local ports; stop this project's conflicting dev servers before running these suites. `E2E_REUSE_SERVERS=1` is an explicit opt-in and should be used only after checking mode/ownership. Mode-specific health assertions still reject the wrong provider.

PowerShell equivalents use `.\.venv\Scripts\python.exe`, and environment variables use `$env:E2E_PROVIDER_MODE = 'simulation'` before the npm command. See the [native Windows guide](windows-setup.md) for installation/startup commands; these instructions are not a claim of local native-Windows verification.

## Visual artifacts

Ignored local screenshots are saved under `.cache/qa/sprint2/`:

- `simulation-desktop-chromium.png`
- `simulation-mobile-chromium.png`
- `denied-desktop-chromium.png`
- `denied-mobile-chromium.png`

The mobile simulation and denied-provider flows explicitly use a 320-pixel viewport and assert no horizontal document overflow.

## Pending evidence and limits

No hosted CI result or native Windows browser execution is claimed here. Browser coverage is Chromium only. Production authorization, provider-specific contracts, real identity-match coverage, retention/deletion against an actual provider, the 50-link study, the 20+ consented repair cohort, and five+ business interviews remain unexecuted external/business work. Synthetic contract tests and preparation templates do not satisfy those targets. Live providers remain disabled.
