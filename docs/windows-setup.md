# Native Windows / PowerShell setup

The Unix `Makefile` is optional. Windows PowerShell normally has no `make`; use the equivalent commands below from the cloned repository root. Install Python 3.12 (with its `py` launcher), Node.js 24 LTS, npm, and Git first.

These are native PowerShell instructions. The current development machine is Linux, so native execution is pending the Windows CI job and user verification. The Python application and npm scripts are shared; no virtualenv activation or execution-policy change is needed.

## Install

From the repository root, the setup script installs both sets of pinned dependencies and verifies that the image decoder is importable:

```powershell
.\scripts\setup.ps1
```

Use `-InstallBrowser` to also install Chromium for browser tests. If Python 3.12+ is already available under a different executable, use `.\scripts\setup.ps1 -PythonCommand python`. The script reuses an existing Windows virtual environment; if that environment uses an unsupported Python version, recreate it intentionally before setup. It does not change execution policy, activate the virtual environment, install Python/Node, or download an AI model.

If local policy blocks `.ps1` files, use the equivalent commands below; no execution-policy change is needed:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r services/api/requirements.txt
npm --prefix apps/web ci
```

If `py -3.12` is unavailable, install Python 3.12 with its launcher. If Python 3.12 is already your `python`, `python -m venv .venv` is equivalent. If npm is installed but PowerShell blocks `npm.ps1`, use `npm.cmd` in these commands.

## Run (two terminals)

The launcher scripts can be invoked from any working directory, using their actual path. They bind development servers to your computer's loopback interface. Run each in its own terminal:

```powershell
.\scripts\start-api.ps1
```

```powershell
.\scripts\start-web.ps1
```

Use `start-api.ps1 -Provider simulation` for the offline simulation mode, or `-Port 8001` for a different API port. When changing the API port, set `$env:API_BASE_URL = "http://127.0.0.1:8001"` in the web terminal before starting it. The scripts preserve other existing process variables, including optional local vision configuration. Use `start-web.ps1 -Production` only after a successful frontend build. Ctrl+C stops the foreground server.

Direct-command equivalents, also useful when script policy prevents running launchers:

Terminal 1, repository root:

```powershell
# Optional: fixture (default), simulation (offline), bidcars (disabled), or apibara.
$env:AUCTION_PROVIDER = "fixture"
.\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir services/api --host 127.0.0.1 --port 8000 --reload
```

Terminal 2, same repository root:

```powershell
$env:NEXT_TELEMETRY_DISABLED = "1"
npm --prefix apps/web run dev
```

Open port 3000 in your own computer's browser. Use the fixture examples in the README. Stop each server with Ctrl+C. Switching `AUCTION_PROVIDER` requires restarting the API; setting it in the web terminal does not reconfigure the API.

`simulation` is also hand-authored offline data, with a SIMULATED label. `bidcars` demonstrates denied access and makes no remote request.

To configure the optional Apibara metadata adapter, stop the API and use the same API terminal:

```powershell
$env:APIBARA_API_KEY = "YOUR_APIBARA_KEY"
$env:APIBARA_ENABLE = "1"
.\scripts\start-api.ps1 -Provider apibara
```

An actual Apibara key is required and remains server-side; never commit it. Without a key and the enable flag, this mode makes no provider request. The provider advertises a free tier, but actual plan entitlements and any charges are determined by the provider. The documented URL endpoint and the adapter have not yet been tested together with a real key. Copart metadata is checked against the submitted source and lot; IAAI page IDs remain distinct from stock numbers and unresolved without a reliable mapping. No third-party photos are fetched or sent for analysis.

## Checks

```powershell
.\.venv\Scripts\python.exe -m pytest services/api/tests
npm --prefix apps/web run typecheck
npm --prefix apps/web run build
```

Run builds separately from browser checks. For a clean browser test run, stop the two servers first. Install a Playwright-managed Chromium once:

```powershell
Push-Location apps/web
npx playwright install chromium
Pop-Location
```

The browser configuration selects `.venv\Scripts\python.exe` on Windows and `.venv/bin/python` on Linux/macOS. It starts its own API and web servers. Run one mode at a time:

```powershell
$env:E2E_PROVIDER_MODE = "fixture"
npm --prefix apps/web run test:e2e -- --workers=2

$env:E2E_PROVIDER_MODE = "simulation"
npm --prefix apps/web run test:e2e -- --workers=2

$env:E2E_PROVIDER_MODE = "bidcars"
npm --prefix apps/web run test:e2e -- --workers=2

Remove-Item Env:E2E_PROVIDER_MODE
```

No provider keys, real auction records, invoices, or images are needed. Keep credential values out of PowerShell history and repository files if a future authorized integration requires them.

## Updating to Sprint 3

Stop the API and web terminals with Ctrl+C, then run from the repository root:

```powershell
git pull
.\.venv\Scripts\python.exe -m pip install -r services/api/requirements.txt
```

The dependency refresh installs the pinned PNG decoder used to validate authored fixture images. Restart the two terminals using the commands above. Resolve the Copart example and select **Open MOCK inspection preview**. The images are project-authored illustrations; no auction photo or AI service is used. See the README for partial, missing-photo and engine-failure examples. This guide does not claim the native Windows test suite has been executed locally.

## Zero-paid-API manual review

After `git pull`, start the existing API and web commands above, then select **Review your own evidence** from the home page. No new API account, key or paid service is required. The existing dependency requirements still apply.

Use an original Copart/IAAI URL and photos you are permitted to process. Photo bytes remain in your browser; the backend validates user-supplied text and declared metadata only. The result is unverified and is not AI analysis. JSON export excludes image bytes; browser print can include the displayed images. Refreshing clears the current review.

## Budget, free VIN details and optional local analysis

After pulling this development increment, use the same backend and frontend startup commands. No new Python/npm dependency or paid API account is required. The home header now links directly to Review evidence, Plan budget and Local photo analysis.

- In Review evidence, enter a full VIN and select **Look up manufacturer details**. This explicitly sends the VIN only to the free official NHTSA service; apply returned fields only after reviewing them. It does not verify the auction listing or vehicle history.
- In Plan budget, provide cost ranges and dated sources, explicit non-applicable categories and the actual fee schedule. No Georgian tax/repair price defaults are fabricated. Missing costs withhold a bid ceiling.
- Local photo analysis needs Ollama, model weights, memory and compute. It is experimental and disabled by default. After installing Ollama from its official site and running `scripts/setup.ps1`, stop any existing Ollama desktop service, then run `.\scripts\start-local-vision.ps1` in place of `start-api.ps1`. The launcher starts its own loopback service with cloud features disabled and downloads the tested model (approximately 1.9 GB) if missing. Start the web app in a separate terminal as usual. It refuses an occupied Ollama port and never stops an existing service. See [local vision setup](local-vision.md) for details and limitations.

Native Windows execution and hosted CI remain unobserved in the Linux workspace; see the current increment test report for what actually ran.

For a release candidate, use the [operational checklist](release-operations.md). A configured Windows CI job is not evidence of a passing hosted run.
