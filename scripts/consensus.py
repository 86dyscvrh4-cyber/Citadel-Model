"""Analyst consensus from Yahoo Finance (the same data shown on its Analysis tab).

Usage: python3 scripts/consensus.py TICKER [TICKER ...]

Prints consensus EPS and revenue (avg/low/high, analyst count, year-ago), the EPS trend
over 90 days, revisions up/down, price targets, and the next earnings date. Cite it as:
  Yahoo Finance consensus | https://finance.yahoo.com/quote/TICKER/analysis | retrieved YYYY-MM-DD
Caveats: Yahoo's EPS basis can differ from company "adjusted" EPS, and REITs report FFO/AFFO,
which Yahoo's EPS fields do not cover. Earnings dates may be estimates until the company confirms.
"""
import logging
import sys
import time
from datetime import date

import pandas as pd

logging.getLogger("yfinance").setLevel(logging.CRITICAL)
PERIODS = {"0q": "current qtr", "+1q": "next qtr", "0y": "current FY", "+1y": "next FY"}


def fmt(v, money=False):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return "n/a"
    if money and abs(v) >= 1e6:
        return f"${v / 1e6:,.1f}M"
    return f"{v:,.2f}" if isinstance(v, float) else str(v)


def show(ticker):
    import yfinance as yf

    t = yf.Ticker(ticker)
    print(f"{ticker}  Yahoo Finance consensus | https://finance.yahoo.com/quote/{ticker}/analysis | retrieved {date.today()}")
    try:
        cal = t.calendar or {}
        ed = cal.get("Earnings Date") or []
        print(f"  next earnings (Yahoo, may be estimated): {', '.join(str(d) for d in ed) or 'n/a'}")
    except Exception as e:
        print(f"  calendar: unavailable ({type(e).__name__})")
    for label, attr, money in [("EPS", "earnings_estimate", False), ("Revenue", "revenue_estimate", True)]:
        try:
            df = getattr(t, attr)
            if df is None or df.empty:
                raise ValueError("empty")
            print(f"  {label} estimates:")
            ya = "yearAgoEps" if label == "EPS" else "yearAgoRevenue"
            for p, row in df.iterrows():
                print(f"    {PERIODS.get(p, p):12} avg {fmt(row.get('avg'), money)}  low {fmt(row.get('low'), money)}  "
                      f"high {fmt(row.get('high'), money)}  n={fmt(row.get('numberOfAnalysts'))}  "
                      f"year-ago {fmt(row.get(ya), money)}")
        except Exception as e:
            print(f"  {label} estimates: unavailable ({type(e).__name__})")
    try:
        tr = t.eps_trend
        print("  EPS trend (current / 30d ago / 90d ago):")
        for p, row in tr.iterrows():
            print(f"    {PERIODS.get(p, p):12} {fmt(row.get('current'))} / {fmt(row.get('30daysAgo'))} / {fmt(row.get('90daysAgo'))}")
    except Exception as e:
        print(f"  EPS trend: unavailable ({type(e).__name__})")
    try:
        rv = t.eps_revisions
        print("  EPS revisions last 30d (up / down):")
        for p, row in rv.iterrows():
            print(f"    {PERIODS.get(p, p):12} {fmt(row.get('upLast30days'))} / {fmt(row.get('downLast30days'))}")
    except Exception as e:
        print(f"  EPS revisions: unavailable ({type(e).__name__})")
    try:
        pt = t.analyst_price_targets or {}
        print(f"  price targets: mean {fmt(pt.get('mean'))}  median {fmt(pt.get('median'))}  "
              f"low {fmt(pt.get('low'))}  high {fmt(pt.get('high'))}")
    except Exception as e:
        print(f"  price targets: unavailable ({type(e).__name__})")


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    for i, tk in enumerate(argv):
        if i:
            time.sleep(1)  # keep Yahoo load low
        show(tk.upper())
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
