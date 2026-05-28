param(
  [string]$Command = "menu",
  [string]$Root = ""
)

$ErrorActionPreference = "Stop"

$ToolsDir = Split-Path -Parent $MyInvocation.MyCommand.Path
. (Join-Path $ToolsDir "python.ps1")
$ProjectRoot = if ($Root) { (Resolve-Path -LiteralPath $Root).Path } else { (Resolve-Path -LiteralPath (Join-Path $ToolsDir "..")).Path }
$SrcPath = Join-Path $ProjectRoot "src"
$env:PYTHONPATH = if ($env:PYTHONPATH) { "$SrcPath;$env:PYTHONPATH" } else { $SrcPath }
$PythonCommand = Get-AnimaPython

function Invoke-Anima {
  param([string[]]$CliArgs)
  & $PythonCommand -m anima_dataset.cli --root $ProjectRoot @CliArgs
  if ($LASTEXITCODE -ne 0) {
    throw "Command failed with exit code $LASTEXITCODE."
  }
}

function Pause-IfInteractive {
  if ($Command -eq "menu") {
    Write-Host ""
    Read-Host "Press Enter to return to menu" | Out-Null
  }
}

function Show-Header {
  try { Clear-Host } catch {}
  Write-Host "Zhenzhen Training Dataset Downloader CLI"
  Write-Host "Project: $ProjectRoot"
  Write-Host "Python: $PythonCommand"
  Write-Host ""
}

function Show-Menu {
  Show-Header
  Write-Host "1. Init workspace"
  Write-Host "2. Download one URL"
  Write-Host "3. Download URL list"
  Write-Host "4. Import local file/folder"
  Write-Host "5. Extract archive"
  Write-Host "6. Hugging Face dataset"
  Write-Host "7. Wikimedia Commons"
  Write-Host "8. Internet Archive"
  Write-Host "9. Recent jobs"
  Write-Host "10. Recent assets"
  Write-Host "0. Exit"
  Write-Host ""
}

function Run-Init {
  Invoke-Anima @("init")
}

function Run-DownloadUrl {
  $url = Read-Host "URL"
  if (-not $url) { return }
  $filename = Read-Host "Optional filename (blank to auto-detect)"
  $header = Read-Host "Optional header, e.g. Authorization=Bearer token (blank to skip)"
  $args = @("download-url", $url)
  if ($filename) { $args += @("--filename", $filename) }
  if ($header) { $args += @("--header", $header) }
  Invoke-Anima $args
}

function Run-DownloadList {
  $file = Read-Host "URL list file path"
  if (-not $file) { return }
  Invoke-Anima @("download-list", $file)
}

function Run-Import {
  $path = Read-Host "Local file or folder path"
  if (-not $path) { return }
  Invoke-Anima @("import", $path)
}

function Run-Extract {
  $path = Read-Host "Archive path (.zip/.cbz/.tar/.tgz)"
  if (-not $path) { return }
  Invoke-Anima @("extract", $path)
}

function Run-HuggingFace {
  $repo = Read-Host "Dataset repo id, e.g. deepghs/anime-bg"
  if (-not $repo) { return }
  $pattern = Read-Host "Include pattern, e.g. *.tar (blank for defaults)"
  $maxFiles = Read-Host "Max files (blank for no limit)"
  $args = @("hf", $repo)
  if ($pattern) { $args += @("--include", $pattern) }
  if ($maxFiles) { $args += @("--max-files", $maxFiles) }
  Invoke-Anima $args
}

function Run-Wikimedia {
  $mode = Read-Host "Use category or search? [c/s]"
  $value = Read-Host "Category/search text"
  if (-not $value) { return }
  $maxFiles = Read-Host "Max files (blank for no limit)"
  $args = @("wikimedia")
  if ($mode -eq "s") {
    $args += @("--search", $value)
  } else {
    $args += @("--category", $value)
  }
  if ($maxFiles) { $args += @("--max-files", $maxFiles) }
  Invoke-Anima $args
}

function Run-InternetArchive {
  $item = Read-Host "Internet Archive item id"
  if (-not $item) { return }
  $pattern = Read-Host "Include pattern, e.g. *.pdf (blank for defaults)"
  $maxFiles = Read-Host "Max files (blank for no limit)"
  $args = @("ia", $item)
  if ($pattern) { $args += @("--include", $pattern) }
  if ($maxFiles) { $args += @("--max-files", $maxFiles) }
  Invoke-Anima $args
}

function Run-Jobs {
  Invoke-Anima @("jobs", "--limit", "20")
}

function Run-Assets {
  Invoke-Anima @("assets", "--limit", "20")
}

function Run-Status {
  Show-Header
  Write-Host "Recent jobs"
  Invoke-Anima @("jobs", "--limit", "10")
  Write-Host ""
  Write-Host "Recent assets"
  Invoke-Anima @("assets", "--limit", "10")
}

switch ($Command) {
  "init" { Run-Init; exit 0 }
  "status" { Run-Status; exit 0 }
  "help" {
    Write-Host "Usage:"
    Write-Host "  .\launch.bat"
    Write-Host "  powershell -ExecutionPolicy Bypass -File tools\launcher.ps1 -Command status"
    exit 0
  }
  "menu" {}
  default { throw "Unknown launcher command: $Command" }
}

while ($true) {
  Show-Menu
  $choice = Read-Host "Select"
  try {
    switch ($choice) {
      "1" { Run-Init; Pause-IfInteractive }
      "2" { Run-DownloadUrl; Pause-IfInteractive }
      "3" { Run-DownloadList; Pause-IfInteractive }
      "4" { Run-Import; Pause-IfInteractive }
      "5" { Run-Extract; Pause-IfInteractive }
      "6" { Run-HuggingFace; Pause-IfInteractive }
      "7" { Run-Wikimedia; Pause-IfInteractive }
      "8" { Run-InternetArchive; Pause-IfInteractive }
      "9" { Run-Jobs; Pause-IfInteractive }
      "10" { Run-Assets; Pause-IfInteractive }
      "0" { exit 0 }
      default {
        Write-Host "Unknown option."
        Pause-IfInteractive
      }
    }
  } catch {
    Write-Host ""
    Write-Host "Error: $($_.Exception.Message)"
    Pause-IfInteractive
  }
}
