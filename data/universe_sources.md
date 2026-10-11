# Universe sources

- data/sp500_constituents.csv: S&P 500 constituents with GICS sector and SEC CIK.
  Source: https://raw.githubusercontent.com/datasets/s-and-p-500-companies/main/data/constituents.csv
  Retrieved: 2026-10-11. Third-party mirror, not S&P itself. Membership may lag index changes.
  Refresh: python3 scripts/screen.py --refresh-universe
- data/etfs.csv: curated list of liquid US-listed ETFs (broad, sector, rates, credit, commodities,
  international). Hand-picked, not exhaustive. Edit to add or remove.
