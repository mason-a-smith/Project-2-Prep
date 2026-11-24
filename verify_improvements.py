"""Independent financial audit and nondefault-input UI regressions."""
from copy import deepcopy
from datetime import datetime, timezone
from itertools import product
from pathlib import Path
import hashlib
import json
import math
import numpy as np
import pandas as pd
from streamlit.testing.v1 import AppTest
import portfolio as p
import audit_controls as archived
import current_rules as rules
import reconciliation as rec

R = Path(__file__).resolve().parent
frozen = ['portfolio.py','audit_controls.py','prices.csv','data_sources.json',
          'docs/locked-input.json','docs/locked-commit.json','outputs/locked-result.json']
def hashes():
    return {n:hashlib.sha256((R/n).read_bytes()).hexdigest() for n in frozen}
before = hashes()
prices = pd.read_csv(R/'prices.csv',index_col=0)
monthly = prices.to_numpy()[1:]/prices.to_numpy()[:-1]-1
means, covariance = monthly.mean(axis=0)*12, np.cov(monthly,rowvar=False,ddof=1)*12
vols = np.sqrt(np.diag(covariance))
assets,corr = p.estimate_from_csv(R/'prices.csv')
for a in assets:
    a['reserve_eligible'] = a['name']=='SGOV'
np.testing.assert_allclose([a['return'] for a in assets], means, atol=1e-12,rtol=0)
np.testing.assert_allclose(p.covariance_matrix(assets,corr),covariance,atol=1e-12,rtol=0)
equal = np.full(4,.25)
inverse = (1/vols)/(1/vols).sum()
np.testing.assert_allclose(p.equal_weights(assets),equal,atol=1e-12,rtol=0)
np.testing.assert_allclose(p.inverse_volatility_weights(assets),inverse,atol=1e-12,rtol=0)
fees = np.array([.0009,.0003,.0003,.0032])
# Independent grid construction: enumerate first three integer sleeves, derive fourth.
grid = np.array([(a,b,c,20-a-b-c) for a,b,c in product(range(21),repeat=3) if a+b+c<=20])/20
assert len(grid)==1771
def independent_best(mu,cov,minimum=.03,cap=.065):
    keep = (grid@mu>=.065-1e-12)&(grid[:,0]>=minimum-1e-12)
    if not keep.any():
        return None
    candidates = grid[keep]
    variance = np.sum((candidates@cov)*candidates,axis=1)
    i = int(variance.argmin())
    return candidates[i] if math.sqrt(variance[i])<=cap+1e-12 else None

saved = json.loads((R/'outputs/results.json').read_text())
verified = {}
for name,s in saved['scenarios'].items():
    recent = '36 months' in name
    data = monthly[-36:] if recent else monthly
    mu = data.mean(axis=0)*12
    cov = np.cov(data,rowvar=False,ddof=1)*12
    if name in ('Fixed baseline under stress','Reoptimized stress'):
        mu = mu.copy(); mu[3]-=.01
    if 'fee stress' in name:
        mu = mu-fees
    if 'transaction cost stress' in name:
        mu = mu-.0025
    w = np.asarray(s['weights'])
    ret,vol,reserve = float(w@mu),float(np.sqrt(w@cov@w)),float(w[0])
    np.testing.assert_allclose([s['return'],s['volatility'],s['reserve_weight']],
                               [ret,vol,reserve],atol=1e-12,rtol=0)
    current = rules.saved_verdict(name,s)
    cap = .05 if name=='Fixed baseline at 5% risk ceiling' else .065
    expected = ret>=.065-1e-12 and vol<=cap+1e-12 and reserve>=.03-1e-12
    assert current['feasible']==expected and not current['live_capital_authorized']
    if name in ('Constrained baseline','Reoptimized stress','Reoptimized fee stress',
                'Reoptimized transaction cost stress','Last 36 months'):
        np.testing.assert_allclose(w,independent_best(mu,cov),atol=1e-12,rtol=0)
    verified[name] = {'return':ret,'volatility':vol,'reserve':reserve,
                      'limits':current['limits'],'feasible':current['feasible'],
                      'failed_rules':current['failed_rules']}
