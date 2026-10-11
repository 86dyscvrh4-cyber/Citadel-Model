"""SYNTHETIC price fixtures for testing script mechanics only. Not real prices.

python3 tests/make_fixtures.py OUT_DIR END_DATE
Tickers: SPY, TLT, XLK (synthetic stand-ins), SYNA (trends up), SYNB (trends up, so a short gets stopped).
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

out, end = Path(sys.argv[1]), pd.Timestamp(sys.argv[2])
out.mkdir(parents=True, exist_ok=True)
days = pd.bdate_range(end=pd.Timestamp("2026-10-09"), periods=320)
rng = np.random.default_rng(7)
mkt = rng.normal(0.0004, 0.010, len(days))
spec = {"SPY": (1.0, 0.000, 0.004, 500), "TLT": (-0.2, 0.000, 0.008, 90),
        "XLK": (1.2, 0.0002, 0.006, 200), "SYNA": (1.1, 0.0010, 0.015, 100),
        "SYNB": (0.9, 0.0040, 0.015, 50)}
for t, (b, drift, idio, p0) in spec.items():
    r = b * mkt + drift + rng.normal(0, idio, len(days))
    close = p0 * np.cumprod(1 + r)
    opn = close / (1 + r) * (1 + rng.normal(0, 0.002, len(days)))
    high = np.maximum(opn, close) * (1 + abs(rng.normal(0, 0.006, len(days))))
    low = np.minimum(opn, close) * (1 - abs(rng.normal(0, 0.006, len(days))))
    vol = rng.integers(2_000_000, 8_000_000, len(days))
    df = pd.DataFrame({"open": opn, "high": high, "low": low,
                       "close": close, "volume": vol}).round(4)
    df.insert(0, "date", days)
    df = df[df["date"] <= end]
    df["date"] = df["date"].dt.date
    df.to_csv(out / f"{t}.csv", index=False)
print(f"SYNTHETIC fixtures written to {out} through {df['date'].iloc[-1]}")
