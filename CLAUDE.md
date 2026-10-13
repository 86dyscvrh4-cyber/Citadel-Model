# citadel-lab

Paper-trading research experiment. Tests whether a three-role AI process (Desk, PM, Risk) beats SPY on a risk-adjusted basis. Not financial advice.

## Hard rules
- Paper only. Never connect to a broker or place real orders. No order APIs of any kind.
- Market data only from scripts/prices.py. Current source: Yahoo Finance (yfinance) only. No CSVs. An IBKR feed may be added later as READ-ONLY market data, only after a dated entry in rules.md section 9. Order, account and trading endpoints stay forbidden.
- Every number or fact in an idea card carries a source URL and a retrieval date. If it cannot be verified, label it UNVERIFIED and exclude it from the thesis.
- Never state a price from memory. Prices come from `python3 scripts/prices.py TICKER`. If the script fails, say so and stop. Do not substitute another source.
- SEC data only through scripts/sec.py (read-only). Its contact comes from SEC_USER_AGENT or the git-ignored .sec_user_agent file. Never send the user's email or any personal detail anywhere else.
- Be honest about uncertainty. Do not praise ideas. Do not invent catalysts.
- rules.md is FROZEN once approved. Never edit it unless the user says so; log every change in its section 9 with date and reason.
- No row is written to ledger.csv until the user replies "approved" to a /decide output. Use scripts/record_trade.py to write rows, never hand-edit.
- Check state/HALT before any new trade. If it exists, no new trades.

## Roles (.claude/agents/)
- desk: research only. Writes ideas/. Cannot size or approve.
- pm: proposes up to 3 trades. Writes proposals/. Cannot override Risk.
- risk: adversarial review. Writes reviews/. APPROVE, RESIZE or REJECT.
- The user approves. Nothing reaches the ledger without the user.

## Commands
/scan, /decide, /mark, /score, /postmortem.

## Files
- rules.md: limits and success criteria (JSON block at the bottom is what scripts read).
- ledger.csv: one row per paper trade.
- scripts/screen.py: full-universe screen (S&P 500 + S&P MidCap 400 + data/etfs.csv). Output in screens/. Desk works from its shortlist.
- scripts/consensus.py: Yahoo analyst consensus (EPS, revenue, trends, revisions, targets) for variant views.
- data/: universe lists and their sources (data/universe_sources.md).
- ideas/YYYY-MM-DD_TICKER.md, proposals/YYYY-MM-DD_pm.md, reviews/YYYY-MM-DD_risk.md, postmortems/YYYY-MM_postmortem.md.
- tests/: synthetic-data mechanics test (tests/dry_run.sh). Never used for real marks.
- state/: equity.csv, HALT flag, close log. Written by scripts only.

## Style
No em dashes. No filler. Short, structured output.
