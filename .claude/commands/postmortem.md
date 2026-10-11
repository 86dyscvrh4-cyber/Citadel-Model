---
description: Monthly postmortem. What did we get wrong.
---
Write postmortems/YYYY-MM_postmortem.md for the month just ended (or $ARGUMENTS).

Inputs: ledger.csv, ideas/, proposals/, reviews/, state/closes.log, and the output of `python3 scripts/scorecard.py` and `python3 scripts/mark_to_market.py --dry-run`.

Sections, short:
1. Scorecard snapshot (paste the numbers).
2. Question: "What did we do wrong over the last month that caused us to underperform?" Answer it even if we outperformed.
3. Three mistakes. Each: trade id(s), what happened, which role failed (Desk, PM or Risk), evidence.
4. Compare each PM's best idea to its risk-adjusted result. Which role was right more often: PM or Risk (on rejected and resized trades, what would have happened)?
5. One new written rule (process rule, one sentence).
6. Rule change check: does the new rule touch anything in rules.md? rules.md is FROZEN. If it would, say "requires user approval" and do not edit rules.md. Process rules go in the postmortem only.

No praise. No em dashes.
