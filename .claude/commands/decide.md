---
description: PM proposes up to 3 trades, then Risk reviews them. Shows both. Nothing goes in the ledger.
---
1. If state/HALT exists, stop and tell me.
2. Use the pm subagent on today's ideas/ cards (or these, if given: $ARGUMENTS). Wait for it to finish.
3. Then use the risk subagent on the proposals file the PM just wrote. Run sequentially, never in parallel, and do not pass the PM's reasoning to Risk beyond the proposals file.
4. Show me both outputs: the PM proposal blocks, then the Risk table and per-trade verdicts with the binding constraint and numbers.
5. Stop. Do not write to ledger.csv. Only when I reply "approved" (optionally naming trades), record each approved trade at the size Risk allowed using scripts/record_trade.py open. REJECTED trades are never recorded.
