"""Reproduce Lab 20 from frozen Lab 15 prices; no new market downloads."""
from pathlib import Path
import copy
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'lab 15'))
import portfolio as p

assets, corr = p.estimate_from_csv(ROOT / 'lab 15' / 'prices.csv')
for asset in assets:
    asset['reserve_eligible'] = asset['name'] == 'SGOV'
baseline = p.search_portfolio(assets, corr, .065, .03)
changed = copy.deepcopy(assets)
equity = next(a for a in changed if a['name'] == 'ACWI')
old = equity['return']
equity['return'] -= .01
stress = p.search_portfolio(changed, corr, .065, .03)
cov = p.covariance_matrix(assets, corr)
fixed = baseline['weights']
report = {
    'scope': 'AI-assisted reproducibility check, not a partner cold run or human locked prediction',
    'weight_order': [a['name'] for a in assets],
    'objective': .065, 'reserve_minimum': .03,
    'baseline': baseline,
    'changed_input': {'asset': 'ACWI', 'old_annual_return': old,
                      'new_annual_return': equity['return'], 'change_percentage_points': -1},
    'baseline_weights_under_stress': {
        'return': p.expected_return(fixed, changed),
        'volatility': p.portfolio_volatility(fixed, cov),
        'reserve_weight': p.reserve_eligible_weight(fixed, changed),
        'meets_return_objective': p.expected_return(fixed, changed) >= .065},
    'reoptimized_stress': stress,
}
for result in (baseline, stress):
    assert result is not None
    assert abs(sum(result['weights']) - 1) < 1e-12
    assert all(w >= 0 for w in result['weights'])
    assert result['return'] >= .065 - 1e-12
    assert result['reserve_weight'] >= .03 - 1e-12
print(json.dumps(report, indent=2))
