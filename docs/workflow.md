# Research Workflow

This repository is a sanitized framework for local quantitative research. It is designed to be useful as public infrastructure while keeping private signal definitions, thresholds, account records, and data outside the repository.

## Flow

1. Prepare market data as CSV files with `date`, `instrument`, `open`, `high`, `low`, `close`, and optional liquidity columns.
2. Build target-position events from a strategy module.
3. Run the event-based backtest with explicit entry date, exit date, entry price mode, exit price mode, commissions, tax, and minimum fee assumptions.
4. Generate CSV and Markdown reports under `outputs/`.
5. Send optional notifications from environment variables only.

## Extension Points

- Add data adapters under `src/research_workflow/data/`.
- Add private strategies in a separate private package or repository.
- Add execution constraints under `src/research_workflow/backtest/`.
- Add report templates under `src/research_workflow/reports.py`.

## Public Strategy Policy

The included strategy is intentionally simple and only demonstrates the framework. Do not publish private signal logic, private parameter values, private performance reports, account positions, brokerage exports, or market-data dumps.
