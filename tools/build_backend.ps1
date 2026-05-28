param(
  [string]$Root = ""
)

$ErrorActionPreference = "Stop"

$ToolsDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = if ($Root) { (Resolve-Path -LiteralPath $Root).Path } else { (Resolve-Path -LiteralPath (Join-Path $ToolsDir "..")).Path }
$PythonEntry = Join-Path $ProjectRoot "tools\backend_entry.py"
$SourcePath = Join-Path $ProjectRoot "src"
$WebPath = Join-Path $ProjectRoot "src\anima_dataset\web"
$SourcesPath = Join-Path $ProjectRoot "sources"
$DistPath = Join-Path $ProjectRoot "dist_backend"
$WorkPath = Join-Path $ProjectRoot "build_backend"

pyinstaller `
  --noconfirm `
  --clean `
  --name zhenzhen-backend `
  --onefile `
  --paths $SourcePath `
  --distpath $DistPath `
  --workpath $WorkPath `
  --specpath $WorkPath `
  --add-data "${WebPath};anima_dataset/web" `
  --add-data "${SourcesPath};sources" `
  $PythonEntry
