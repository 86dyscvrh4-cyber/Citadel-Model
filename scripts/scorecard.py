"""Scorecard: book vs SPY over the same dates, plus trade stats and the
pre-registered success criteria from rules.md.

Usage: python3 scripts/scorecard.py
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import book  # noqa: E402
import prices  # noqa: E402


def ratio(ret_pct, dd_pct):
    return float("nan") if dd_pct == 0 else ret_pct / dd_pct


def f(x, nd=2):
    return "n/a" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:,.{nd}f}"


def main():
    rules = book.load_rules()
    rows = book.read_ledger()
    if not rows:
        print("SCORE  ledger empty. 0 resolved trades.")
        print("WARNING: sample too small to conclude anything (0 < 30 resolved trades)")
        return
    bench = rules["benchmark"]
    eq = book.equity_series(rows, rules)
    if eq is None:
        print("SCORE  no completed session since the first entry yet.")
        return
    start, end = eq.index[0].date(), eq.index[-1].date()
    book_ret = (eq["equity"].iloc[-1] / rules["starting_capital"] - 1) * 100
    spy_ret = (eq[bench].iloc[-1] / eq[bench].iloc[0] - 1) * 100
    book_dd = book.max_drawdown_pct(eq["equity"])
    spy_dd = book.max_drawdown_pct(eq[bench])
    rf = rules["cash_rate_annual_pct"]
    book_sh, spy_sh = book.sharpe(eq["equity"], rf), book.sharpe(eq[bench], rf)
    book_rd, spy_rd = ratio(book_ret, book_dd), ratio(spy_ret, spy_dd)

    resolved = [r for r in rows if not book.is_open(r)]
    pnls = [book.trade_pnl(r, rules) for r in resolved]
    wins = [p for p in pnls if p > 0]
    losses = [p for p in pnls if p < 0]
    hit = len(wins) / len(pnls) * 100 if pnls else float("nan")
    avg_w = sum(wins) / len(wins) if wins else float("nan")
    avg_l = sum(losses) / len(losses) if losses else float("nan")

    print(f"SCORE  {start} to {end}  ({len(eq)} trading days, paper only)")
    print(f"{'':16}{'BOOK':>12}{bench:>12}")
    print(f"{'return %':16}{f(book_ret):>12}{f(spy_ret):>12}")
    print(f"{'max drawdown %':16}{f(book_dd):>12}{f(spy_dd):>12}")
    print(f"{'sharpe (rf ' + f(rf, 1) + '%)':16}{f(book_sh):>12}{f(spy_sh):>12}")
    print(f"{'return / maxDD':16}{f(book_rd):>12}{f(spy_rd):>12}")
    print(f"trades: {len(rows)} total, {len(resolved)} resolved, {len(rows) - len(resolved)} open")
    print(f"hit rate {f(hit,1)}{'%' if pnls else ''}  avg win ${f(avg_w,0)}  avg loss ${f(avg_l,0)}  (wins {len(wins)}, losses {len(losses)})")

    def beats(a, b):
        return None if math.isnan(a) or math.isnan(b) else a > b

    crit = {
        "1 sharpe > SPY": beats(book_sh, spy_sh),
        "2 return/maxDD > SPY": beats(book_rd, spy_rd),
        "3 avg win > |avg loss|": None if math.isnan(avg_w) or math.isnan(avg_l) else avg_w > abs(avg_l),
    }
    print("criteria: " + "  ".join(f"[{k}: {'n/a' if v is None else ('PASS' if v else 'FAIL')}]" for k, v in crit.items()))
    n_min = rules["min_resolved_trades"]
    if len(resolved) < n_min:
        print(f"WARNING: sample too small to conclude anything ({len(resolved)} < {n_min} resolved trades)")
        verdict = "INCONCLUSIVE"
    elif all(v is True for v in crit.values()):
        verdict = "PASS"
    else:
        verdict = "FAIL"
    print(f"verdict: {verdict}")
    if book_dd == 0 or spy_dd == 0:
        print("note: zero drawdown makes return/maxDD undefined")


if __name__ == "__main__":
    try:
        main()
    except prices.PriceError as e:
        print(f"DATA ERROR: {e}")
        sys.exit(1)
