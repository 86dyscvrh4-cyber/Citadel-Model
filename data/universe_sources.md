# Universe sources

- data/sp500_constituents.csv: S&P 500 constituents with GICS sector and SEC CIK.
  Source: https://raw.githubusercontent.com/datasets/s-and-p-500-companies/main/data/constituents.csv
  Retrieved: 2026-10-11. Third-party mirror, not S&P itself. Membership may lag index changes.
  Refresh: python3 scripts/screen.py --refresh-universe
- data/sp400_constituents.csv: S&P MidCap 400 with GICS sector/industry and SEC CIK.
  Source: SEC N-PORT filing of the iShares Core S&P Mid-Cap ETF (IJH), holdings as of 2026-06-30,
  https://www.sec.gov/Archives/edgar/data/1100663/000094040026034996/ (retrieved 2026-10-11).
  Lags the index by up to one quarter plus 60 days. Names acquired or renamed since then show as NO_PRICE_DATA.
  Refresh: python3 scripts/build_universe.py
- data/etfs.csv: curated list of liquid US-listed ETFs (broad, sector, rates, credit, commodities,
  international). Hand-picked, not exhaustive. Edit to add or remove.
