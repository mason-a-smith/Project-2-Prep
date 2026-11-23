"""Compare preserved Lab 15 adjusted-price vintage with a fresh Yahoo vintage.

Run: uv run --with pandas --with yfinance python audit_project2_funds.py
Does not overwrite the Lab 15 archive or pretend Yahoo supports ALFRED vintages.
"""
from datetime import datetime, timezone
from pathlib import Path
import json
import pandas as pd
import yfinance as yf

ROOT = Path(__file__).resolve().parent
LAB15 = ROOT.parent / "lab 15"
meta = json.loads((LAB15 / "data_sources.json").read_text())
old = pd.read_csv(LAB15 / "prices.csv", index_col=0, parse_dates=True)
rows = []
for sid in ("SGOV", "VGIT", "VCIT", "ACWI"):
    try:
        fresh = yf.download(sid, start=meta["request_start_inclusive"],
                            end=meta["request_end_exclusive"], auto_adjust=False,
                            actions=True, progress=False, threads=False)
        if isinstance(fresh.columns, pd.MultiIndex):
            fresh.columns = fresh.columns.get_level_values(0)
        if fresh.empty:
            raise ValueError("No Yahoo observations returned")
        fresh.to_csv(ROOT / f"{sid}_daily_current.csv")
        adj = fresh["Adj Close"].dropna()
        adj.index = pd.to_datetime(adj.index).tz_localize(None)
        sampled = adj.groupby(adj.index.to_period("M")).tail(1)
        shared = old.index.intersection(sampled.index)
        if len(shared) != len(old):
            raise ValueError(f"Only {len(shared)} of {len(old)} archived dates matched")
        before, after = old.loc[shared, sid], sampled.loc[shared]
        price_diff = (after - before).abs()
        return_diff = (after.pct_change(fill_method=None) - before.pct_change(fill_method=None)).abs().dropna()
        rows.append({"Series": sid, "Shared month-end dates": len(shared),
                     "Changed adjusted levels (> $0.000001)": int((price_diff > 1e-6).sum()),
                     "Max adjusted level difference ($)": float(price_diff.max()),
                     "Changed monthly returns (> 0.000001)": int((return_diff > 1e-6).sum()),
                     "Max return difference (percentage points)": float(return_diff.max() * 100),
                     "Last measured date": shared[-1].date().isoformat(),
                     "Archived last adjusted price": float(before.iloc[-1]),
                     "Current last adjusted price": float(after.iloc[-1])})
    except Exception as exc:
        rows.append({"Series": sid, "Error": str(exc)})
stamp = datetime.now(timezone.utc).isoformat()
results = pd.DataFrame(rows)
results.to_csv(ROOT / "fund_vintage_comparison.csv", index=False)
fence = "`" * 3
report = ("# Project 2 fund vintage audit\n\n"
          f"Archived download: {meta['downloaded_at_utc']}. Fresh audit completed: {stamp}.\n\n"
          "Same measured window: September 2021–September 2026. This compares two actual download vintages, not reconstructed September 30 availability. Yahoo has no ALFRED-style historical-vintage endpoint used here.\n\n"
          f"{fence}text\n{results.to_string(index=False)}\n{fence}\n\n"
          "Return tolerance is 0.000001 in decimal return (0.0001 percentage point); level tolerance is $0.000001 to avoid counting CSV rounding noise. Adjusted-level changes do not necessarily change returns: a common multiplicative adjustment cancels in the return ratio. A zero count across these two downloads does not prove zero revisions over the entire history.\n")
(ROOT / "fund_vintage_audit.md").write_text(report, encoding="utf-8")
print(report)
