# Sprint 1 verification

Executed against the local fixture provider. No real auction record or provider integration was validated; all vehicle metadata is synthetic.

## Results

- **75 pytest tests passed**: parser, matching rules, disabled provider, FastAPI request validation and result contracts.
- **22 Playwright tests passed**: 11 browser flows on desktop Chromium and mobile Chromium, using the actual FastAPI service through the Next.js proxy.
- The mobile archived-result flow also verifies no horizontal overflow at 320px.
- The only pytest warning comes from the framework's TestClient/httpx deprecation; test results are unaffected.
- Confirmed all 75 backend tests again in a fresh virtual environment installed only from `services/api/requirements.txt`.
- Verified `make install` is repeatable, `make check` generates route types and passes TypeScript, and the Next.js 16 production build succeeds.
- After supported dependency updates, npm audit reports zero vulnerabilities and pip-audit reports no known vulnerabilities for the pinned Python requirements.
- Started the documented `make api` and `make web` commands and verified API health, rendered mock-data notice, and both Copart/IAAI fixture resolutions through the frontend proxy.
- Added GitHub Actions configuration for the same install/check/build/browser workflow. The hosted workflow has not been run from this workspace.

```bash
# From repository root, after make install
.venv/bin/python -m pytest services/api/tests -q
cd apps/web
PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH=/usr/bin/chromium npm run test:e2e -- --workers=2
```

The browser executable override is specific to the current cloud image. Without it, Playwright uses its installed managed Chromium. Browser tests start and stop their own API and web servers when those ports are free.

## Handover acceptance coverage

| Criterion | Evidence |
| --- | --- |
| 1–2: Copart desktop/trailing slash/tracking | Parser cases, fixture API and keyboard browser flow |
| 3: IAAI page ID distinct from stock | Numeric and alphanumeric parser/API cases; browser shows page `41000001` and stock `45371195` separately |
| 4: Exact source/identifier/VIN | Independent reference metadata match and conflict tests |
| 5: Same VIN, multiple events | Matcher preserves both candidate record IDs; ambiguous fixture browser state |
| 6: Wrong VIN | Independent VIN conflict test and single-candidate conflict fixture `70000006` |
| 7–9: Missing, unavailable, unauthorized | API matrix and separate browser headings; BidCarsProvider refuses both interface operations |
| 10: Unsafe URL rejection | Exact host allowlist, credentials, ports, private/loopback addresses, misleading domains, redirect routes, encoded paths, whitespace and backslashes |
| 11: Identifier strings | Leading-zero lot and alphanumeric IAAI page cases in parser/API; leading-zero browser output |
| 12: Archived is historical | API provenance checks; explicit historical browser copy |
| 13: No photos/partial metadata | Nullable VIN/year API checks, `Not supplied` and no-licensed-photos browser output |
| 14: No arbitrary fetch or prompt execution | Socket/DNS operations patched to fail during parser, API fixture resolution and disabled-provider tests; malicious query is discarded |
| 15: Unmistakable mock mode | API provenance and visible browser MOCK label for every provider outcome |

Additional browser checks cover Enter submission, accessible validation association, preserved invalid input, clearing a previous vehicle after a new failed lookup, retrieval timestamp, and non-live provenance.

## Limits

Browser execution covers Chromium only. No authorized live provider contract exists, so production access, live matching coverage, photo rights, and the proposed 50-link feasibility study remain untested. The disabled Bid.Cars adapter is intentionally not an integration.
