"""Interactive Lab 15 and Project 2 portfolio model controls."""
from copy import deepcopy
from io import BytesIO
from pathlib import Path
import hashlib
import importlib.util

import pandas as pd
import streamlit as st

import audit_controls as controls
import current_rules as rules

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('portfolio_engine', ROOT / 'portfolio.py')
engine = importlib.util.module_from_spec(spec)
spec.loader.exec_module(engine)


def render_portfolio():
    st.subheader('Interactive portfolio model')
    st.caption(
        'Change return assumptions, reserve rules, or the estimation window to examine conditional scenarios. '
        'Uploaded inputs are not treated as verified point-in-time sources.'
    )
    objective = st.sidebar.number_input(
        'Expected return objective (%)', value=6.5, step=0.1
    ) / 100
    minimum = st.sidebar.number_input(
        'Reserve minimum (%)', min_value=0.0, max_value=100.0, value=3.0, step=1.0
    ) / 100
    ceiling = st.sidebar.number_input(
        'Annual volatility ceiling (%)', min_value=0.0, value=6.5, step=0.1
    ) / 100
    selected_labels = rules.verdict([1.0],0,0,0,objective,minimum,ceiling)['labels']
    upload = st.sidebar.file_uploader('Upload prices.csv', type='csv')
    dataset = st.sidebar.selectbox(
        'Dataset (when no upload)', ['Project 2: local prices.csv', 'Meridian training']
    )
    recent = st.sidebar.checkbox('Use last 36 months', value=False)
    st.sidebar.button('Refresh engine', help='Rerun after saving changes to portfolio.py.')

    try:
        if upload is None and dataset == 'Meridian training':
            baseline_sleeves, baseline_corr = deepcopy(engine.SLEEVES), deepcopy(engine.CORRELATIONS)
            sleeves, corr = deepcopy(baseline_sleeves), deepcopy(baseline_corr)
            source_key = 'meridian'
            st.caption('Meridian training estimates. The 36-month switch applies to uploaded prices only.')
        else:
            data = upload.getvalue() if upload is not None else (ROOT / 'prices.csv').read_bytes()
            source_key = hashlib.sha256(data).hexdigest()
            baseline_sleeves, baseline_corr = engine.estimate_from_csv(BytesIO(data))
            sleeves, corr = engine.estimate_from_csv(BytesIO(data), recent)
            for item in baseline_sleeves + sleeves:
                item['reserve_eligible'] = item['name'] == 'SGOV'
            st.caption(
                'Return estimates: historical arithmetic monthly mean × 12; not a forecast. '
                'Volatility: sample monthly standard deviation × √12. SGOV is selected for the '
                'provisional reserve rule; VGIT eligibility remains unconfirmed.'
            )
            with st.expander('Historical estimates, correlations, and annualized covariance'):
                names = [sleeve['name'] for sleeve in sleeves]
                st.dataframe([{
                    'Ticker': sleeve['name'],
                    'Historical return (%)': sleeve['return'] * 100,
                    'Annual volatility (%)': sleeve['volatility'] * 100,
                } for sleeve in sleeves], hide_index=True)
                st.write('Correlation matrix')
                st.dataframe(pd.DataFrame(corr, index=names, columns=names))
                st.write('Annualized covariance matrix (decimal return squared)')
                st.dataframe(pd.DataFrame(
                    engine.covariance_matrix(sleeves, corr), index=names, columns=names
                ).style.format('{:.8f}'))

        st.subheader('Edit expected returns and reserve eligibility')
        for index, sleeve in enumerate(sleeves):
            left, right = st.columns([3, 1])
            sleeve['return'] = left.number_input(
                f"{sleeve['name']} expected return (%)",
                value=sleeve['return'] * 100,
                step=0.1,
                key=f'{source_key}_{recent}_{index}_return',
            ) / 100
            eligible = right.checkbox(
                'Reserve-eligible',
                value=sleeve['reserve_eligible'],
                key=f'{source_key}_{index}_reserve',
            )
            sleeve['reserve_eligible'] = eligible
            baseline_sleeves[index]['reserve_eligible'] = eligible
        baseline = rules.search(baseline_sleeves, baseline_corr, objective, minimum, ceiling)
        result = rules.search(sleeves, corr, objective, minimum, ceiling)

        def display(column, title, answer):
            column.subheader(title)
            if answer is None:
                column.warning('no mix meets the objective and reserve/risk rules')
                return
            column.table([{
                'Asset': asset['name'],
                'Weight (%)': f'{weight * 100:.2f}',
            } for asset, weight in zip(sleeves, answer['weights'])])
            column.metric('Expected return', f"{answer['return']:.2%}")
            column.metric('Volatility', f"{answer['volatility']:.2%}")
            column.metric('Reserve-eligible weight', f"{answer['reserve_weight']:.2%}")

        left, right = st.columns(2)
        display(left, 'Current inputs — lowest-risk mix', result)
        display(right, 'As loaded — all months, original returns', baseline)
        st.caption(
            'Both answers use the current objective, reserve minimum, and eligibility selections. '
            'Search: fully invested, long-only, 5 percentage point increments. A feasible result is not authorization to invest.'
        )
        if result is not None and baseline is not None:
            weight_change = max(
                abs(current - original)
                for current, original in zip(result['weights'], baseline['weights'])
            ) * 100
            st.metric('Largest weight change (percentage points)', f'{weight_change:.2f}')
        else:
            st.info('Largest weight change unavailable unless both cases have a feasible mix.')
        st.caption('Active scenario limits: ' + ' | '.join(selected_labels[k] for k in ('return','reserve','risk')))

        with st.expander('Historical losses for the selected feasible target'):
            if result is not None and source_key != 'meridian':
                from reconciliation import history
                historical_prices = pd.read_csv(BytesIO(data), index_col=0)
                if recent:
                    historical_prices = historical_prices.tail(37)
                historical = history(historical_prices, result['weights'])
                st.write(f"Maximum month-end drawdown: {historical['max_drawdown']:.2%}")
                worst = historical['worst_calendar']
                st.write('Worst complete calendar-year return: ' + ('NOT TESTED: no complete year' if worst is None else f'{worst:.2%}'))
                st.caption('Annual December rebalancing of the selected fixed target; ex-post diagnostic. Edited expected returns do not rewrite historical prices. No foundation payouts or trading/advisory costs. Monthly data misses intramonth troughs; neither statistic is a future loss guarantee.')
            else:
                st.info('Historical losses NOT TESTED: no feasible target or no price path for training estimates.')

        st.subheader('Same-sample baselines and proposed-rule verdicts')
        rows = []
        covariance = engine.covariance_matrix(sleeves, corr)
        baseline_weights = [
            ('Equal weight', engine.equal_weights(sleeves)),
            ('Inverse volatility', engine.inverse_volatility_weights(sleeves)),
        ]
        if [asset['name'] for asset in sleeves] == list(controls.FEES):
            baseline_weights.append(('Inherited reference benchmark', [0, 0, .4, .6]))
        baseline_weights.append(
            ('Constrained portfolio', None if result is None else result['weights'])
        )
        for label, weights in baseline_weights:
            if weights is None:
                rows.append({'Portfolio': label, 'Verdict': 'FAIL: no feasible mix'})
                continue
            portfolio_return = engine.expected_return(weights, sleeves)
            reserve = engine.reserve_eligible_weight(weights, sleeves)
            volatility = engine.portfolio_volatility(weights, covariance)
            return_ok = portfolio_return >= objective - 1e-12
            reserve_ok = reserve >= minimum - 1e-12
            risk_ok = volatility <= ceiling + 1e-12
            rows.append({
                'Portfolio': label,
                'Weights (%)': ' / '.join(f'{weight * 100:.4f}' for weight in weights),
                'Return (%)': portfolio_return * 100,
                'Volatility (%)': volatility * 100,
                'Reserves (%)': reserve * 100,
                'Return rule': 'PASS' if return_ok else 'FAIL',
                'Reserve rule': 'PASS' if reserve_ok else 'FAIL',
                'Risk rule': 'PASS' if risk_ok else 'FAIL',
                'Selected limits': ' | '.join(selected_labels[k] for k in ('return','reserve','risk')),
                'Verdict': 'PASS' if return_ok and reserve_ok and risk_ok else 'FAIL',
            })
        chart_left, chart_right = st.columns(2)
        with chart_left:
            st.markdown('**Interactive risk vs. return**')
            chart_rows = [
                row for row in rows
                if 'Return (%)' in row and 'Volatility (%)' in row
            ]
            st.scatter_chart(
                pd.DataFrame(chart_rows),
                x='Volatility (%)',
                y='Return (%)',
                color='Verdict',
                height=360,
                alt='Current editable portfolio baselines plotted by annualized volatility and estimated return.',
            )
        with chart_right:
            st.markdown('**Interactive allocation mix**')
            allocation_chart_rows = [
                {
                    'Portfolio': label,
                    **{
                        sleeve['name']: weight
                        for sleeve, weight in zip(sleeves, weights)
                    },
                }
                for label, weights in baseline_weights
                if weights is not None
            ]
            st.bar_chart(
                pd.DataFrame(allocation_chart_rows),
                x='Portfolio',
                y=[sleeve['name'] for sleeve in sleeves],
                stack=True,
                height=360,
                alt='Current editable baseline portfolio weights by asset.',
            )
        st.dataframe(rows, hide_index=True, width='stretch')
        st.caption(
            'Weights follow: ' + ' / '.join(asset['name'] for asset in sleeves) +
            f'. Selected volatility ceiling: {ceiling:.2%}; inherited benchmark is provisional. '
            'Only the selected numerical pilot rules are tested; original operational requirements remain NOT TESTED.'
        )
        with st.expander('Proposed educational mandate'):
            st.markdown((ROOT / 'docs' / 'proposed-mandate.md').read_text(encoding='utf-8'))

        st.subheader('Descriptive completed-month signal')
        pit = controls.signal(verified_local=upload is None and dataset == 'Project 2: local prices.csv')
        if pit['available']:
            st.dataframe([{
                'Ticker': ticker,
                'September simple return (%)': value * 100,
            } for ticker, value in pit['simple_returns'].items()], hide_index=True)
        else:
            st.warning('Signal unavailable: ' + pit['reason'])
        with st.expander('Fund signal data card'):
            st.markdown((ROOT / 'docs' / 'signal-data-card.md').read_text(encoding='utf-8'))

        st.subheader('Illustrative incremental operating-fee stress')
        if all(asset['name'] in controls.FEES for asset in sleeves):
            fee_assets = controls.fee_stressed(sleeves)
            fee_result = rules.search(fee_assets, corr, objective, minimum, ceiling)
            cost_rows = []
            for label, answer in [
                ('Fixed current allocation', result),
                ('Reoptimized fee stress', fee_result),
            ]:
                if answer is None:
                    cost_rows.append({'Scenario': label, 'Verdict': 'FAIL: no feasible mix'})
                    continue
                weights = answer['weights']
                check = rules.evaluate(weights, fee_assets, corr, objective, minimum, ceiling)
                annual_increment = controls.annual_fee(weights, sleeves) * 10000
                cost_rows.append({
                    'Scenario': label,
                    'Weights (%)': ' / '.join(f'{weight * 100:.4f}' for weight in weights),
                    'Stressed return (%)': check['return'] * 100,
                    'Volatility (%)': check['volatility'] * 100,
                    'Current fee exposure annual dollars per $10,000': annual_increment,
                    'Incremental annual dollars per $10,000': annual_increment,
                    'Return rule': 'PASS' if check['checks']['return'] else 'FAIL',
                    'Reserve rule': 'PASS' if check['checks']['reserve'] else 'FAIL',
                    'Risk rule': 'PASS' if check['checks']['risk'] else 'FAIL',
                    'Selected limits': ' | '.join(check['labels'][k] for k in ('return','reserve','risk')),
                    'Failed rules': ' | '.join(check['failed_rules']) or 'None',
                    'Verdict': 'PASS' if check['feasible'] else 'FAIL',
                })
            st.dataframe(cost_rows, hide_index=True, width='stretch')
        else:
            st.warning('Fee stress unavailable: no verified issuer ratios for this training/upload universe.')
        with st.expander('Operating-fee data card'):
            st.markdown((ROOT / 'docs' / 'cost-data-card.md').read_text(encoding='utf-8'))
        st.write(
            'Estimate stress: lower ACWI by one percentage point. Window stress: select last 36 months '
            'versus all months. Constraint stress: change reserves or eligibility. These controls explore '
            'scenarios without approving a new mandate.'
        )
        st.warning(
            'Transaction costs unresolved: the dashboard includes an assumed 25 bp annual drag; observed spreads and commissions remain unavailable. Historical adjusted returns '
            'are already net of fund operating expenses; the fee stress subtracts only one additional ratio.'
        )
        st.error(
            'STOP live allocation pending client mandate approval, trading-cost evidence and human validation. '
            'Stop on infeasibility, unavailable inputs, failed rules, or unsupported historical-as-of claims.'
        )
        with st.expander('Optional DGS10 context only'):
            st.markdown((ROOT / 'evidence' / 'Lab 17' / 'DGS10_data_card.md').read_text(encoding='utf-8'))
    except (ValueError, TypeError, KeyError, OSError) as error:
        st.error(str(error))
