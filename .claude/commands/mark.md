---
description: Mark open paper positions to market, apply stops, log closes.
---
Run `python3 scripts/mark_to_market.py` and show me the output as is. If it prints HALT, say so first. If it prints CATALYST PASSED for a position, list those positions and ask me whether to close them (close only after I confirm, with scripts/record_trade.py close). If it prints DATA ERROR, tell me which CSV to supply.
