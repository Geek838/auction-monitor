# Connected workflow, exchange reference and release checks

Executed **30 October 2026 (Asia/Tbilisi)**. This report records a development increment, not automatic Auction Intelligence 1.0 certification. Requirements are in [the PO selection](v1-next-requirements.md); remaining product gates are in [readiness](v1-release-readiness.md).

## Delivered behavior

- Connected navigation carries a validated Copart/IAAI URL between listing identity, manual evidence, optional local analysis and budget planning. Query tracking is discarded; leading zeros and IAAI page references are preserved. No photos, notes, costs or verification assertions transfer. The URL appears in browser history, as disclosed.
- Explicit USD/GEL reference conversion uses a fixed official NBG feed, decimal parsing, quoted quantity normalization, HALF_UP final-cent rounding and separately displayed publication/effective/retrieval dates. Future-effective and more-than-four-calendar-day-old quotes produce no conversion. The four-day threshold is an application policy, not an NBG legal expiry. USD budget calculations remain unchanged.
- A restricted current-2026 Georgia excise component uses primary Tax Code Article 188(12), (13), (18), checked against seven actual official RS calculator cases. Unsupported/unknown facts withhold the component. Production-year edits clear the evidence confirmation. Import duty, VAT treatment, fees and registration remain unknown; no clearance-budget category is populated.
- Photo selection stays disabled until client handlers attach. Browser tests explicitly wait for readiness before setting files; a no-JavaScript regression checks that server-rendered file controls remain disabled.
- Offline visual-evidence accounting binds exact report/finding/model/prompt/image bytes to explicit human adjudications. Missing evidence withholds metrics; repeated identical inference image sets cannot inflate the cohort. No independently reviewed automotive dataset was produced.
- PowerShell setup checks pinned dependencies including Pillow; launchers bind to loopback. CI has bounded test diagnostics, matching cache paths and native Windows launcher smoke configuration.

## Backend and tool execution

```sh
.venv/bin/python -m pytest -c services/api/pyproject.toml services/api/tests tools/tests -q
```

**706 passed**: 668 backend checks (the inherited 520 plus 73 exchange and 75 excise checks) and 38 evaluation-accounting checks. One inherited Starlette/httpx deprecation warning remains. No dependencies changed. The bounded release runner also completed these checks successfully.

Exchange checks cover decimal input and rounding, unit quantities, ordered/duplicate/missing source rows, effective/publication dates, Georgia calendar boundaries, weekend-age disclosure, future/stale withholding, malformed/nonfinite values, redirect/timeout/response-size failures, concurrency, API contracts and preparse body limits. All routine source tests use deterministic transport doubles.

The evaluation CLI was also exercised with Python `-S`, without editable-package activation, from an unrelated working directory. It imports repository API contracts directly; a hidden local editable installation is not required.

A disposable Linux Python 3.12.14 environment installed only `requirements.txt`, with no editable API package, and passed all **706** final backend/tool checks through `scripts/check-api.py` in 8.93 seconds. This verifies clean-install reproducibility without the onboarding environment's editable installation. Dependency consistency checks also passed.

## Browser and build execution

Browser runs use the installed `/usr/bin/chromium` through `PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH`, two workers, desktop Chromium and Pixel 7 Chromium emulation. Native mobile devices, additional browser engines and screen readers were not tested.

The first default browser invocation failed to launch because its expected downloaded Chromium executable was absent. Configuring the already installed system browser resolved that environment issue. The first executable-browser run exposed six ambiguous new FX assertions: source/unit quotes shared text, and Next's route announcer shared the alert role. Tests now target the labeled quote row and converter region. All twelve FX checks subsequently passed.

A simulation run exposed one early file-selection failure. Its exact cause was not established from the preparation-state snapshot. Hydration readiness now protects both file controls and tests explicitly await enablement. The subsequent 28-check manual/local/workflow simulation run passed, including invalid photo rejection and the new server-rendered-control regression.

Final TypeScript and production build passed with the connected workflow, hydration guards, exchange page and excise page. Browser response doubles exercise NBG UI states; they do not prove upstream availability. Existing manual/budget/resolver flows and the new excise checks use the real local API where their tests are designed to do so. Excise browser checks cover the age-rate change, unsupported/unknown facts, historical-date withholding, cm³ units, explicit production-year confirmation, stale response discarding and changed-request rejection.

| Provider configuration | Executed distinct desktop/mobile browser checks |
| --- | --- |
| Fixture | **122 passed** in the final full run, including final production-year reconfirmation behavior |
| Simulation | **72 passed** in its final full run, after the hydration fix |
| Disabled Bid.Cars | **46 passed** in its full run |
| Total | **240 distinct checks passed** across the three configurations |

Targeted reruns are not added to this total. Simulation and disabled-provider suites ran before the subsequent excise addition; excise scenarios run in fixture configuration against the actual backend. Existing provider behavior was not changed by adding that independent route. The exchange page at 360 CSS pixels was visually inspected with no horizontal overflow; its initial screenshot also exposed a screenshot-time caret-style hydration warning, so that capture is not used as evidence of a general application hydration failure.

## External-source observations

PO ordinary official NBG research reads returned HTTP 200 and the USD row `quantity=1`, `rate=2.5959`, effective 30 October 2026, published 29 October at 17:01:14.556 UTC. Those research requests used standard `urlopen` redirect handling, and the exact raw response was not retained. They are not a strict-transport integration smoke.

Actual application source requests encountered denial/self-redirect behavior and safely returned `UNAVAILABLE`, with no invented quote or converted amount. **No successful production live conversion is claimed.** The public canonical feed is documented, but its availability from this environment remains limited. No source-block bypass or undocumented date endpoint was added.

The [new provider review](research/free-auction-provider-review-2026-10-30.md) identifies documented MarketCheck auction APIs and an advertised free tier. Exact Copart/IAAI coverage, IAAI page mapping, endpoint billing and commercial/photo/inference use remain unverified. No account, API key, provider data call, outreach or purchase occurred.

## Hosted and operational evidence

The [previous 29 October CI run](https://github.com/Geek838/auction-monitor/actions/runs/40859118207) failed after passing Linux checks because setup-python cached a different directory from installation. Windows timed out; its logs were unavailable. The new cache path matches actual installation, and the runner has finite diagnostics instead of an unexplained full-job wait.

Packaging commit `0c4d88c` triggered [hosted run 41045518354](https://github.com/Geek838/auction-monitor/actions/runs/41045518354). Windows PowerShell parsing and installation through the new setup script completed successfully. Final hosted tests/build/startup status must be read from the actual run; configuring a Windows job does not constitute a pass. No production service was deployed.

That diagnostic run remained active beyond its reported test deadlines with no accessible logs and was explicitly cancelled after being superseded. Cancellation is not a test fix or passing result. Commit `41b50a2` adds explicit pytest configuration and native Windows production-launcher/proxy smoke. Its [replacement run](https://github.com/Geek838/auction-monitor/actions/runs/41046811512) started after the cancellation; the final application push triggers its own checks. Hosted execution/reporting remains a separately recorded operational limitation until completed results exist.

## Remaining release evidence

No real exact-auction provider was activated, no automotive quality score established, no supplier-backed Georgian price cohort collected and no complete clearance formula validated. Seven official UI cases now validate the supported excise component, with [unchanged screenshots and captured results](georgia-excise-component-requirements.md) retained in the repository. Wider clearance and the remaining original-product evidence remain explicit 1.0 gates.
