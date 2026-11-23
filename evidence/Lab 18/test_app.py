"""UI probes on an isolated synthetic company, never a purported SEC result."""
import json
import shutil
import tempfile
from pathlib import Path
from streamlit.testing.v1 import AppTest
from test_engine import e, fact

BASE = Path(__file__).resolve().parent
with tempfile.TemporaryDirectory(prefix='app_test_', dir=BASE) as tmp:
    root = Path(tmp)
    shutil.copy(BASE / 'app.py', root / 'app.py')
    shutil.copytree(BASE / 'buffett-sec', root / 'buffett-sec')
    facts = {'facts': {'us-gaap': {tag[0]: {'units': {'USD': [fact(100_000_000, start=None if metric not in e.FLOW else '2023-09-04')]}} for metric, tag in e.TAGS.items()}}}
    rows = [e.year_row(facts, '2024-09-01') for _ in range(5)]
    result = dict(ticker='COST', company='SYNTHETIC UI TEST — NOT COSTCO DATA', rows=rows, checks=e.checks(rows))
    folder = root / 'results/COST'
    folder.mkdir(parents=True)
    (folder/'analysis.json').write_text(json.dumps(result))
    (folder/'memo.md').write_text('Watch it. These are synthetic inputs.')
    app = AppTest.from_file(str(root/'app.py'), default_timeout=45).run()
    assert not app.exception, app.exception
    assert len(app.dataframe) == 1
    assert len(app.table) == 1
    assert len(app.get('vega_lite_chart')) == 1
    app.text_area[0].set_value('My ROE claim is 40.0%.').run()
    assert any('40.0%' in item.value for item in app.error)
    app.text_input[0].set_value('UNKNOWN').run()
    assert any('No saved SEC results' in item.value for item in app.info)
    assert not app.exception
    print('PASS: chart, table, checks, edited-number warning, unknown ticker; isolated synthetic data only.')
