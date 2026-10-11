"""Build data/sp400_constituents.csv (S&P MidCap 400) from the latest SEC N-PORT
holdings filing of the iShares Core S&P Mid-Cap ETF (IJH), via scripts/sec.py.

Usage: python3 scripts/build_universe.py

Tickers and CUSIPs come from the filing's primary_doc.xml. GICS sector comes from the
industry headings in the filing's schedule of investments, mapped to sectors below.
Holdings lag: N-PORT is quarterly and filed up to 60 days after quarter end.
"""
import difflib
import json
import re
import sys
from html import unescape
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sec  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
FUND = "iShares Core S&P Mid-Cap ETF"
TRUST_CIK = 1100663

# GICS industry -> sector (GICS 2023 structure)
GICS = {
    "Energy": ["Energy Equipment & Services", "Oil, Gas & Consumable Fuels"],
    "Materials": ["Chemicals", "Construction Materials", "Containers & Packaging", "Metals & Mining",
                  "Paper & Forest Products"],
    "Industrials": ["Aerospace & Defense", "Building Products", "Construction & Engineering",
                    "Electrical Equipment", "Industrial Conglomerates", "Machinery",
                    "Trading Companies & Distributors", "Commercial Services & Supplies",
                    "Professional Services", "Air Freight & Logistics", "Passenger Airlines",
                    "Marine Transportation", "Ground Transportation", "Transportation Infrastructure"],
    "Consumer Discretionary": ["Automobile Components", "Automobiles", "Household Durables",
                               "Leisure Products", "Textiles, Apparel & Luxury Goods",
                               "Hotels, Restaurants & Leisure", "Diversified Consumer Services",
                               "Distributors", "Broadline Retail", "Specialty Retail"],
    "Consumer Staples": ["Consumer Staples Distribution & Retail", "Beverages", "Food Products",
                         "Tobacco", "Household Products", "Personal Care Products"],
    "Health Care": ["Health Care Equipment & Supplies", "Health Care Providers & Services",
                    "Health Care Technology", "Biotechnology", "Pharmaceuticals",
                    "Life Sciences Tools & Services"],
    "Financials": ["Banks", "Financial Services", "Consumer Finance", "Capital Markets",
                   "Mortgage Real Estate Investment Trusts (REITs)", "Insurance"],
    "Information Technology": ["IT Services", "Software", "Communications Equipment",
                               "Technology Hardware, Storage & Peripherals",
                               "Electronic Equipment, Instruments & Components",
                               "Semiconductors & Semiconductor Equipment"],
    "Communication Services": ["Diversified Telecommunication Services",
                               "Wireless Telecommunication Services", "Media", "Entertainment",
                               "Interactive Media & Services"],
    "Utilities": ["Electric Utilities", "Gas Utilities", "Multi-Utilities", "Water Utilities",
                  "Independent Power and Renewable Electricity Producers"],
    "Real Estate": ["Diversified REITs", "Industrial REITs", "Hotel & Resort REITs", "Office REITs",
                    "Health Care REITs", "Residential REITs", "Retail REITs", "Specialized REITs",
                    "Real Estate Management & Development"],
}
INDUSTRY_TO_SECTOR = {i.lower(): s for s, inds in GICS.items() for i in inds}
STOP = {"INC", "CORP", "CORPORATION", "CO", "COMPANY", "LTD", "PLC", "THE", "HOLDINGS", "HOLDING",
        "GROUP", "CLASS", "A", "B", "C", "NV", "SA", "LP", "LLC", "TRUST", "REIT", "COM", "NEW", "DE"}


def norm(name):
    words = re.sub(r"[^A-Z0-9 ]", " ", name.upper().replace("&", " AND ")).split()
    return " ".join(w for w in words if w not in STOP)


def latest_filing():
    q = ("https://efts.sec.gov/LATEST/search-index?q=%22iShares%20Core%20S%26P%20Mid-Cap%20ETF%22"
         "&forms=NPORT-P")
    hits = json.loads(sec.get(q))["hits"]["hits"]
    hits.sort(key=lambda h: h["_source"].get("period_ending", ""), reverse=True)
    for h in hits:
        adsh, doc = h["_id"].split(":")
        base = f"https://www.sec.gov/Archives/edgar/data/{TRUST_CIK}/{adsh.replace('-', '')}/"
        html = sec.get(base + doc)
        if FUND in unescape(html).replace("®", ""):
            return base, html, h["_source"]["period_ending"]
    raise SystemExit(f"no N-PORT filing found for {FUND}")


def industries_from_html(html):
    """Map normalized company name -> GICS industry from the schedule of investments."""
    txt = sec.to_text(html)
    out, current = {}, None
    for line in (ln.strip() for ln in txt.splitlines()):
        m = re.match(r"^(.*?)\s+[—-]\s+\d+(\.\d+)?%$", line)
        if m and m.group(1).lower() in INDUSTRY_TO_SECTOR:
            current = m.group(1)
            continue
        if current and re.search(r"[A-Za-z]", line) and not re.match(r"^[\d$,. ()%]+$", line):
            out.setdefault(norm(re.sub(r"\([a-z]\)", "", line)), current)
    return out


def main():
    base, html, period = latest_filing()
    xml = sec.get(base + "primary_doc.xml")
    inds = industries_from_html(html)
    tick = json.loads(sec.get("https://www.sec.gov/files/company_tickers.json"))
    cik_by_ticker = {r["ticker"].upper(): r["cik_str"] for r in tick.values()}

    rows, unmatched = [], []
    for blk in re.findall(r"<invstOrSec>(.*?)</invstOrSec>", xml, re.S):
        if "<assetCat>EC</assetCat>" not in blk:
            continue
        name = re.search(r"<name>(.*?)</name>", blk).group(1)
        t = re.search(r'<ticker value="([^"]+)"', blk)
        if not t:
            unmatched.append(f"{name} (no ticker)")
            continue
        sym = t.group(1).upper().replace("/", ".").replace("-", ".")
        n = norm(unescape(name))
        ind = inds.get(n)
        if ind is None:
            close = difflib.get_close_matches(n, inds.keys(), n=1, cutoff=0.8)
            ind = inds[close[0]] if close else None
        if ind is None:
            unmatched.append(f"{sym} {name} (no industry)")
        rows.append({"Symbol": sym, "Security": unescape(name).title(),
                     "GICS Sector": INDUSTRY_TO_SECTOR.get((ind or "").lower(), ""),
                     "GICS Industry": ind or "",
                     "CIK": cik_by_ticker.get(sym.replace(".", "-"), cik_by_ticker.get(sym, ""))})
    df = pd.DataFrame(rows).drop_duplicates("Symbol").sort_values("Symbol")
    df.to_csv(ROOT / "data/sp400_constituents.csv", index=False)
    print(f"{len(df)} S&P MidCap 400 names as of {period} from {base}")
    print(f"sector filled: {(df['GICS Sector'] != '').sum()}  CIK filled: {(df['CIK'] != '').sum()}")
    if unmatched:
        print("unmatched: " + "; ".join(unmatched[:20]) + (f" ... +{len(unmatched) - 20}" if len(unmatched) > 20 else ""))
    return base, period


if __name__ == "__main__":
    main()
