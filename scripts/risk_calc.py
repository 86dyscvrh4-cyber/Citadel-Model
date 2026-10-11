"""Risk numbers for proposed trades vs rules.md and the current book.

Usage:
  python3 scripts/risk_calc.py --trade TICKER,DIRECTION,SIZE_PCT,STOP[,ENTRY] [--trade ...]
                               [--sector TICKER:ETF ...] [--rates-proxy TLT] [--json]

SIZE_PCT is percent of starting capital. ENTRY defaults to the latest close.
Example:
  python3 scripts/risk_calc.py --trade AAPL,long,4,190 --sector AAPL:XLK
"""
import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import book  # noqa: E402
import prices  # noqa: E402

LOOKBACK = 252
SHOCKS = {"market": -0.10, "rates_proxy": -0.05, "sector": -0.15}


def parse_trade(s):
    parts = [p.strip() for p in s.split(",")]
    if len(parts) not in (4, 5):
        raise SystemExit(f"bad --trade '{s}': need TICKER,DIRECTION,SIZE_PCT,STOP[,ENTRY]")
    t = {"ticker": parts[0].upper(), "direction": parts[1].lower(),
         "size_pct": float(parts[2]), "stop": float(parts[3])}
    if t["direction"] not in ("long", "short"):
        raise SystemExit(f"direction must be long or short, got {parts[1]}")
    if len(parts) == 5:
        t["entry"] = float(parts[4])
    return t


def returns(ticker):
    df, src = prices.history(ticker)
    return df, df["close"].pct_change().dropna(), src


def beta(r, rb):
    j = pd.concat([r, rb], axis=1, join="inner").dropna().iloc[-LOOKBACK:]
    if len(j) < 20 or j.iloc[:, 1].var() == 0:
        return float("nan"), len(j)
    return float(j.cov().iloc[0, 1] / j.iloc[:, 1].var()), len(j)


