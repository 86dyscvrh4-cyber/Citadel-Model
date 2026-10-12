"""Full-universe screen. Every S&P 500 and S&P MidCap 400 stock plus the curated ETF list, same rules every run.

Usage:
  python3 scripts/screen.py [--top 25] [--exclude-top-mcap 0] [--days-8k 5] [--max-days-to-event 30]
  python3 scripts/screen.py --refresh-universe     # re-download the constituent list

Writes:
  screens/YYYY-MM-DD_full.csv   every name with every metric (audit trail)
  screens/YYYY-MM-DD.md         funnel counts + ranked shortlist for Desk

Data: prices, earnings dates, market cap, short interest, analyst count from Yahoo;
8-K filings from the SEC daily index via scripts/sec.py. Earnings dates from Yahoo can be
estimates: Desk must confirm any catalyst date against a company source.
"""
import argparse
import json
import logging
import math
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import book  # noqa: E402
import sec  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
UNIVERSE_URL = "https://raw.githubusercontent.com/datasets/s-and-p-500-companies/main/data/constituents.csv"
SECTOR_ETF = {
    "Communication Services": "XLC", "Consumer Discretionary": "XLY", "Consumer Staples": "XLP",
    "Energy": "XLE", "Financials": "XLF", "Health Care": "XLV", "Industrials": "XLI",
    "Information Technology": "XLK", "Materials": "XLB", "Real Estate": "XLRE", "Utilities": "XLU",
}
logging.getLogger("yfinance").setLevel(logging.CRITICAL)


def yahoo_symbol(s):
    return s.replace(".", "-")


def load_universe():
    frames = []
    for f, idx in [("sp500_constituents.csv", "S&P 500"), ("sp400_constituents.csv", "S&P 400")]:
        d = pd.read_csv(ROOT / "data" / f)
        frames.append(pd.DataFrame({"symbol": d["Symbol"], "name": d["Security"], "sector": d["GICS Sector"],
                                    "cik": pd.to_numeric(d["CIK"], errors="coerce"), "kind": "stock", "index": idx}))
    sp = pd.concat(frames, ignore_index=True)
    etf = pd.read_csv(ROOT / "data/etfs.csv")
    etf = pd.DataFrame({"symbol": etf["Symbol"], "name": etf["Name"], "sector": "ETF:" + etf["Group"],
                        "cik": np.nan, "kind": "etf", "index": "ETF"})
    u = pd.concat([sp, etf], ignore_index=True).drop_duplicates("symbol")
    u["ysym"] = u["symbol"].map(yahoo_symbol)
    return u


def download_prices(symbols):
    import yfinance as yf
    df = yf.download(symbols, period="1y", interval="1d", auto_adjust=False, group_by="ticker",
                     threads=True, progress=False)
    from prices import _drop_unfinished_bar
    out = {}
    for s in symbols:
        try:
            d = _drop_unfinished_bar(df[s].dropna(subset=["Close"]))
            if len(d) >= 40:
                out[s] = d
        except KeyError:
            pass
    return out


def fetch_meta(symbols, cache_path):
    cache = json.loads(cache_path.read_text()) if cache_path.exists() else {}
    todo = [s for s in symbols if s not in cache]

    def one(s):
        import yfinance as yf
        t = yf.Ticker(s)
        m = {"earnings_date": None, "market_cap": None, "short_pct_float": None, "analysts": None}
        try:
            ed = (t.calendar or {}).get("Earnings Date") or []
            m["earnings_date"] = str(ed[0]) if ed else None
        except Exception:
            pass
        try:
            info = t.info or {}
            m["market_cap"] = info.get("marketCap")
            m["short_pct_float"] = info.get("shortPercentOfFloat")
            m["analysts"] = info.get("numberOfAnalystOpinions")
        except Exception:
            pass
        return s, m

    def empty(m):
        return all(v is None for v in m.values())

    if todo:
        with ThreadPoolExecutor(8) as ex:
            got = dict(ex.map(one, todo))
        for attempt in range(2):  # Yahoo throttles bursts: retry blanks slowly
            missing = [s for s, m in got.items() if empty(m)]
            if not missing:
                break
            time.sleep(5)
            with ThreadPoolExecutor(2) as ex:
                got.update(dict(ex.map(one, missing)))
        cache.update({s: m for s, m in got.items() if not empty(m)})
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(json.dumps(cache))
    return cache


