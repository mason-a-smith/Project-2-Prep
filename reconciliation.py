"""Additive Lab 13 reconciliation; no changes to the frozen optimizer."""
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
TICKERS = ['SGOV', 'VGIT', 'VCIT', 'ACWI']


def history(prices, weights, rebalance='annual'):
    """Gross of trading/advisory costs; adjusted fund prices include fund expenses.

    Start at first price with target holdings. Rebalance after December returns,
    so January begins at target. No external cash flows or future optimization.
    """
    dates = pd.to_datetime(prices.index)
    if dates.has_duplicates or not dates.is_monotonic_increasing:
        raise ValueError('Dates must be unique and increasing.')
    periods = dates.to_period('M').astype('int64')
    if len(dates) < 2 or not np.all(np.diff(periods) == 1):
        raise ValueError('Consecutive monthly prices required.')
    values = prices.to_numpy(dtype=float)
    w = np.asarray(weights, dtype=float)
    if (not np.isfinite(values).all() or (values <= 0).any() or
            len(w) != values.shape[1] or not np.isfinite(w).all() or
            (w < 0).any() or not np.isclose(w.sum(), 1, atol=1e-12, rtol=0)):
        raise ValueError('Positive finite prices and valid fully invested long-only weights required.')
    if rebalance not in ('annual', 'buy and hold'):
        raise ValueError('Unknown rebalance convention.')
    holdings = w.copy()
    wealth, rets, turnovers = [1.0], [], []
    for i in range(1, len(values)):
        before = holdings.sum()
        holdings *= values[i] / values[i-1]
        after = holdings.sum()
        rets.append(after / before - 1)
        wealth.append(after)
        if rebalance == 'annual' and dates[i].month == 12 and i < len(values)-1:
            turnovers.append({'date': dates[i], 'turnover': float(np.abs(w-holdings/after).sum()/2)})
            holdings = after*w
    r = pd.Series(rets, index=dates[1:], name='return')
    nav = pd.Series(wealth, index=dates, name='Growth of $1')
    dd = nav/nav.cummax()-1
    years = []
    for year, group in r.groupby(r.index.year):
        if len(group) == 12 and set(group.index.month) == set(range(1,13)):
            years.append({'year': int(year), 'return': float((1+group).prod()-1)})
    annual = pd.DataFrame(years, columns=['year','return'])
    roll12 = (1+r).rolling(12).apply(np.prod, raw=True)-1
    roll60 = (1+r).rolling(60).apply(np.prod, raw=True)**(1/5)-1
    return {'returns': r, 'wealth': nav, 'drawdown': dd, 'calendar': annual, 'rebalance':rebalance,
            'turnover': pd.DataFrame(turnovers, columns=['date','turnover']),
            'rolling60': roll60.dropna(), 'rolling12': roll12.dropna(),
            'max_drawdown': float(dd.min()), 'worst_month': float(r.min()),
            'worst_12_months': float(roll12.min()) if len(r)>=12 else None,
            'worst_calendar': float(annual['return'].min()) if len(annual) else None,
            'cagr': float(nav.iloc[-1]**(12/len(r))-1),
            'annual_volatility': float(r.std(ddof=1)*np.sqrt(12))}


