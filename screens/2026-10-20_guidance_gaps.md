# Guidance vs consensus gaps, 2026-10-20

8-Ks with Item 2.02/7.01 from 2026-10-15; companies checked: 106; guidance ranges parsed: 7; flagged: 4.
Machine-extracted with regex. Verify every number against the filing before using it. Period matching is approximate:
the consensus period closest to the guide midpoint is shown (yahoo_period). Yahoo EPS basis may differ from company adjusted EPS.
Consensus: Yahoo Finance (https://finance.yahoo.com/quote/TICKER/analysis), retrieved 2026-10-20.

## Flagged (consensus outside guided range, or gap >= 2.0% from midpoint)

| symbol | filed | period | basis | guide | yahoo period | consensus (n) | gap vs mid | outside | filing |
|---|---|---|---|---|---|---|---|---|---|
| SMTC | 2026-10-15 | Q | adjusted | 12.40-13.00 | +1q | 1.29 (15) | -89.8% | YES | https://www.sec.gov/Archives/edgar/data/88941/000008894126000041/smtc-20261015.htm |
| PLD | 2026-10-15 | ? | GAAP? | 4.40-4.55 | 0y | 3.08 (2) | -31.3% | YES | https://www.sec.gov/Archives/edgar/data/1045609/000119312526422375/pld-20261015.htm |
| RTX | 2026-10-20 | FY | adjusted | 7.65-7.75 | +1y | 7.87 (23) | +2.2% | YES | https://www.sec.gov/Archives/edgar/data/101829/000010182926000030/a2026-10x208xkerexhibit99.htm |
| NOC | 2026-10-20 | ? | adjusted | 29.35-29.75 | 0y | 28.98 (23) | -1.9% | YES | https://www.sec.gov/Archives/edgar/data/1133421/000113342126000037/noc-09302026xearningsrelea.htm |

### Guidance sentences for flagged rows

- SMTC: "Adjusted operating margin* 48% to 50% | Free cashflow as a percentage of net sales* 35% | Adjusted diluted earnings per share* $12.40 to $13.00"
- PLD: "2026 GUIDANCE | Earnings (per diluted share)** Previous Current | $4.40 to $4.55"
- RTX: "Adjusted sales* of $97.0 - $97.5 billion, up from $95.0 - $96.0 billion | Organic sales growth* of 10 to 11 percent, up from 8 to 9 percent | Adjusted EPS* of $7.65 - $7.75, up from $7.10 - $7.25"
- NOC: "$4,940 — $5,040 | Prior: $4,850 — $5,000 | MTM-adjusted EPS 1 | $29.35 — $29.75"

## Not flagged

- VMI ? guide 22.25-23.50 vs 0y consensus 22.94 (+0.3%)
- GM ? guide 9.72-10.72 vs 0y consensus 13.42 (+31.3%)
- GM ? guide 12.75-13.75 vs 0y consensus 13.42 (+1.3%)
- AXP 2026-10-15: no EPS guidance found
- BALL 2026-10-19: no EPS guidance found
- WRB 2026-10-19: no EPS guidance found
- CRS 2026-10-15: no EPS guidance found
- CMC 2026-10-15: no EPS guidance found
- EFX 2026-10-20: no EPS guidance found
- FITB 2026-10-19: no EPS guidance found
- FFIN 2026-10-16: no EPS guidance found
- USB 2026-10-15: no EPS guidance found
- MTB 2026-10-16: no EPS guidance found
- FHN 2026-10-15: no EPS guidance found
- FNB 2026-10-20: no EPS guidance found
- GE 2026-10-20: guidance found, no Yahoo consensus
- ALLY 2026-10-20: no EPS guidance found
- GPC 2026-10-20: guidance found, no Yahoo consensus
- GPC 2026-10-20: guidance found, no Yahoo consensus
- GPC 2026-10-20: guidance found, no Yahoo consensus
- HAL 2026-10-20: no EPS guidance found
- HAL 2026-10-15: no EPS guidance found
- HAS 2026-10-20: no EPS guidance found
- KMB 2026-10-15: no EPS guidance found
- KR 2026-10-20: no EPS guidance found
- MRSH 2026-10-15: no EPS guidance found
- MAT 2026-10-19: no EPS guidance found
- MMM 2026-10-20: guidance found, no Yahoo consensus
- MMM 2026-10-19: no EPS guidance found
- RLI 2026-10-19: no EPS guidance found
- TRV 2026-10-16: no EPS guidance found
- KEY 2026-10-20: no EPS guidance found
- TFC 2026-10-16: no EPS guidance found
- TFC 2026-10-16: no EPS guidance found
- JEF 2026-10-19: no EPS guidance found
- UNP 2026-10-16: no EPS guidance found
- ZION 2026-10-19: no EPS guidance found
- SCHW 2026-10-15: no EPS guidance found
- AN 2026-10-16: no EPS guidance found
- PNC 2026-10-15: no EPS guidance found
- PNC 2026-10-15: no EPS guidance found
- JBHT 2026-10-15: no EPS guidance found
- VICR 2026-10-20: no EPS guidance found
- CFG 2026-10-16: no EPS guidance found
- CLF 2026-10-19: no EPS guidance found
- SLGN 2026-10-19: no EPS guidance found
- EXE 2026-10-19: no EPS guidance found
- ALL 2026-10-15: no EPS guidance found
- CPRT 2026-10-16: no EPS guidance found
- WTFC 2026-10-19: no EPS guidance found
- MMS 2026-10-20: no EPS guidance found
- CHTR 2026-10-19: no EPS guidance found
- EG 2026-10-19: no EPS guidance found
- PFG 2026-10-19: no EPS guidance found
- PRU 2026-10-20: no EPS guidance found
- PRU 2026-10-15: no EPS guidance found
- WAL 2026-10-19: no EPS guidance found
- CCK 2026-10-19: no EPS guidance found
- RF 2026-10-16: no EPS guidance found
- IBKR 2026-10-15: no EPS guidance found
- BNY 2026-10-15: no EPS guidance found
- CDW 2026-10-19: no EPS guidance found
- MSCI 2026-10-20: no EPS guidance found
- HLNE 2026-10-15: no EPS guidance found
- CHRD 2026-10-19: no EPS guidance found
- FBIN 2026-10-15: no EPS guidance found
- VOYA 2026-10-15: no EPS guidance found
- HLT 2026-10-20: no EPS guidance found
- SYF 2026-10-20: no EPS guidance found
- SYF 2026-10-20: no EPS guidance found
- MDT 2026-10-19: no EPS guidance found
- AA 2026-10-15: no EPS guidance found
- BILL 2026-10-15: no EPS guidance found
- XOM 2026-10-16: no EPS guidance found
