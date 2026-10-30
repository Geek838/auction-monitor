[CmdletBinding()]
param(
    # CI or an existing installation may supply a Python 3.12+ executable.
    [string]$PythonCommand = '',
    [switch]$InstallBrowser
)

$ErrorActionPreference = 'Stop'
$repository = Split-Path -Parent $PSScriptRoot
Push-Location $repository
try {
    if (-not (Test-Path '.venv\Scripts\python.exe')) {
        if ($PythonCommand) {
            & $PythonCommand -m venv .venv
        } else {
            & py -3.12 -m venv .venv
        }
        if ($LASTEXITCODE -ne 0) { throw 'Virtual environment creation failed. Install Python 3.12 or supply -PythonCommand.' }
    }

    $python = Join-Path $repository '.venv\Scripts\python.exe'
    & $python -c 'import sys; sys.exit(0 if sys.version_info >= (3, 12) else 1)'
    if ($LASTEXITCODE -ne 0) { throw 'Unsupported virtual environment.' }
    & $python -m pip install -r services/api/requirements.txt
    if ($LASTEXITCODE -ne 0) { throw 'Python dependency installation failed.' }
    & $python -m pip check
    if ($LASTEXITCODE -ne 0) { throw 'Python dependencies are inconsistent.' }
    & $python -c 'import fastapi, PIL, pydantic, uvicorn; from PIL import Image'
    if ($LASTEXITCODE -ne 0) { throw 'API dependency import check failed.' }
    Write-Host 'API dependencies, including Pillow, are available.'

    # npm.cmd avoids PowerShell selecting the npm.ps1 shim.
    & npm.cmd --prefix apps/web ci
    if ($LASTEXITCODE -ne 0) { throw 'Frontend dependency installation failed.' }
    if ($InstallBrowser) {
        Push-Location apps/web
        try {
            & npx.cmd playwright install chromium
            if ($LASTEXITCODE -ne 0) { throw 'Playwright Chromium installation failed.' }
        } finally { Pop-Location }
    }
    Write-Host 'Setup complete. Start the API and web app in separate terminals using scripts/start-api.ps1 and scripts/start-web.ps1.'
} finally { Pop-Location }