def table(weights, estimate, hist):
    reserve = weights[0]*100_000_000
    annual = hist['calendar']
    turnovers = hist['turnover']
    rows = []
    def add(rule, requirement, model, result, status, limits):
        rows.append({'Rule':rule, 'Original requirement':requirement,
                     'Authority':'AI-assisted provisional pilot' if rule.startswith('Pilot') else 'Original Lab 13 requirement',
                     'Source':('Lab13.md: proposed personal-client section; docs/proposed-mandate.md' if rule.startswith('Pilot') else 'Lab 13 Lab13.md: '+rule.split(' /')[0]),
                     'Model':model,'Numerical result':result,'Status':status,'Limitations':limits})
    add('S1 / horizon','Seven-year investment horizon','Compare observed history with 84 months',
        f"{len(hist['returns'])}/84 months; 28 quarterly payouts = $21m nominal over seven years",'NOT TESTED',
        'Only five years available. No seven-year forecast or terminal-value requirement supplied; no payout escalation assumed.')
    add('S1 / rebalance','Annual rebalancing',
        'Historical diagnostic resets after December return' if hist['rebalance']=='annual' else 'Selected buy-and-hold diagnostic: no rebalancing',
        f'{len(turnovers)} simulated rebalances','NOT TESTED','Calendar-year convention is illustrative. No actual holdings or execution record; optimizer is a static target.')
    add('S2','CPI + 4% annually, net of costs, rolling five years','Compound 60 monthly portfolio returns; CPI and all-in costs missing',
        f"{len(hist['rolling60'])} complete window(s); nominal CAGR {hist['cagr']:.4%}",'NOT TESTED',
        'Cannot test real/net objective without CPI, approved additive-versus-geometric interpretation and full costs. Ex-post fixed weights fitted to this same sample; not a tradable backtest.')
    add('S3 / distributions','$0.75m each quarter','Four payouts = $3m/year; compare initial modeled SGOV value',
        f'Initial SGOV ${reserve/1e6:.2f}m; {reserve/750_000:.2f} quarterly payouts at unchanged value','NOT TESTED',
        'Static coverage only, not paid distributions. No approved withdrawal dates, sale/replenishment policy or account cash-flow record; adjusted prices assume reinvested fund distributions.')
    add('S3 / reserve','Twelve months in cash or daily-liquid government securities','Required $3m / $100m = 3%; SGOV is pilot proxy',
        f'${reserve/1e6:.2f}m versus $3m; {weights[0]:.2%} versus 3%', 'PASS' if reserve>=3_000_000-1e-8 else 'FAIL',
        'Conditional initial proxy test only. SGOV fund eligibility is proposed, not client-approved. Original direct 10-year Treasury eligibility does not automatically make VGIT eligible; reserve must remain $3m as NAV changes.')
    add('S4','60% global equities / 40% US investment-grade bonds','60% ACWI / 40% VCIT reference',
        '60% / 40% reference; no tracking-error limit','NOT TESTED','Reference, not binding allocation rule. VCIT is a corporate intermediate-duration proxy, not the whole US investment-grade market.')
    add('S5 / weights','Long-only, no borrowing or shorts','Nonnegative target weights sum to one',
        f'Sum {sum(weights):.4%}; minimum {min(weights):.4%}', 'PASS' if min(weights)>=0 and abs(sum(weights)-1)<1e-12 else 'FAIL',
        'Target-level test; no financing or actual account balances supplied.')
    add('S5 / instruments','No derivatives','Four ETF target holdings; instrument-level restriction review absent',
        '0 direct derivative positions modeled','NOT TESTED','No current fund holdings or approved treatment of derivatives inside funds; do not infer instrument compliance from weights.')
    add('S6','No single issuer above 8%; cash/Treasury/diversified funds exempt','Apply original diversified-fund exemption to four ETF sleeves',
        '0% nonexempt company exposure at sleeve level','PASS','Case exemption only; no look-through issuer test required by original case. Does not assert absence of underlying company or bond exposure.')
    max_turn = turnovers.turnover.max() if len(turnovers) else None
    add('S7','Annual turnover <=25% without committee approval','One-way half-sum absolute drift-to-target changes at annual reset',
        f'Max simulated reset {max_turn:.4%}' if max_turn is not None else 'No resets', 'FAIL' if max_turn is not None and max_turn>.25+1e-12 else 'NOT TESTED',
        'Diagnostic excludes initial funding, distributions, intra-year trades, cash flows and discretionary trades. Not actual annual turnover; no approval history. Passing diagnostic cannot pass original rule.')
    add('S8','At least 90% redeemable within five business days','No verified ETF redemption/settlement evidence supplied',
        'Verified share unavailable; required >=90%','NOT TESTED','Original case redemption days cannot be assigned to these ETFs without evidence. Exchange listing is not verified stressed liquidation capacity for $100m.')
    worst = hist['worst_calendar']
    add('S9 / observed','No calendar-year loss greater than 10%','Compound January–December returns; exclude incomplete years',
        f'Worst complete year {worst:.4%}; {len(annual)} complete years' if worst is not None else 'No complete years',
        ('PASS' if worst>=-.10-1e-12 else 'FAIL') if worst is not None else 'NOT TESTED',
        'Historical diagnostic only, before full costs and without foundation payouts. Month-end data misses intramonth losses; future limit not established.')
    add('S9 / future','Cannot have calendar-year loss >10%','No enforceable guarantee or approved breach process',
        'Future maximum loss unknown','NOT TESTED','Annual volatility is dispersion, drawdown is peak-to-trough decline, annual loss is January–December return. None guarantees the others; live use remains stopped.')
    add('S10','No sector, ESG, tax or home-bias preference; ranking criterion absent','Pilot minimizes sample volatility; no extra preference filters',
        '0 extra preference filters; minimum-volatility grid ranking','NOT TESTED','Ranking criterion is an educational proposal, not original client instruction or approval.')
    add('Pilot / return','Later pilot target: annual estimated return >=6.5%','Arithmetic monthly mean ×12, 2.5% assumed CPI +4 percentage points',
        f"{estimate['return']:.4%}", 'PASS' if estimate['return']>=.065-1e-12 else 'FAIL',
        '2.5% is planning inflation, not observed CPI. Exact 4% real return at 2.5% inflation needs 1.025×1.04−1=6.6%. Historical arithmetic mean is not five-year CAGR or net real return.')
    add('Pilot / risk','Later illustrative annual volatility ceiling <=6.5%','sqrt(w transpose covariance w), annualized monthly sample covariance',
        f"{estimate['volatility']:.4%}", 'PASS' if estimate['volatility']<=.065+1e-12 else 'FAIL',
        'Proposed ceiling chosen in later educational overlay; not original S9 and not client risk approval. Historical realized-path volatility differs as weights drift.')
    return pd.DataFrame(rows)


