$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$env:PYTHONPATH = Join-Path $Root "src"

python -m research_workflow.cli example-backtest `
  --data-path (Join-Path $Root "examples\data\sample_prices.csv") `
  --start-date "2024-01-02" `
  --end-date "2024-01-31" `
  --run-name "example_momentum"
