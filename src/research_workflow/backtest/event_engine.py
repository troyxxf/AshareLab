from __future__ import annotations

import pandas as pd

from research_workflow.models import BacktestConfig, BacktestResult


def run_event_backtest(
    targets: pd.DataFrame,
    price_frames: dict[str, pd.DataFrame],
    config: BacktestConfig,
) -> BacktestResult:
    price_map = _price_map(price_frames)
    cash = config.initial_capital
    holdings: dict[str, dict[str, object]] = {}
    equity_rows = []
    trade_rows = []
    dates = sorted(
        date
        for date in price_map.reset_index()["date"].unique().tolist()
        if config.start_date <= date <= config.end_date
    )
    active_targets = targets[
        (targets["buy_date"].astype(str) >= config.start_date)
        & (targets["buy_date"].astype(str) <= config.end_date)
    ].copy()
    targets_by_date = {date: block.copy() for date, block in active_targets.groupby("buy_date")}

    for date in dates:
        due_sells = [
            instrument
            for instrument, position in holdings.items()
            if str(position["sell_date"]) <= date
        ]
        for instrument in due_sells:
            position = holdings.pop(instrument)
            price = _price_or_none(price_map, date, instrument, str(position["exit_price_mode"]))
            if price is None:
                holdings[instrument] = position
                continue
            shares = int(position["shares"])
            gross = shares * price
            fee = _sell_cost(gross, config)
            cash += gross - fee
            trade_rows.append(
                {
                    "date": date,
                    "instrument": instrument,
                    "side": "SELL",
                    "price": price,
                    "shares": shares,
                    "gross": gross,
                    "fee": fee,
                }
            )

        today_targets = targets_by_date.get(date)
        if today_targets is not None and not today_targets.empty:
            equity_before_buys = cash + _market_value(holdings, price_map, date)
            for row in today_targets.sort_values("score", ascending=False).to_dict("records"):
                instrument = str(row["instrument"])
                if instrument in holdings:
                    continue
                price = _price_or_none(price_map, date, instrument, str(row["entry_price_mode"]))
                if price is None:
                    continue
                capital = equity_before_buys * float(row["position"])
                fee_estimate = _buy_cost(capital, config)
                shares = int(max(capital - fee_estimate, 0) / price)
                if shares <= 0:
                    continue
                gross = shares * price
                fee = _buy_cost(gross, config)
                if gross + fee > cash:
                    continue
                cash -= gross + fee
                holdings[instrument] = {
                    "shares": shares,
                    "sell_date": row["sell_date"],
                    "exit_price_mode": row["exit_price_mode"],
                }
                trade_rows.append(
                    {
                        "date": date,
                        "instrument": instrument,
                        "side": "BUY",
                        "price": price,
                        "shares": shares,
                        "gross": gross,
                        "fee": fee,
                    }
                )

        market_value = _market_value(holdings, price_map, date)
        equity_rows.append(
            {
                "date": date,
                "cash": cash,
                "market_value": market_value,
                "total_equity": cash + market_value,
            }
        )

    equity = pd.DataFrame(equity_rows)
    trades = pd.DataFrame(trade_rows)
    summary = _summary(equity, trades, config)
    return BacktestResult(equity_curve=equity, trades=trades, summary=summary)


def _price_map(price_frames: dict[str, pd.DataFrame]) -> pd.DataFrame:
    frames = []
    for frame in price_frames.values():
        frames.append(frame[["date", "instrument", "open", "close"]].copy())
    return pd.concat(frames, ignore_index=True).set_index(["date", "instrument"]).sort_index()


def _price_or_none(price_map: pd.DataFrame, date: str, instrument: str, mode: str) -> float | None:
    if mode not in {"open", "close"}:
        mode = "open"
    if (date, instrument) not in price_map.index:
        return None
    value = pd.to_numeric(price_map.loc[(date, instrument)][mode], errors="coerce")
    if pd.isna(value) or float(value) <= 0:
        return None
    return float(value)


def _market_value(holdings: dict[str, dict[str, object]], price_map: pd.DataFrame, date: str) -> float:
    total = 0.0
    for instrument, position in holdings.items():
        price = _price_or_none(price_map, date, instrument, "close")
        if price is not None:
            total += int(position["shares"]) * price
    return total


def _buy_cost(amount: float, config: BacktestConfig) -> float:
    return max(amount * config.buy_commission, config.min_commission)


def _sell_cost(amount: float, config: BacktestConfig) -> float:
    return max(amount * config.sell_commission, config.min_commission) + amount * config.sell_tax


def _summary(equity: pd.DataFrame, trades: pd.DataFrame, config: BacktestConfig) -> pd.DataFrame:
    if equity.empty:
        return pd.DataFrame([{"metric": "status", "value": "empty"}])
    ending_equity = float(equity.iloc[-1]["total_equity"])
    peak = equity["total_equity"].cummax()
    drawdown = equity["total_equity"] / peak - 1
    return pd.DataFrame(
        [
            {"metric": "initial_capital", "value": config.initial_capital},
            {"metric": "ending_equity", "value": ending_equity},
            {"metric": "total_return", "value": ending_equity / config.initial_capital - 1},
            {"metric": "max_drawdown", "value": float(drawdown.min())},
            {"metric": "trade_count", "value": int(len(trades))},
        ]
    )
