# dev-environment-setup probe (Windows)
# 协议：见 ..\references\probe-snapshot.md

$ErrorActionPreference = 'SilentlyContinue'

function Test-Tool {
  param([string]$Name, [string]$VersionFlag = '--version')
  $cmd = Get-Command $Name -ErrorAction SilentlyContinue
  if (-not $cmd) {
    return @{ available = $false }
  }
  $output = & $Name $VersionFlag 2>&1 | Select-Object -First 1
  $version = ''
  if ($output -match '(\d+\.\d+(?:\.\d+)?)') { $version = $Matches[1] }
  return @{ available = $true; path = $cmd.Source; version = $version }
}

# DesireCore API 探测
$portFile = Join-Path $env:USERPROFILE '.desirecore\agent-service.port'
$desirecoreApi = ''
$portFileExists = Test-Path $portFile
if ($portFileExists) {
  $port = (Get-Content $portFile -Raw).Trim()
  if ($port) {
    try {
      [System.Net.ServicePointManager]::ServerCertificateValidationCallback = { $true }
      $resp = Invoke-WebRequest -Uri "https://127.0.0.1:$port/api/runtime/environment" `
        -TimeoutSec 1 -UseBasicParsing -ErrorAction Stop
      if ($resp.StatusCode -eq 200) { $desirecoreApi = "https://127.0.0.1:$port" }
    } catch { }
  }
}

# WSL 检测
$wsl = $null
$wslOut = wsl --status 2>&1
if ($LASTEXITCODE -eq 0) {
  $version = ''
  $defaultDistro = ''
  if ($wslOut -match '(\d+)') { $version = $Matches[1] }
  $wsl = @{ installed = $true; version = $version; defaultDistro = $defaultDistro }
} else {
  $wsl = @{ installed = $false }
}

$arch = if ([Environment]::Is64BitOperatingSystem) { 'x64' } else { 'x86' }
if ($env:PROCESSOR_ARCHITECTURE -eq 'ARM64') { $arch = 'arm64' }

$result = @{
  platform              = 'win32'
  arch                  = $arch
  desirecore_api        = $desirecoreApi
  desirecore_port_file  = $portFileExists
  tools = @{
    python3 = (Test-Tool python)
    pip3    = (Test-Tool pip)
    node    = (Test-Tool node)
    npm     = (Test-Tool npm)
    docker  = (Test-Tool docker)
    podman  = (Test-Tool podman)
    git     = (Test-Tool git)
  }
  wsl = $wsl
}

$result | ConvertTo-Json -Depth 5 -Compress:$false
