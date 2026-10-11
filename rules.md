# rules.md

STATUS: DRAFT, awaiting user approval. Once approved, this file is FROZEN.
Approved on: (pending)

Paper trading only. Not financial advice.

## 1. Book
- Starting paper capital: $1,000,000.
- Directions allowed: long and short. Shorts are paper only; no borrow cost modeled.
- Gross exposure (sum of |position notional|) at or below 100% of book equity. No leverage.
- No maximum position count. Full deployment at the 5% cap means 20 or more names.
- Idle cash (equity minus gross exposure, floored at 0) earns a fixed 4.0% annual rate, accrued per trading day (rate / 252).
- size_pct in ledger.csv is percent of starting capital ($1,000,000). Share count = size_pct x $1,000,000 / entry.

## 2. Universe
- US large caps: S&P 500 constituents at the time of entry.
- US-listed ETFs, as trades or hedges.
- Liquidity floor: 20-day average dollar volume at or above $50M (checked by risk_calc.py when volume data exists; otherwise Risk flags it UNVERIFIED).

## 3. Position limits
- Max loss per position at stop: 1% of starting capital ($10,000).
- Max single-name weight: 5% of starting capital ($50,000 at entry). Combined size across trades in the same ticker counts toward this cap.
- Every position has a stop at entry. Stops are not widened after entry.
- PM proposes at most 3 trades per run.

## 4. Drawdown halt
- If book equity falls 10% or more from its running peak: no new trades.
- Existing positions run to their stops or planned exits.
- Trading resumes only when the user says so, logged in section 9.

## 5. Benchmark
- SPY price return (close) over the same dates as the book. Positions also mark on close and dividends are ignored on both sides, so the comparison is like for like.

## 6. Run
- Length: 12 weeks, starting on the date of the first approved trade.
- Cadence: /scan and /decide daily on trading days, plus on demand.
- /postmortem on the last trading day of each month and at the end of the run.

## 7. Fills and marks (paper conventions)
- Entry fill: latest close from the data script on the approval date.
- Stops are checked on daily bars. If high/low data exists, a long stops when low <= stop, a short when high >= stop. Fill at the stop, or at the open if the bar gapped through the stop.
- If only close data exists, stops trigger on close and fill at that close.
- No commissions or slippage modeled beyond the gap rule.
- Planned (non-stop) exits fill at the latest close from the data script on the exit date.

## 8. Pre-registered success criteria
Evaluated by scripts/scorecard.py at the end of the run. All three must hold:
1. Annualized Sharpe of daily book returns (rf = 4.0%) exceeds SPY's over the same dates.
2. Total return divided by max drawdown exceeds SPY's over the same dates.
3. Average winning trade ($) exceeds average losing trade ($, absolute).

If fewer than 30 trades have resolved, the result is INCONCLUSIVE regardless of 1 to 3.

## 9. Change log
Rules change only when the user says so. Each change: date, rule, old value, new value, reason.

| date | rule | old | new | reason |
|------|------|-----|-----|--------|

## Machine-readable parameters (scripts read this block; keep in sync with the text above)
```json
{
  "starting_capital": 1000000,
  "max_gross_pct": 100,
  "max_loss_per_position_pct": 1.0,
  "max_single_name_pct": 5.0,
  "max_trades_per_run": 3,
  "drawdown_halt_pct": 10.0,
  "cash_rate_annual_pct": 4.0,
  "benchmark": "SPY",
  "run_weeks": 12,
  "min_adv_usd": 50000000,
  "min_resolved_trades": 30,
  "allow_short": true
}
```
