"""Guidance vs consensus gap finder.

For universe companies that filed an 8-K with Item 2.02 (results) or 7.01 (Reg FD) in the
last N business days, pull the press-release text, extract EPS guidance ranges, and compare
them with Yahoo consensus. Flags consensus outside the guided range or far from its midpoint.

Usage: python3 scripts/guidance_gap.py [--days 3] [--min-gap 2.0] [--tickers A,B]

Writes screens/YYYY-MM-DD_guidance_gaps.md. Extraction is regex-based (machine-read):
every flag must be checked against the filing before it goes on an idea card.
"""
import argparse
import json
import logging
import re
import sys
import time
from datetime import date
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sec  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
logging.getLogger("yfinance").setLevel(logging.CRITICAL)

NUM = r"\$?\s?(\d{1,3}\.\d{2})"
RANGE = re.compile(NUM + r"\s*(?:to|-|–|—|and)\s*" + NUM)
FLOOR = re.compile(r"(?:at least|no less than|of at least|minimum of)\s*" + NUM, re.I)
EPS_WORDS = re.compile(r"(earnings per (?:diluted )?share|\bEPS\b|per diluted share|per share)", re.I)
GUIDE_WORDS = re.compile(r"(guidance|outlook|expects?|expected|anticipates?|forecast|projects?|raises?|raised|lowers?|lowered|reaffirm|now sees)", re.I)
FY = re.compile(r"(full[- ]year|fiscal(?: year)?\s*(?:20\d\d)?|FY\s?\d{2,4}|for 20\d\d|year 20\d\d)", re.I)
QTR = re.compile(r"(fourth[- ]quarter|third[- ]quarter|first[- ]quarter|second[- ]quarter|next quarter|Q[1-4]\b)", re.I)
ADJ = re.compile(r"(adjusted|non-GAAP|core|operating)", re.I)


def universe():
    frames = []
    for f in ["sp500_constituents.csv", "sp400_constituents.csv"]:
        d = pd.read_csv(ROOT / "data" / f)
        frames.append(pd.DataFrame({"symbol": d["Symbol"], "cik": pd.to_numeric(d["CIK"], errors="coerce")}))
    u = pd.concat(frames).dropna().drop_duplicates("symbol")
    return {int(c): s for s, c in zip(u.symbol, u.cik)}


def live_feed_ciks(ciks, day):
    """CIKs in `ciks` with an 8-K on `day` in SEC's current-filings feed (covers today, before the daily index)."""
    hits = set()
    for start in range(0, 1000, 100):
        x = sec.get("https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type=8-K&company=&dateb="
                    f"&owner=include&start={start}&count=100&output=atom")
        entries = re.findall(r"<entry>(.*?)</entry>", x, re.S)
        if not entries:
            break
        for e in entries:
            m = re.search(r"\((\d{6,10})\)", re.search(r"<title>(.*?)</title>", e).group(1))
            if m and re.search(r"<updated>" + day, e) and int(m.group(1)) in ciks:
                hits.add(int(m.group(1)))
        if not any(re.search(r"<updated>" + day, e) for e in entries):
            break
    return hits


def recent_8k_ciks(ciks, days):
    hits = set()
    for d in pd.bdate_range(end=pd.Timestamp(date.today()), periods=days + 1):
        q = (d.month - 1) // 3 + 1
        try:
            txt = sec.get(f"https://www.sec.gov/Archives/edgar/daily-index/{d.year}/QTR{q}/form.{d:%Y%m%d}.idx")
        except Exception:
            hits |= live_feed_ciks(ciks, str(d.date()))  # index not published yet (same day): use the live feed
            continue
        for line in txt.splitlines():
            if line.startswith("8-K "):
                parts = line.split()
                if len(parts) >= 5 and parts[-3].isdigit() and int(parts[-3]) in ciks:
                    hits.add(int(parts[-3]))
    return hits


def guidance_filings(cik, since):
    sub = json.loads(sec.get(f"https://data.sec.gov/submissions/CIK{cik:010d}.json"))["filings"]["recent"]
    out = []
    for i, form in enumerate(sub["form"]):
        if form != "8-K" or sub["filingDate"][i] < since:
            continue
        items = sub.get("items", [""] * len(sub["form"]))[i]
        if "2.02" in items or "7.01" in items:
            out.append((sub["filingDate"][i], sub["accessionNumber"][i].replace("-", ""), items))
    return out


