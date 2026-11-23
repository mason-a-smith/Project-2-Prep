"""Educational mandate controls; preserve the original portfolio engine."""
from copy import deepcopy
from datetime import datetime
from pathlib import Path
import hashlib
import json
import pandas as pd
import portfolio as p

ROOT = Path(__file__).resolve().parent
RISK_LIMIT = .065
FEES = {'SGOV': .0009, 'VGIT': .0003, 'VCIT': .0003, 'ACWI': .0032}
PRICE_HASH = 'fb1ab89b2c06603c13917b5a112b3a24a13ff5872803d560dce28f2490891be1'
SOURCE_HASH = 'e6b00f8ded037d2df098c1ea3e888926ceac225dae720933fadcf1ac1306a6e8'


def search(assets, corr, objective=.065, minimum=.03, ceiling=RISK_LIMIT):
    # The existing engine finds the minimum variance among return/reserve-feasible
    # grid points. If that minimum exceeds the ceiling, no grid point can pass.
    result = p.search_portfolio(assets, corr, objective, minimum)
    return result if result is not None and result['volatility'] <= ceiling + 1e-12 else None


def evaluate(weights, assets, corr, objective=.065, minimum=.03, ceiling=RISK_LIMIT):
    ret = p.expected_return(weights, assets)
    reserve = p.reserve_eligible_weight(weights, assets)
    vol = p.portfolio_volatility(weights, p.covariance_matrix(assets, corr))
    checks = {'fully_invested': abs(sum(weights) - 1) <= 1e-12,
              'long_only': min(weights) >= 0,
              'return_at_least_6_5_percent': ret >= objective - 1e-12,
              'reserve_at_least_3_percent': reserve >= minimum - 1e-12,
              'volatility_at_most_6_5_percent': vol <= ceiling + 1e-12}
    return {'weights': weights, 'return': ret, 'volatility': vol,
            'reserve_weight': reserve, 'checks': checks, 'mandate_pass': all(checks.values())}


def fee_stressed(assets):
    if any(s['name'] not in FEES for s in assets):
        raise ValueError('Fee stress unavailable: issuer ratios missing for this universe.')
    adjusted = deepcopy(assets)
    for s in adjusted:
        s['return'] -= FEES[s['name']]
    return adjusted


def annual_fee(weights, assets):
    return sum(w * FEES[s['name']] for w, s in zip(weights, assets))


def signal(decision='2026-11-17T00:00:00+00:00', verified_local=True):
    if not verified_local:
        return {'available': False, 'reason': 'No verified snapshot timestamp for uploads or Meridian training.'}
    if hashlib.sha256((ROOT / 'data_sources.json').read_bytes()).hexdigest() != SOURCE_HASH:
        return {'available': False, 'reason': 'STOP: provenance hash differs from the verified frozen metadata.'}
    source = json.loads((ROOT / 'data_sources.json').read_text(encoding='utf-8'))
    cutoff = datetime.fromisoformat(decision.replace('Z', '+00:00'))
    downloaded = datetime.fromisoformat(source['downloaded_at_utc'])
    if cutoff.tzinfo is None:
        raise ValueError('Decision must include a timezone.')
    if cutoff <= downloaded:
        return {'available': False, 'reason': 'STOP historical-as-of claim: snapshot not available before this decision; Yahoo vintages unavailable.'}
    if hashlib.sha256((ROOT / 'prices.csv').read_bytes()).hexdigest() != PRICE_HASH:
        return {'available': False, 'reason': 'STOP: local price hash differs from the verified frozen snapshot.'}
    prices = pd.read_csv(ROOT / 'prices.csv', index_col=0)
    if list(prices.index[-2:]) != ['2026-08-31', '2026-09-30'] or list(prices.columns) != list(FEES):
        raise ValueError('Signal requires the frozen August/September 2026 fund observations.')
    return {'available': True, 'decision_cutoff': cutoff.isoformat(),
            'downloaded_at_utc': source['downloaded_at_utc'],
            'prior_month': prices.index[-2], 'latest_completed_month': prices.index[-1],
            'simple_returns': (prices.iloc[-1] / prices.iloc[-2] - 1).to_dict(),
            'use': 'Descriptive context only; not an optimizer predictor. No later publications loaded.'}
