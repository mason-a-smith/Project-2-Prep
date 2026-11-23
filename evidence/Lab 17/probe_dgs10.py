"""Check the requested last-month-end and today's vintage through app controls."""
from datetime import date, timedelta
from pathlib import Path
from streamlit.testing.v1 import AppTest

today = date.today()
month_end = today.replace(day=1) - timedelta(days=1)
app = AppTest.from_file(str(Path(__file__).with_name("asof_app.py")), default_timeout=240).run()
app.multiselect[0].set_value([])
app.text_input[0].set_value("DGS10")
for vintage in (month_end, today):
    app.date_input[1].set_value(vintage).run()
    assert not app.exception and not app.error
    assert len(app.get("vega_lite_chart")) == 1
    row = app.dataframe[0].value.iloc[0]
    print(vintage, row.to_dict())
    if today == date(2026, 10, 29):
        expected = ("2026-09-29", 5.26, 20) if vintage == month_end else ("2026-10-28", 5.05, 0)
        assert (row["Last date known then"], row["Value known then"], row["Values after last date known then"]) == expected
        assert row["Revised values on shared dates"] == 0
print("PASS: DGS10 entered through the extra-series field; both vintage settings verified.")
