# Native Windows / PowerShell setup

The Unix `Makefile` is optional. Windows PowerShell normally has no `make`; use the equivalent commands below from the cloned repository root. Install Python 3.12 (with its `py` launcher), Node.js 24 LTS, npm, and Git first.

These are native PowerShell instructions. The current development machine is Linux, so native execution is pending the Windows CI job and user verification. The Python application and npm scripts are shared; no virtualenv activation or execution-policy change is needed.

## Install

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r services/api/requirements.txt
npm --prefix apps/web ci
```

If `py -3.12` is unavailable, install Python 3.12 with its launcher. If Python 3.12 is already your `python`, `python -m venv .venv` is equivalent. If npm is installed but PowerShell blocks `npm.ps1`, use `npm.cmd` in these commands.

## Run (two terminals)

Terminal 1, repository root:

```powershell
# Optional: fixture (default), simulation (offline), or bidcars (disabled).
$env:AUCTION_PROVIDER = "fixture"
.\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir services/api --host 127.0.0.1 --port 8000 --reload
```

Terminal 2, same repository root:

```powershell
$env:NEXT_TELEMETRY_DISABLED = "1"
npm --prefix apps/web run dev
```

Open port 3000 in your own computer's browser. Use the fixture examples in the README. Stop each server with Ctrl+C. Switching `AUCTION_PROVIDER` requires restarting the API; setting it in the web terminal does not reconfigure the API.

`simulation` is also hand-authored offline data, with a SIMULATED label. `bidcars` demonstrates denied access and makes no remote request. No mode configures or enables a commercial integration.

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