assert independent_best(means,covariance,cap=.05) is None
assert independent_best(means,covariance,minimum=.70) is None
np.testing.assert_allclose(saved['scenarios']['Constrained baseline']['weights'],[.65,0,0,.35])
np.testing.assert_allclose(saved['scenarios']['Last 36 months']['weights'],[.85,0,0,.15])
np.testing.assert_allclose(np.array(saved['scenarios']['Constrained baseline']['weights'])@fees*10000,17.05)
np.testing.assert_allclose(.25*.01,.0025)
np.testing.assert_allclose((1.025*1.04)-1,.066)
assert 4*750_000 == 3_000_000 and 28*750_000 == 21_000_000
signal = archived.signal()
np.testing.assert_allclose(list(signal['simple_returns'].values()),monthly[-1],atol=1e-12,rtol=0)
assert not archived.signal('2026-09-30T00:00:00Z')['available']
actual = rules.evaluate([.65,0,0,.35],assets,corr,.07,.10,.05)
assert actual['labels']['return']=='Estimated annual return >= 7%'
assert actual['labels']['reserve']=='Reserve-eligible weight >= 10%'
assert actual['labels']['risk']=='Annual sample volatility <= 5%'
assert actual['checks']['return'] is False and actual['checks']['risk'] is False
for settings in [(float('nan'),.03,.065),(.065,-.01,.065),(.065,.03,-.1)]:
    try:
        rules.search(assets,corr,*settings)
    except ValueError:
        pass
    else:
        raise AssertionError('Invalid rule inputs admitted')
bad = deepcopy(corr)
bad[0][1]=bad[1][0]=1
bad[0][2]=bad[2][0]=1
bad[1][2]=bad[2][1]=-1
try:
    rules.search(assets,bad)
except ValueError:
    pass
else:
    raise AssertionError('Indefinite covariance admitted')

app = AppTest.from_file(str(R/'app.py'),default_timeout=60).run()
assert not app.exception,app.exception
dashboard = next(d.value for d in app.dataframe if 'Failed rules' in d.value.columns)
assert 'volatility <= 5%' in dashboard.loc[dashboard.Scenario=='Fixed baseline at 5% risk ceiling','Failed rules'].iloc[0]
assert (dashboard['Live capital authorized']=='No').all()
assert (dashboard['Original mandate fully verified']=='NOT TESTED').all()
assert any('seven years' in c.value for c in app.caption)
assert any('Historical maximum month-end drawdown'==x.label for x in app.metric)
app.radio[0].set_value('Interactive portfolio model').run()
assert not app.exception,app.exception
def number(label,value):
    next(x for x in app.number_input if x.label==label).set_value(value).run()
    assert not app.exception,app.exception
number('Expected return objective (%)',7)
number('Reserve minimum (%)',10)
number('Annual volatility ceiling (%)',8)
comparison = next(d.value for d in app.dataframe if 'Portfolio' in d.value.columns)
assert comparison['Selected limits'].str.contains('return >= 7%',regex=False).all()
assert comparison['Selected limits'].str.contains('weight >= 10%',regex=False).all()
assert comparison['Selected limits'].str.contains('volatility <= 8%',regex=False).all()
cost = next(d.value for d in app.dataframe if 'Stressed return (%)' in d.value.columns)
assert cost['Selected limits'].str.contains('volatility <= 8%',regex=False).all()
number('Annual volatility ceiling (%)',5)
assert any('no mix meets the objective' in x.value for x in app.warning)
number('Expected return objective (%)',6.5)
number('Reserve minimum (%)',3)
number('Annual volatility ceiling (%)',6.5)
next(x for x in app.checkbox if x.label=='Use last 36 months').check().run()
assert app.table[0].value.iloc[-1]['Weight (%)']=='15.00'
next(x for x in app.selectbox if x.label=='Dataset (when no upload)').select('Meridian training').run()
assert not app.exception,app.exception
assert any('no price path for training' in x.value for x in app.info)
for section in ['Mandate reconciliation','Data & timing','Company research & labs','Validation']:
    app.radio[0].set_value(section).run()
    assert not app.exception,(section,app.exception)
    if section=='Mandate reconciliation':
        table = app.dataframe[0].value
        assert set(table.loc[table.Rule.str.startswith('Pilot'),'Authority'])=={'AI-assisted provisional pilot'}
assert hashes()==before
h = rec.history(prices,saved['scenarios']['Constrained baseline']['weights'])
report = {'verified_at_utc':datetime.now(timezone.utc).isoformat(),'status':'PASS',
          'scenario_count':len(verified),'independent_grid_points':len(grid),'scenarios':verified,
          'checks':['Independent means/covariance/baselines','All saved financial results recomputed',
                    'Independent exhaustive grid minima and infeasibility','Expenses, payout arithmetic and real compounding',
                    'Signal formula and availability','Nondefault rule labels, fee labels, window and cap interactions',
                    'All six sections and training losses unavailable','Frozen artifacts unchanged'],
          'baseline_historical':{k:h[k] for k in ('max_drawdown','worst_calendar','worst_12_months')},
          'frozen_sha256':before,'scope':'Assistant-run implementation audit; not partner review or investment authorization'}
(R/'outputs/improvements-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k not in ('scenarios','frozen_sha256')},indent=2))
