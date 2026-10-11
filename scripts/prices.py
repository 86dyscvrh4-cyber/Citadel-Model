"""Price data layer. The only place prices come from.

Order of sources: yfinance, then prices/<TICKER>.csv. Raises if neither works.
Set CITADEL_PRICE_SOURCE=csv to skip yfinance, or CITADEL_PRICES_DIR to point
at another CSV folder (used by tests).

CLI: python3 scripts/prices.py TICKER [TICKER ...]  -> latest close, date, source
"""
import os
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
COLUMNS = ["open", "high", "low", "close", "adj_close", "volume"]


class PriceError(RuntimeError):
    pass


def _prices_dir():
    return Path(os.environ.get("CITADEL_PRICES_DIR", ROOT / "prices"))


def _from_yfinance(ticker, start):
    import logging

    import yfinance as yf

    logging.getLogger("yfinance").setLevel(logging.CRITICAL)

    df = yf.Ticker(ticker).history(start=start, auto_adjust=False, actions=False)
    if df is None or df.empty:
        raise PriceError(f"yfinance returned no data for {ticker}")
    df = df.rename(columns={"Open": "open", "High": "high", "Low": "low",
                            "Close": "close", "Adj Close": "adj_close",
                            "Volume": "volume"})
    df.index = pd.to_datetime(df.index).tz_localize(None).normalize()
    return df[[c for c in COLUMNS if c in df.columns]]


def _from_csv(ticker):
    path = _prices_dir() / f"{ticker.upper()}.csv"
    if not path.exists():
        raise PriceError(f"no CSV at {path}")
    df = pd.read_csv(path)
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    if "date" not in df.columns or "close" not in df.columns:
        raise PriceError(f"{path} needs at least 'date' and 'close' columns")
    df["date"] = pd.to_datetime(df["date"])
    df = df.set_index("date").sort_index()
    return df[[c for c in COLUMNS if c in df.columns]].astype(float)


def history(ticker, start="2015-01-01"):
    """Daily bars for ticker. Returns (DataFrame, source_label)."""
    errors = []
    if os.environ.get("CITADEL_PRICE_SOURCE", "auto") != "csv":
        try:
            return _from_yfinance(ticker, start), "yfinance"
        except Exception as e:  # network blocked, missing module, bad ticker
            errors.append(f"yfinance: {type(e).__name__}: {str(e)[:120]}")
    try:
        df = _from_csv(ticker)
        return df[df.index >= pd.Timestamp(start)], f"csv:{_prices_dir() / (ticker.upper() + '.csv')}"
    except PriceError as e:
        errors.append(f"csv: {e}")
    raise PriceError(f"No price data for {ticker}. " + " | ".join(errors) +
                     f". Supply prices/{ticker.upper()}.csv (date, close [, open, high, low, adj_close, volume]).")


def total_return_series(df):
    """Adjusted close if present, else close."""
    if "adj_close" in df.columns and df["adj_close"].notna().all():
        return df["adj_close"]
    return df["close"]


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    rc = 0
    for t in argv:
        try:
            df, src = history(t.upper())
            last = df.iloc[-1]
            print(f"{t.upper()}  close={last['close']:.2f}  date={df.index[-1].date()}  source={src}")
        except PriceError as e:
            print(f"{t.upper()}  ERROR  {e}")
            rc = 1
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
