from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class BacktestConfig:
    start_date: str
    end_date: str
    initial_capital: float = 100_000.0
    buy_commission: float = 0.0005
    sell_commission: float = 0.0005
    sell_tax: float = 0.0
    min_commission: float = 0.0
    output_dir: Path = Path("outputs")


@dataclass(slots=True)
class ExecutionConfig:
    slippage_bps: float = 30.0
    lot_size: int = 100
    max_participation_rate: float = 0.10


@dataclass(slots=True)
class BacktestResult:
    equity_curve: object
    trades: object
    summary: object
