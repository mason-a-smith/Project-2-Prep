"""Execute the user's locked allocation comparison only after a verified precommit."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
from data_integrity import verify,load_committee
import current_rules as rules
import portfolio as p

ROOT = Path(__file__).resolve().parent


def main():
    started = datetime.now(timezone.utc)
    path = ROOT/'docs/mason-locked-commit.json'
    if not path.exists():
        raise SystemExit('STOP: pre-run GitHub commit receipt is missing.')
    receipt = json.loads(path.read_text(encoding='utf-8'))
    committed = datetime.fromisoformat(receipt['committed_at_utc'].replace('Z','+00:00'))
    if committed.tzinfo is None or committed>=started:
        raise ValueError('STOP: pre-run commit timestamp must precede execution.')
    for name,digest in receipt['locked_sha256'].items():
        if hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=digest:
            raise ValueError('STOP: locked pre-run artifact changed: '+name)
    audit = verify(ROOT)
    spec = json.loads((ROOT/'docs/mason-locked-input.json').read_text(encoding='utf-8'))
    for name,digest in spec['frozen_sha256'].items():
        if hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=digest:
            raise ValueError('STOP: frozen input changed: '+name)
    baseline = load_committee(ROOT)['scenarios']['Constrained baseline']
    if baseline['weights']!=spec['original_weights']:
        raise ValueError('STOP: original allocation differs from locked specification.')
    assets,corr = p.estimate_from_csv(ROOT/'prices.csv')
    for a in assets:
        a['reserve_eligible'] = a['name']=='SGOV'
    original = rules.evaluate(spec['original_weights'],assets,corr)
    changed = rules.evaluate(spec['revised_weights'],assets,corr)
    # Independent direct NumPy calculation, separate from engine covariance construction.
    monthly = audit['prices'].pct_change(fill_method=None).iloc[1:]
    for evaluated in (original,changed):
        w = np.asarray(evaluated['weights'])
        np.testing.assert_allclose(evaluated['return'], w@(monthly.mean().to_numpy()*12),atol=1e-12,rtol=0)
        np.testing.assert_allclose(evaluated['volatility'],np.sqrt(w@(monthly.cov().to_numpy()*12)@w),atol=1e-12,rtol=0)
    outcomes = {'lower_expected_return':changed['return']<original['return'],
                'lower_annualized_volatility':changed['volatility']<original['volatility'],
                'fails_minimum_return':not changed['checks']['return'],
                'passes_reserve':changed['checks']['reserve'],
                'passes_volatility':changed['checks']['risk']}
    result = {'run_at_utc':started.isoformat(),'completed_at_utc':datetime.now(timezone.utc).isoformat(),
              'authorship':'User-supplied prediction; AI-off preparation self-reported by Mason. Execution and arithmetic checks assisted by OpenAI Codex; not independent validation.',
              'pre_run_commit':receipt,'weight_order':list(audit['prices'].columns),
              'original':original,'revised':changed,'prediction_outcomes':outcomes,
              'all_predictions_supported':all(outcomes.values()),
              'return_change_basis_points':(changed['return']-original['return'])*10000,
              'volatility_change_percentage_points':(changed['volatility']-original['volatility'])*100,
              'decision':'Reject revised allocation: it fails selected pilot rules; retain original only conditionally for simulation review.' if not changed['feasible'] else 'Revised allocation is numerically feasible; review the user prediction and original mandate before any decision.',
              'live_capital_authorized':False,
              'limits':'Historical arithmetic return and sample covariance estimates, not forecasts. No new cost stress, no foundation payout path, no independent partner validation. This result does not establish original mandate compliance.'}
    (ROOT/'outputs/mason-locked-result.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))

if __name__=='__main__':
    main()
