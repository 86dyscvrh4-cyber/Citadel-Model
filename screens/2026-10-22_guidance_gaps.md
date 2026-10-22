# Guidance vs consensus gaps, 2026-10-22

8-Ks with Item 2.02/7.01 from 2026-10-19; companies checked: 155; guidance ranges parsed: 33; flagged: 15.
Machine-extracted with regex. Verify every number against the filing before using it. Period matching is approximate:
the consensus period closest to the guide midpoint is shown (yahoo_period). Yahoo EPS basis may differ from company adjusted EPS.
Consensus: Yahoo Finance (https://finance.yahoo.com/quote/TICKER/analysis), retrieved 2026-10-22.

## Flagged (consensus outside guided range, or gap >= 2.0% from midpoint)

| symbol | filed | period | basis | guide | yahoo period | consensus (n) | gap vs mid | outside | filing |
|---|---|---|---|---|---|---|---|---|---|
| ADC | 2026-10-20 | ? | GAAP? | 4.57-4.59 | 0y | 1.92 (2) | -58.1% | YES | https://www.sec.gov/Archives/edgar/data/917251/000091725126000075/adc-20261020.htm |
| ELV | 2026-10-21 | FY | adjusted | 22.00+ | 0y | 27.53 (22) | +25.1% |  | https://www.sec.gov/Archives/edgar/data/1156039/000115603926000068/a3q2026elvearningsrelease.htm |
| CCI | 2026-10-21 | FY | GAAP? | 1.70-2.35 | 0y | 2.49 (3) | +23.0% | YES | https://www.sec.gov/Archives/edgar/data/1051470/000105147026000085/cci-20261021.htm |
| CCI | 2026-10-21 | ? | GAAP? | 1.76-2.41 | 0y | 2.49 (3) | +19.5% | YES | https://www.sec.gov/Archives/edgar/data/1051470/000105147026000085/cci-20261021.htm |
| TDY | 2026-10-21 | FY | adjusted | 21.71-21.87 | 0y | 24.77 (9) | +13.7% | YES | https://www.sec.gov/Archives/edgar/data/1094285/000109428526000055/q3-2026earningsrelease.htm |
| ELV | 2026-10-21 | ? | adjusted | 29.00+ | 0y | 27.53 (22) | -5.1% | YES | https://www.sec.gov/Archives/edgar/data/1156039/000115603926000068/a3q2026elvearningsrelease.htm |
| SON | 2026-10-21 | FY | adjusted | 5.30-5.50 | 0y | 5.63 (5) | +4.2% | YES | https://www.sec.gov/Archives/edgar/data/91767/000009176726000047/ex99q32026earningsrelease.htm |
| MCO | 2026-10-21 | FY | adjusted | 16.00-16.50 | 0y | 16.87 (24) | +3.8% | YES | https://www.sec.gov/Archives/edgar/data/1059556/000162828026066594/a3q26earningsrelease.htm |
| LUV | 2026-10-21 | FY | adjusted | 2.60-2.85 | 0y | 2.81 (23) | +3.3% |  | https://www.sec.gov/Archives/edgar/data/92380/000009238026000104/er-9302026xerdoc.htm |
| RTX | 2026-10-20 | FY | adjusted | 7.65-7.75 | 0y | 7.48 (24) | -2.8% | YES | https://www.sec.gov/Archives/edgar/data/101829/000010182926000030/a2026-10x208xkerexhibit99.htm |
| HXL | 2026-10-21 | FY | adjusted | 2.30-2.40 | 0y | 2.40 (17) | +2.3% | YES | https://www.sec.gov/Archives/edgar/data/717605/000119312526427875/hxl-20261021.htm |
| R | 2026-10-22 | FY | adjusted | 14.85-15.05 | 0y | 14.67 (11) | -1.9% | YES | https://www.sec.gov/Archives/edgar/data/85961/000008596126000023/a3q26pressreleasedocument.htm |
| WH | 2026-10-21 | ? | adjusted | 4.84-4.92 | 0y | 4.80 (18) | -1.6% | YES | https://www.sec.gov/Archives/edgar/data/1722684/000172268426000081/exhibit9912026930.htm |
| ALLE | 2026-10-22 | FY | adjusted | 9.05-9.10 | 0y | 8.97 (11) | -1.2% | YES | https://www.sec.gov/Archives/edgar/data/1579241/000157924126000032/alle-20261022.htm |
| DGX | 2026-10-22 | FY | adjusted | 11.25-11.35 | 0y | 11.20 (16) | -0.9% | YES | https://www.sec.gov/Archives/edgar/data/1022079/000102207926000097/dgx-20261022.htm |

### Guidance sentences for flagged rows

- ADC: "Guidance | AFFO per share (1)(2) | $4.57 to $4.59"
- ELV: "RAISES FULL-YEAR GUIDANCE | 3Q 2026 operating revenue of $50.4 billion, up 0.7% from 3Q 2025 | 3Q 2026 diluted EPS 1 of $6.27 and adjusted diluted EPS 2 of $6.99"
- CCI: "Full Year 2026 Outlook | per share (a) | $730 to $1,010 $1.70 to $2.35"
- CCI: "Net income (loss) (e) | 755 to 1,035 25 | Net income (loss) per share—diluted (e) | 1.76 to 2.41 0.06"
- TDY: "Raising full year 2026 GAAP diluted earnings per share outlook to $21.71 to $21.87 compared with the prior outlook of $20.73 to $20.99, and raising full year 2026 non-GAAP earnings per share outlook to $25.40 to $25.50, compared with the prior outlook of $24.4"
- ELV: "adjusted diluted EPS 2 guidance raised to at least $29.00 on continued operating momentum"
- SON: "Revised Full-Year 2026 | Net Sales: $7.20 billion to $7.40 billion | Adjusted EPS (2) : Targeting diluted earnings per share between $5.30 to $5.50"
- MCO: "MCO revenue of $2.0 billion increased 1% from the prior-year period and 3% on an organic constant currency 1 basis. | MCO’s operating margin was 44.8% and MCO’s Adjusted Operating Margin 1 was 52.6%. | Diluted EPS and Adjusted Diluted EPS 1 increased 18% and 6"
- LUV: "4.0% to 4.5% | 2026 Forecast | Adjusted EPS 1,2 | $2.60 to $2.85"
- RTX: "Adjusted sales* of $97.0 - $97.5 billion, up from $95.0 - $96.0 billion | Organic sales growth* of 10 to 11 percent, up from 8 to 9 percent | Adjusted EPS* of $7.65 - $7.75, up from $7.10 - $7.25"
- HXL: "Net cash provided by operating activities in the first nine months of 2026 was $171.1 million, compared to $105.0 million for the first nine months of 2025. Working capital was a cash use of $78.1 million for the first nine months of 2026 and a use of $63.8 mi"
- R: "Full Year 2026 Forecast | ROE (non-GAAP) raised to 18% - 19% | Comparable EPS (non-GAAP) range raised to $14.85 - $15.05"
- WH: "$740 - $745 million $735 - $745 million | Adjusted net income $363 - $369 million $355 - $365 million | Adjusted diluted EPS $4.84 - $4.92 $4.71 - $4.83"
- ALLE: "The company is raising the outlook for full-year 2026 adjusted EPS to be in the range of $9.05 to $9.10. The company is updating the outlook for full-year 2026 reported EPS and expects it to be in the range of $8.35 to $8.40. Adjustments to 2026 EPS include es"
- DGX: "Full year 2026 revenues now expected to be between $12.065 billion and $12.105 billion | Full year 2026 reported diluted EPS now expected to be between $10.21 and $10.31 | and adjusted diluted EPS expected to be between $11.25 and $11.35"

## Not flagged

- R FY guide 9.75-9.95 vs 0y consensus 14.67 (+48.9%)
- R FY guide 4.25-4.45 vs 0y consensus 14.67 (+237.2%)
- LUV FY guide 0.55-0.80 vs 0y consensus 2.81 (+316.8%)
- VMI ? guide 22.25-23.50 vs 0y consensus 23.24 (+1.6%)
- HON ? guide 8.05-8.35 vs 0y consensus 8.30 (+1.2%)
- TSCO FY guide 1.78-1.88 vs 0y consensus 1.81 (-0.9%)
- TSCO FY guide 1.90-2.00 vs +1y consensus 2.02 (+3.6%)
- ADC ? guide 4.58-4.59 vs 0y consensus 1.92 (-58.2%)
- LMT ? guide 30.35-30.75 vs 0y consensus 30.41 (-0.4%)
- DGX FY guide 10.21-10.31 vs 0y consensus 11.20 (+9.1%)
- CCI ? guide 4.54-4.66 vs 0y consensus 2.49 (-45.8%)
- MCO ? guide 16.50-17.00 vs 0y consensus 16.87 (+0.7%)
- TDY FY guide 5.68-5.83 vs 0y consensus 24.77 (+330.4%)
- NOC ? guide 29.35-29.75 vs 0y consensus 29.74 (+0.7%)
- COR FY guide 17.75-17.95 vs 0y consensus 17.88 (+0.2%)
- GM ? guide 9.72-10.72 vs 0y consensus 13.36 (+30.7%)
- GM ? guide 12.75-13.75 vs 0y consensus 13.36 (+0.8%)
- KNX Q guide 0.78-0.84 vs 0q consensus 0.82 (+1.3%)
- ABT 2026-10-21: guidance found, no Yahoo consensus
- ABT 2026-10-21: guidance found, no Yahoo consensus
- AAL 2026-10-22: no EPS guidance found
- BALL 2026-10-19: no EPS guidance found
- WRB 2026-10-19: no EPS guidance found
- CACI 2026-10-21: guidance found, no Yahoo consensus
- CBSH 2026-10-20: no EPS guidance found
- DOV 2026-10-22: no EPS guidance found
- EFX 2026-10-20: no EPS guidance found
- FITB 2026-10-19: no EPS guidance found
- FNB 2026-10-20: no EPS guidance found
- GE 2026-10-20: guidance found, no Yahoo consensus
- ALLY 2026-10-20: no EPS guidance found
- GPC 2026-10-20: guidance found, no Yahoo consensus
- GPC 2026-10-20: guidance found, no Yahoo consensus
- GPC 2026-10-20: guidance found, no Yahoo consensus
- HAL 2026-10-20: no EPS guidance found
- HAS 2026-10-20: no EPS guidance found
- HBAN 2026-10-22: no EPS guidance found
- EGP 2026-10-21: guidance found, no Yahoo consensus
- EGP 2026-10-21: guidance found, no Yahoo consensus
- EGP 2026-10-21: guidance found, no Yahoo consensus
- IBM 2026-10-21: no EPS guidance found
- KR 2026-10-20: no EPS guidance found
- MAT 2026-10-22: no EPS guidance found
- MAT 2026-10-19: no EPS guidance found
- MMM 2026-10-20: guidance found, no Yahoo consensus
- MMM 2026-10-19: no EPS guidance found
- NTRS 2026-10-21: no EPS guidance found
- NTRS 2026-10-20: no EPS guidance found
- UDR 2026-10-21: guidance found, no Yahoo consensus
- PG 2026-10-22: guidance found, no Yahoo consensus
- RLI 2026-10-21: no EPS guidance found
- RLI 2026-10-19: no EPS guidance found
- ROL 2026-10-21: no EPS guidance found
- RGLD 2026-10-20: no EPS guidance found
- MLI 2026-10-20: no EPS guidance found
- SNA 2026-10-22: no EPS guidance found
- KEY 2026-10-20: no EPS guidance found
- JEF 2026-10-20: no EPS guidance found
- JEF 2026-10-19: no EPS guidance found
- TXN 2026-10-21: no EPS guidance found
- TMO 2026-10-21: no EPS guidance found
- UAL 2026-10-20: no EPS guidance found
- UNP 2026-10-22: no EPS guidance found
- ZION 2026-10-19: no EPS guidance found
- LHX 2026-10-22: no EPS guidance found
- CSX 2026-10-21: no EPS guidance found
- DHR 2026-10-21: no EPS guidance found
- GL 2026-10-21: no EPS guidance found
- SEIC 2026-10-21: no EPS guidance found
- ONB 2026-10-21: no EPS guidance found
- LRCX 2026-10-21: no EPS guidance found
- VLY 2026-10-22: no EPS guidance found
- SF 2026-10-21: no EPS guidance found
- T 2026-10-21: no EPS guidance found
- HWC 2026-10-20: no EPS guidance found
- VICR 2026-10-20: no EPS guidance found
- NEE 2026-10-21: no EPS guidance found
- SSB 2026-10-21: no EPS guidance found
- CLF 2026-10-19: no EPS guidance found
- ALK 2026-10-20: no EPS guidance found
- PHM 2026-10-22: no EPS guidance found
- SLGN 2026-10-19: no EPS guidance found
- LSCC 2026-10-22: no EPS guidance found
- RS 2026-10-21: no EPS guidance found
- ROP 2026-10-22: no EPS guidance found
- EXE 2026-10-19: no EPS guidance found
- ELS 2026-10-21: no EPS guidance found
- CB 2026-10-20: no EPS guidance found
- DAR 2026-10-22: no EPS guidance found
- LH 2026-10-21: no EPS guidance found
- FR 2026-10-21: no EPS guidance found
- COF 2026-10-20: no EPS guidance found
- COF 2026-10-20: no EPS guidance found
- WAB 2026-10-21: no EPS guidance found
- MSM 2026-10-22: no EPS guidance found
- PEGA 2026-10-20: no EPS guidance found
- WTFC 2026-10-19: no EPS guidance found
- STLD 2026-10-20: no EPS guidance found
- LAD 2026-10-21: no EPS guidance found
- MMS 2026-10-20: no EPS guidance found
- ISRG 2026-10-20: no EPS guidance found
- NLY 2026-10-20: no EPS guidance found
- NLY 2026-10-20: no EPS guidance found
- NFLX 2026-10-20: no EPS guidance found
- URI 2026-10-21: no EPS guidance found
- EWBC 2026-10-20: no EPS guidance found
- TCBI 2026-10-21: no EPS guidance found
- CHTR 2026-10-19: no EPS guidance found
- EG 2026-10-19: no EPS guidance found
- CRM 2026-10-20: no EPS guidance found
- VC 2026-10-22: no EPS guidance found
- TTMI 2026-10-22: no EPS guidance found
- NDAQ 2026-10-22: no EPS guidance found
- PFG 2026-10-19: no EPS guidance found
- PRU 2026-10-20: no EPS guidance found
- CBRE 2026-10-22: no EPS guidance found
- CBRE 2026-10-20: no EPS guidance found
- CME 2026-10-21: no EPS guidance found
- CMCSA 2026-10-22: no EPS guidance found
- WAL 2026-10-19: no EPS guidance found
- CCK 2026-10-19: no EPS guidance found
- LVS 2026-10-21: no EPS guidance found
- TSLA 2026-10-21: no EPS guidance found
- META 2026-10-21: no EPS guidance found
- SMCI 2026-10-20: no EPS guidance found
- BX 2026-10-22: no EPS guidance found
- CDW 2026-10-19: no EPS guidance found
- MSCI 2026-10-20: no EPS guidance found
- PM 2026-10-21: no EPS guidance found
- FAF 2026-10-21: no EPS guidance found
- CHRD 2026-10-19: no EPS guidance found
- KMI 2026-10-21: no EPS guidance found
- MTDR 2026-10-21: no EPS guidance found
- HLT 2026-10-20: no EPS guidance found
- SYF 2026-10-20: no EPS guidance found
- SYF 2026-10-20: no EPS guidance found
- WFRD 2026-10-20: no EPS guidance found
- MDT 2026-10-19: no EPS guidance found
- ROIV 2026-10-21: no EPS guidance found
- MEDP 2026-10-21: no EPS guidance found
- DOW 2026-10-22: no EPS guidance found
- APO 2026-10-20: no EPS guidance found
- PNFP 2026-10-21: no EPS guidance found
