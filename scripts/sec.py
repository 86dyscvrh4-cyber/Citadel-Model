"""Read-only SEC EDGAR helper for Desk research.

  python3 scripts/sec.py filings TICKER [--forms 8-K,10-Q,10-K] [--n 10]
  python3 scripts/sec.py fetch URL [--max-chars 20000] [--grep WORD]

The SEC requires a User-Agent with a name and contact email. It is read from the
SEC_USER_AGENT env var, else from the git-ignored file .sec_user_agent at the repo
root. Never hard-code or substitute any other contact.
"""
import argparse
import html
import json
import os
import re
import sys
import time
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
ALLOWED_HOSTS = {"sec.gov", "www.sec.gov", "data.sec.gov", "efts.sec.gov"}


def user_agent():
    ua = os.environ.get("SEC_USER_AGENT", "").strip()
    f = ROOT / ".sec_user_agent"
    if not ua and f.exists():
        ua = f.read_text().strip()
    if not ua or "@" not in ua:
        raise SystemExit("SEC contact not configured: set SEC_USER_AGENT or create .sec_user_agent. Ask the user; do not invent one.")
    return ua


def get(url):
    host = urlparse(url).hostname or ""
    if host not in ALLOWED_HOSTS:
        raise SystemExit(f"refused: {host} is not an SEC host")
    req = urllib.request.Request(url, headers={"User-Agent": user_agent(), "Accept-Encoding": "identity"})
    time.sleep(0.15)  # stay well under the SEC's 10 requests/second limit
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", errors="replace")


def cik_for(ticker):
    data = json.loads(get("https://www.sec.gov/files/company_tickers.json"))
    for row in data.values():
        if row["ticker"].upper() == ticker.upper():
            return int(row["cik_str"]), row["title"]
    raise SystemExit(f"ticker {ticker} not found in SEC company_tickers.json")


def cmd_filings(a):
    cik, name = cik_for(a.ticker)
    sub = json.loads(get(f"https://data.sec.gov/submissions/CIK{cik:010d}.json"))
    rec = sub["filings"]["recent"]
    forms = {f.strip().upper() for f in a.forms.split(",")} if a.forms else None
    print(f"{a.ticker.upper()}  {name}  CIK {cik}")
    shown = 0
    for i, form in enumerate(rec["form"]):
        if forms and form.upper() not in forms:
            continue
        acc = rec["accessionNumber"][i].replace("-", "")
        url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{acc}/{rec['primaryDocument'][i]}"
        items = rec.get("items", [""] * len(rec["form"]))[i]
        print(f"{rec['filingDate'][i]}  {form:8} {('items ' + items) if items else ''}  {url}")
        shown += 1
        if shown >= a.n:
            break


def to_text(raw):
    raw = re.sub(r"(?is)<(script|style).*?</\1>", " ", raw)
    raw = re.sub(r"(?i)<br\s*/?>|</(p|div|tr|li|h\d)>", "\n", raw)
    txt = html.unescape(re.sub(r"<[^>]+>", " ", raw))
    txt = re.sub(r"[ \t\xa0]+", " ", txt)
    return re.sub(r"\n\s*\n+", "\n\n", txt).strip()


def cmd_fetch(a):
    txt = to_text(get(a.url))
    if a.grep:
        pat = re.compile(re.escape(a.grep), re.I)
        lines = [ln.strip() for ln in txt.splitlines() if pat.search(ln)]
        print("\n".join(lines)[: a.max_chars] or f"no lines contain '{a.grep}'")
    else:
        print(txt[: a.max_chars])
        if len(txt) > a.max_chars:
            print(f"\n[truncated: {len(txt):,} chars total; use --grep or a larger --max-chars]")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("filings")
    f.add_argument("ticker")
    f.add_argument("--forms", default="")
    f.add_argument("--n", type=int, default=10)
    g = sub.add_parser("fetch")
    g.add_argument("url")
    g.add_argument("--max-chars", type=int, default=20000)
    g.add_argument("--grep", default="")
    a = ap.parse_args()
    (cmd_filings if a.cmd == "filings" else cmd_fetch)(a)


if __name__ == "__main__":
    main()
