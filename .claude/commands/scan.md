---
description: Desk research run. Up to 5 sourced idea cards into ideas/.
---
1. Prep: if screens/<today>_new.md does not exist, run `python3 scripts/daily_prep.py` (screen, new-or-changed filter, guidance gaps, consensus snapshot; about 3 to 5 minutes). If it fails, show the error and stop. Show me its summary lines.
2. If the list has 0 names, say so and stop: nothing new to examine today.
3. Use the desk subagent on screens/<today>_new.md with the snapshot screens/<today>_consensus.txt and screens/<today>_guidance_gaps.md. For more than 25 names, split into batches and run up to 3 desk subagents in parallel, each writing its own funnel file (ideas/<today>_funnel_N.md). Extra focus from the user, if any: $ARGUMENTS
4. Show me the index (ticker, direction, driver, variant view, catalyst date, file) and the drop-label tally. Remove cross-batch duplicates by driver. List any card with UNVERIFIED items or PRICE UNAVAILABLE. Do not propose trades.
