# Auction Intelligence — Sprint 1

A fixture-only auction listing resolver for buyers importing damaged vehicles into Georgia. Paste a supported Copart or IAAI URL to see whether synthetic provider records corroborate the exact listing identity.

**All displayed records are MOCK data.** No auction website is fetched. Bid.Cars is an unlicensed integration candidate, not an enabled service. This sprint contains no AI analysis, repair estimates, bid recommendations, login, payments, or third-party photographs.

## Run locally

Prerequisites: Python 3.12+, Node.js 24 LTS, npm, and a Chromium browser for browser tests. No database, API keys, or Docker daemon is needed.

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

Install a Playwright-managed browser once, then run the desktop and mobile Chromium suite. Playwright starts both applications automatically when they are not already running:

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

`make test` runs pytest and browser tests together. To serve the production frontend after `make build`, run `npm --prefix apps/web start` with the API running. Test output directories, dependencies, virtualenvs, and build files are ignored by Git.

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

The API returns HTTP 200 for these domain outcomes, with `status`, parsed `reference`, corroborated `identity` when available, candidates, evidence, reasons, and warnings. Invalid/unsupported URL input returns HTTP 422. Provider errors remain distinct from missing records. A successful result includes vehicle metadata, provenance, per-field evidence, and event metadata.

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
services/api/tests/       Parser, matcher, provider, API regression tests
docs/                     Handover, acceptance criteria, design, architecture
```

The fixture dataset is versioned with the provider implementation. It uses in-memory records and no persistent user state. Its source timestamps describe synthetic snapshots; they do not promise freshness. See [architecture decisions](docs/decisions/001-resolver-boundaries.md), [provider integration guide](docs/source-integrations.md), [acceptance criteria](docs/sprint-1-requirements.md), and the [supplied handover](docs/auction_intelligence_handover.md).

Local validation results and acceptance coverage are recorded in the [Sprint 1 test report](docs/sprint-1-test-report.md). The GitHub Actions workflow runs these checks after the project is pushed; it has not been executed remotely here. Python's `requirements.txt` pins the tested runtime and test dependencies; `pyproject.toml` declares the package and direct dependencies. Refresh the pinned file in an isolated environment when intentionally updating those declarations, then rerun the suites and dependency audit.

## Limits and next decisions

English is the prototype language; Georgian localization timing remains open. Production coverage, data/photo rights, provider contracts, persistence, retention, and freshness require separate decisions. Fixture tests verify resolution behavior and app integration, not live auction accuracy. The disabled Bid.Cars placeholder must remain disabled until authorized integration work is explicitly undertaken.
