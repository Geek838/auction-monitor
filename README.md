# Auction Intelligence — vehicle evidence review

A local evidence and budget-planning application for buyers importing damaged vehicles into Georgia. Review your own photos and notes, optionally retrieve manufacturer details through the free official NHTSA VIN service, and calculate USD cost scenarios and a fee-aware planning bid ceiling from your entered sources. Optional local-model photo analysis uses installed weights rather than a paid AI API.

**Identity, provenance and unknowns stay explicit.** The auction resolver still uses synthetic fixture/simulation data; no live auction website or licensed provider is queried. Manufacturer decoding is not an auction match. Budget inputs are user declarations, not verified Georgian prices or tax calculations. Local-model findings remain experimental and unreviewed. No paid API, subscription, account or key is required for these delivered workflows.

Manual-review photos stay in the browser. The separate local-analysis action explicitly sends prepared photo copies to your backend and its loopback Ollama service after permission. VIN lookup sends the entered VIN only to NHTSA after you click its lookup button. Existing fixtures, manual reports, manufacturer metadata and model output are kept separate.

## Run locally

Prerequisites: Python 3.12+, Node.js 24 LTS, npm, and a Chromium browser for browser tests. No database, API keys, or Docker daemon is needed.

**Windows PowerShell:** use the [native Windows commands](docs/windows-setup.md), which do not require `make` or virtualenv activation. The Makefile commands below are for Linux/macOS or an appropriate Unix shell. Windows CI is configured; native Windows execution has not been verified from this Linux development machine.

PowerShell shortcuts from the repository root are `.\scripts\setup.ps1`, then `.\scripts\start-api.ps1` and `.\scripts\start-web.ps1` in separate terminals. Setup refreshes the pinned dependencies and checks Pillow. Direct-command equivalents are available if local script policy blocks `.ps1` files. See the [operational release checklist](docs/release-operations.md) for clean-checkout verification and the limits of configured versus observed CI evidence.

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

## Available tools

The home-page header links to **Review evidence**, **Plan budget** and **Local photo analysis**.

| Tool | Route | What works |
| --- | --- | --- |
| Vehicle evidence review | `/review` | User-entered details, browser-local photos, observations, JSON export and printing |
| Free manufacturer lookup | In `/review`, below the VIN fields | Explicit NHTSA vPIC lookup and optional application of make/model/year; no auction or history verification |
| Budget planner | `/budget` | Entered low/base/high costs, auction-fee bands, coverage/evidence gaps, indicative bid ceiling, export/print/reset |
| Local photo analysis | `/local-inspection` | Optional installed-model experiment; disabled until local runtime/model are configured |
| Auction reference resolver | `/` | Existing clearly labelled synthetic identity and authored MOCK-preview demonstrations |

## Budget planning

Enter a hammer-bid assumption and your sourced cost ranges. Address every category with costs or an explicit not-applicable reason. Unknown categories and auction fees remain missing; they are not silently counted as zero. Sources need dates, and user-labelled quotes need an explicit validity end date. The application does not invent a quote expiry or fetch supplier prices.

Auction fees can vary by bid. Enter contiguous bands from zero to an open-ended final band; each band's flat fee plus percentage applies to the **entire bid**, not just its marginal portion. Exclude the same fee from fixed broker costs to avoid double counting. No Copart/IAAI fee table or Georgian tax default is supplied.

For a planning ceiling, also enter conservative market value, required savings and an additional risk reserve; zero must be intentional. The solver uses high costs and bid-dependent fees, testing whole cents. Missing required inputs withhold the ceiling. The result is indicative and based on user inputs, never an independently validated bid recommendation. Costs and results are USD-only; no exchange rate is guessed.

Read the [calculator requirements](docs/v1-budget-requirements.md), [current official Georgian cost evidence](docs/georgia-cost-evidence.md), and [executed increment tests](docs/v1-increment-test-report.md). A researched statute is not a fully validated tax engine.

## Optional local AI

This requires a separate trusted local Ollama installation and eligible image-capable model; the normal app and budget planner work without it. The application never downloads a model from an HTTP request or silently uses a hosted AI service. Start the local runtime with cloud features disabled, then explicitly enable the API feature. See [local vision setup](docs/local-vision.md) and [actual runtime/model smoke evidence](docs/local-model-smoke.md) for tested artifacts, observed limitations and commands.

The first small-model experiment produced weak semantic output. The subsequently tested `qwen3-vl:2b` completed the real browser-proxy/API/runtime path in about 46 seconds and correctly abstained on the owned non-vehicle engineering image. This is runtime and one-case instruction-following evidence, not an automotive benchmark. All model findings remain experimental, with safety-critical systems unknown and no localization overlays or confident safety verdicts.

The [1.0 readiness assessment](docs/v1-release-readiness.md) records the remaining exact-auction, real-image quality, pricing/tax and deployment gates. This delivery is a development increment, not a declaration that the full automatic product is finished.

## Review your own evidence — no paid APIs

From the home page select **Review your own evidence**, or open `/review` on your local app.

1. Enter the original Copart or IAAI URL and any vehicle details you know. An IAAI stock number is an optional user claim, separate from the page ID in the URL.
2. Optionally select up to six permitted local JPEG/PNG images (8 MiB each, 24 MiB total, at most 20 megapixels per original). The browser checks and resizes them, strips metadata from prepared copies, and computes their hashes. It does not upload photo bytes. Use photos you are permitted to process; selecting a photo does not establish its rights or auction identity.
3. Add your observations, possible concerns or unknowns, linked to an image where applicable. These are **USER_REPORTED** entries; no damage is automatically detected.
4. Prepare the review. Read the unverified identity, user-reported entries and physical-inspection checklist. Structural, SRS, ADAS, cooling, suspension and mechanical condition remain unknown.
5. Download the JSON report or print the review using the browser's print dialog. JSON contains metadata and text, not photo bytes. Keep your own images if you need to retain their evidence; print can include the currently displayed local images.

The review is held only in the current page; **Clear review** or refreshing clears it. Editing inputs invalidates the old report. There is no database, saved account history or server photo store. A downloaded or printed copy is under your control and can contain sensitive vehicle information.

`POST /api/v1/manual-reviews` validates bounded user-supplied metadata without calling a provider. It never returns `MATCHED`. Image hashes are client declarations, not server verification of pixels. This route works independently of the configured demonstration provider. The manual-review JSON body is limited to 32 KiB; existing resolver/preview requests retain their 16 KiB limit.

No API subscription or token is required. Hosting, your own device resources and printing are separate operating costs. The [zero-API scope](docs/sprint-4-zero-api-scope.md), [delivery record](docs/sprint-4-delivery.md) and [executed test report](docs/sprint-4-test-report.md) record the delivered boundary and unresolved automatic lookup/AI work.

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

Provider discovery: the [current research recommendation](docs/research/provider-selection-2026-10-22.md) and [reviewable commercial inquiry drafts](docs/research/provider-findings-2026-10-22.md) record verified public findings and unresolved access questions. No external provider is enabled.
