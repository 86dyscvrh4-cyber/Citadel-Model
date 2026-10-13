"""Mark open paper positions to the latest prices, apply stops, log closes.

Usage: python3 scripts/mark_to_market.py [--dry-run]

Writes: ledger.csv (stopped trades), state/equity.csv, state/closes.log, state/HALT.
"""
import argparse
import sys
from datetime import date
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import book  # noqa: E402
import prices  # noqa: E402


def check_stop(row, df):
    """Return (exit_price, exit_date) for the first stop hit after entry, else None."""
    entry_day = pd.Timestamp(row["date"])
    stop = float(row["stop"])
    long_ = row["direction"].lower() == "long"
    bars = df[df.index > entry_day]
    has_hl = {"high", "low"} <= set(bars.columns) and bars[["high", "low"]].notna().all().all()
    for day, b in bars.iterrows():
        if has_hl:
            hit = b["low"] <= stop if long_ else b["high"] >= stop
            if hit:
                o = b.get("open")
                gapped = o is not None and not pd.isna(o) and (o <= stop if long_ else o >= stop)
                return (float(o) if gapped else stop), day
        else:
            hit = b["close"] <= stop if long_ else b["close"] >= stop
            if hit:
                return float(b["close"]), day
    return None


def outcome(pnl):
    return "WIN" if pnl > 0 else "LOSS" if pnl < 0 else "FLAT"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="print only, write nothing")
    a = ap.parse_args()
    rules = book.load_rules()
    rows = book.read_ledger()
    sd = book.state_dir()
    if not rows:
        print("MARK  ledger empty, nothing to mark")
        return

    today = date.today()
    closed_now, open_lines, closed_now_ids = [], [], []
    for r in rows:
        if not book.is_open(r):
            continue
        df, src = prices.history(r["ticker"], start=r["date"])
        if df.empty:
            open_lines.append(f"{r['id']} {r['ticker']} {r['direction']} entry {float(r['entry']):.2f} stop {float(r['stop']):.2f}  no completed session since entry yet")
            continue
        hit = check_stop(r, df)
        if hit:
            px, day = hit
            r["exit"] = f"{px:.4f}"
            r["exit_date"] = str(day.date())
            pnl = book.trade_pnl(r, rules)
            r["outcome"] = outcome(pnl)
            closed_now.append(f"{r['id']} {r['ticker']} {r['direction']} STOP @ {px:.2f} on {day.date()}  pnl ${pnl:,.0f}  ({src})")
            closed_now_ids.append(r["id"])
        else:
            last = float(df["close"].iloc[-1])
            pnl = book.trade_pnl(r, rules, last)
            flag = ""
            if r.get("catalyst_date") and pd.Timestamp(r["catalyst_date"]).date() < today:
                flag = "  CATALYST PASSED: review thesis"
            open_lines.append(f"{r['id']} {r['ticker']} {r['direction']} last {last:.2f} ({df.index[-1].date()}) entry {float(r['entry']):.2f} stop {float(r['stop']):.2f}  pnl ${pnl:,.0f}{flag}")

    # linked exits: when a leg closes on a stop, close its open partner(s) at that day's close
    links = book.read_links()
    by_id = {r["id"]: r for r in rows}
    for r in list(rows):
        if book.is_open(r) or r["id"] not in closed_now_ids:
            continue
        for pid in links.get(r["id"], ()):
            p = by_id.get(pid)
            if p is None or not book.is_open(p):
                continue
            dfp, srcp = prices.history(p["ticker"], start=p["date"])
            day = pd.Timestamp(r["exit_date"])
            px = float(dfp.loc[dfp.index <= day, "close"].iloc[-1])
            p["exit"], p["exit_date"] = f"{px:.4f}", str(day.date())
            pnl = book.trade_pnl(p, rules)
            p["outcome"] = outcome(pnl)
            closed_now.append(f"{p['id']} {p['ticker']} {p['direction']} LINKED EXIT (partner {r['id']} stopped) @ {px:.2f} close {day.date()}  pnl ${pnl:,.0f}  ({srcp})")
            open_lines[:] = [ln for ln in open_lines if not ln.startswith(f"{p['id']} ")]

    eq = book.equity_series(rows, rules)
    if eq is None or eq.empty:
        print("MARK  (paper only)  no completed session since the first entry; equity unchanged")
        for line in open_lines:
            print("  OPEN   " + line)
        return
    last = eq.iloc[-1]
    dd = float(last["drawdown_pct"])
    halt = dd <= -rules["drawdown_halt_pct"]

    print(f"MARK  {eq.index[-1].date()}  (paper only)")
    print(f"  equity ${last['equity']:,.0f}  peak ${last['peak']:,.0f}  drawdown {dd:.2f}%  gross {last['gross'] / last['equity'] * 100:.1f}%  net {last['net'] / last['equity'] * 100:.1f}%  cash interest ${last['cash_interest']:,.0f}")
    for line in open_lines:
        print("  OPEN   " + line)
    for line in closed_now:
        print("  CLOSED " + line)
    if halt:
        print(f"  HALT: drawdown {dd:.2f}% breaches {rules['drawdown_halt_pct']}% limit. No new trades until the user says so.")

    if a.dry_run:
        print("  (dry run: nothing written)")
        return
    book.write_ledger(rows)
    eq.to_csv(sd / "equity.csv")
    if closed_now:
        with (sd / "closes.log").open("a") as f:
            for line in closed_now:
                f.write(f"{today} {line}\n")
    if halt and not (sd / "HALT").exists():
        (sd / "HALT").write_text(f"{today} drawdown {dd:.2f}%\n")


if __name__ == "__main__":
    try:
        main()
    except prices.PriceError as e:
        print(f"DATA ERROR: {e}")
        sys.exit(1)
