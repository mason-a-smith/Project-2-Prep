"""36/24 chronological diagnostic; no weights chosen using evaluation returns."""
from io import StringIO
import numpy as np
import pandas as pd
import portfolio as p
import current_rules as rules
from reconciliation import history


def evaluate_path(prices,weights):
    h = history(prices,weights)
    return {'months':len(h['returns']),'total_return':float(h['wealth'].iloc[-1]-1),
            'cagr':h['cagr'],'annual_sample_volatility':h['annual_volatility'],
            'max_month_end_drawdown':h['max_drawdown'],'worst_calendar_return':h['worst_calendar']}


def run(prices):
    if len(prices)!=61:
        raise ValueError('STOP: chronological diagnostic requires exactly 61 prices / 60 returns.')
    # Slice PRICES first, before estimates or optimization. 37 prices -> 36 returns.
    train = prices.iloc[:37].copy()
    evaluation = prices.iloc[36:].copy()  # common boundary price, no common return
    assets,corr = p.estimate_from_csv(StringIO(train.to_csv(index_label='date')))
    for a in assets:
        a['reserve_eligible'] = a['name']=='SGOV'
    targets = {'Equal weight':p.equal_weights(assets),'Inverse volatility':p.inverse_volatility_weights(assets)}
    selected = rules.search(assets,corr)  # original 6.5% return/cap and 3% reserve
    if selected is not None:
        targets['Constrained portfolio'] = selected['weights']
    training = {name:rules.evaluate(w,assets,corr) for name,w in targets.items()}
    evaluated = {name:{'weights':w,**evaluate_path(evaluation,w)} for name,w in targets.items()}
    return {'status':'COMPLETED' if selected is not None else 'CONSTRAINED STOP: no feasible training allocation',
            'training_price_start':str(train.index[0].date()),'training_return_start':str(train.index[1].date()),
            'training_end':str(train.index[-1].date()),'training_months':36,
            'evaluation_boundary_price':str(evaluation.index[0].date()),
            'evaluation_return_start':str(evaluation.index[1].date()),'evaluation_end':str(evaluation.index[-1].date()),
            'evaluation_months':24,'training_results':training,'evaluation_results':evaluated,
            'constrained_evaluation':None if selected is None else evaluated['Constrained portfolio'],
            'rules':rules.limits(),'method':'Target weights derived solely from first 36 returns; fixed annual-December rebalancing convention, no evaluation-based tuning. Evaluation starts from unit NAV at boundary price. Separate baselines are descriptive even if training rules fail.',
            'limitations':'Retrospective chronological diagnostic: the full dataset was previously examined. Not an untouched holdout, independent validation, or proof of prospective robustness. The October 2026 adjusted-price vintage was not available at the September 2024 training boundary. No actual trading-as-of claim. No foundation payouts, full implementation costs, or inflation adjustment; no live authorization.'}
