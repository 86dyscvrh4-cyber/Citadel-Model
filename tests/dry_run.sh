#!/usr/bin/env bash
# Mechanics test on SYNTHETIC data. Writes only to tests/out/. Never touches ledger.csv.
set -euo pipefail
cd "$(dirname "$0")/.."
OUT=tests/out; rm -rf "$OUT"; mkdir -p "$OUT/state"
export CITADEL_PRICE_SOURCE=csv CITADEL_PRICES_DIR="$OUT/prices" CITADEL_LEDGER="$OUT/ledger.csv" CITADEL_STATE_DIR="$OUT/state"
head -1 ledger.csv > "$OUT/ledger.csv"
echo "== 1. fixtures through 2026-08-14 (entry day)"; python3 tests/make_fixtures.py "$OUT/prices" 2026-08-14
echo; echo "== 2. latest price"; python3 scripts/prices.py SYNA SYNB
echo; echo "== 3. risk_calc on sample idea (SYNA long 5%, stop 8% below) + SYNB short"
P=$(python3 scripts/prices.py SYNA | sed -E 's/.*close=([0-9.]+).*/\1/')
Q=$(python3 scripts/prices.py SYNB | sed -E 's/.*close=([0-9.]+).*/\1/')
SA=$(python3 -c "print(round($P*0.92,2))"); SB=$(python3 -c "print(round($Q*1.04,2))")
python3 scripts/risk_calc.py --trade SYNA,long,5,$SA --trade SYNB,short,5,$SB --sector SYNA:XLK --sector SYNB:XLK
echo; echo "== 4. guardrail: oversized trade must be refused"
python3 scripts/record_trade.py open --ticker SYNA --direction long --size-pct 20 --stop $SA --thesis t --catalyst c --catalyst-date 2026-09-01 --allow-draft || true
echo; echo "== 5. record both (test ledger only)"
python3 scripts/record_trade.py open --ticker SYNA --direction long --size-pct 5 --stop $SA --thesis "SYNTHETIC sample" --catalyst "synthetic event" --catalyst-date 2026-09-15 --allow-draft
python3 scripts/record_trade.py open --ticker SYNB --direction short --size-pct 5 --stop $SB --thesis "SYNTHETIC sample" --catalyst "synthetic event" --catalyst-date 2026-09-15 --allow-draft
echo; echo "== 6. extend fixtures to 2026-10-09 and mark"
python3 tests/make_fixtures.py "$OUT/prices" 2026-10-09 >/dev/null
python3 scripts/mark_to_market.py
echo; echo "== 7. scorecard"; python3 scripts/scorecard.py
echo; echo "== 8. test ledger"; cat "$OUT/ledger.csv"
