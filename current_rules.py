"""Current rule labels and validation; frozen audit_controls remains evidence."""
import math
import numpy as np
import portfolio as p
import audit_controls as archived


def limits(objective=.065, minimum=.03, ceiling=.065):
    if not all(math.isfinite(x) for x in (objective, minimum, ceiling)):
        raise ValueError('All rule inputs must be finite.')
    if not 0 <= minimum <= 1 or ceiling < 0:
        raise ValueError('Reserve minimum must be 0–100%; risk ceiling must be nonnegative.')
    return {'return_minimum':objective, 'reserve_minimum':minimum, 'volatility_ceiling':ceiling}


def verdict(weights, ret, reserve, vol, objective=.065, minimum=.03, ceiling=.065):
    selected = limits(objective, minimum, ceiling)
    if not weights or not all(math.isfinite(x) for x in [*weights,ret,reserve,vol]):
        raise ValueError('Portfolio results must be finite and weights nonempty.')
    labels = {'fully_invested':'Weights total = 100%', 'long_only':'All weights >= 0%',
              'return':f'Estimated annual return >= {objective*100:.6g}%',
              'reserve':f'Reserve-eligible weight >= {minimum*100:.6g}%',
              'risk':f'Annual sample volatility <= {ceiling*100:.6g}%'}
    checks = {'fully_invested':abs(sum(weights)-1)<=1e-12,'long_only':min(weights)>=0,
              'return':ret>=objective-1e-12,'reserve':reserve>=minimum-1e-12,'risk':vol<=ceiling+1e-12}
    return {'limits':selected,'labels':labels,'checks':checks,'feasible':all(checks.values()),
            'failed_rules':[labels[k] for k,ok in checks.items() if not ok],
            'live_capital_authorized':False}


def evaluate(weights, assets, corr, objective=.065, minimum=.03, ceiling=.065):
    if len(weights) != len(assets):
        raise ValueError('Weight count must match assets.')
    ret = p.expected_return(weights,assets)
    reserve = p.reserve_eligible_weight(weights,assets)
    vol = p.portfolio_volatility(weights,p.covariance_matrix(assets,corr))
    return {'weights':weights,'return':ret,'reserve_weight':reserve,'volatility':vol,
            **verdict(weights,ret,reserve,vol,objective,minimum,ceiling)}


def search(assets,corr,objective=.065,minimum=.03,ceiling=.065):
    limits(objective,minimum,ceiling)
    # Validate the full covariance, not just the winning candidate variance.
    covariance = np.asarray(p.covariance_matrix(assets,corr))
    if np.linalg.eigvalsh(covariance).min() < -1e-12:
        raise ValueError('Covariance must be positive semidefinite.')
    answer = archived.search(assets,corr,objective,minimum,ceiling)
    return None if answer is None else evaluate(answer['weights'],assets,corr,objective,minimum,ceiling)


def saved_verdict(name, scenario):
    """Saved risk stress explicitly used 5%, while other scenarios used 6.5%."""
    return verdict(scenario['weights'],scenario['return'],scenario['reserve_weight'],
                   scenario['volatility'],ceiling=.05 if name=='Fixed baseline at 5% risk ceiling' else .065)
