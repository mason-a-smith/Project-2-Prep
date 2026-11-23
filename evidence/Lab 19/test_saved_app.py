"""Verify saved live company results render with complete memos."""
from pathlib import Path
from streamlit.testing.v1 import AppTest

app = AppTest.from_file(str(Path(__file__).with_name('app.py'))).run()
for ticker in ['COST', 'AAPL']:
    app.text_input[0].set_value(ticker).run()
    assert not app.exception, app.exception
    assert len(app.table) == 2
    assert not app.error, app.error
    memos = [x for x in app.text_area if 'memo and verdict' in x.label]
    assert len(memos) == 3 and all('verdict:' in x.value.lower() for x in memos)
    print(f'PASS: {ticker} live saved panel, three verdicts and memos, numeric flag clear.')
