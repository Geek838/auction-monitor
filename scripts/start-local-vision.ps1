[CmdletBinding()]
param(
    [ValidateRange(1, 65535)]
    [int]$Port = 8000
)

$ErrorActionPreference = 'Stop'
$repository = Split-Path -Parent $PSScriptRoot
$python = Join-Path $repository '.venv\Scripts\python.exe'
$ollama = Get-Command ollama.exe -ErrorAction SilentlyContinue
if (-not $ollama) { throw 'Ollama was not found. Install it from https://ollama.com/download and restart this terminal.' }
if (-not (Test-Path $python)) { throw 'Run scripts/setup.ps1 first to install the application dependencies.' }

# Never take over an existing desktop service: its cloud settings are unknown.
$probe = [System.Net.Sockets.TcpClient]::new()
try {
    $connect = $probe.ConnectAsync('127.0.0.1', 11434)
    try { $occupied = $connect.Wait(1000) -and $probe.Connected }
    catch [System.AggregateException] { $occupied = $false }
    if ($occupied) {
        throw 'Port 11434 is already in use. Close the existing Ollama application, then retry. This script cannot verify another service is configured for local-only inference.'
    }
} finally { $probe.Dispose() }

$variables = @('OLLAMA_HOST', 'OLLAMA_NO_CLOUD', 'OLLAMA_NUM_PARALLEL', 'OLLAMA_MAX_QUEUE', 'LOCAL_VISION_ENABLED', 'LOCAL_VISION_MODEL')
$previous = @{}
foreach ($name in $variables) { $previous[$name] = [Environment]::GetEnvironmentVariable($name, 'Process') }
$daemon = $null
Push-Location $repository
try {
    $env:OLLAMA_HOST = '127.0.0.1:11434'
    $env:OLLAMA_NO_CLOUD = '1'
    $env:OLLAMA_NUM_PARALLEL = '1'
    $env:OLLAMA_MAX_QUEUE = '1'
    $env:LOCAL_VISION_ENABLED = '1'
    $env:LOCAL_VISION_MODEL = 'qwen3-vl:2b'
    Write-Warning 'Photo analysis is experimental. Real-vehicle smoke tests did not produce usable findings; model output is not a qualified inspection.'
    Write-Host 'Starting local Ollama with cloud features disabled.'
    $daemon = Start-Process -FilePath $ollama.Source -ArgumentList 'serve' -NoNewWindow -PassThru
    $ready = $false
    for ($attempt = 0; $attempt -lt 40; $attempt++) {
        if ($daemon.HasExited) { throw 'The local Ollama service exited before startup. Check whether another service is using port 11434.' }
        $listeners = @(Get-NetTCPConnection -LocalPort 11434 -State Listen -ErrorAction SilentlyContinue)
        if ($listeners.Count -eq 0) { Start-Sleep -Milliseconds 250; continue }
        if (@($listeners | Where-Object { $_.OwningProcess -ne $daemon.Id -or $_.LocalAddress -ne '127.0.0.1' }).Count -gt 0) {
            throw 'Another process owns port 11434, or the listener is not loopback-only. No photo analysis was started.'
        }
        try {
            $inventory = Invoke-RestMethod -Uri 'http://127.0.0.1:11434/api/tags' -TimeoutSec 2
            if ($null -ne $inventory.models) { $ready = $true; break }
        } catch { Start-Sleep -Milliseconds 250 }
    }
    if (-not $ready) { throw 'The local Ollama service did not become ready.' }

    if (-not ($inventory.models | Where-Object { $_.name -eq 'qwen3-vl:2b' })) {
        Write-Host 'Downloading qwen3-vl:2b from Ollama (approximately 1.9 GB). This requires disk space and an internet connection.'
        & $ollama.Source pull 'qwen3-vl:2b'
        if ($LASTEXITCODE -ne 0) { throw 'The local model download failed. Check your connection and available disk space.' }
    }
    if ($daemon.HasExited) { throw 'The local Ollama service stopped; no analysis is available.' }
    Write-Host 'Starting the API with experimental local photo analysis enabled. Press Ctrl+C to stop.'
    & $python -m uvicorn app.main:app --app-dir services/api --host 127.0.0.1 --port $Port
    if ($LASTEXITCODE -ne 0) { throw "API exited with code $LASTEXITCODE." }
} finally {
    # Only stop the process tree started by this invocation, never a pre-existing service.
    if ($daemon -and -not $daemon.HasExited) {
        & taskkill.exe /PID $daemon.Id /T /F | Out-Null
    }
    foreach ($name in $variables) { [Environment]::SetEnvironmentVariable($name, $previous[$name], 'Process') }
    Pop-Location
}