def recent_8k(ciks, asof, days):
    """{cik: [filing dates]} for 8-Ks filed in the last `days` business days up to asof."""
    hits = {}
    for d in pd.bdate_range(end=asof, periods=days):
        q = (d.month - 1) // 3 + 1
        url = f"https://www.sec.gov/Archives/edgar/daily-index/{d.year}/QTR{q}/form.{d:%Y%m%d}.idx"
        try:
            txt = sec.get(url)
        except Exception:
            continue  # holiday or not yet published
        for line in txt.splitlines():
            if not line.startswith("8-K "):
                continue
            parts = line.split()  # form, company name..., CIK, date filed, file name
            if len(parts) >= 5 and parts[-3].isdigit() and int(parts[-3]) in ciks:
                hits.setdefault(int(parts[-3]), set()).add(str(d.date()))
    return {k: sorted(v) for k, v in hits.items()}


def metrics(d):
    c, v = d["Close"], d["Volume"]
    r = c.pct_change().dropna()
    vol63 = float(r.iloc[-63:].std())
    ret5 = float(c.iloc[-1] / c.iloc[-6] - 1)
    return {
        "close": float(c.iloc[-1]), "asof": str(d.index[-1].date()),
        "ret_1d": float(r.iloc[-1]),
        "z_1d": float(r.iloc[-1] / vol63) if vol63 else np.nan,
        "ret_5d": ret5, "ret_21d": float(c.iloc[-1] / c.iloc[-22] - 1),
        "vol63_ann": vol63 * math.sqrt(252),
        "z_5d": ret5 / (vol63 * math.sqrt(5)) if vol63 else np.nan,
        "vol_spike": float(v.iloc[-5:].mean() / v.iloc[-63:].mean()) if v.iloc[-63:].mean() else np.nan,
        "adv20_usd": float((c * v).iloc[-20:].mean()),
        "pct_from_52w_high": float(c.iloc[-1] / c.max() - 1),
        "pct_from_52w_low": float(c.iloc[-1] / c.min() - 1),
    }, r


def num(v):
    return 0 if v is None or pd.isna(v) else v


