from __future__ import annotations

from collections import defaultdict, deque

import pandas as pd


def build_round_trips(trades: pd.DataFrame) -> pd.DataFrame:
    if trades.empty:
        return pd.DataFrame(columns=["instrument", "buy_date", "sell_date", "pnl", "return"])
    open_lots: dict[str, deque[dict[str, object]]] = defaultdict(deque)
    rows = []
    work = trades.copy()
    work["date"] = pd.to_datetime(work["date"])
    for row in work.sort_values("date").to_dict("records"):
        instrument = str(row["instrument"])
        side = str(row["side"]).upper()
        shares = float(row["shares"])
        price = float(row["price"])
        fee = float(row.get("fee", 0.0))
        if side == "BUY":
            open_lots[instrument].append(
                {
                    "date": row["date"],
                    "price": price,
                    "shares": shares,
                    "remaining": shares,
                    "fee": fee,
                }
            )
            continue
        if side != "SELL":
            continue
        remaining = shares
        while remaining > 1e-9 and open_lots[instrument]:
            lot = open_lots[instrument][0]
            qty = min(remaining, float(lot["remaining"]))
            buy_fee = float(lot["fee"]) * qty / float(lot["shares"])
            sell_fee = fee * qty / shares
            buy_cost = float(lot["price"]) * qty + buy_fee
            sell_value = price * qty - sell_fee
            pnl = sell_value - buy_cost
            rows.append(
                {
                    "instrument": instrument,
                    "buy_date": lot["date"],
                    "sell_date": row["date"],
                    "pnl": pnl,
                    "return": pnl / buy_cost if buy_cost else 0.0,
                }
            )
            lot["remaining"] = float(lot["remaining"]) - qty
            remaining -= qty
            if float(lot["remaining"]) <= 1e-9:
                open_lots[instrument].popleft()
    return pd.DataFrame(rows)


def win_rate(round_trips: pd.DataFrame) -> float:
    if round_trips.empty:
        return 0.0
    return float((round_trips["pnl"] > 0).mean())


def yearly_equity_summary(equity: pd.DataFrame) -> pd.DataFrame:
    if equity.empty:
        return pd.DataFrame()
    work = equity.copy()
    work["date"] = pd.to_datetime(work["date"])
    work["year"] = work["date"].dt.year
    rows = []
    for year, block in work.groupby("year"):
        block = block.sort_values("date")
        start_equity = float(block.iloc[0]["total_equity"])
        end_equity = float(block.iloc[-1]["total_equity"])
        peak = block["total_equity"].cummax()
        drawdown = block["total_equity"] / peak - 1
        rows.append(
            {
                "year": int(year),
                "return": end_equity / start_equity - 1 if start_equity else 0.0,
                "max_drawdown": float(drawdown.min()),
            }
        )
    return pd.DataFrame(rows)
