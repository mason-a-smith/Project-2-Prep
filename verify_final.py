"""Financial behavior and interactive app verification."""
from pathlib import Path
import json
import subprocess
import sys
from streamlit.testing.v1 import AppTest
import portfolio as p
import audit_controls as c
R = Path(__file__).resolve().parent
subprocess.run([sys.executable, str(R/'run.py')], check=True, capture_output=True)
data = json.loads((R/'outputs/results.json').read_text())
s = data['scenarios']
assert s['Constrained baseline']['mandate_pass']
assert not s['Equal weight']['mandate_pass'] and not s['Inverse volatility']['mandate_pass']
assert not s['Fixed baseline transaction cost stress']['mandate_pass']
assert abs(s['Constrained baseline']['return'] - s['Fixed baseline transaction cost stress']['return'] - .0025) < 1e-12
assert not s['Fixed baseline at 5% risk ceiling']['mandate_pass']
assets, corr = p.estimate_from_csv(R/'prices.csv')
for a in assets:
    a['reserve_eligible'] = a['name'] == 'SGOV'
assert c.search(assets, corr, ceiling=.05) is None
assert not c.signal('2026-09-30T00:00:00Z')['available']
app = AppTest.from_file(str(R/'app.py'), default_timeout=60).run()
assert not app.exception, app.exception
table = next(d.value for d in app.dataframe if 'Failed rules' in d.value.columns)
assert 'Estimated annual return >= 6.5%' in table.loc[table.Scenario == 'Equal weight','Failed rules'].iloc[0]
for section in ['Mandate reconciliation','Interactive portfolio model','Data & timing','Company research & labs','Validation']:
    app.radio[0].set_value(section).run()
    assert not app.exception, (section, app.exception)
print('PASS: financial scenarios, actual-limit labels, source gate, and all six app sections.')
