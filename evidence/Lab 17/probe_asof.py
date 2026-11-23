"""Live acceptance checks: uv run --with streamlit --with pandas --with requests python probe_asof.py"""
from datetime import date
from pathlib import Path

from streamlit.testing.v1 import AppTest


def run():
    app = AppTest.from_file(str(Path(__file__).with_name("asof_app.py")), default_timeout=240)
    app.run()
    app.date_input[1].set_value(date(2026, 10, 5)).run()
    assert not app.exception, [e.value for e in app.exception]
    assert not app.error, [e.value for e in app.error]
    rates = app.dataframe[0].value.copy()
    expected = {
        "BAA": ("2026-09-01", 6.47),
        "FEDFUNDS": ("2026-09-01", 3.75),
        "DGS10": ("2026-10-02", 5.28),
        "MORTGAGE30US": ("2026-10-01", 7.28),
    }
    for sid, (measured, value) in expected.items():
        row = rates[rates["Series"].str.endswith("/" + sid)].iloc[0]
        assert row["Last date known then"] == measured, (sid, row.to_dict())
        assert row["Value known then"] == value, (sid, row.to_dict())
    assert len(app.get("vega_lite_chart")) == 4
    app.text_input[0].set_value("PAYEMS")
    app.date_input[1].set_value(date(2025, 1, 15)).run()
    assert not app.exception, [e.value for e in app.exception]
    assert not app.error, [e.value for e in app.error]
    payroll = app.dataframe[0].value
    row = payroll[payroll["Series"].str.endswith("/PAYEMS")].iloc[0]
    assert row["Last date known then"] == "2024-12-01", row.to_dict()
    assert row["Value known then"] == 159536, row.to_dict()
    assert row["Today's value for last date known then"] < 159536, row.to_dict()
    assert row["Revised values on shared dates"] > 100, row.to_dict()
    assert len(app.get("vega_lite_chart")) == 5
    fence = "`" * 3
    output = (
        f"# Lab 17 vintage acceptance probes\n\nRun date: {date.today()}. Live FRED and ALFRED public CSV downloads.\n\n"
        "## As known on 5 October 2026\n\nAll four expected dates and values match. Four charts; no errors. Monthly observation dates use the first day of the measured month.\n\n"
        f"{fence}text\n{rates.to_string(index=False)}\n{fence}\n\n"
        "## PAYEMS as known on 15 January 2025\n\nDecember 2024 was 159,536 thousand jobs. Today's value for that same month is lower; revisions are counted only on shared observation dates. Five charts; no errors.\n\n"
        f"{fence}text\n{row.to_string()}\n{fence}\n"
    )
    Path(__file__).with_name("vintage_probe_results.md").write_text(output, encoding="utf-8")
    print(output)


if __name__ == "__main__":
    run()