def render(results):
    import streamlit as st
    st.subheader('Lab 13 mandate reconciliation')
    st.warning('A pilot numerical PASS does not establish full Lab 13 compliance. Unverified requirements remain NOT TESTED; live capital remains deferred.')
    options = ['Constrained baseline','Equal weight','Inverse volatility','Inherited reference benchmark']
    name = st.selectbox('Portfolio to reconcile', options)
    mode = st.selectbox('Historical diagnostic rebalancing', ['annual','buy and hold'])
    prices = pd.read_csv(ROOT/'prices.csv', index_col=0)[TICKERS]
    scenario = results['scenarios'][name]
    hist = history(prices, scenario['weights'], mode)
    frame = table(scenario['weights'], scenario, hist)
    statuses = st.multiselect('Show statuses', ['PASS','FAIL','NOT TESTED'], default=['PASS','FAIL','NOT TESTED'])
    query = st.text_input('Find requirement or source')
    shown = frame[frame.Status.isin(statuses)]
    if query:
        shown = shown[shown.apply(lambda row: query.lower() in ' '.join(row.astype(str)).lower(), axis=1)]
    st.dataframe(shown, hide_index=True, width='stretch')
    st.download_button('Download full reconciliation CSV', frame.to_csv(index=False), 'mandate-reconciliation.csv','text/csv')
    with st.expander('Original mandate source and methods'):
        st.markdown((ROOT/'evidence/Lab 13/Lab13.md').read_text(encoding='utf-8'))
        st.markdown((ROOT/'docs/mandate-reconciliation.md').read_text(encoding='utf-8'))
    st.subheader('Historical losses: distinct measures')
    st.caption('Fixed targets selected with hindsight; retrospective descriptive reconstruction, not out-of-sample performance. No foundation withdrawals. Fund expenses reflected in adjusted prices; trading, advisory fees and taxes excluded. Annual reset follows December return; buy-and-hold makes no resets.')
    metrics = pd.DataFrame([{'Measure':'Annual sample volatility of realized path','Value':hist['annual_volatility']},
        {'Measure':'Maximum month-end drawdown (signed)','Value':hist['max_drawdown']},
        {'Measure':'Worst month','Value':hist['worst_month']},
        {'Measure':'Worst rolling 12-month return','Value':hist['worst_12_months']},
        {'Measure':'Worst complete calendar-year return','Value':hist['worst_calendar']}])
    st.dataframe(metrics,hide_index=True,column_config={'Value':st.column_config.NumberColumn(format='percent')})
    st.line_chart(hist['drawdown'].rename('Drawdown'), y_label='Fraction of prior peak', height=260)
    st.dataframe(hist['calendar'],hide_index=True,column_config={'return':st.column_config.NumberColumn(format='percent')})
    trough = hist['drawdown'].idxmin()
    peak = hist['wealth'].loc[:trough].idxmax()
    st.write(f'Maximum drawdown peak: {peak.date()}; trough: {trough.date()}. Worst month ends {hist["returns"].idxmin().date()}.')
    if not hist['rolling12'].empty:
        end = hist['rolling12'].idxmin()
        start = prices.index[pd.to_datetime(prices.index).get_loc(end)-12]
        st.write(f'Worst rolling 12-month holding interval: {start} to {end.date()}.')
    st.caption('Only complete January–December years test the historical S9 diagnostic. Rolling 12-month losses and drawdowns use different endpoints. Month-end drawdown understates any deeper intramonth drawdown. No future loss guarantee follows from a historical pass.')
    st.dataframe(hist['turnover'],hide_index=True)
    st.caption('Simulated annual drift-reset turnover is shown for diagnosis, not evidence of actual S7 compliance. No payout trading policy has been invented.')
