from __future__ import annotations

from pathlib import Path

from research_workflow.backtest.event_engine import run_event_backtest
from research_workflow.backtest.metrics import build_round_trips, win_rate
from research_workflow.data.csv_loader import load_price_csv, split_by_instrument
from research_workflow.models import BacktestConfig
from research_workflow.security.secret_scan import scan_path
from research_workflow.strategies.example_momentum import build_example_momentum_targets


ROOT = Path(__file__).resolve().parents[1]


def test_example_backtest_runs() -> None:
    prices = load_price_csv(ROOT / "examples" / "data" / "sample_prices.csv")
    frames = split_by_instrument(prices)
    targets = build_example_momentum_targets(frames)
    result = run_event_backtest(
        targets,
        frames,
        BacktestConfig(start_date="2024-01-02", end_date="2024-01-31"),
    )

    assert not result.equity_curve.empty
    assert not result.summary.empty
    assert "total_equity" in result.equity_curve.columns

    round_trips = build_round_trips(result.trades)
    assert 0.0 <= win_rate(round_trips) <= 1.0


def test_open_source_tree_has_no_obvious_secrets() -> None:
    findings = scan_path(ROOT)
    assert findings == []
