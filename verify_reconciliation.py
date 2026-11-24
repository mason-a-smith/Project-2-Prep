"""Known-answer calculations, UI interactions and immutable-evidence checks."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import numpy as np
import pandas as pd
from streamlit.testing.v1 import AppTest
import reconciliation as m

R = Path(__file__).resolve().parent
immutable = ['portfolio.py','audit_controls.py','prices.csv','data_sources.json',
             'docs/locked-input.json','docs/locked-commit.json','outputs/locked-result.json',
             'evidence/Lab 13/Lab13.md']
before = {n:hashlib.sha256((R/n).read_bytes()).hexdigest() for n in immutable}
# First loss must count against the initial peak; recovery is not a new loss.
dates = pd.date_range('2020-12-31', periods=13, freq='ME')
values = [100,80,100]+[100]*10
toy = pd.DataFrame({'A':values},index=dates)
h = m.history(toy,[1.])
np.testing.assert_allclose(h['max_drawdown'], -.20, atol=1e-12)
np.testing.assert_allclose(h['worst_month'], -.20, atol=1e-12)
np.testing.assert_allclose(h['calendar']['return'], [0], atol=1e-12)
np.testing.assert_allclose(h['worst_12_months'], 0, atol=1e-12)
assert len(h['calendar']) == 1 and h['calendar'].year.iloc[0] == 2021
assert m.history(toy.iloc[:-1],[1.])['calendar'].empty
# Annual reset after December: doubled A creates 2/3 weight, one-way trade 1/6.
dates2 = pd.date_range('2020-12-31',periods=14,freq='ME')
a = [100]*12+[200,100]
toy2 = pd.DataFrame({'A':a,'B':[100]*14},index=dates2)
annual = m.history(toy2,[.5,.5])
hold = m.history(toy2,[.5,.5],'buy and hold')
np.testing.assert_allclose(annual['turnover'].turnover, [1/6], atol=1e-12)
np.testing.assert_allclose(annual['wealth'].iloc[-1],1.125,atol=1e-12)
np.testing.assert_allclose(hold['wealth'].iloc[-1],1,atol=1e-12)
assert hold['turnover'].empty
assert hold['rebalance']=='buy and hold' and annual['rebalance']=='annual'
for bad in [toy.iloc[[0,2,3]],toy.assign(A=-1),toy.iloc[::-1]]:
    try:
        m.history(bad,[1.])
    except ValueError:
        pass
    else:
        raise AssertionError('Invalid price data admitted')
try:
    m.history(toy,[-1.])
except ValueError:
    pass
else:
    raise AssertionError('Invalid weights admitted')

results = json.loads((R/'outputs/results.json').read_text())
prices = pd.read_csv(R/'prices.csv',index_col=0)[m.TICKERS]
s = results['scenarios']['Constrained baseline']
h = m.history(prices,s['weights'])
frame = m.table(s['weights'],s,h)
assert len(frame) == 16
assert all(frame.loc[frame.Rule.isin(['S1 / horizon','S2','S7','S8','S9 / future']),'Status']=='NOT TESTED')
assert len(h['returns']) == 60 and len(h['rolling60']) == 1
assert h['calendar'].year.tolist()==[2022,2023,2024,2025]
# Reconcile a distinct buy-and-hold calculation directly to normalized fund prices.
direct = (prices/prices.iloc[0]).to_numpy() @ np.array(s['weights'])
np.testing.assert_allclose(m.history(prices,s['weights'],'buy and hold')['wealth'],direct,atol=1e-12)
app = AppTest.from_file(str(R/'app.py'),default_timeout=60).run()
app.radio[0].set_value('Mandate reconciliation').run()
assert not app.exception, app.exception
assert len(app.dataframe[0].value)==16
app.selectbox[0].select('Equal weight').run()
assert not app.exception,app.exception
app.selectbox[1].select('buy and hold').run()
assert not app.exception,app.exception
app.multiselect[0].set_value(['NOT TESTED']).run()
assert set(app.dataframe[0].value.Status)=={'NOT TESTED'}
app.text_input[0].set_value('S8').run()
assert app.dataframe[0].value.Rule.tolist()==['S8']
after = {n:hashlib.sha256((R/n).read_bytes()).hexdigest() for n in immutable}
assert before == after
frame.to_csv(R/'outputs/mandate-reconciliation.csv',index=False)
summary = {k:h[k] for k in ['max_drawdown','worst_month','worst_12_months','worst_calendar','cagr','annual_volatility']}
record = {'verified_at_utc':datetime.now(timezone.utc).isoformat(),'status':'PASS',
          'checks':['First-period drawdown includes initial wealth','Geometric calendar compounding and partial-year exclusion',
                    'Known annual-rebalance NAV and one-way turnover','Invalid input rejection',
                    'Independent buy-and-hold fund-level reconciliation','All S1–S10 mapped separately from pilot',
                    'All reconciliation selectors, status filter and source search','Frozen engine, data and locked evidence unchanged'],
          'baseline_annual_rebalance_diagnostic':summary,'calendar_years':h['calendar'].to_dict(orient='records'),
          'source_sha256':before}
(R/'outputs/reconciliation-verification.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
print(json.dumps(record,indent=2))
