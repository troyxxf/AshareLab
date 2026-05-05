# Research Workflow Template

This repository is a sanitized template for building a local quantitative research workflow.

It includes:

- generic CSV market-data loading;
- event-based backtesting;
- realistic execution assumptions;
- report generation;
- notification adapters that read credentials from environment variables;
- example strategies that are intentionally simple and not production advice.

It does not include private strategies, private thresholds, account details, tokens, local market databases, cached data, or backtest outputs from any private project.

## Quick Start

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\research-workflow example-backtest --run-name demo
```

The example uses synthetic sample data in `examples/data/sample_prices.csv`.

## Layout

```text
src/research_workflow/
  backtest/       Event backtest engines
  data/           CSV loading and validation
  execution/      Scheduling and notification helpers
  strategies/     Example non-proprietary strategies
  security/       Secret scanning utilities
examples/
  data/           Tiny synthetic sample data
  strategies/     Example strategy configuration
docs/             Workflow notes
scripts/          Local helper scripts
tests/            Lightweight tests
```

## Safety Rules

- Never commit `.env`.
- Never commit `cache/`, `outputs/`, `data/`, `bundle/`, local databases, broker exports, or market-data dumps.
- Keep proprietary strategies in a separate private repository.
- Treat this repository as infrastructure only.

## Disclaimer

This project is for research workflow engineering only. It is not investment advice and contains no profitable trading strategy.
