"""Corruption, leakage, known-answer and safe-stop tests; assistant-run only."""
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import numpy as np
import pandas as pd
from streamlit.testing.v1 import AppTest
import data_integrity as di
import chronological as chrono
import current_rules as rules
import portfolio as p

R = Path(__file__).resolve().parent
audit = di.verify(R)
prices = audit['prices']
frozen_before = audit['verified_hashes']
diagnostic = chrono.run(prices)
assert diagnostic['training_months']==36 and diagnostic['evaluation_months']==24
assert diagnostic['training_end']=='2024-09-30' and diagnostic['evaluation_return_start']=='2024-10-31'
assert diagnostic['constrained_evaluation'] is None
# Evaluation-only perturbation must not change ANY training estimate, weight or feasibility.
altered = prices.copy()
altered.iloc[37:] *= np.linspace(1,2,24)[:,None]
perturbed = chrono.run(altered)
assert diagnostic['training_results']==perturbed['training_results']
assert diagnostic['status']==perturbed['status']
assert diagnostic['evaluation_results']!=perturbed['evaluation_results']
assert not set(prices.index[1:37]) & set(prices.index[37:])
# Independently check first-36 statistics; demonstrate infeasibility by a separate grid.
monthly = prices.to_numpy()[1:]/prices.to_numpy()[:-1]-1
training = monthly[:36]
mu,cov = training.mean(axis=0)*12,np.cov(training,rowvar=False,ddof=1)*12
inv = (1/np.sqrt(np.diag(cov))); inv/=inv.sum()
np.testing.assert_allclose(diagnostic['training_results']['Inverse volatility']['weights'],inv,atol=1e-12)
feasible_count = 0
for a in range(21):
    for b in range(21-a):
        for c in range(21-a-b):
            w = np.array([a,b,c,20-a-b-c])/20
            feasible_count += bool(w[0]>=.03-1e-12 and w@mu>=.065-1e-12 and np.sqrt(w@cov@w)<=.065+1e-12)
assert feasible_count==0

# Highest-risk formulas: hand-computable two-asset covariance and cost units.
assets=[{'name':'A','return':.04,'volatility':.1,'reserve_eligible':True},
        {'name':'B','return':.1,'volatility':.2,'reserve_eligible':False}]
known = rules.evaluate([.6,.4],assets,[[1,.5],[.5,1]],.06,.03,.13)
np.testing.assert_allclose(known['return'],.064,atol=1e-12)
np.testing.assert_allclose(known['volatility'],math.sqrt(.0148),atol=1e-12)
np.testing.assert_allclose(known['reserve_weight'],.6,atol=1e-12)
np.testing.assert_allclose(.65*.0009+.35*.0032,.001705,atol=1e-12)
np.testing.assert_allclose(.35*.01,.0035,atol=1e-12)
np.testing.assert_allclose(.25*.01*10000,25,atol=1e-12)
for w in ([.5,.4],[1.1,-.1],[float('nan'),1]):
    try: rules.evaluate(w,assets,[[1,.5],[.5,1]])
    except ValueError: pass
    else: raise AssertionError('Invalid weights not stopped')
bad = deepcopy(assets);bad[0]['reserve_eligible']='yes'
try: rules.search(bad,[[1,.5],[.5,1]])
except ValueError: pass
else: raise AssertionError('Ambiguous eligibility not stopped')
good = 'date,A,B,C\n2024-01-31,100,100,100\n2024-02-29,101,99,102\n2024-03-31,103,101,104\n'
di.parse_prices(good)
invalid = [good.replace('A,B,C','A,A,C'),good.replace('101,99,102','nan,99,102'),
           good.replace('101,99,102','0,99,102'),good.replace('2024-02-29','2024-04-30'),
           good.replace('2024-02-29','2024-01-31'),good.replace('101,99,102','inf,99,102')]
for content in invalid:
    try: di.parse_prices(content)
    except (ValueError,TypeError): pass
    else: raise AssertionError('Corrupted CSV admitted')
for cutoff in ['2026-10-22T21:27:42.703541Z','2026-11-17']:
    try: di.verify(R,cutoff)
    except ValueError: pass
    else: raise AssertionError('Invalid decision timestamp admitted')

target = Path(tempfile.mkdtemp(prefix='project2-integrity-'))/'Project2'
shutil.copytree(R,target,ignore=shutil.ignore_patterns('.venv','__pycache__','.git'))
corruption_cases = ['prices.csv','data_sources.json','evidence/lab 15/raw/ACWI_daily.csv',
                    'outputs/committee_snapshot.json','integrity-manifest.json']
for name in corruption_cases:
    path = target/name
    original = path.read_bytes()
    path.write_bytes(original+b'\n')
    try: di.verify(target)
    except ValueError: pass
    else: raise AssertionError(f'Corrupt {name} admitted')
    path.write_bytes(original)
assert di.load_committee(target)['scenarios']['Constrained baseline']['weights']==[.65,0,0,.35]
# A semantically wrong but valid-JSON committee result also stops by sealed hash.
path = target/'outputs/committee_snapshot.json'; original = path.read_bytes()
changed = json.loads(original); changed['scenarios']['Constrained baseline']['return']=.99
path.write_text(json.dumps(changed))
try: di.load_committee(target)
except ValueError: pass
else: raise AssertionError('Altered committee numbers admitted')
path.write_bytes(original)
# Console run cannot overwrite results after the input gate fails.
output_before = (target/'outputs/results.json').read_bytes()
path = target/'prices.csv'; original=path.read_bytes(); path.write_bytes(original+b'\n')
console = subprocess.run([sys.executable,str(target/'run.py')],cwd=target,capture_output=True,text=True)
assert console.returncode!=0 and 'STOP' in console.stderr
assert (target/'outputs/results.json').read_bytes()==output_before
app = AppTest.from_file(str(target/'app.py'),default_timeout=60).run()
assert not app.exception and app.error
assert not any('Baseline return'==x.label for x in app.metric)
path.write_bytes(original)
app.run(); assert not app.exception,app.exception
app.radio[0].set_value('Validation').run()
assert not app.exception,app.exception
assert any('full dataset was previously examined' in x.value for x in app.caption)
assert any('AI-off' in x.label for x in app.get('download_button'))
assert (R/'templates/AI_OFF_LOCKED_CHANGED_INPUT.md').read_text().count('UNFILLED')==1
assert di.verify(R)['verified_hashes']==frozen_before
report = {'verified_at_utc':datetime.now(timezone.utc).isoformat(),'status':'PASS',
          'checks':['All sealed source/output hashes','Four raw-to-monthly reconstructions',
                    'Recorded timestamp gate','Malformed CSV and invalid weights/eligibility rejected',
                    'Corrupted manifest/raw/source/snapshot stops','Console failed gate writes no results',
                    'Dashboard corrupted-source safe stop','Known-answer covariance/return/reserves/cost units',
                    'Independent 36-month grid infeasibility','Evaluation perturbation leaves training selection unchanged',
                    '36/24 disjoint returns','Blank templates and retrospective disclosure visible'],
          'scope':'Assistant-run tests; not AI-off prediction, partner cold run, independent review or untouched holdout',
          'integrity':{k:v for k,v in audit.items() if k!='prices'},'chronological':diagnostic}
(R/'outputs/validation-controls.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':'PASS','checks':len(report['checks']),'chronological_status':diagnostic['status']},indent=2))
