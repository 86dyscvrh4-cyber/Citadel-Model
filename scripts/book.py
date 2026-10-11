"""Shared book logic: rules, ledger I/O, position sizing, daily equity series.

Env overrides (tests only): CITADEL_LEDGER, CITADEL_STATE_DIR.
"""
import csv
import json
import os
import re
from pathlib import Path

import numpy as np
import pandas as pd

import prices

ROOT = Path(__file__).resolve().parent.parent
LEDGER_FIELDS = ["id", "date", "ticker", "direction", "thesis", "catalyst",
                 "catalyst_date", "entry", "stop", "size_pct", "exit",
                 "exit_date", "outcome", "lessons"]
TRADING_DAYS = 252


def ledger_path():
    return Path(os.environ.get("CITADEL_LEDGER", ROOT / "ledger.csv"))


def state_dir():
    d = Path(os.environ.get("CITADEL_STATE_DIR", ROOT / "state"))
    d.mkdir(parents=True, exist_ok=True)
    return d


def load_rules():
    text = (ROOT / "rules.md").read_text()
    m = re.search(r"```json\s*(\{.*?\})\s*```", text, re.S)
    if not m:
        raise RuntimeError("rules.md has no machine-readable JSON block")
    rules = json.loads(m.group(1))
    rules["approved"] = "STATUS: DRAFT" not in text
    return rules


def read_ledger():
    path = ledger_path()
    if not path.exists():
        return []
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def write_ledger(rows):
    with ledger_path().open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=LEDGER_FIELDS)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in LEDGER_FIELDS})


def is_open(row):
    return not row.get("exit_date")


def sign(row):
    return 1.0 if row["direction"].lower() == "long" else -1.0


def shares(row, rules):
    return float(row["size_pct"]) / 100 * rules["starting_capital"] / float(row["entry"])


def trade_pnl(row, rules, price=None):
    px = float(row["exit"]) if price is None else price
    return sign(row) * shares(row, rules) * (px - float(row["entry"]))


def loss_at_stop(row, rules):
    """Dollar loss if the stop fills exactly at the stop price (positive number)."""
    return -trade_pnl(row, rules, float(row["stop"]))


def load_closes(tickers, start):
    out = {}
    for t in sorted(set(tickers)):
        df, _ = prices.history(t, start=start)
        out[t] = df["close"]
    return pd.DataFrame(out).sort_index()


def equity_series(rows, rules, end=None):
    """Daily book equity from the first trade date. Returns DataFrame or None."""
    if not rows:
        return None
    start = min(pd.Timestamp(r["date"]) for r in rows)
    bench = rules["benchmark"]
    closes = load_closes([r["ticker"] for r in rows] + [bench], start.strftime("%Y-%m-%d"))
    closes = closes[closes.index >= start].ffill()
    if end is not None:
        closes = closes[closes.index <= pd.Timestamp(end)]
    cap = rules["starting_capital"]
    daily_rate = rules["cash_rate_annual_pct"] / 100 / TRADING_DAYS
    interest = 0.0
    prev_equity, prev_gross = cap, 0.0
    recs = []
    for day, px in closes.iterrows():
        interest += daily_rate * max(0.0, prev_equity - prev_gross) if recs else 0.0
        realized = unrealized = gross = net = 0.0
        for r in rows:
            d0 = pd.Timestamp(r["date"])
            if d0 > day:
                continue
            closed_by_today = r.get("exit_date") and pd.Timestamp(r["exit_date"]) <= day
            if closed_by_today:
                realized += trade_pnl(r, rules)
                continue
            p = px[r["ticker"]]
            unrealized += trade_pnl(r, rules, p)
            notional = shares(r, rules) * p
            gross += notional
            net += sign(r) * notional
        equity = cap + realized + unrealized + interest
        recs.append({"date": day, "equity": equity, "gross": gross, "net": net,
                     "cash_interest": interest, bench: px[bench]})
        prev_equity, prev_gross = equity, gross
    df = pd.DataFrame(recs).set_index("date")
    df["peak"] = df["equity"].cummax()
    df["drawdown_pct"] = (df["equity"] / df["peak"] - 1) * 100
    return df


def max_drawdown_pct(series):
    s = pd.Series(series).astype(float)
    return float(((s / s.cummax()) - 1).min() * -100)


def sharpe(series, rf_annual_pct):
    r = pd.Series(series).astype(float).pct_change().dropna()
    if len(r) < 2 or r.std() == 0:
        return float("nan")
    excess = r - rf_annual_pct / 100 / TRADING_DAYS
    return float(excess.mean() / r.std() * np.sqrt(TRADING_DAYS))
