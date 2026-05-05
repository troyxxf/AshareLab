from __future__ import annotations

import pandas as pd


TARGET_COLUMNS = [
    "date",
    "buy_date",
    "sell_date",
    "instrument",
    "score",
    "position",
    "entry_price_mode",
    "exit_price_mode",
]


def build_example_momentum_targets(
    price_frames: dict[str, pd.DataFrame],
    *,
    top_n: int = 3,
    lookback: int = 5,
    holding_days: int = 1,
    gross_exposure: float = 1.0,
) -> pd.DataFrame:
    """Build a simple public example target list.

    This is a naive example: rank instruments by trailing return and buy the top
    few at next open. It is intended to demonstrate the workflow only.
    """
    events = []
    for instrument, frame in price_frames.items():
        work = frame.copy().sort_values("date").reset_index(drop=True)
        work["score"] = work["close"] / work["close"].shift(lookback) - 1
        work["buy_date"] = work["date"].shift(-1)
        work["sell_date"] = work["date"].shift(-(1 + holding_days))
        selected = work.dropna(subset=["score", "buy_date", "sell_date"])
        for row in selected.to_dict("records"):
            events.append(
                {
                    "date": row["date"],
                    "buy_date": row["buy_date"],
                    "sell_date": row["sell_date"],
                    "instrument": instrument,
                    "score": float(row["score"]),
                }
            )
    if not events:
        return pd.DataFrame(columns=TARGET_COLUMNS)
    ranked = pd.DataFrame(events).sort_values(["date", "score"], ascending=[True, False])
    ranked["rank"] = ranked.groupby("date")["score"].rank(method="first", ascending=False)
    ranked = ranked[ranked["rank"] <= top_n].copy()
    ranked["position"] = gross_exposure / ranked.groupby("date")["instrument"].transform("count")
    ranked["entry_price_mode"] = "open"
    ranked["exit_price_mode"] = "open"
    return ranked[TARGET_COLUMNS].reset_index(drop=True)
