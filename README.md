# Auction Intelligence — identity and inspection preview

A local auction listing resolver and mock inspection preview for buyers importing damaged vehicles into Georgia. Paste a supported Copart or IAAI URL to corroborate a synthetic listing identity, then open an eligible example's evidence-linked preview. Sprint 3 adds authored illustrations, categorized findings and physical-inspection questions without enabling external access or AI analysis.

**All records are synthetic.** The default fixture mode displays MOCK; the explicit offline simulation mode displays SIMULATED. No auction website is fetched. Bid.Cars remains an unlicensed integration candidate with a disabled adapter. There is no AI analysis, repair estimation, bid recommendation, login, payment, or third-party photograph ingestion.

## Run locally

Prerequisites: Python 3.12+, Node.js 24 LTS, npm, and a Chromium browser for browser tests. No database, API keys, or Docker daemon is needed.

**Windows PowerShell:** use the [native Windows commands](docs/windows-setup.md), which do not require `make` or virtualenv activation. The Makefile commands below are for Linux/macOS or an appropriate Unix shell. Windows CI is configured; native Windows execution has not been verified from this Linux development machine.

From the repository root:

```sh
make install
```

Start the API and frontend in separate terminals:

```sh
make api
```

```sh
make web
```

The API listens on port 8000 and Next.js on port 3000. `GET /api/v1/health` checks API availability. Next.js forwards `/api/v1/*` to the API; `API_BASE_URL` overrides the default server-side destination. See `.env.example`. No environment file is required. To run Next.js with a different API, export `API_BASE_URL` before starting it.

## Provider modes (all offline)

Set `AUCTION_PROVIDER` in the **API terminal** before starting/restarting the API. An environment file is not loaded automatically.

| Value | Behavior |
| --- | --- |
| `fixture` (default) | Hand-authored MOCK records; original fixture examples below. |
| `simulation` | Hand-authored SIMULATED records for permission/evidence/freshness demonstrations; no commercial rights or live auction access implied. |
| `bidcars` | Disabled external-provider placeholder. Resolution returns `NOT_AUTHORIZED` before any provider request. |

For example on Linux/macOS, stop your API, then run `AUCTION_PROVIDER=simulation make api`. In PowerShell, set `$env:AUCTION_PROVIDER = "simulation"` before the API command in the Windows guide. The UI obtains provider context from the API; no provider selector, API key, or policy override is accepted from the URL form. Unknown configuration fails at API startup. A service failure never silently falls back to synthetic matched data.

Structured policy checks guard provider operations. Image display/storage, inference, training, redistribution and caching remain separate permissions, denied by default. No persistent provider-data cache is implemented. Authorization and freshness are separate: licensed does not mean live, recent retrieval does not make an old snapshot fresh, and unknown source age remains unknown.

The local fixture/simulation modes explicitly permit display of this project's authored preview illustrations. That narrow permission does not enable third-party image ingestion, real AI inference, model training or a photo upload feature.

```sh
curl --fail http://127.0.0.1:8000/api/v1/health
curl --fail http://127.0.0.1:8000/api/v1/auction/resolve \
  -H 'Content-Type: application/json' \
  -d '{"url":"https://www.copart.com/lot/51374586"}'
```

## Test and build

```sh
make test-api
make check
make build
```

Install a Playwright-managed browser once, then run the desktop and mobile Chromium suite. Stop your development servers first: Playwright starts isolated API and frontend servers, and fails on an occupied port rather than silently reusing the wrong provider mode.

```sh
cd apps/web
npx playwright install chromium
cd ../..
make test-web
```

Alternatively, use an already installed Chromium:

```sh
PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH=/usr/bin/chromium make test-web
```

Run alternate-mode browser suites separately:

```sh
E2E_PROVIDER_MODE=simulation PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH=/usr/bin/chromium make test-web
E2E_PROVIDER_MODE=bidcars PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH=/usr/bin/chromium make test-web
```

Omit the executable override when using Playwright-managed Chromium. Tests use fixture mode by default. Each mode runs against its actual configured backend; no commercial access is exercised.

`make test` runs pytest and browser tests together. To serve the production frontend after `make build`, run `npm --prefix apps/web start` with the API running. Test output directories, dependencies, virtualenvs, and build files are ignored by Git.

## Sprint 3: try the inspection preview

After pulling this change, refresh Python dependencies before restarting the backend: image validation adds pinned Pillow. On Linux/macOS use `make install`; on PowerShell:

```powershell
.\.venv\Scripts\python.exe -m pip install -r services/api/requirements.txt
```

1. Use `fixture` or `simulation` mode, resolve the Copart or IAAI example below, then select **Open MOCK inspection preview**.
2. The gallery contains project-authored raster illustrations, each marked **NOT AUCTION PHOTO**. They are generic drawn examples, not images of the resolved real-world vehicle.
3. Select an image or a finding to navigate its evidence. Findings distinguish **OBSERVED** features of the drawing, **SUSPECTED** inspection questions and **UNKNOWN** condition. No model ran and no confidence percentage is assigned.
4. Read the physical-inspection checks and evidence gaps. An unmarked illustration does not establish absence of damage or safe operation.
5. Edit the listing URL or resolve another listing: the previous preview clears. A changed snapshot, altered image, lost permission or unknown scenario cannot reuse the old report.

| URL | Mock-preview behavior |
| --- | --- |
| `https://www.copart.com/lot/51374586` | Complete authored front/side example |
| `https://www.iaai.com/VehicleDetail/41000001~US` | Complete authored example, retaining distinct page/stock identity |
| `https://www.copart.com/lot/70000002` | Historical, partial example; one view deliberately excluded |
| `https://www.copart.com/lot/00012345` | Matched metadata; no eligible preview images |
| `https://www.copart.com/lot/70000007` | Explicit mock engine failure; no findings released |
| `https://www.copart.com/lot/70000008` | Unmarked rear illustration; safety-critical systems remain UNKNOWN |

