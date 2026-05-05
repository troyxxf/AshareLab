from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from research_workflow.backtest.event_engine import run_event_backtest
from research_workflow.backtest.metrics import build_round_trips, win_rate, yearly_equity_summary
from research_workflow.data.csv_loader import load_price_csv, split_by_instrument
from research_workflow.models import BacktestConfig
from research_workflow.reports import write_backtest_outputs
from research_workflow.security.secret_scan import scan_path
from research_workflow.strategies.example_momentum import build_example_momentum_targets

app = typer.Typer(help="Sanitized research workflow CLI")
console = Console()


@app.command("example-backtest")
def example_backtest(
    data_path: str = typer.Option("examples/data/sample_prices.csv", help="CSV price data"),
    start_date: str = typer.Option("2024-01-01", help="Start date"),
    end_date: str = typer.Option("2024-01-31", help="End date"),
    run_name: str = typer.Option("example_momentum", help="Output file prefix"),
) -> None:
    prices = load_price_csv(data_path)
    frames = split_by_instrument(prices)
    targets = build_example_momentum_targets(frames)
    config = BacktestConfig(start_date=start_date, end_date=end_date)
    result = run_event_backtest(targets, frames, config)
    paths = write_backtest_outputs(result, config.output_dir, run_name)
    round_trips = build_round_trips(result.trades)
    yearly = yearly_equity_summary(result.equity_curve)
    console.print("Backtest complete", style="green")
    console.print(f"win_rate: {win_rate(round_trips):.2%}")
    if not yearly.empty:
        console.print(yearly.to_string(index=False))
    for name, path in paths.items():
        console.print(f"{name}: {path}")


@app.command("secret-scan")
def secret_scan(
    root: str = typer.Option(".", help="Path to scan"),
) -> None:
    findings = scan_path(Path(root))
    if not findings:
        console.print("No obvious secrets found", style="green")
        return
    for path, line_number, line in findings:
        console.print(f"{path}:{line_number}: {line}", style="red")
    raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
