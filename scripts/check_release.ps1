$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$env:PYTHONPATH = Join-Path $Root "src"

Push-Location $Root
try {
  python -m compileall -q src tests
  python -m research_workflow.cli example-backtest `
    --data-path "examples\data\sample_prices.csv" `
    --start-date "2024-01-02" `
    --end-date "2024-01-31" `
    --run-name "release_check"
  python -m research_workflow.cli secret-scan --root "."
  if (Get-Command pytest -ErrorAction SilentlyContinue) {
    pytest -q
  }
  Write-Host "Release check passed."
}
finally {
  Pop-Location
}
