[CmdletBinding()]
param(
    [ValidateRange(1, 65535)]
    [int]$Port = 3000,
    [switch]$Production
)

$ErrorActionPreference = 'Stop'
$repository = Split-Path -Parent $PSScriptRoot
if (-not (Test-Path (Join-Path $repository 'apps/web/node_modules/next/package.json'))) {
    throw 'Run scripts/setup.ps1 first; frontend dependencies are missing.'
}
$previousTelemetry = $env:NEXT_TELEMETRY_DISABLED
Push-Location $repository
try {
    $env:NEXT_TELEMETRY_DISABLED = '1'
    if ($Production) {
        # Production requires an existing successful npm --prefix apps/web run build.
        & npm.cmd --prefix apps/web run start -- --hostname 127.0.0.1 --port $Port
    } else {
        & npm.cmd --prefix apps/web run dev -- --hostname 127.0.0.1 --port $Port
    }
    if ($LASTEXITCODE -ne 0) { throw "Web app exited with code $LASTEXITCODE." }
} finally {
    $env:NEXT_TELEMETRY_DISABLED = $previousTelemetry
    Pop-Location
}
