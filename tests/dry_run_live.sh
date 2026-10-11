#!/usr/bin/env bash
# Dry test on LIVE Yahoo data with one SAMPLE idea. Writes only to tests/out_live/.
# The sample is a mechanics test, not a researched idea or a recommendation.
# Usage: tests/dry_run_live.sh [TICKER] [ENTRY_DATE] [SIZE_PCT] [STOP_PCT_BELOW]
set -euo pipefail
cd "$(dirname "$0")/.."
T=${1:-AAPL}; D=${2:-2026-08-14}; S=${3:-4}; SP=${4:-8}
OUT=tests/out_live; rm -rf "$OUT"; mkdir -p "$OUT/state"
export CITADEL_LEDGER="$OUT/ledger.csv" CITADEL_STATE_DIR="$OUT/state"
echo "== 1. prices (Yahoo)"; python3 scripts/prices.py "$T" SPY TLT XLK
echo; echo "== 2. risk_calc: SAMPLE $T long $S%, stop $SP% below latest close"
P=$(python3 scripts/prices.py "$T" | sed -E 's/.*close=([0-9.]+).*/\1/')
STOP=$(python3 -c "print(round($P*(1-$SP/100),2))")
python3 scripts/risk_calc.py --trade "$T,long,$S,$STOP" --sector "$T:XLK"
echo; echo "== 3. backdated SAMPLE row in test ledger: entry = Yahoo close on $D"
python3 - "$T" "$D" "$S" "$SP" <<'PY'
import sys; sys.path.insert(0, "scripts"); import book, prices, pandas as pd
t, d, s, sp = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4])
df, src = prices.history(t, start="2026-01-01")
day = df.index[df.index >= pd.Timestamp(d)][0]
e = float(df.loc[day, "close"])
book.write_ledger([{"id": 1, "date": str(day.date()), "ticker": t, "direction": "long",
  "thesis": "SAMPLE mechanics test", "catalyst": "none (sample)", "catalyst_date": "2026-09-15",
  "entry": f"{e:.4f}", "stop": round(e * (1 - sp / 100), 2), "size_pct": s, "outcome": "OPEN"}])
print(f"test row: {t} long {s}% entry {e:.2f} on {day.date()} ({src}) stop {e*(1-sp/100):.2f}")
PY
echo; echo "== 4. mark_to_market"; python3 scripts/mark_to_market.py
echo; echo "== 5. scorecard"; python3 scripts/scorecard.py
echo; echo "== 6. test ledger"; cat "$OUT/ledger.csv"
echo; echo "== real ledger.csv rows (must be 0):"; tail -n +2 ledger.csv | wc -l
