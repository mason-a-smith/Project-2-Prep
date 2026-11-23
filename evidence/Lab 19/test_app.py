"""Isolated Streamlit integration test; synthetic facts never enter results/."""
import json
import shutil
import sys
import tempfile
from pathlib import Path
from streamlit.testing.v1 import AppTest
import panel
from test_panel import Checks

base = Path(__file__).resolve().parent
with tempfile.TemporaryDirectory() as tmp:
    target = Path(tmp)
    shutil.copy(base / 'app.py', target / 'app.py')
    shutil.copy(base / 'panel.py', target / 'panel.py')
    shutil.copytree(base / 'buffett-sec', target / 'buffett-sec')
    fixture = Checks()
    fixture.setUp()
    result = panel.enrich(dict(ticker='COST', company='SYNTHETIC UI TEST ONLY', rows=fixture.rows, checks=panel.sec.checks(fixture.rows)))
    panel.save(result, target / 'results')
    folder = target / 'results/COST'
    for filename in ['memo.md', 'cathie_memo.md', 'burry_memo.md']:
        (folder / filename).write_text('AI simulation. Verdict: watch. Evidence requires further research.', encoding='utf-8')
    app = AppTest.from_file(str(target / 'app.py')).run()
    assert not app.exception, app.exception
    assert len(app.columns) == 3
    assert len(app.table) == 2
    for label in ['Buffett memo and verdict', 'Cathie Wood memo and verdict', 'Burry memo and verdict']:
        editor = next(x for x in app.text_area if x.label == label)
        editor.set_value('Unsupported 987654321.123%').run()
        assert any('Unprinted-number flag' in error.value for error in app.error)
        next(x for x in app.text_area if x.label == label).set_value('AI simulation. Verdict: watch.').run()
    app.selectbox[0].set_value(.05).run()
    assert not app.exception
    assert any('5%' in str(table.value) for table in app.table)
print('PASS: isolated panel table, side-by-side memos, threshold probe and all memo flags.')