def fmt(x, nd=2):
    return "n/a" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:,.{nd}f}"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--trade", action="append", required=True)
    ap.add_argument("--sector", action="append", default=[], help="TICKER:ETF")
    ap.add_argument("--rates-proxy", default="TLT")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    rules = book.load_rules()
    cap = rules["starting_capital"]
    bench = rules["benchmark"]
    trades = [parse_trade(s) for s in a.trade]
    sector_map = dict(s.upper().split(":") for s in a.sector)
    warnings = []
    if not rules["approved"]:
        warnings.append("rules.md is still DRAFT (not approved)")
    halted = (book.state_dir() / "HALT").exists()

    _, rb, bench_src = returns(bench)
    try:
        _, rr, _ = returns(a.rates_proxy)
    except prices.PriceError:
        rr = None
        warnings.append(f"rates proxy {a.rates_proxy} has no data: rates scenario UNAVAILABLE")

    # current book
    rows = book.read_ledger()
    open_rows = [r for r in rows if book.is_open(r)]
    eq = book.equity_series(rows, rules) if rows else None
    equity = float(eq["equity"].iloc[-1]) if eq is not None else float(cap)
    gross_now = float(eq["gross"].iloc[-1]) if eq is not None else 0.0
    existing_pct = {}
    for r in open_rows:
        existing_pct[r["ticker"]] = existing_pct.get(r["ticker"], 0.0) + float(r["size_pct"])

    out_trades, ret_cols = [], {}
    for r in open_rows:
        key = f"{r['ticker']} (open)"
        if key not in ret_cols:
            ret_cols[key] = returns(r["ticker"])[1]

    for t in trades:
        df, r, src = returns(t["ticker"])
        entry = t.get("entry", float(df["close"].iloc[-1]))
        row = {"direction": t["direction"], "size_pct": t["size_pct"], "entry": entry, "stop": t["stop"]}
        sgn = book.sign(row)
        notional = t["size_pct"] / 100 * cap
        stop_dist = sgn * (entry - t["stop"]) / entry  # positive if stop is on the correct side
        loss = book.loss_at_stop(row, rules)
        daily_vol = float(r.iloc[-63:].std())
        b_mkt, n_obs = beta(r, rb)
        b_rates = beta(r, rr)[0] if rr is not None else float("nan")
        sec = sector_map.get(t["ticker"])
        b_sec = float("nan")
        if sec:
            try:
                b_sec = beta(r, returns(sec)[1])[0]
            except prices.PriceError:
                warnings.append(f"sector ETF {sec} has no data")
        adv = None
        if "volume" in df.columns:
            adv = float((df["close"] * df["volume"]).iloc[-20:].mean())

        combined = existing_pct.get(t["ticker"], 0.0) + t["size_pct"]
        checks = {
            "stop_on_correct_side": stop_dist > 0,
            "loss_at_stop_le_max": loss <= rules["max_loss_per_position_pct"] / 100 * cap + 1e-6,
            "name_weight_le_max": combined <= rules["max_single_name_pct"] + 1e-9,
            "short_allowed": t["direction"] == "long" or rules["allow_short"],
            "liquidity_ge_floor": None if adv is None else adv >= rules["min_adv_usd"],
            "not_halted": not halted,
        }
        sec_beta_used = b_sec if not math.isnan(b_sec) else 1.0
        scen = {
            "market_-10%": sgn * notional * (b_mkt if not math.isnan(b_mkt) else 1.0) * SHOCKS["market"],
            "rates_proxy_-5%": (sgn * notional * b_rates * SHOCKS["rates_proxy"]) if not math.isnan(b_rates) else float("nan"),
            "sector_-15%": sgn * notional * sec_beta_used * SHOCKS["sector"],
            "liquidity_gap_2x_stop": -2 * loss,
        }
        if math.isnan(b_sec):
            warnings.append(f"{t['ticker']}: sector scenario ASSUMES sector beta 1.0 (pass --sector {t['ticker']}:ETF)")
        out_trades.append({
            "ticker": t["ticker"], "direction": t["direction"], "size_pct": t["size_pct"],
            "combined_name_pct": combined, "entry": entry, "entry_source": src,
            "entry_date": str(df.index[-1].date()), "stop": t["stop"],
            "stop_distance_pct": stop_dist * 100,
            "stop_distance_in_daily_vols": stop_dist / daily_vol if daily_vol else float("nan"),
            "vol_63d_ann_pct": daily_vol * math.sqrt(252) * 100,
            "vol_252d_ann_pct": float(r.iloc[-252:].std() * math.sqrt(252) * 100),
            "beta_spy": b_mkt, "beta_obs": n_obs, "beta_rates_proxy": b_rates,
            "sector_etf": sec, "beta_sector": b_sec, "adv20_usd": adv,
            "loss_at_stop_usd": loss, "loss_at_stop_pct_cap": loss / cap * 100,
            "max_size_pct_for_loss_cap": (rules["max_loss_per_position_pct"] / 100 * cap) / (stop_dist * cap) * 100 if stop_dist > 0 else 0.0,
            "scenarios_usd": scen, "checks": checks,
        })
        ret_cols[t["ticker"] + " (new)"] = r

    # concentration
    new_gross = sum(t["size_pct"] / 100 * cap for t in trades)
    gross_after_pct = (gross_now + new_gross) / equity * 100
    beta_net = sum(book.sign(t) * t["size_pct"] / 100 * cap * (t["beta_spy"] if not math.isnan(t["beta_spy"]) else 1.0)
                   for t in out_trades)
    conc = {
        "equity_now": equity, "gross_now_pct": gross_now / equity * 100,
        "gross_after_pct": gross_after_pct,
        "gross_ok": gross_after_pct <= rules["max_gross_pct"] + 1e-9,
        "new_trades_beta_adj_net_usd": beta_net,
        "open_positions": len(open_rows), "halted": halted,
        "drawdown_pct_now": float(eq["drawdown_pct"].iloc[-1]) if eq is not None else 0.0,
    }
    scen_total = {k: float(np.nansum([t["scenarios_usd"][k] for t in out_trades])) for k in out_trades[0]["scenarios_usd"]}

    corr = pd.DataFrame(ret_cols).dropna().iloc[-LOOKBACK:].corr() if len(ret_cols) > 1 else None

    if len(trades) > rules["max_trades_per_run"]:
        warnings.append(f"{len(trades)} trades exceeds max_trades_per_run={rules['max_trades_per_run']}")

    result = {"rules_approved": rules["approved"], "benchmark_source": bench_src,
              "trades": out_trades, "concentration": conc, "scenario_totals_usd": scen_total,
              "correlation": None if corr is None else corr.round(3).to_dict(), "warnings": warnings}
    if a.json:
        print(json.dumps(result, indent=2, default=str))
        return

    print("RISK_CALC  (paper only)")
    if warnings:
        for w in warnings:
            print(f"  WARNING: {w}")
    for t in out_trades:
        print(f"\n{t['ticker']} {t['direction'].upper()} {t['size_pct']}% (name total {t['combined_name_pct']}%)")
        print(f"  entry {fmt(t['entry'])} ({t['entry_date']}, {t['entry_source']})  stop {fmt(t['stop'])}  dist {fmt(t['stop_distance_pct'])}% = {fmt(t['stop_distance_in_daily_vols'],1)} daily vols")
        print(f"  vol63 {fmt(t['vol_63d_ann_pct'],1)}%  vol252 {fmt(t['vol_252d_ann_pct'],1)}%  beta_SPY {fmt(t['beta_spy'])} (n={t['beta_obs']})  beta_rates {fmt(t['beta_rates_proxy'])}  beta_sector[{t['sector_etf'] or '-'}] {fmt(t['beta_sector'])}")
        print(f"  ADV20 ${fmt(t['adv20_usd'],0)}  loss_at_stop ${fmt(t['loss_at_stop_usd'],0)} ({fmt(t['loss_at_stop_pct_cap'])}% cap)  max size for loss cap {fmt(t['max_size_pct_for_loss_cap'])}%")
        print("  scenarios $: " + "  ".join(f"{k} {fmt(v,0)}" for k, v in t["scenarios_usd"].items()))
        print("  checks: " + "  ".join(f"{k}={'n/a' if v is None else ('PASS' if v else 'FAIL')}" for k, v in t["checks"].items()))
    c = conc
    print(f"\nBOOK  equity ${fmt(c['equity_now'],0)}  gross {fmt(c['gross_now_pct'],1)}% -> {fmt(c['gross_after_pct'],1)}% ({'PASS' if c['gross_ok'] else 'FAIL'})  open {c['open_positions']}  drawdown {fmt(c['drawdown_pct_now'],2)}%  halted={c['halted']}")
    print(f"  new trades beta-adj net ${fmt(c['new_trades_beta_adj_net_usd'],0)}")
    print("  scenario totals $ (new trades): " + "  ".join(f"{k} {fmt(v,0)}" for k, v in scen_total.items()))
    if corr is not None:
        print("\nCORRELATION (daily returns, up to 252d)")
        print(corr.round(2).to_string())


if __name__ == "__main__":
    try:
        main()
    except prices.PriceError as e:
        print(f"DATA ERROR: {e}")
        sys.exit(1)