The API provides additive `snapshot_fingerprint` and `preview_eligibility` fields on resolution. `POST /api/v1/inspections` accepts only `url` and `expected_snapshot_fingerprint`; it re-resolves the target server-side and returns `COMPLETED`, `PARTIAL`, `BLOCKED` or `FAILED`. Completion describes the mock workflow, never a vehicle passing inspection. The guarded asset route checks the same target binding, current permissions, SHA-256 and decoded PNG type/dimensions before serving an illustration with non-cacheable headers.

No report history, database, jobs, uploads, remote image downloads or model service is involved. Asset source, hashes, authorship and regeneration are documented in [inspection fixtures](docs/inspection-fixtures.md); future real-vision requirements are in [vision readiness](docs/vision-readiness.md).

## Synthetic examples

Identifiers are strings, including leading zeros. These URL-shaped examples are local fixture keys, not assertions about current real-world lots.

| Paste this URL | Expected result |
|---|---|
| `https://www.copart.com/lot/51374586` | `MATCHED` — synthetic Toyota Camry |
| `https://www.copart.com/lot/00012345` | `MATCHED` — leading zeros preserved |
| `https://www.iaai.com/VehicleDetail/41000001~US` | `MATCHED` — page `41000001` explicitly maps to stock `45371195` |
| `https://www.iaai.com/VehicleDetail/UNMAPPED123~US` | `UNRESOLVED_ID` — page ID cannot be treated as stock |
| `https://www.copart.com/lot/70000001` | `AMBIGUOUS` — competing fixture sale events |
| `https://www.copart.com/lot/70000006` | `AMBIGUOUS` — one record conflicts with independently supplied fixture VIN |
| `https://www.copart.com/lot/70000002` | `MATCHED` — archived fixture, visibly historical |
| `https://www.copart.com/lot/70000003` | `SOURCE_UNAVAILABLE` — simulated provider failure |
| `https://www.copart.com/lot/70000004` | `NOT_AUTHORIZED` — simulated missing permission |
| `https://www.copart.com/lot/99999999` | `NOT_FOUND` — absent from the fixture dataset |

The API returns HTTP 200 for these domain outcomes, with `status`, parsed `reference`, corroborated `identity` when available, candidates, evidence, reasons, and warnings. Provider context is returned even when no record is available. Invalid/unsupported URL input returns HTTP 422. Provider errors remain distinct from missing records. A successful result includes vehicle metadata, provenance, field and mapping evidence, source freshness, and event metadata. The existing health `provider` string remains available alongside structured `provider_context`.

## Supported URL forms and identity

- Exact hostnames: `copart.com`, `www.copart.com`, `m.copart.com`, `iaai.com`, `www.iaai.com`, `m.iaai.com`. HTTPS only, default/443 port only.
- Copart: `/lot/<digits>` with an optional locale prefix and vehicle slug.
- IAAI: `/VehicleDetail/<alphanumeric-or-hyphen-page-id>~US` (country suffix optional), with an optional locale prefix.
- Tracking queries, fragments, and trailing slashes do not affect identity. Shorteners and redirect wrappers are not followed. Credentials, encoded path tricks, unsupported hosts, private-network URLs, whitespace/control characters, and arbitrary paths are rejected.

Canonical listing identity is `(auction house, lot or stock number)`. IAAI's URL page ID remains separate. The adapter must supply an explicit mapping before the matcher can assert stock identity. Matching auction identity is required; independent VIN/year/make/model evidence gates the match where present. VIN alone cannot join different listing identities or sale events. Competing or conflicting evidence produces `AMBIGUOUS`, never a guessed best match.

## Repository layout

```text
apps/web/                 Next.js App Router, typed UI, Playwright
services/api/app/
  domain/                 Pydantic identities, evidence, outcomes
  resolution/             Local URL parser and exact-match validator
  providers/              AuctionSource, FixtureProvider, disabled BidCarsProvider
  inspections/            Guarded authored assets, mock engine, snapshot-bound preview
services/api/tests/       Parser, matcher, provider, API regression tests
docs/                     Handover, acceptance criteria, design, architecture
```

The fixture dataset is versioned with the provider implementation. It uses in-memory records and no persistent user state. Its source timestamps describe synthetic snapshots; they do not promise freshness. See [architecture decisions](docs/decisions/001-resolver-boundaries.md), [provider integration guide](docs/source-integrations.md), [acceptance criteria](docs/sprint-1-requirements.md), and the [supplied handover](docs/auction_intelligence_handover.md).

The [Sprint 1 test report](docs/sprint-1-test-report.md) records the original baseline. See [Sprint 3 delivery](docs/sprint-3-delivery.md), [requirements](docs/sprint-3-requirements.md), [test report](docs/sprint-3-test-report.md), and [research templates](docs/research/README.md) for the delivered scope and pending external work. The GitHub Actions workflow is configured for Linux and Windows; do not infer a hosted run has passed from a local result. Python's `requirements.txt` pins the tested runtime and test dependencies; `pyproject.toml` declares the package and direct dependencies. Refresh the pinned file in an isolated environment when intentionally updating those declarations, then rerun the suites and dependency audit.

## Limits and next decisions

English is the prototype language; Georgian localization timing remains open. Production coverage, data/photo rights, provider contracts, persistence, retention, and freshness require separate decisions. Fixture tests verify resolution behavior and app integration, not live auction accuracy. The disabled Bid.Cars placeholder must remain disabled until authorized integration work is explicitly undertaken.
