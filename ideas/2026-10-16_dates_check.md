# Results-date check for open positions | 2026-10-16

Purpose: Risk conditions in reviews/2026-10-12_risk.md (CCI) and reviews/2026-10-13_risk.md (FANG/XOP) require the results date to be confirmed by a company or SEC source.

## SEC (scripts/sec.py, retrieved 2026-10-16)
- CCI: latest 8-K is 2026-09-14 (items 5.02, 7.01, 9.01). No results date in it.
- FANG: latest 8-K is 2026-10-08 (item 2.02, Q3 realized prices and share counts). No results date in it.
- So the SEC alone does not confirm either date.

## Company announcements (WebSearch, snippet only; WebFetch does not work in this environment)
- CCI: Crown Castle press release of 2026-09-30, "Crown Castle Announces Third Quarter 2026 Earnings Conference Call Details". Results after the close on Wed 2026-10-21, call 4:45 p.m. ET. Also listed on the company IR events page.
  - https://www.globenewswire.com/news-release/2026/09/30/3372471/7657/en/crown-castle-announces-third-quarter-2026-earnings-conference-call-details.html | retrieved 2026-10-16 | snippet only
  - https://investor.crowncastle.com/events/event-details/q3-2026-crown-castle-earnings-conference-call | retrieved 2026-10-16 | snippet only
- FANG: Diamondback press release of 2026-09-30, "Diamondback Energy, Inc. Schedules Third Quarter 2026 Conference Call for November 3, 2026". Results after the close on Mon 2026-11-02, call Tue 2026-11-03 at 8:00 a.m. CT.
  - https://ca.finance.yahoo.com/news/diamondback-energy-inc-schedules-third-140000757.html | retrieved 2026-10-16 | snippet only
  - https://www.stocktitan.net/news/FANG/diamondback-energy-inc-schedules-third-quarter-2026-conference-call-56gsdwu2mm1m.html | retrieved 2026-10-16 | snippet only

## Effect on Risk conditions
- CCI: date confirmed by company release (snippet only). The 2026-10-20 forced exit does not trigger. Stop stays 85.00. First session that reacts to the print: 2026-10-22.
- FANG/XOP: date confirmed by company release (snippet only). The 2026-10-30 forced exit does not trigger. First session that reacts: 2026-11-03. Planned exit at the 2026-11-04 close is unchanged.
- Caveat: both confirmations are from search snippets of the company press releases, not the full page or an SEC filing. If the user wants SEC-grade confirmation, recheck sec.py for an 8-K closer to each date.
