# Installation and release operations

Reviewed **30 October 2026 (Asia/Tbilisi)**. This is the repeatable installation and verification procedure for the development application, not an approval to advertise automatic auction inspection as released 1.0. The [readiness assessment](v1-release-readiness.md) tracks product and evidence gates separately.

## Supported configuration and installation

Use Git to clone `https://github.com/Geek838/auction-monitor.git`, Python 3.12+ and Node.js 24 LTS (`.nvmrc`). Keep the same repository root in both server terminals. No database, provider credentials, account or paid API is required for the default synthetic resolver, manual review and budget tools. Optional free network integrations and local model processing are separate explicit actions.

On Windows, follow [PowerShell setup](windows-setup.md). `scripts/setup.ps1` creates or reuses `.venv`, installs `services/api/requirements.txt`, checks dependency consistency and imports Pillow before installing the frontend from its lockfile. Re-run it after pulling a dependency change; an old virtual environment is a common cause of `No module named PIL`. Start `scripts/start-api.ps1` and `scripts/start-web.ps1` in separate terminals. Script-policy restrictions have direct-command equivalents in the Windows guide; no system policy change is required.

On Linux/macOS, use `make install`, then `make api` and `make web` in separate terminals. Defaults are API `127.0.0.1:8000` and frontend port 3000. Existing npm commands bind frontend to all interfaces; use `npm --prefix apps/web run dev -- --hostname 127.0.0.1` when you want loopback only. Environment variables belong to the process that uses them; `.env.example` documents settings, but the API does not automatically read an environment file.

Setup/start scripts do not download or launch Ollama. Local photo inference remains disabled unless explicitly configured; see [local vision](local-vision.md).

## Release-candidate checks

Run checks from a clean checkout with servers stopped. Do not run a production build, type generation and browser/dev server concurrently against the same `.next` directory.

1. Install pinned Python dependencies and `npm ci`; run `python -m pip check` through the repository virtual environment.
2. Run `.venv/bin/python scripts/check-api.py` (Windows: `.\.venv\Scripts\python.exe scripts/check-api.py`). This runs backend and any installed offline evaluation-tool tests, prints verbose test IDs, emits diagnostic stacks after a 60-second stall and terminates only its owned test process group after five minutes. JUnit results are written to `.cache/qa/backend-results.xml`. The direct `python -m pytest services/api/tests` command remains available for development.
3. Run `npm --prefix apps/web run typecheck`, then `npm --prefix apps/web run build` sequentially.
4. Install Playwright Chromium once. Run `npm --prefix apps/web run test:e2e -- --workers=2` separately for `E2E_PROVIDER_MODE=fixture`, `simulation` and `bidcars`. Clear the mode variable afterward. Browser tests start their own isolated servers and should fail on occupied ports.
5. Start the API and built frontend (`npm --prefix apps/web run start -- --hostname 127.0.0.1`). Check `http://127.0.0.1:8000/api/v1/health` and the homepage. Exercise a clearly labelled fixture resolution, manual review, incomplete budget and any specifically configured free network/local model capability.
6. Stop foreground servers with Ctrl+C, and verify only the owned server processes have stopped. Keep dependency directories, model weights, secrets and generated test files out of commits.

API/provider status in the health response describes the configured service; it does not prove live auction access or model availability. Test doubles and authored fixtures do not substitute for recorded live-service checks, automotive evaluation, official calculator comparisons or actual user validation.

## CI evidence

`.github/workflows/ci.yml` configures Linux and Windows jobs for Python 3.12 and Node.js 24. Both install pinned dependencies, run backend/tool tests through the bounded diagnostic runner, typecheck, build, then run desktop/mobile Chromium suites for all three offline provider modes. The Windows job parses the PowerShell launchers and installs through `scripts/setup.ps1`, using Windows PowerShell. After building, it also starts `start-api.ps1 -NoReload` and `start-web.ps1 -Production`, checks real loopback API/homepage/proxy responses, and stops only those owned process trees. The startup check refuses occupied ports, waits at most 60 seconds for each server and records separate logs under `.cache/qa/`. Tests do not require paid services or local model downloads. Backend JUnit output and browser/startup failure artifacts are retained for seven days. Jobs have finite timeouts and a newer run cancels an older run for the same ref. Python/npm cache settings point to the same workspace directories used by installation.

The prior [29 October run](https://github.com/Geek838/auction-monitor/actions/runs/40859118207) is not a passing release run: Linux test/build steps succeeded, but the post-job Python cache save failed because the cache action expected a different directory from the Makefile; Windows exceeded its 20-minute job limit during pytest. Its Windows log archive was unavailable, so no particular stuck test or locking cause was established. The cache path is corrected, and verbose bounded test execution now provides evidence for diagnosing any repeat instead of silently waiting for the whole job to time out.

Review actual GitHub Actions run results and artifacts before recording CI as passed. The [first diagnostic run](https://github.com/Geek838/auction-monitor/actions/runs/41045518354) reported successful native Windows launcher parsing and execution of `setup.ps1`, but both backend steps continued to report in-progress beyond their configured deadlines without accessible logs during the bounded observation. This is unresolved hosted execution/reporting evidence, not a passing Windows suite. A subsequent push can cancel that run; do not count cancellation as a fix or infer a particular hanging test without a log.

A disposable Linux Python 3.12.14 virtual environment installed only `requirements.txt` and ran the combined backend/tool checks successfully with the explicit pytest configuration. `pip show auction-intelligence-api` confirmed no editable API package was installed. This verifies the runner does not depend on the onboarding environment's editable installation; it does not establish Windows or hosted CI success. Record the final frozen-suite counts in the increment's execution report.

## Release boundary

There is no production deployment, persistent user store, backup process, account system or payment service in this increment. Do not expose the local development application publicly as though it included authentication, multi-user isolation or production abuse controls. User-exported files remain under the user's control; selecting or printing third-party images does not establish rights to process them.

Before a public release, document the chosen host and TLS, request limits, free service usage requirements, retained data/deletion policy, operational owner and actual deployment smoke results. Optional local inference needs a trusted loopback-only, cloud-disabled runtime with hardware limits and a supported model. The application should continue to fail explicitly when data or permissions are absent.
