"""Verify actual-price lineage, estimates, covariance, and app windows."""
from pathlib import Path
import numpy as np
import pandas as pd
from streamlit.testing.v1 import AppTest
import portfolio as engine

ROOT = Path(__file__).resolve().parent
prices = pd.read_csv(ROOT / 'prices.csv', index_col=0, parse_dates=True)
assert len(prices) == 61 and list(prices.columns) == ['SGOV', 'VGIT', 'VCIT', 'ACWI']
for ticker in prices.columns:
    raw = pd.read_csv(ROOT / 'raw' / f'{ticker}_daily.csv', index_col=0, parse_dates=True)
    sampled = raw['Adj Close'].groupby(raw.index.to_period('M')).last()
    assert np.allclose(prices[ticker], sampled, rtol=0, atol=1e-10)
returns = prices.pct_change(fill_method=None).iloc[1:]
for recent in [False, True]:
    sleeves, correlation = engine.estimate_from_csv(ROOT / 'prices.csv', recent)
    sample = returns.tail(36) if recent else returns
    assert np.allclose([s['return'] for s in sleeves], sample.mean() * 12)
    assert np.allclose([s['volatility'] for s in sleeves], sample.std(ddof=1) * np.sqrt(12))
    assert np.allclose(correlation, sample.corr())
    assert np.allclose(engine.covariance_matrix(sleeves, correlation), sample.cov() * 12)

app = AppTest.from_file(str(ROOT / 'app.py')).run(timeout=30)
assert not app.exception, app.exception
sgov_input = next(x for x in app.number_input if 'SGOV expected return' in x.label)
assert np.isclose(sgov_input.value, returns.SGOV.mean() * 1200)
assert next(x for x in app.checkbox if x.key.endswith('_0_reserve')).value
assert not next(x for x in app.checkbox if x.key.endswith('_1_reserve')).value
next(x for x in app.checkbox if x.label == 'Use last 36 months').check().run(timeout=30)
assert not app.exception, app.exception
sgov_input = next(x for x in app.number_input if 'SGOV expected return' in x.label)
assert np.isclose(sgov_input.value, returns.SGOV.tail(36).mean() * 1200)
app.selectbox[0].select('Meridian training').run(timeout=30)
assert not app.exception, app.exception
assert app.metric[0].value == '6.51%'
print('PASS: raw Yahoo lineage, 60 returns, both estimation windows, covariance identity, local dataset default, reserve settings, app switch, Meridian isolation.')
