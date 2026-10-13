"""Write approved paper trades to ledger.csv. Only after the user says "approved".

Open:  python3 scripts/record_trade.py open --ticker T --direction long|short --size-pct 4
           --stop 180 --thesis "..." --catalyst "..." --catalyst-date YYYY-MM-DD
Close: python3 scripts/record_trade.py close --id 3 [--lessons "..."]

Entry and exit prices come from scripts/prices.py execution_price(): the 1-minute bar close at the
time the user asked to execute (--at), or the latest close if the market was closed. Refuses
trades that break rules.md limits or when state/HALT exists.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import book  # noqa: E402
import prices  # noqa: E402
from mark_to_market import outcome  # noqa: E402


def cmd_open(a, rules, rows):
    if (book.state_dir() / "HALT").exists():
        raise SystemExit("REFUSED: state/HALT exists (drawdown halt). No new trades.")
    if not rules["approved"] and not a.allow_draft:
        raise SystemExit("REFUSED: rules.md is still DRAFT. Approve it first.")
    if a.direction == "short" and not rules["allow_short"]:
        raise SystemExit("REFUSED: shorts not allowed by rules.md")
    entry, when, src = prices.execution_price(a.ticker, a.at)
    day = when[:10]
    row = {"direction": a.direction, "size_pct": a.size_pct, "entry": entry, "stop": a.stop}
    cap = rules["starting_capital"]
    loss = book.loss_at_stop(row, rules)
    if loss <= 0:
        raise SystemExit(f"REFUSED: stop {a.stop} is on the wrong side of entry {entry:.2f}")
    if loss > rules["max_loss_per_position_pct"] / 100 * cap + 1e-6:
        raise SystemExit(f"REFUSED: loss at stop ${loss:,.0f} exceeds {rules['max_loss_per_position_pct']}% of capital")
    name_total = a.size_pct + sum(float(r["size_pct"]) for r in rows if book.is_open(r) and r["ticker"] == a.ticker)
    if name_total > rules["max_single_name_pct"] + 1e-9:
        raise SystemExit(f"REFUSED: {a.ticker} total {name_total}% exceeds {rules['max_single_name_pct']}% cap")
    eq = book.equity_series(rows, rules) if rows else None
    equity = float(eq["equity"].iloc[-1]) if eq is not None else cap
    gross = float(eq["gross"].iloc[-1]) if eq is not None else 0.0
    if (gross + a.size_pct / 100 * cap) / equity * 100 > rules["max_gross_pct"] + 1e-9:
        raise SystemExit("REFUSED: gross exposure would exceed limit")
    new_id = max([int(r["id"]) for r in rows] + [0]) + 1
    rows.append({"id": new_id, "date": day, "ticker": a.ticker, "direction": a.direction,
                 "thesis": a.thesis, "catalyst": a.catalyst, "catalyst_date": a.catalyst_date,
                 "entry": f"{entry:.4f}", "stop": a.stop, "size_pct": a.size_pct,
                 "exit": "", "exit_date": "", "outcome": "OPEN", "lessons": ""})
    book.write_ledger(rows)
    if a.link_to:
        book.add_link(str(a.link_to), str(new_id), a.link_reason)
        print(f"LINKED id={new_id} with id={a.link_to}: exits together")
    print(f"RECORDED id={new_id} {a.ticker} {a.direction} {a.size_pct}% entry {entry:.4f} ({when}, {src}) stop {a.stop} loss_at_stop ${loss:,.0f}")


def cmd_close(a, rules, rows):
    r = next((r for r in rows if r["id"] == str(a.id)), None)
    if r is None or not book.is_open(r):
        raise SystemExit(f"no open trade with id {a.id}")
    px, when, src = prices.execution_price(r["ticker"], a.at)
    r["exit"] = f"{px:.4f}"
    r["exit_date"] = when[:10]
    pnl = book.trade_pnl(r, rules)
    r["outcome"] = outcome(pnl)
    if a.lessons:
        r["lessons"] = a.lessons
    for pid in book.read_links().get(r["id"], ()):  # linked legs exit in the same session
        p = next((x for x in rows if x["id"] == pid), None)
        if p is not None and book.is_open(p):
            ppx, pwhen, psrc = prices.execution_price(p["ticker"], a.at)
            p["exit"], p["exit_date"] = f"{ppx:.4f}", pwhen[:10]
            p["outcome"] = outcome(book.trade_pnl(p, rules))
            print(f"LINKED CLOSE id={pid} {p['ticker']} @ {ppx:.4f} ({pwhen}, {psrc}) pnl ${book.trade_pnl(p, rules):,.0f} {p['outcome']}")
    book.write_ledger(rows)
    print(f"CLOSED id={a.id} {r['ticker']} @ {px:.4f} ({when}, {src}) pnl ${pnl:,.0f} {r['outcome']}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    o = sub.add_parser("open")
    o.add_argument("--ticker", required=True, type=str.upper)
    o.add_argument("--direction", required=True, choices=["long", "short"])
    o.add_argument("--size-pct", required=True, type=float)
    o.add_argument("--stop", required=True, type=float)
    o.add_argument("--thesis", required=True)
    o.add_argument("--catalyst", required=True)
    o.add_argument("--catalyst-date", required=True)
    o.add_argument("--at", default="now", help='"now" or "YYYY-MM-DD HH:MM" ET: when the user asked to execute')
    o.add_argument("--link-to", type=int, default=None, help="id of an open trade this one must exit with")
    o.add_argument("--link-reason", default="")
    o.add_argument("--allow-draft", action="store_true", help="tests only")
    c = sub.add_parser("close")
    c.add_argument("--id", required=True, type=int)
    c.add_argument("--lessons", default="")
    c.add_argument("--at", default="now", help='"now" or "YYYY-MM-DD HH:MM" ET: when the user asked to execute')
    a = ap.parse_args()
    rules, rows = book.load_rules(), book.read_ledger()
    (cmd_open if a.cmd == "open" else cmd_close)(a, rules, rows)


if __name__ == "__main__":
    try:
        main()
    except prices.PriceError as e:
        print(f"DATA ERROR: {e}")
        sys.exit(1)
