"""Price data layer. The only place prices come from.

Source: Yahoo Finance via yfinance. No other source in normal operation.
Tests only: CITADEL_PRICE_SOURCE=csv reads CSVs from CITADEL_PRICES_DIR.

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


def _drop_unfinished_bar(df):
    """Drop today's bar until the US close is final (16:30 ET), so 'close' is never intraday."""
    from datetime import datetime
    from zoneinfo import ZoneInfo

    now = datetime.now(ZoneInfo("America/New_York"))
    today = pd.Timestamp(now.date())
    if (now.hour, now.minute) < (16, 30) and len(df) and df.index[-1] >= today:
        return df[df.index < today]
    return df


def history(ticker, start="2015-01-01"):
    """Daily bars for ticker (completed sessions only). Returns (DataFrame, source_label)."""
    if os.environ.get("CITADEL_PRICE_SOURCE") == "csv":
        df = _from_csv(ticker)
        return df[df.index >= pd.Timestamp(start)], f"csv:{_prices_dir() / (ticker.upper() + '.csv')}"
    try:
        return _drop_unfinished_bar(_from_yfinance(ticker, start)), "yahoo"
    except Exception as e:  # network blocked, missing module, bad ticker
        hint = ""
        if "403" in str(e) or "CONNECT" in str(e):
            hint = (" Yahoo is blocked by this environment's network policy: allow query1.finance.yahoo.com,"
                    " query2.finance.yahoo.com, fc.yahoo.com, guce.yahoo.com, consent.yahoo.com"
                    " under Network access in the environment settings.")
        raise PriceError(f"No Yahoo data for {ticker}: {type(e).__name__}: {str(e)[:100]}.{hint}")


def execution_price(ticker, at="now"):
    """Paper fill price when the user asks to execute.

    at: "now" or "YYYY-MM-DD HH:MM" (US/Eastern). Uses the close of the 1-minute Yahoo bar
    containing that time. Outside market hours, falls back to the latest completed close.
    Returns (price, timestamp_str, source_label).
    """
    from datetime import datetime
    from zoneinfo import ZoneInfo
    import yfinance as yf

    if os.environ.get("CITADEL_PRICE_SOURCE") == "csv":  # tests: latest CSV close
        df, src = history(ticker)
        return float(df["close"].iloc[-1]), str(df.index[-1].date()) + " close", src
    et = ZoneInfo("America/New_York")
    t = datetime.now(et) if at == "now" else datetime.strptime(at, "%Y-%m-%d %H:%M").replace(tzinfo=et)
    mins = yf.Ticker(ticker).history(start=t.date(), end=pd.Timestamp(t.date()) + pd.Timedelta(days=1),
                                     interval="1m")
    if mins is not None and not mins.empty:
        mins.index = mins.index.tz_convert(et)
        bar_time = pd.Timestamp(t).floor("min")
        upto = mins[mins.index <= bar_time]
        in_session = mins.index[0] <= bar_time <= mins.index[-1] + pd.Timedelta(minutes=1)
        if len(upto) and in_session:
            return float(upto["Close"].iloc[-1]), str(upto.index[-1]), "yahoo 1m bar close"
    df, src = history(ticker)
    return float(df["close"].iloc[-1]), str(df.index[-1].date()) + " close", src + " daily close (market closed)"


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
