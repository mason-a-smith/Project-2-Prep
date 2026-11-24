"""Verify the real user-supplied locked record without rerunning/rewriting it."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import tempfile
import shutil
import numpy as np
import pandas as pd
from streamlit.testing.v1 import AppTest
from mason_record import load_record

R=Path(__file__).resolve().parent
names=['docs/mason-locked-prediction.md','docs/mason-locked-input.json','mason_locked_run.py',
       'docs/mason-locked-commit.json','docs/mason-locked-result-receipt.json','outputs/mason-locked-result.json',
       'outputs/committee_snapshot.json','integrity-manifest.json']
before={n:hashlib.sha256((R/n).read_bytes()).hexdigest() for n in names}
result=load_record(R)
commit=datetime.fromisoformat(result['pre_run_commit']['committed_at_utc'].replace('Z','+00:00'))
run=datetime.fromisoformat(result['run_at_utc'])
assert commit<run
assert result['original']['weights']==[.65,0,0,.35]
assert result['revised']['weights']==[.55,.10,.10,.25]
assert all(result['prediction_outcomes'].values())
assert not result['revised']['feasible'] and not result['live_capital_authorized']
prices=pd.read_csv(R/'prices.csv',index_col=0).to_numpy()
returns=prices[1:]/prices[:-1]-1
means=returns.mean(axis=0)
# Independent covariance formula: centered cross-products / (n-1), not engine construction.
centered=returns-means
cov=(centered.T@centered)/(len(returns)-1)*12
for key in ['original','revised']:
    w=np.array(result[key]['weights'])
    np.testing.assert_allclose(result[key]['return'],sum(w[i]*means[i]*12 for i in range(4)),atol=1e-12,rtol=0)
    variance=sum(w[i]*w[j]*cov[i,j] for i in range(4) for j in range(4))
    np.testing.assert_allclose(result[key]['volatility'],np.sqrt(variance),atol=1e-12,rtol=0)
np.testing.assert_allclose(result['revised']['return'],.051133790852839145,atol=1e-12,rtol=0)
np.testing.assert_allclose(result['revised']['volatility'],.04795115728508332,atol=1e-12,rtol=0)
assert result['revised']['checks']=={'fully_invested':True,'long_only':True,'return':False,'reserve':True,'risk':True}
app=AppTest.from_file(str(R/'app.py'),default_timeout=60).run()
assert not app.exception and not app.error,(app.exception,app.error)
for section in ['Committee dashboard','Validation']:
    app.radio[0].set_value(section).run()
    assert not app.exception and not app.error,(app.exception,app.error)
    table=next(d.value for d in app.dataframe if 'Allocation' in d.value.columns)
    revised=table.iloc[1]
    assert revised['Expected annual return']=='5.1134%'
    assert revised['Annualized volatility']=='4.7951%'
    assert revised['Numerical pilot verdict']=='FAIL'
    assert any('Mason submission summary' in x.label for x in app.get('download_button'))
# Corruption tests in a copy leave all submitted evidence untouched.
target=Path(tempfile.mkdtemp(prefix='mason-locked-verify-'))/'Project2'
shutil.copytree(R,target,ignore=shutil.ignore_patterns('.venv','__pycache__','.git'))
for name in ['docs/mason-locked-prediction.md','docs/mason-locked-input.json','outputs/mason-locked-result.json']:
    f=target/name; original=f.read_bytes(); f.write_bytes(original+b'\n')
    try:load_record(target)
    except ValueError:pass
    else:raise AssertionError('Changed locked record/result admitted: '+name)
    f.write_bytes(original)
after={n:hashlib.sha256((R/n).read_bytes()).hexdigest() for n in names}
assert before==after
report={'status':'PASS','verified_at_utc':datetime.now(timezone.utc).isoformat(),
        'checks':['Pre-run commit timestamp precedes recorded execution','User weights and prediction preserved',
                  'Independent centered-cross-product covariance and scalar return calculations',
                  'All actual rule verdicts and prediction comparisons','App recalculation visible in dashboard and Validation',
                  'Changed prediction/specification/result rejected','No submitted or frozen evidence rewritten'],
        'source_sha256':before,'scope':'Assistant-run verification of user-submitted prediction and actual model run; AI-off authorship self-reported, not independently verified; no partner cold run'}
(R/'outputs/mason-locked-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':report['status'],'pre_run_commit':result['pre_run_commit']['commit_sha'],
                  'revised_return':result['revised']['return'],'revised_volatility':result['revised']['volatility']},indent=2))
