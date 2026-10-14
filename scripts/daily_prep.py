"""Morning prep for /scan: screen, new-or-changed filter, guidance gaps, consensus snapshot.

Usage: python3 scripts/daily_prep.py [--lookback-days 5] [--skip-screen]

Steps:
  1. scripts/screen.py (unless --skip-screen or today's screen exists)
  2. Drop names already given a verdict in ideas/*funnel*/recheck* files within the lookback,
     unless they have an 8-K since the last close or a 1-day move |z| >= 2.5. Drop open positions.
  3. scripts/guidance_gap.py over the last 3 business days of 8-Ks (adds flagged names).
  4. Yahoo consensus snapshot for the final list (throttled), so Desk never loops on Yahoo.
Writes screens/DATE_new.md, screens/DATE_consensus.txt, screens/DATE_guidance_gaps.md.
"""
import argparse
import contextlib
import io
import re
import subprocess
import sys
import time
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import book  # noqa: E402
import consensus  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
LABELS = r"(CARD|NO_VARIANT|NO_CATALYST|PRICED_IN|CROWDED|DUPLICATE|DATA)"


def recently_seen(lookback_days):
    """{symbol: latest date it got a verdict} within the lookback."""
    cutoff = date.today() - timedelta(days=lookback_days)
    seen = {}
    for f in sorted((ROOT / "ideas").glob("*.md")):
        m = re.match(r"(\d{4}-\d{2}-\d{2})_(funnel|recheck)", f.name)
        if not m or date.fromisoformat(m.group(1)) < cutoff:
            continue
        for line in f.read_text().splitlines():
            for mm in re.finditer(r"\b([A-Z][A-Z.]{0,5})\b[^|\n]{0,40}\|?\s*\**" + LABELS + r"\b", line):
                seen[mm.group(1)] = max(seen.get(mm.group(1), ""), m.group(1))
    return seen