def crowding(row):
    score = 1
    if num(row["market_cap"]) >= 1e12:
        score += 2
    if num(row["short_pct_float"]) >= 0.10:
        score += 1
    if num(row["analysts"]) >= 40:
        score += 1
    return min(score, 5)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--top", type=int, default=25)
    ap.add_argument("--exclude-mega", type=float, default=0,
                    help="drop stocks with market cap >= this many $ trillions (0 = keep all)")
    ap.add_argument("--days-8k", type=int, default=5)
    ap.add_argument("--max-days-to-event", type=int, default=30)
    ap.add_argument("--refresh-universe", action="store_true")
    a = ap.parse_args()

    if a.refresh_universe:
        with urllib.request.urlopen(UNIVERSE_URL, timeout=30) as r:
            (ROOT / "data/sp500_constituents.csv").write_bytes(r.read())
        print(f"universe refreshed from {UNIVERSE_URL} on {date.today()}")
        return

    rules = book.load_rules()
    u = load_universe()
    px = download_prices(list(u["ysym"]))
    if not px:
        raise SystemExit("Yahoo returned no prices (likely rate limited). Wait 15 to 60 minutes and rerun.")
    asof = max(d.index[-1] for d in px.values())
    today = date.today()
    filings = recent_8k(set(u["cik"].dropna().astype(int)), asof, a.days_8k)

    sector_ret = {}
    for etf in SECTOR_ETF.values():
        if etf in px:
            sector_ret[etf] = px[etf]["Close"].pct_change().dropna()

    rows = []
    for _, x in u.iterrows():
        d = px.get(x.ysym)
        if d is None:
            rows.append({"symbol": x.symbol, "name": x["name"], "kind": x.kind, "index": x["index"], "sector": x.sector,
                         "status": "NO_PRICE_DATA"})
            continue
        m, r = metrics(d)
        etf = SECTOR_ETF.get(x.sector)
        resid_z = np.nan
        if etf in sector_ret:
            j = pd.concat([r, sector_ret[etf]], axis=1, join="inner").dropna()
            if len(j) > 60:
                jj = j.iloc[-252:]
                beta = jj.cov().iloc[0, 1] / jj.iloc[:, 1].var()
                resid = j.iloc[:, 0] - beta * j.iloc[:, 1]
                sd = resid.iloc[-63:].std()
                resid_z = float(resid.iloc[-5:].sum() / (sd * math.sqrt(5))) if sd else np.nan
        ciks = filings.get(int(x.cik), []) if not pd.isna(x.cik) else []
        rows.append({"symbol": x.symbol, "ysym": x.ysym, "name": x["name"], "kind": x.kind, "index": x["index"],
                     "sector": x.sector, "status": "OK", **m, "resid_z_5d": resid_z,
                     "new_8k_dates": ";".join(ciks), "new_8k": len(ciks)})

    df = pd.DataFrame(rows)
    f0 = len(df)
    ok = df[df.status == "OK"].copy()
    zcol = ok["resid_z_5d"].where(ok["resid_z_5d"].notna(), ok["z_5d"])
    ok = ok.assign(move_z=zcol, move_score=np.fmax(zcol.abs(), ok["z_1d"].abs() / 1.5))

    # funnel
    f1 = ok[ok["adv20_usd"] >= rules["min_adv_usd"]]
    changed = f1[(f1.move_z.abs() >= 2) | (f1.z_1d.abs() >= 3) | (f1.vol_spike >= 2) | (f1.new_8k > 0)].copy()

    # Yahoo metadata only for names that changed (keeps request count low)
    meta = fetch_meta(list(changed.loc[changed.kind == "stock", "ysym"]), ROOT / f"state/cache/meta_{today}.json")
    for col in ["earnings_date", "market_cap", "short_pct_float", "analysts"]:
        changed[col] = changed["ysym"].map(lambda y: meta.get(y, {}).get(col))
    changed["days_to_earnings"] = changed["earnings_date"].map(
        lambda e: (pd.Timestamp(e).date() - today).days if isinstance(e, str) and e else np.nan)
    changed["crowding"] = changed.apply(crowding, axis=1)
    no_meta = changed[(changed.kind == "stock") & changed.earnings_date.isna()]
    mega = changed[(changed.kind == "stock") & (changed.market_cap.fillna(0) >= a.exclude_mega * 1e12)] if a.exclude_mega else changed.iloc[0:0]
    f2 = changed.drop(mega.index)
    has_event = f2[changed.days_to_earnings.between(1, a.max_days_to_event) | (changed.new_8k > 0)
                        | (changed.kind == "etf")]
    has_event = has_event.assign(rank_score=has_event.move_score.fillna(0) + (has_event.vol_spike.fillna(1) - 1)
                                 + 0.5 * (has_event.new_8k > 0) - 0.25 * (has_event.crowding - 1))
    short = has_event.sort_values("rank_score", ascending=False).head(a.top)

    out = ROOT / "screens"
    out.mkdir(exist_ok=True)
    extra = ["earnings_date", "days_to_earnings", "market_cap", "short_pct_float", "analysts", "crowding"]
    df.merge(changed[["symbol"] + extra], on="symbol", how="left").to_csv(out / f"{today}_full.csv", index=False)

    def pct(v):
        return "" if v is None or pd.isna(v) else f"{v * 100:+.1f}%"

    lines = [f"# Screen {today} (prices as of {asof.date()})", "",
             "## Funnel",
             f"- universe: {f0} ({(df['index'] == 'S&P 500').sum()} S&P 500, {(df['index'] == 'S&P 400').sum()} S&P 400 midcaps, {(df.kind == 'etf').sum()} ETFs)",
             f"- with price data: {len(ok)}  (no data: {', '.join(df[df.status != 'OK'].symbol) or 'none'})",
             f"- liquidity >= ${rules['min_adv_usd'] / 1e6:.0f}M/day: {len(f1)}",
             f"- something changed (|5d resid z| >= 2, |1d z| >= 3, volume >= 2x, or new 8-K in {a.days_8k} days): {len(changed)}",
             f"- no Yahoo earnings date (kept only if new 8-K): {', '.join(no_meta.symbol) or 'none'}",
             f"- after excluding market cap >= ${a.exclude_mega}T: {len(f2)}" + (f" (dropped {', '.join(mega.symbol)})" if len(mega) else "") if a.exclude_mega else f"- mega-cap exclusion: off",
             f"- with event in 1 to {a.max_days_to_event} days (earnings) or new 8-K: {len(has_event)}",
             f"- shortlist (top {a.top} by score): {len(short)}", "",
             "Score = max(|sector-residual 5d z|, |1d z| / 1.5) + (volume spike - 1) + 0.5 if new 8-K - 0.25 x (crowding - 1).",
             "Earnings dates are Yahoo's and may be estimates. Crowding 1 to 5 is a heuristic: +2 market cap >= $1T, +1 short >= 10% of float, +1 analysts >= 40.",
             "", "## Shortlist", "",
             "| # | symbol | index | sector | 1d | 1d z | 5d | 5d resid z | vol x | earnings (days) | new 8-K | crowd | close |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for i, (_, s) in enumerate(short.iterrows(), 1):
        ev = f"{s.earnings_date} ({int(s.days_to_earnings)})" if pd.notna(s.days_to_earnings) else "unknown"
        if pd.notna(s.days_to_earnings) and s.days_to_earnings < 0:
            ev += " reported"
        lines.append(f"| {i} | {s.symbol} | {s['index']} | {s.sector} | {pct(s.ret_1d)} | {s.z_1d:+.1f} | {pct(s.ret_5d)} | {s.move_z:+.1f} | {s.vol_spike:.1f} | {ev} | {s.new_8k_dates or ''} | {int(s.crowding)} | {s.close:.2f} |")
    (out / f"{today}.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nfull table: screens/{today}_full.csv")


if __name__ == "__main__":
    main()