def filing_text(cik, acc):
    base = f"https://www.sec.gov/Archives/edgar/data/{cik}/{acc}/"
    idx = json.loads(sec.get(base + "index.json"))
    texts, urls = [], []
    for f in idx["directory"]["item"]:
        n = f["name"].lower()
        if n.endswith((".htm", ".html")) and "index" not in n and not re.match(r"r\d+\.htm", n):
            try:
                texts.append(sec.to_text(sec.get(base + f["name"])))
                urls.append(base + f["name"])
            except Exception:
                pass
    return "\n".join(texts), urls


def extract(text):
    """Find EPS guidance in prose or tables.

    Prose: one sentence with guidance words + EPS words + a range or floor.
    Tables: inside a guidance/outlook section (guidance word within the previous 40 lines),
    an EPS row label followed within 4 lines by the first range (the current guide; prior
    guidance columns usually come after it).
    """
    lines = [c.strip() for ln in text.splitlines() for c in re.split(r"\s*[\u2022;]\s*", ln) if c.strip()]
    found, last_guide = [], -999
    for i, ln in enumerate(lines):
        if GUIDE_WORDS.search(ln) and re.search(r"(guidance|outlook)", ln, re.I):
            last_guide = i
        if len(ln) > 700 or "billion" in ln.lower() or "million" in ln.lower():
            continue
        prose = GUIDE_WORDS.search(ln) and EPS_WORDS.search(ln)
        table = EPS_WORDS.search(ln) and i - last_guide <= 40
        if not (prose or table):
            continue
        window = [ln] if prose else lines[i:i + 5]
        for w in window:
            if "billion" in w.lower() or "million" in w.lower() or "%" in w:
                continue
            m = RANGE.search(w)
            if m:
                lo, hi = float(m.group(1)), float(m.group(2))
                if 0 < lo <= hi and hi / lo < 1.5:
                    ctx = " | ".join(lines[max(last_guide, i - 2):i + 1] + ([w] if w != ln else []))
                    found.append({"lo": lo, "hi": hi, "sent": ctx, "hdr": lines[last_guide] if last_guide >= 0 else ""})
                    break
            f = FLOOR.search(w)
            if f:
                found.append({"lo": float(f.group(1)), "hi": None, "sent": " | ".join(lines[max(last_guide, i - 2):i + 1]),
                              "hdr": lines[last_guide] if last_guide >= 0 else ""})
                break
    for g in found:
        s = g["sent"] + " " + g.get("hdr", "")
        g["period"] = "FY" if FY.search(s) else ("Q" if QTR.search(s) else "?")
        g["basis"] = "adjusted" if ADJ.search(s) else "GAAP?"
    seen, uniq = set(), []
    for g in found:
        k = (g["lo"], g["hi"])
        if k not in seen:
            seen.add(k)
            uniq.append(g)
    return uniq[:4]


