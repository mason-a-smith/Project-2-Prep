"""Run with: uv run --with streamlit python verify_lab15.py"""
from copy import deepcopy
from io import StringIO
from contextlib import redirect_stdout
from pathlib import Path
import numpy as np
import pandas as pd
from streamlit.testing.v1 import AppTest
import portfolio as p

capture = StringIO()
with redirect_stdout(capture):
    p.main()
original = Path('lab14.md').read_text(encoding='utf-8').split('\n# Lab 15')[0].strip()
assert capture.getvalue().strip() == original, 'Tuesday output changed'
base = p.search_portfolio(p.SLEEVES, p.CORRELATIONS)
assert base['weights'] == [0, .2, .25, .55]
assert p.search_portfolio(p.SLEEVES, p.CORRELATIONS, .2) is None
changed = deepcopy(p.SLEEVES)
changed[3]['return'] = .07
shock = p.search_portfolio(changed, p.CORRELATIONS)
assert shock['weights'] == [0, .1, .1, .8]
corr = deepcopy(p.CORRELATIONS)
corr[2][3] = corr[3][2] = .5
assert p.search_portfolio(p.SLEEVES, corr)['weights'] == [0, .4, 0, .6]

# Synthetic data validates estimation without pretending to be market prices.
rng = np.random.default_rng(15)
prices = pd.DataFrame(100 * np.exp(np.cumsum(rng.normal(.005, .03, (61, 3)), axis=0)), columns=['A', 'B', 'C'])
prices.insert(0, 'date', pd.date_range('2021-01-01', periods=61, freq='MS'))
csv = prices.to_csv(index=False)
for recent in (False, True):
    sleeves, matrix = p.estimate_from_csv(StringIO(csv), recent)
    returns = prices.iloc[:, 1:].pct_change().iloc[1:]
    if recent:
        returns = returns.tail(36)
    assert np.allclose([s['return'] for s in sleeves], returns.mean() * 12)
    assert np.allclose([s['volatility'] for s in sleeves], returns.std() * np.sqrt(12))
    assert np.allclose(matrix, returns.corr())

app = AppTest.from_file('app.py').run(timeout=30)
assert not app.exception
assert app.metric[0].value == '6.51%'
equity = next(x for x in app.number_input if 'Global equity' in x.label)
equity.set_value(7).run(timeout=30)
assert not app.exception
assert app.metric[0].value == '6.53%'
assert app.metric[-1].value == '25.00'
app.sidebar.number_input[0].set_value(20).run(timeout=30)
assert not app.exception
assert any(x.value == 'no mix meets the objective' for x in app.warning)
print('PASS: Tuesday output, three known answers, infeasible objective, CSV windows, app controls.')
