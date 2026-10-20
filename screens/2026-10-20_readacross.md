# Peer read-across list 2026-10-20 (on demand, user asked for a new idea)

Method: universe companies with an Item 2.02 8-K filed 2026-10-13 to 2026-10-19 (SEC daily index via scripts/guidance_gap.py helpers), 2-day price reaction vs SPY from Yahoo (full table: screens/2026-10-20_reporters.csv). For the largest reactions, same-industry peers in the universe that have not reported yet. Built because the guidance-gap pass (screens/2026-10-20_preprint_gaps.md, 164 names reporting 10-22 to 11-06) found only extraction errors or names already reviewed.

| driver (filed, 2d excess vs SPY) | industry | peers to test |
|---|---|---|
| UNH (10-13, +5.6%) | Managed Health Care | ELV, CNC, HUM, CI, CVS |
| CLF (10-19, +15.9%) | Steel | NUE, STLD, RS |
| DPZ (10-13, -3.7%) | Restaurants | YUM, MCD, CMG, WING, TXRH, CAVA |
| MRSH (10-15, +6.4%) | Insurance Brokers | AON, AJG, WTW, BRO |
| PGR (10-14, -3.3%) | P&C Insurance | ALL, CB, HIG, CINF |
| ACI (10-13, +5.4%) | Grocery | SFM, KR |

Rule for a card: the driver's filing states an industry-level number (cost trend, pricing, volumes, comps, loss trend) that applies to the peer, the peer prints inside the run, and the peer's consensus has not moved to reflect it (Yahoo 7d/30d EPS trend).