def consensus(ticker):
    import yfinance as yf
    try:
        df = yf.Ticker(ticker.replace(".", "-")).earnings_estimate
        return {p: (float(r["avg"]), int(r["numberOfAnalysts"])) for p, r in df.iterrows() if pd.notna(r["avg"])}
    except Exception:
        return {}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--days", type=int, default=3)
    ap.add_argument("--min-gap", type=float, default=2.0, help="flag if consensus is this %% from guide midpoint")
    ap.add_argument("--tickers", default="")
    a = ap.parse_args()

    u = universe()
    since = str(pd.bdate_range(end=pd.Timestamp(date.today()), periods=a.days + 1)[0].date())
    if a.tickers:
        want = {t.strip().upper() for t in a.tickers.split(",")}
        ciks = {c for c, s in u.items() if s in want}
    else:
        ciks = recent_8k_ciks(set(u), a.days)

    rows = []
    for cik in sorted(ciks):
        sym = u[cik]
        try:
            fl = guidance_filings(cik, since)
        except Exception as e:
            rows.append({"symbol": sym, "status": f"submissions error {type(e).__name__}"})
            continue
        for fdate, acc, items in fl:
            text, urls = filing_text(cik, acc)
            guides = extract(text)
            if not guides:
                rows.append({"symbol": sym, "date": fdate, "items": items, "status": "no EPS guidance found", "url": urls[0] if urls else ""})
                continue
            cons = consensus(sym)
            time.sleep(1)
            for g in guides:
                keys = ["0y", "+1y"] if g["period"] == "FY" else (["0q", "+1q"] if g["period"] == "Q" else ["0q", "0y"])
                mid = g["lo"] if g["hi"] is None else (g["lo"] + g["hi"]) / 2
                best = None
                for k in keys:  # compare with each candidate period; report all, flag on any outside-range
                    if k not in cons:
                        continue
                    c, n = cons[k]
                    gap = (c - mid) / mid * 100
                    outside = (c < g["lo"]) or (g["hi"] is not None and c > g["hi"])
                    r = {"symbol": sym, "date": fdate, "items": items, "period": g["period"], "basis": g["basis"],
                         "guide": f"{g['lo']:.2f}" + ("+" if g["hi"] is None else f"-{g['hi']:.2f}"),
                         "yahoo_period": k, "consensus": c, "n": n, "gap_pct": gap, "outside": outside,
                         "url": urls[0] if urls else "", "sent": g["sent"][:260], "status": "ok"}
                    if best is None or abs(gap) < abs(best["gap_pct"]):
                        best = r
                if best:
                    rows.append(best)
                else:
                    rows.append({"symbol": sym, "date": fdate, "status": "guidance found, no Yahoo consensus",
                                 "guide": f"{g['lo']:.2f}-{g['hi'] if g['hi'] else ''}", "url": urls[0] if urls else ""})

    # per company and period: keep the guide closest to consensus; flag only if consensus is outside it
    ok_rows = [r for r in rows if r.get("status") == "ok"]
    best_by = {}
    for r in ok_rows:
        k = (r["symbol"], r["period"])
        if k not in best_by or abs(r["gap_pct"]) < abs(best_by[k]["gap_pct"]):
            best_by[k] = r
    for r in ok_rows:
        b = best_by[(r["symbol"], r["period"])]
        r["flag"] = (r is b) and (b["outside"] or abs(b["gap_pct"]) >= a.min_gap)

    today = date.today()
    out = ROOT / "screens" / f"{today}_guidance_gaps.md"
    ok = [r for r in rows if r.get("status") == "ok"]
    flagged = sorted([r for r in ok if r.get("flag")], key=lambda r: -abs(r["gap_pct"]))
    lines = [f"# Guidance vs consensus gaps, {today}", "",
             f"8-Ks with Item 2.02/7.01 from {since}; companies checked: {len(ciks)}; guidance ranges parsed: {len(ok)}; flagged: {len(flagged)}.",
             "Machine-extracted with regex. Verify every number against the filing before using it. Period matching is approximate:",
             "the consensus period closest to the guide midpoint is shown (yahoo_period). Yahoo EPS basis may differ from company adjusted EPS.",
             f"Consensus: Yahoo Finance (https://finance.yahoo.com/quote/TICKER/analysis), retrieved {today}.", "",
             "## Flagged (consensus outside guided range, or gap >= " + f"{a.min_gap}% from midpoint)", "",
             "| symbol | filed | period | basis | guide | yahoo period | consensus (n) | gap vs mid | outside | filing |",
             "|---|---|---|---|---|---|---|---|---|---|"]
    for r in flagged:
        lines.append(f"| {r['symbol']} | {r['date']} | {r['period']} | {r['basis']} | {r['guide']} | {r['yahoo_period']} | "
                     f"{r['consensus']:.2f} ({r['n']}) | {r['gap_pct']:+.1f}% | {'YES' if r['outside'] else ''} | {r['url']} |")
    lines += ["", "### Guidance sentences for flagged rows", ""]
    for r in flagged:
        lines.append(f"- {r['symbol']}: \"{r['sent']}\"")
    lines += ["", "## Not flagged", ""]
    for r in ok:
        if not r.get("flag"):
            lines.append(f"- {r['symbol']} {r['period']} guide {r['guide']} vs {r['yahoo_period']} consensus {r['consensus']:.2f} ({r['gap_pct']:+.1f}%)")
    for r in rows:
        if r.get("status") != "ok":
            lines.append(f"- {r['symbol']} {r.get('date', '')}: {r['status']}")
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines[:12 + len(flagged)]))
    print(f"\nfull report: screens/{today}_guidance_gaps.md")


if __name__ == "__main__":
    main()
