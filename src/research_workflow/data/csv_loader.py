from __future__ import annotations

from pathlib import Path

import pandas as pd


REQUIRED_PRICE_COLUMNS = {"date", "instrument", "open", "high", "low", "close"}


def load_price_csv(path: Path | str) -> pd.DataFrame:
    """Load a generic OHLCV CSV file.

    Expected columns:
    date, instrument, open, high, low, close, volume, turnover
    """
    frame = pd.read_csv(path)
    missing = REQUIRED_PRICE_COLUMNS - set(frame.columns)
    if missing:
        raise ValueError(f"price CSV missing columns: {', '.join(sorted(missing))}")
    frame = frame.copy()
    frame["date"] = pd.to_datetime(frame["date"], errors="coerce").dt.strftime("%Y-%m-%d")
    frame = frame.dropna(subset=["date", "instrument"])
    numeric_columns = [column for column in frame.columns if column not in {"date", "instrument"}]
    for column in numeric_columns:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    frame = frame.dropna(subset=["open", "high", "low", "close"])
    return frame.sort_values(["date", "instrument"]).reset_index(drop=True)


def split_by_instrument(prices: pd.DataFrame) -> dict[str, pd.DataFrame]:
    return {
        str(instrument): block.sort_values("date").reset_index(drop=True)
        for instrument, block in prices.groupby("instrument")
    }
