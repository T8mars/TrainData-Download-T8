function Test-AnimaPython {
  param([string]$Path)
  if (-not $Path) { return $false }
  if ($Path -like "*\WindowsApps\python.exe") { return $false }
  if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { return $false }
  & $Path -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)" *> $null
  return $LASTEXITCODE -eq 0
}

function Get-AnimaPython {
  $candidates = New-Object System.Collections.Generic.List[string]
  if ($env:ANIMA_PYTHON) { $candidates.Add($env:ANIMA_PYTHON) }
  $candidates.Add("C:\ProgramData\anaconda3\python.exe")
  $candidates.Add("C:\Program Files\Python312\python.exe")
  $candidates.Add("C:\Program Files\Python311\python.exe")
  foreach ($cmd in Get-Command python -All -ErrorAction SilentlyContinue) {
    $candidates.Add($cmd.Source)
  }

  foreach ($candidate in $candidates) {
    if (Test-AnimaPython $candidate) {
      return (Resolve-Path -LiteralPath $candidate).Path
    }
  }

  throw "Python 3.10+ was not found. Set ANIMA_PYTHON to a real python.exe, for example C:\ProgramData\anaconda3\python.exe."
}
