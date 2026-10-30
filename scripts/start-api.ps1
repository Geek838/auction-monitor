[CmdletBinding()]
param(
    [ValidateSet('fixture', 'simulation', 'bidcars')]
    [string]$Provider = 'fixture',
    [ValidateRange(1, 65535)]
    [int]$Port = 8000,
    [switch]$NoReload
)

$ErrorActionPreference = 'Stop'
$repository = Split-Path -Parent $PSScriptRoot
$python = Join-Path $repository '.venv\Scripts\python.exe'
if (-not (Test-Path $python)) { throw 'Run scripts/setup.ps1 first; the Windows virtual environment is missing.' }
$previousProvider = $env:AUCTION_PROVIDER
Push-Location $repository
try {
    & $python -c 'import fastapi, PIL, uvicorn'
    if ($LASTEXITCODE -ne 0) { throw 'API dependencies are missing. Run scripts/setup.ps1 to install the pinned requirements.' }
    $env:AUCTION_PROVIDER = $Provider
    $uvicornArguments = @('-m', 'uvicorn', 'app.main:app', '--app-dir', 'services/api', '--host', '127.0.0.1', '--port', "$Port")
    if (-not $NoReload) { $uvicornArguments += '--reload' }
    & $python @uvicornArguments
    if ($LASTEXITCODE -ne 0) { throw "API exited with code $LASTEXITCODE." }
} finally {
    $env:AUCTION_PROVIDER = $previousProvider
    Pop-Location
}
