from __future__ import annotations

from pathlib import Path

import pandas as pd

from research_workflow.models import BacktestResult


def write_backtest_outputs(result: BacktestResult, output_dir: Path | str, run_name: str) -> dict[str, Path]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    paths = {
        "equity": output_path / f"{run_name}_equity.csv",
        "trades": output_path / f"{run_name}_trades.csv",
        "summary": output_path / f"{run_name}_summary.csv",
        "report": output_path / f"{run_name}_report.md",
    }
    result.equity_curve.to_csv(paths["equity"], index=False, encoding="utf-8")
    result.trades.to_csv(paths["trades"], index=False, encoding="utf-8")
    result.summary.to_csv(paths["summary"], index=False, encoding="utf-8")
    paths["report"].write_text(markdown_report(result.summary), encoding="utf-8")
    return paths


def markdown_report(summary: pd.DataFrame) -> str:
    lines = ["# Backtest Report", "", "## Summary", ""]
    for row in summary.to_dict("records"):
        lines.append(f"- {row['metric']}: {row['value']}")
    return "\n".join(lines)
