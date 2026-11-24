"""Expose existing calculations and preserve a readable audit output offline."""
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import importlib.metadata

import numpy as np
import pandas as pd
import portfolio as p

ROOT = Path(__file__).resolve().parent


from audit_controls import evaluate, search, signal, fee_stressed, annual_fee


def main():
    from data_integrity import verify
    verify(ROOT)  # fail before calculations or writing outputs
    generated_at = datetime.now(timezone.utc)
    assets, corr = p.estimate_from_csv(ROOT / 'prices.csv')
    for asset in assets:
        asset['reserve_eligible'] = asset['name'] == 'SGOV'
    original = search(assets, corr, .065, .03)
    if original is None:
        raise ValueError('Frozen baseline unexpectedly has no feasible mix.')
    baseline = evaluate(original['weights'], assets, corr)
    saved = json.loads((ROOT / 'evidence/lab 15/optimization_results.json').read_text())['all_months']
    for key in ('weights', 'return', 'volatility', 'reserve_weight'):
        np.testing.assert_allclose(baseline[key], saved[key], rtol=0, atol=1e-12)
    returns = pd.read_csv(ROOT / 'prices.csv', index_col=0).pct_change(fill_method=None).iloc[1:]
    np.testing.assert_allclose(p.covariance_matrix(assets, corr), returns.cov().to_numpy() * 12,
                               rtol=0, atol=1e-12)
    stress_assets = deepcopy(assets)
    equity = next(asset for asset in stress_assets if asset['name'] == 'ACWI')
    old = equity['return']
    equity['return'] -= .01
    stressed = search(stress_assets, corr, .065, .03)
    if stressed is None:
        raise ValueError('Frozen stress unexpectedly has no feasible mix.')
    scenarios = {
        'Equal weight': evaluate(p.equal_weights(assets), assets, corr),
        'Inverse volatility': evaluate(p.inverse_volatility_weights(assets), assets, corr),
        'Constrained baseline': baseline,
        'Fixed baseline under stress': evaluate(original['weights'], stress_assets, corr),
        'Reoptimized stress': evaluate(stressed['weights'], stress_assets, corr),
    }
    fee_assets = fee_stressed(assets)
    fee_result = search(fee_assets, corr)
    assert fee_result is not None
    scenarios['Fixed baseline under fee stress'] = evaluate(original['weights'], fee_assets, corr)
    scenarios['Reoptimized fee stress'] = evaluate(fee_result['weights'], fee_assets, corr)
    scenarios['Inherited reference benchmark'] = evaluate([0, 0, .4, .6], assets, corr)
    recent_assets, recent_corr = p.estimate_from_csv(ROOT / 'prices.csv', True)
    for asset in recent_assets:
        asset['reserve_eligible'] = asset['name'] == 'SGOV'
    recent_result = search(recent_assets, recent_corr)
    assert recent_result is not None
    scenarios['Last 36 months'] = evaluate(recent_result['weights'], recent_assets, recent_corr)
    scenarios['Fixed baseline last 36 months'] = evaluate(original['weights'], recent_assets, recent_corr)
    scenarios['Fixed baseline at 5% risk ceiling'] = evaluate(original['weights'], assets, corr, ceiling=.05)
    # Assumed annual implementation drag: 25% one-way turnover * 100 bp
    # cost per dollar traded = 25 bp of NAV. Not an observed ETF quote.
    trading_assets = deepcopy(assets)
    for asset in trading_assets:
        asset['return'] -= .0025
    scenarios['Fixed baseline transaction cost stress'] = evaluate(original['weights'], trading_assets, corr)
    trading_result = search(trading_assets, corr)
    if trading_result is not None:
        scenarios['Reoptimized transaction cost stress'] = evaluate(trading_result['weights'], trading_assets, corr)
    for name, scenario in scenarios.items():
        scenario['current_fee_annual_dollars_per_10000'] = annual_fee(scenario['weights'], assets) * 10000
        scenario['incremental_fee_stress_annual_dollars_per_10000'] = (annual_fee(scenario['weights'], assets) * 10000 if 'fee stress' in name else None)
    assert not scenarios['Fixed baseline under fee stress']['mandate_pass']
    assert scenarios['Reoptimized fee stress']['mandate_pass']
    assert search(assets, corr, ceiling=.05) is None
    assert not signal('2026-10-22T21:27:42.703541Z')['available']
    assert not signal(verified_local=False)['available']
    for scenario in scenarios.values():
        assert abs(sum(scenario['weights']) - 1) <= 1e-12
        assert min(scenario['weights']) >= 0
    assert search(assets, corr, 1, .03) is None
    assert not scenarios['Fixed baseline under stress']['mandate_pass']
    assert scenarios['Reoptimized stress']['mandate_pass']
    source = json.loads((ROOT / 'data_sources.json').read_text())
    report = {
        'generated_at_utc': generated_at.isoformat(),
        'model_decision_date': '2026-11-17',
        'prep_review_date': '2026-11-23',
        'recommendation': 'Pilot in simulation only; defer capital allocation pending confirmed mandate and validation.',
        'data_downloaded_at_utc': source['downloaded_at_utc'],
        'price_window': 'September 2021 through September 2026',
        'return_window': 'October 2021 through September 2026; 60 monthly returns',
        'weight_order': [asset['name'] for asset in assets],
        'provisional_rules': {'annual_return_objective': .065, 'reserve_minimum': .03,
                              'reserve_eligible': ['SGOV'], 'grid_step': .05, 'annual_volatility_ceiling': .065,
                              'status': 'Proposed educational mandate; ceiling is an AI-assisted illustrative proposal, not client-validated'},
        'changed_input': {'ACWI_annual_return_old': old, 'ACWI_annual_return_new': equity['return'],
                          'status': 'AI-assisted sensitivity; not a human Locked Changed-Input Record'},
        'point_in_time_signal': signal(),
        'cost_stress': {'method': 'Subtract one current issuer expense ratio incrementally from already-net historical returns; hypothetical doubling, not forecast or transaction costs',
                        'expense_ratios': {'SGOV': .0009, 'VGIT': .0003, 'VCIT': .0003, 'ACWI': .0032},
                        'retrieved': '2026-11-23', 'Vanguard_expenseRatioAsOfDate': '2025-12-19',
                        'iShares_market_spread_as_of': '2026-11-20', 'card': 'docs/cost-data-card.md',
                        'timing': 'Nov 23 sensitivity overlay; not information asserted known on Nov 17 model decision'},
        'scenarios': scenarios,
        'verification': ['Matches archived all-month result to 1e-12',
                         'Covariance matches independent pandas sample covariance annualized by 12',
                         'All allocations are long-only and fully invested',
                         'Fee stress fails fixed weights and passes after reoptimization',
                         '5% volatility ceiling stops without relaxing return or reserve rules',
                         'Signal unavailable at/before snapshot and for unverified sources',
                         'Impossible 100% annual objective returns no feasible mix',
                         'Stress fails at fixed weights and passes after reoptimization'],
        'sha256': {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
                   for name in ('prices.csv', 'portfolio.py', 'app.py', 'data_sources.json', 'run.py', 'audit_controls.py')},
        'environment': {'python': platform.python_version(), **{name: importlib.metadata.version(name)
                        for name in ('numpy', 'pandas', 'streamlit')}},
    }
    out = ROOT / 'outputs'
    out.mkdir(exist_ok=True)
    (out / 'results.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    lines = ['# Executed portfolio output', '',
             'AI assistance: OpenAI Codex packaged and checked the existing model; the Copilot SDK assistant reviewed the package. Education, not investment advice.', '',
             report['recommendation'], '',
             'Model decision: November 17, 2026. Preparation review: November 23, 2026. '
             'Frozen prices downloaded October 22, 2026; returns October 2021–September 2026. '
             'This run does not update the market data.', '',
             'Proposed educational rules: return >=6.5%, SGOV reserves >=3%, volatility <=6.5%. '
             'Weights follow SGOV / VGIT / VCIT / ACWI.', '',
             '| Scenario | Weights (%) | Return (%) | Volatility (%) | Reserves (%) | Risk rule | Mandate verdict | Current fee exposure $/10,000/year | Incremental fee $/10,000/year |',
             '| --- | --- | ---: | ---: | ---: | --- | --- | ---: | ---: |']
    for name, s in scenarios.items():
        weights = ' / '.join(f'{w * 100:.4f}' for w in s['weights'])
        failed = ', '.join(k for k, v in s['checks'].items() if not v)
        verdict = 'PASS' if s['mandate_pass'] else f'FAIL: {failed}'
        increment = s['incremental_fee_stress_annual_dollars_per_10000']
        increment_label = 'Not applied' if increment is None else f'{increment:.2f}'
        lines.append(f"| {name} | {weights} | {s['return'] * 100:.6f} | {s['volatility'] * 100:.6f} | {s['reserve_weight'] * 100:.4f} | {'PASS' if s['checks']['volatility_at_most_6_5_percent'] else 'FAIL'} | {verdict} | {s['current_fee_annual_dollars_per_10000']:.2f} | {increment_label} |")
    lines += ['', f'Changed input: ACWI annual return estimate {old:.8%} to {equity["return"]:.8%}. '
              'Volatilities, correlations, objective, and eligibility stay fixed.', '',
              'The fixed allocation loses 0.35 percentage point of return. Reoptimization increases equity '
              'by 5 percentage points. These are conditional model estimates; no realized performance or '
              'historical point-in-time backtest is established.', '',
              '## Verification', '', *['- ' + item for item in report['verification']], '',
              'Detailed inputs, source hashes, dependency versions, and execution timestamp: [results.json](results.json).', '']
    lines += ['', '## Descriptive point-in-time signal', '',
              'September 2026 versus August 2026; snapshot available only after October 22 download. '
              'No historical Yahoo vintage claim; not an optimizer input.', '']
    for ticker, value in report['point_in_time_signal']['simple_returns'].items():
        lines.append(f'- {ticker}: {value:.8%}')
    lines += ['', 'Historical adjusted-price returns already reflect operating expenses. '
              'The illustrative fee stress subtracts only one additional current ratio. '
              'Fee sources retrieved November 23 are a later sensitivity overlay, not November 17 information. '
              'Spreads and commissions remain unmodelled. See [cost card](../docs/cost-data-card.md).', '',
              'The 6.5% volatility ceiling is an AI-assisted illustrative choice made at user request, chosen above the '
              'existing 6.0178% stressed volatility; it is not validated client risk appetite. '
              'The inherited 40% VCIT / 60% ACWI benchmark is provisional. '
              'STOP on infeasibility, unavailable inputs, a rule failure or unsupported historical-as-of claim. '
              'Live allocation remains deferred pending client approval and validation.', '']
    text = '\n'.join(lines)
    (out / 'VISIBLE_OUTPUT.md').write_text(text, encoding='utf-8')
    print(text)
    print('Saved outputs/VISIBLE_OUTPUT.md and outputs/results.json')


if __name__ == '__main__':
    main()
