param(
  [string]$Root = "",
  [string]$DataRoot = "",
  [int]$Port = 8422,
  [switch]$NoOpen,
  [switch]$Foreground
)

$ErrorActionPreference = "Stop"

$ToolsDir = Split-Path -Parent $MyInvocation.MyCommand.Path
. (Join-Path $ToolsDir "python.ps1")

$ProjectRoot = if ($Root) { (Resolve-Path -LiteralPath $Root).Path } else { (Resolve-Path -LiteralPath (Join-Path $ToolsDir "..")).Path }
$DefaultDataRoot = if ($env:ANIMA_DATASET_ROOT) { $env:ANIMA_DATASET_ROOT } else { "D:\zhenzhen-asset" }
$WorkspaceRoot = if ($DataRoot) { [System.IO.Path]::GetFullPath($DataRoot) } else { [System.IO.Path]::GetFullPath($DefaultDataRoot) }
$SrcPath = Join-Path $ProjectRoot "src"
$env:PYTHONPATH = if ($env:PYTHONPATH) { "$SrcPath;$env:PYTHONPATH" } else { $SrcPath }
$PythonCommand = Get-AnimaPython
$LogDir = Join-Path $ProjectRoot "logs"
$PidFile = Join-Path $ProjectRoot "gui_server_pid.txt"
$PortFile = Join-Path $ProjectRoot "gui_server_port.txt"
$StdOut = Join-Path $LogDir "gui_stdout.log"
$StdErr = Join-Path $LogDir "gui_stderr.log"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

Write-Host "Zhenzhen Training Dataset Downloader"
Write-Host "Project: $ProjectRoot"
Write-Host "Download root: $WorkspaceRoot"
Write-Host "Python: $PythonCommand"
Write-Host ""

function Test-GuiServer {
  param([int]$CandidatePort)
  try {
    $status = Invoke-RestMethod -Uri "http://127.0.0.1:${CandidatePort}/api/status" -TimeoutSec 1
    if ($status.root) { return $status }
  } catch {}
  return $null
}

function Find-GuiServer {
  $trimChars = [System.IO.Path]::DirectorySeparatorChar, [System.IO.Path]::AltDirectorySeparatorChar
  $desiredRoot = [System.IO.Path]::GetFullPath($WorkspaceRoot).TrimEnd($trimChars)
  for ($candidate = $Port; $candidate -lt ($Port + 20); $candidate++) {
    $status = Test-GuiServer $candidate
    if ($status) {
      $serverRoot = [System.IO.Path]::GetFullPath([string]$status.root).TrimEnd($trimChars)
      if ($serverRoot -ieq $desiredRoot) {
        return [pscustomobject]@{ Port = $candidate; Status = $status }
      }
    }
  }
  return $null
}

function Open-GuiBrowser {
  param([int]$OpenPort)
  $url = "http://127.0.0.1:${OpenPort}/"
  if (-not $NoOpen) {
    Start-Process $url | Out-Null
  }
  Write-Host "URL: $url"
}

$existing = Find-GuiServer
if ($existing) {
  Write-Host "Server is already running."
  Set-Content -Path $PortFile -Value $existing.Port -Encoding ASCII
  Open-GuiBrowser $existing.Port
  exit 0
}

$argsList = @("-u", "-m", "anima_dataset.gui_server", "--root", $WorkspaceRoot, "--port", "$Port", "--no-open")

if ($Foreground) {
  & $PythonCommand @argsList
  if ($LASTEXITCODE -ne 0) {
    throw "GUI server exited with code $LASTEXITCODE."
  }
  exit 0
}

Remove-Item -LiteralPath $StdOut,$StdErr -Force -ErrorAction SilentlyContinue
$process = Start-Process -FilePath $PythonCommand -ArgumentList $argsList -RedirectStandardOutput $StdOut -RedirectStandardError $StdErr -PassThru -WindowStyle Hidden
Set-Content -Path $PidFile -Value $process.Id -Encoding ASCII

Write-Host "Starting local server, PID: $($process.Id)"
$started = $null
for ($i = 0; $i -lt 40; $i++) {
  Start-Sleep -Milliseconds 500
  if ($process.HasExited) { break }
  $started = Find-GuiServer
  if ($started) { break }
}

if (-not $started) {
  Write-Host ""
  Write-Host "Startup failed. Logs:"
  Write-Host "---- stdout ----"
  Get-Content -Raw $StdOut -ErrorAction SilentlyContinue
  Write-Host "---- stderr ----"
  Get-Content -Raw $StdErr -ErrorAction SilentlyContinue
  if (-not $process.HasExited) {
    Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
  }
  exit 1
}

Set-Content -Path $PortFile -Value $started.Port -Encoding ASCII
Write-Host "Startup succeeded."
Open-GuiBrowser $started.Port
Write-Host ""
Write-Host "The server keeps running in the background. To stop it, end the process id written in gui_server_pid.txt."