def run(cmd):
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(f"{' '.join(cmd)} failed:\n{r.stdout[-2000:]}\n{r.stderr[-2000:]}")
    return r.stdout


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--lookback-days", type=int, default=5)
    ap.add_argument("--skip-screen", action="store_true")
    a = ap.parse_args()
    today = date.today()
    full = ROOT / "screens" / f"{today}_full.csv"

    if not a.skip_screen and not full.exists():
        run([sys.executable, "scripts/screen.py", "--top", "30"])
    if not full.exists():
        raise SystemExit(f"no screen for {today}; run scripts/screen.py")
    head = (ROOT / "screens" / f"{today}.md").read_text().splitlines()[0]
    asof = re.search(r"prices as of (\d{4}-\d{2}-\d{2})", head).group(1)

    # 2. new-or-changed filter (same scoring as screen.py)
    df = pd.read_csv(full)
    ok = df[df.status == "OK"].copy()
    ok["move_z"] = ok.resid_z_5d.where(ok.resid_z_5d.notna(), ok.z_5d)
    ok["move_score"] = np.fmax(ok.move_z.abs(), ok.z_1d.abs() / 1.5)
    f1 = ok[ok.adv20_usd >= book.load_rules()["min_adv_usd"]]
    ch = f1[(f1.move_z.abs() >= 2) | (f1.z_1d.abs() >= 3) | (f1.vol_spike >= 2) | (f1.new_8k > 0)]
    ev = ch[ch.days_to_earnings.between(1, 30) | (ch.new_8k > 0) | (ch.kind == "etf")].copy()
    ev["rank_score"] = ev.move_score.fillna(0) + (ev.vol_spike.fillna(1) - 1) + 0.5 * (ev.new_8k > 0) - 0.25 * (ev.crowding.fillna(1) - 1)
    ev = ev.sort_values("rank_score", ascending=False).reset_index(drop=True)
    ev.index += 1
    seen = recently_seen(a.lookback_days)
    open_t = {r["ticker"] for r in book.read_ledger() if book.is_open(r)}
    # an 8-K is new information only if filed after the name's last review (or on/after the last close if never reviewed)
    fresh = pd.Series([[d for d in str(k).split(";") if d > seen.get(sym, "") and d >= asof] if isinstance(k, str) else []
                       for sym, k in zip(ev.symbol, ev.new_8k_dates)], index=ev.index)
    big_new_move = (ev.z_1d.abs() >= 2.5) & ev.symbol.map(lambda x: seen.get(x, "") < asof)
    keep = (~ev.symbol.isin(seen)) | (fresh.map(len) > 0) | big_new_move
    pick = ev[keep & ~ev.symbol.isin(open_t)].copy()
    pick["why"] = [("new name" if s not in seen else ("new 8-K" if f else "big 1d move")) for s, f in zip(pick.symbol, fresh[pick.index])]

    # 3. guidance gaps
    run([sys.executable, "scripts/guidance_gap.py", "--days", "3"])
    gg = (ROOT / "screens" / f"{today}_guidance_gaps.md").read_text()
    flagged = re.findall(r"^\| ([A-Z.]+) \| \d{4}-\d{2}-\d{2} \|", gg.split("## Flagged", 1)[1].split("###", 1)[0], re.M)
    extra = [s for s in flagged if s not in set(pick.symbol) and s not in open_t and seen.get(s, "") < asof]

    def pct(v):
        return "" if pd.isna(v) else f"{v * 100:+.1f}%"
    lines = [f"# Desk list {today} (prices as of {asof})", "",
             f"Eventful names: {len(ev)}. Already reviewed in the last {a.lookback_days} days with nothing new: {len(ev) - keep.sum()}. "
             f"Open positions excluded: {', '.join(sorted(open_t)) or 'none'}.",
             f"Names to examine: {len(pick)} from the screen + {len(extra)} from guidance gaps ({', '.join(extra) or 'none'}).",
             f"Guidance gap flags (all): {', '.join(flagged) or 'none'}; see screens/{today}_guidance_gaps.md.", "",
             "| rank | symbol | index | sector | 1d | 1d z | 5d | 5d resid z | vol x | earnings (days) | new 8-K | crowd | close | why |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for i, s in pick.iterrows():
        e = f"{s.earnings_date} ({int(s.days_to_earnings)})" if pd.notna(s.days_to_earnings) else "unknown"
        lines.append(f"| {i} | {s.symbol} | {s['index']} | {s.sector} | {pct(s.ret_1d)} | {s.z_1d:+.1f} | {pct(s.ret_5d)} | "
                     f"{s.move_z:+.1f} | {s.vol_spike:.1f} | {e} | {s.new_8k_dates if isinstance(s.new_8k_dates, str) else ''} | "
                     f"{int(s.crowding) if pd.notna(s.crowding) else ''} | {s.close:.2f} | {s.why} |")
    for s in extra:
        lines.append(f"| gg | {s} |  |  |  |  |  |  |  |  |  |  |  | guidance gap flag |")
    (ROOT / "screens" / f"{today}_new.md").write_text("\n".join(lines) + "\n")

    # 4. consensus snapshot
    names = list(pick.symbol) + extra
    out = [f"# Yahoo Finance consensus snapshot, retrieved {today}, {len(names)} names",
           f"# Cite per ticker: Yahoo Finance consensus | https://finance.yahoo.com/quote/TICKER/analysis | retrieved {today}", ""]
    for n in names:
        if n in set(ev[ev.kind == "etf"].symbol):
            continue
        for _ in range(3):
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                consensus.show(n.replace(".", "-"))
            txt = buf.getvalue()
            if txt.count("unavailable") < 4:
                break
            time.sleep(20)
        out.append(txt)
        time.sleep(2)
    (ROOT / "screens" / f"{today}_consensus.txt").write_text("\n".join(out) + "\n")
    print("\n".join(lines[:5]))
    print(f"wrote screens/{today}_new.md, screens/{today}_consensus.txt, screens/{today}_guidance_gaps.md")


if __name__ == "__main__":
    main()
