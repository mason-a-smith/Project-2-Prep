"""Integrated Streamlit workspace for the Project 2 portfolio and lab evidence."""
import hashlib
import json
from pathlib import Path

import pandas as pd
import streamlit as st

import audit_controls as controls
from portfolio_view import render_portfolio
from reconciliation import render as render_reconciliation
from reconciliation import history as portfolio_history
from current_rules import saved_verdict
from data_integrity import load_committee, verify as verify_frozen
from mason_record import render as render_mason_record

ROOT = Path(__file__).resolve().parent
EVIDENCE = ROOT / 'evidence'

st.set_page_config(page_title='Portfolio decision studio', page_icon='📊', layout='wide')
st.title('Investment Management | Decision Studio')
st.caption(
    'AI assistance: OpenAI Codex and the Copilot SDK assistant helped assemble and check this saved-coursework app; '
    'Mason owns the final review. Education, not investment advice.'
)


def read_markdown(relative_path):
    return (ROOT / relative_path).read_text(encoding='utf-8')


def show_portfolio_summary(results):
    verify_frozen(ROOT)
    st.caption('FROZEN COMMITTEE RECORD: sealed snapshot; interactive scenarios and retrospective diagnostics do not amend it.')
    scenarios = results['scenarios']
    baseline = scenarios['Constrained baseline']
    estimate_stress = scenarios['Reoptimized stress']
    fee_stress = scenarios['Fixed baseline under fee stress']

    with st.expander('Mandate: objective, universe, benchmark, risk and limits'):
        st.markdown(read_markdown('docs/proposed-mandate.md'))
    st.caption('Intended user: Mason Smith and the fictional foundation investment committee. '
               'Investment horizon: seven years; proposed monthly paper monitoring is a review cadence, not a shorter investment horizon. '
               'Committee decision: whether to approve a paper pilot; live investment authorization remains absent.')
    with st.expander('Edition A versus Edition B and assumption provenance'):
        st.markdown(read_markdown('docs/edition-and-decision.md'))
    st.subheader('Committee decision')
    st.info(
        'Pilot the process in simulation only; defer capital allocation pending a confirmed mandate, '
        'trading-cost evidence, and human validation.'
    )
    st.caption(
        'Review cadence: proposed monthly paper reviews, with annual rebalancing. Frozen market data ends September 2026; '
        'this app reproduces the saved analysis and does not refresh prices.'
    )

    metric_columns = st.columns(3)
    metric_columns[0].metric('SGOV / ACWI weights', f"{baseline['weights'][0]:.0%} / {baseline['weights'][3]:.0%}")
    metric_columns[1].metric('Baseline return', f"{baseline['return']:.2%}")
    metric_columns[2].metric('Baseline volatility', f"{baseline['volatility']:.2%}")
    st.caption(
        'Proposed educational rules: annual estimated return at least 6.5%, SGOV reserves at least 3%, '
        f"and annualized sample volatility no more than 6.5%. Baseline verdict: "
        f"{'PASS' if baseline['mandate_pass'] else 'FAIL'}. Client approval is unresolved."
    )
    hist = portfolio_history(pd.read_csv(ROOT/'prices.csv',index_col=0),baseline['weights'])
    loss_cols = st.columns(2)
    loss_cols[0].metric('Historical maximum month-end drawdown', f"{hist['max_drawdown']:.2%}")
    loss_cols[1].metric('Worst complete calendar-year return', f"{hist['worst_calendar']:.2%}")
    st.caption('Annual-rebalanced retrospective fixed-target reconstruction, not actual or out-of-sample performance. '
               'No foundation payouts or full trading/advisory costs; month-end data misses intramonth troughs. '
               'Drawdown, calendar-year loss and annual volatility are distinct. See Mandate reconciliation for all periods and untested requirements.')
    st.write('Conditional paper-allocation range: 60–65% SGOV / 35–40% ACWI, with 0% VGIT/VCIT in these separate full-window estimate and cost cases. '
             'These paired scenario endpoints are not a confidence interval or permission to select any combination. '
             'The last-36-month search instead selects 85% SGOV / 15% ACWI, a 20 percentage-point equity shift from the full-window baseline. '
             'That sensitivity prevents treating the 60–65% / 35–40% span as robust across estimation windows; no averaging or automatic trading is authorized.')

    st.subheader('What the stress tests change')
    stress_columns = st.columns(2)
    stress_columns[0].metric(
        'ACWI estimate reduced by 1 percentage point',
        f"{scenarios['Fixed baseline under stress']['return']:.2%}",
        delta='Original weights fail return target',
        delta_color='inverse',
    )
    stress_columns[0].write(
        f"Reoptimization selects 60% SGOV / 40% ACWI: return {estimate_stress['return']:.2%}, "
        f"volatility {estimate_stress['volatility']:.2%}. This is a separate estimate stress."
    )
    stress_columns[1].metric(
        'Hypothetical doubled operating fees',
        f"{fee_stress['return']:.4%}",
        delta='$17.05 incremental annual cost per $10,000',
        delta_color='inverse',
    )
    stress_columns[1].write(
        'The original 65/35 weights miss the return objective under this separate fee stress. '
        'Reoptimization produces another conditional pass; this is not a transaction-cost analysis.'
    )

    st.subheader('Scenario comparison')
    display_names = [
        'Equal weight',
        'Inverse volatility',
        'Constrained baseline',
        'Fixed baseline under stress',
        'Reoptimized stress',
        'Fixed baseline under fee stress',
        'Reoptimized fee stress',
        'Inherited reference benchmark',
        'Last 36 months',
        'Fixed baseline last 36 months',
        'Fixed baseline at 5% risk ceiling',
        'Fixed baseline transaction cost stress',
        'Reoptimized transaction cost stress',
    ]
    chart_labels = {
        'Equal weight': 'Equal weight',
        'Inverse volatility': 'Inverse vol',
        'Constrained baseline': 'Baseline',
        'Fixed baseline under stress': 'ACWI stress fixed',
        'Reoptimized stress': 'ACWI stress reopt',
        'Fixed baseline under fee stress': 'Fee stress fixed',
        'Reoptimized fee stress': 'Fee stress reopt',
        'Inherited reference benchmark': '40/60 benchmark',
        'Last 36 months': 'Last 36 months',
    }
    for name in display_names:
        chart_labels.setdefault(name, name)
    rows = []
    allocation_rows = []
    for name in display_names:
        scenario = scenarios[name]
        weights = scenario['weights']
        selected = saved_verdict(name,scenario)
        rows.append({
            'Scenario': name,
            'Weights (SGOV / VGIT / VCIT / ACWI)': ' / '.join(
                f'{weight:.0%}' for weight in weights
            ),
            'Estimated return': f"{scenario['return']:.3%}",
            'Estimated volatility': f"{scenario['volatility']:.3%}",
            'SGOV reserve weight': f"{scenario['reserve_weight']:.0%}",
            'Mandate verdict': 'PASS' if scenario['mandate_pass'] else 'FAIL',
            'Failed rules': ' | '.join(selected['failed_rules']) or 'None',
            'Selected limits': ' | '.join(selected['labels'][k] for k in ('return','reserve','risk')),
            'Original mandate fully verified': 'NOT TESTED',
            'Live capital authorized': 'No',
            'Annual incremental fee per $10,000': (
                '—' if scenario['incremental_fee_stress_annual_dollars_per_10000'] is None
                else f"${scenario['incremental_fee_stress_annual_dollars_per_10000']:.2f}"
            ),
        })
        allocation_rows.append({
            'Scenario': chart_labels[name],
            'SGOV': weights[0],
            'VGIT': weights[1],
            'VCIT': weights[2],
            'ACWI': weights[3],
        })

    chart_data = pd.DataFrame([
        {
            'Scenario': chart_labels[name],
            'Estimated return (%)': scenarios[name]['return'] * 100,
            'Estimated volatility (%)': scenarios[name]['volatility'] * 100,
            'Mandate verdict': 'PASS' if scenarios[name]['mandate_pass'] else 'FAIL',
        }
        for name in display_names
    ])
    scatter_column, return_column = st.columns(2)
    with scatter_column:
        st.markdown('**Risk vs. estimated return**')
        st.scatter_chart(
            chart_data,
            x='Estimated volatility (%)',
            y='Estimated return (%)',
            color='Mandate verdict',
            height=360,
            alt='Portfolio scenarios plotted by estimated annual volatility and estimated annual return.',
        )
        st.caption('Up and left indicates higher estimated return and lower estimated risk; thresholds are 6.5% for both axes.')
    with return_column:
        st.markdown('**Estimated return by scenario**')
        st.bar_chart(
            chart_data,
            x='Scenario',
            y='Estimated return (%)',
            color='Mandate verdict',
            height=360,
            alt='Estimated annual return for each portfolio scenario, colored by proposed mandate verdict.',
        )
        st.caption('Historical estimates are not forecasts. The 6.5% objective is the proposed threshold.')
    st.markdown('**Allocation mix by scenario**')
    st.bar_chart(
        pd.DataFrame(allocation_rows),
        x='Scenario',
        y=['SGOV', 'VGIT', 'VCIT', 'ACWI'],
        stack=True,
        height=420,
        alt='Stacked portfolio weights by scenario for SGOV, VGIT, VCIT, and ACWI.',
    )
    st.caption('Each bar totals 100%; weights are percentages of the modeled portfolio.')

    st.dataframe(pd.DataFrame(rows), hide_index=True, width='stretch')
    st.caption(
        'Return and volatility are in-sample historical estimates, not forecasts or realized portfolio outcomes. '
        'The estimate and fee stresses are separate, not a combined scenario. Grid search uses 5% increments.'
    )
    download_columns = st.columns(2)
    download_columns[0].download_button(
        'Download visible model output',
        data=(ROOT / 'outputs' / 'VISIBLE_OUTPUT.md').read_bytes(),
        file_name='VISIBLE_OUTPUT.md',
        mime='text/markdown',
    )
    download_columns[1].download_button(
        'Download frozen committee results (JSON)',
        data=json.dumps(results, indent=2),
        file_name='committee_snapshot.json',
        mime='application/json',
    )

    st.subheader('Decision and reversal conditions')
    st.markdown(
        'Continue only as a **simulation-only pilot**. Stop or reverse if the confirmed mandate differs '
        'from the proposed rules, a required input is missing or mistimed, no allocation meets every '
        'unchanged rule, or paper outcomes and cost evidence undermine the assumptions. Live use stays '
        'deferred pending client approval and independent validation.'
    )
    st.write('Reverse the original 65/35 target if its estimated return falls below 6.5%, volatility exceeds 6.5%, or reserve coverage is below $3m. '
             'A one-percentage-point ACWI return haircut already fails the fixed target; doubled operating fees and the assumed 25 bp annual trading drag also fail it separately. '
             'A 5% volatility ceiling leaves no feasible grid portfolio under the unchanged return target. '
             'Reopen the allocation decision if the 36-month window is preferred, eligibility changes, costs are unsupported, or original liquidity/turnover/loss controls remain unresolved. '
             'Feasibility after reoptimization permits further paper review only; it never authorizes live capital.')
    with st.expander('Read the full decision memo draft'):
        st.markdown(read_markdown('docs/decision-memo.md'))
    with st.expander("Mason's locked allocation comparison"):
        render_mason_record(ROOT)


def show_market_data_and_timing(prices, source, results):
    st.subheader('Frozen portfolio data')
    price_hash = hashlib.sha256((ROOT / 'prices.csv').read_bytes()).hexdigest()
    source_hash = hashlib.sha256((ROOT / 'data_sources.json').read_bytes()).hexdigest()
    if price_hash == controls.PRICE_HASH and source_hash == controls.SOURCE_HASH:
        st.success('Saved prices and provenance match the verified snapshot hashes.')
    else:
        st.error(
            'STOP: a saved price or provenance hash differs from the verified snapshot. '
            'Do not use the descriptive signal or treat saved outputs as verified.'
        )
    st.write(
        f"Provider: {source['provider']} | Field: {source['field']} | Downloaded: "
        f"{source['downloaded_at_utc']} | Window: {results['price_window']}."
    )
    st.caption(
        f"{source['price_rows']} monthly adjusted-price observations create {source['monthly_return_rows']} "
        'monthly returns. Sampling takes the final available daily observation in each completed month; '
        'no missing months are filled.'
    )
    indexed_prices = prices.div(prices.iloc[0]).mul(100)
    indexed_prices.index = pd.to_datetime(indexed_prices.index)
    indexed_prices.index = indexed_prices.index.strftime('%Y-%m')
    indexed_prices.index.name = 'Month'
    st.markdown('**Growth of 100 from the first adjusted-price observation**')
    chart_data = indexed_prices.reset_index()
    st.line_chart(
        chart_data,
        x='Month',
        y=list(prices.columns),
        y_label='Index (first month = 100)',
    )
    st.caption('Adjusted prices include distributions as represented in the saved provider data; this is not a portfolio backtest.')
    with st.expander('Source definition and retrieval metadata'):
        st.json(source)
        st.caption(f'prices.csv SHA-256: `{price_hash}`')
        st.caption(f'data_sources.json SHA-256: `{source_hash}`')
    st.caption(
        'The frozen Yahoo Finance data are retained for this coursework reproduction; subsequent adjusted-price '
        'revisions are possible, and redistribution/licensing terms were not independently cleared. No live market '
        'or SEC request is made by this app. No personal data is used.'
    )

    returns = prices.pct_change(fill_method=None).dropna()
    annual_summary = pd.DataFrame({
        'Annualized arithmetic return (%)': returns.mean().mul(12).mul(100),
        'Annualized sample volatility (%)': returns.std(ddof=1).mul(12 ** 0.5).mul(100),
    })
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('**All-month estimates**')
        st.dataframe(annual_summary.round(4), width='stretch')
    with c2:
        st.markdown('**Monthly return correlation**')
        st.dataframe(returns.corr().round(4), width='stretch')
    st.markdown('**Saved month-end adjusted closes**')
    st.dataframe(prices.tail(12), width='stretch')
    st.markdown('**Annualized return and volatility estimates by fund**')
    st.scatter_chart(
        annual_summary.reset_index().rename(columns={'index': 'Fund'}),
        x='Annualized sample volatility (%)',
        y='Annualized arithmetic return (%)',
        color='Fund',
        height=360,
        alt='Fund estimates plotted by annualized sample volatility and annualized arithmetic return.',
    )
    st.caption('These are asset-level estimates from the same historical window, not expected future performance.')

    st.divider()
    st.subheader('Point-in-time signal and admission rule')
    pit = results['point_in_time_signal']
    signal_rows = pd.DataFrame([
        {'Fund': fund, 'September 2026 simple return (%)': value * 100}
        for fund, value in pit['simple_returns'].items()
    ])
    st.dataframe(signal_rows, hide_index=True, width='stretch')
    st.info(
        f"Signal = {pit['latest_completed_month']} adjusted close / {pit['prior_month']} adjusted close − 1. "
        f"Frozen snapshot retrieved {pit['downloaded_at_utc']}. Use only for decisions strictly after retrieval."
    )
    st.warning(
        'This is descriptive context, not an optimizer predictor. Current Yahoo adjusted-price vintages are '
        'not a historical archive: do not claim these exact observations were known at older decision dates.'
    )
    with st.expander('Lab 16: synthetic as-of panel, row funnel, and sanity check'):
        st.markdown(read_markdown('evidence/Lab 16/asof_results.md'))
    with st.expander('Lab 17: Project 2 data-admission analysis'):
        st.markdown(read_markdown('evidence/Lab 17/Project2_data_admission.md'))
    with st.expander('Lab 17: DGS10 context card (not an optimizer input)'):
        st.markdown(read_markdown('evidence/Lab 17/DGS10_data_card.md'))


def company_records(ticker):
    path = EVIDENCE / 'Lab 19' / 'results' / ticker / 'analysis.json'
    if not path.exists():
        raise FileNotFoundError(f'Saved Lab 19 analysis is missing: {path.name}')
    data = json.loads(path.read_text(encoding='utf-8'))
    return data


def render_company_panel():
    st.subheader('Separate company-screening research | Labs 18–19')
    st.warning(
        'These SEC company screens are a separate educational research exercise. They do not feed the ETF '
        'optimizer, are not investment recommendations, and should not be read as a Project 2 portfolio signal.'
    )
    ticker = st.selectbox('Saved company case', ['AAPL', 'COST'], key='company_case')
    data = company_records(ticker)
    rows = data['rows']
    revenue_start = rows[0]['revenue']
    revenue_end = rows[-1]['revenue']
    revenue_cagr = (revenue_end / revenue_start) ** (1 / (len(rows) - 1)) - 1
    latest = rows[-1]
    latest_rd = latest.get('research_to_revenue')

    st.markdown(f"**{data['company']} ({ticker})** | SEC Company Facts, five saved annual periods.")
    st.caption(
        'The saved Company Facts pulls use filings through early November 2026. AAPL selection is documented '
        'in the Lab 19 ACWI-holdings research; these results are separate from the November 17 portfolio model.'
    )
    headline_top = st.columns(2)
    headline_top[0].metric('Five-year revenue CAGR', f'{revenue_cagr:.2%}')
    headline_top[1].metric('Latest ROE', f"{latest['roe']:.1%}")
    headline_bottom = st.columns(2)
    headline_bottom[0].metric('Latest owner earnings', f"${latest['owner_earnings'] / 1e6:,.0f}m")
    headline_bottom[1].metric(
        'Latest R&D / revenue',
        'Not known' if not isinstance(latest_rd, (int, float)) else f'{latest_rd:.2%}',
    )

    display = []
    for row in rows:
        rd_value = row.get('research_to_revenue')
        display.append({
            'Fiscal year end': row['fiscal_year_end'],
            'Revenue ($m)': row['revenue'] / 1e6,
            'Net income ($m)': row['net_income'] / 1e6,
            'Operating cash flow ($m)': row['operating_cash_flow'] / 1e6,
            'ROE (%)': row['roe'] * 100,
            'Owner earnings ($m)': row['owner_earnings'] / 1e6,
            'Liabilities / equity': row['liabilities_to_equity'],
            'R&D / revenue (%)': None if not isinstance(rd_value, (int, float)) else rd_value * 100,
        })
    st.dataframe(pd.DataFrame(display).round(2), hide_index=True, width='stretch')
    financial_trend = pd.DataFrame({
        'Fiscal year': [row['fiscal_year_end'][:4] for row in rows],
        'Revenue': [row['revenue'] / 1e6 for row in rows],
        'Operating cash flow': [row['operating_cash_flow'] / 1e6 for row in rows],
        'Owner earnings (simplified)': [row['owner_earnings'] / 1e6 for row in rows],
    })
    st.markdown('**Five-year financial trend (USD millions)**')
    st.line_chart(
        financial_trend,
        x='Fiscal year',
        y=['Revenue', 'Operating cash flow', 'Owner earnings (simplified)'],
        height=360,
        alt='Company revenue, operating cash flow, and simplified owner earnings by fiscal year.',
    )
    company_ratios = pd.DataFrame({
        'Fiscal year': [row['fiscal_year_end'][:4] for row in rows],
        'ROE (%)': [row['roe'] * 100 for row in rows],
        'R&D / revenue (%)': [
            None if not isinstance(row.get('research_to_revenue'), (int, float))
            else row['research_to_revenue'] * 100
            for row in rows
        ],
    })
    st.markdown('**Profitability and research intensity checks**')
    st.line_chart(
        company_ratios,
        x='Fiscal year',
        y=['ROE (%)', 'R&D / revenue (%)'],
        height=300,
        alt='Company return on equity and R&D as a percent of revenue by fiscal year.',
    )

    control_columns = st.columns(2)
    growth_hurdle = control_columns[0].slider(
        'Wood-style revenue CAGR screen (%)', min_value=0, max_value=25, value=15, key='growth_hurdle'
    ) / 100
    rd_hurdle = control_columns[1].slider(
        'R&D / revenue screen (%)', min_value=0, max_value=15, value=5, key='rd_hurdle'
    ) / 100
    pass_growth = revenue_cagr >= growth_hurdle
    growth_label = 'PASS' if pass_growth else 'FAIL'
    if isinstance(latest_rd, (int, float)):
        rd_label = 'PASS' if latest_rd >= rd_hurdle else 'FAIL'
    else:
        rd_label = 'NOT KNOWN'
    result_columns = st.columns(2)
    result_columns[0].metric('Revenue growth threshold check', growth_label)
    result_columns[0].caption(f'{revenue_cagr:.2%} observed CAGR vs {growth_hurdle:.2%} selected threshold.')
    result_columns[1].metric('Latest R&D threshold check', rd_label)
    result_columns[1].caption(
        'A missing issuer fact remains not known; a threshold change does not create missing data.'
    )
    st.caption(
        'Threshold controls reproduce only two screen predicates. The Lab 19 Buffett/Wood/Burry panel has '
        'shared underlying facts and correlated code; its perspectives are not independent witnesses.'
    )

    memo_options = {
        'Saved numeric evidence': 'numbers.md',
        'Buffett-inspired AI simulation': 'memo.md',
        'Wood-inspired AI simulation': 'cathie_memo.md',
        'Burry-inspired AI simulation': 'burry_memo.md',
        'Threshold probe record': 'threshold_probe.md',
    }
    memo_choice = st.selectbox('Company evidence to inspect', list(memo_options), key='company_evidence')
    memo_path = EVIDENCE / 'Lab 19' / 'results' / ticker / memo_options[memo_choice]
    st.markdown(memo_path.read_text(encoding='utf-8'))
    st.caption('AI-written company memos are judgment examples; numeric checks are the reproducible outputs.')

    with st.expander('Lab 18 and Lab 19 workflow limits'):
        st.markdown(read_markdown('evidence/Lab 18/README.txt'))
        st.markdown(read_markdown('evidence/Lab 19/README.md'))


def render_lab_timeline():
    st.subheader('Coursework-to-product map')
    rows = [
        ('Lab 13', 'Personal mandate', 'Recovered personal-client mandate; see bundled Lab 13 evidence.'),
        ('Lab 14', 'Objective and baseline rules', '6.5% return target, inherited 40/60 reference benchmark, baseline verdicts.'),
        ('Lab 15', 'Fund data and constrained search', 'Four-fund monthly history, covariance, 5% grid, estimation-window and return stresses.'),
        ('Lab 16', 'Publication timing', 'Synthetic as-of row-funnel exercise; signal must use only eligible observations.'),
        ('Lab 17', 'Data admission and vintage limits', 'Frozen fund snapshot gate, provenance, adjusted-price vintage limitation, DGS10 context.'),
        ('Lab 18', 'SEC extraction and Buffett-style check', 'Saved company screen workflow; SEC-derived values and AI memo are separate evidence types.'),
        ('Lab 19', 'Three-perspective company panel', 'AAPL/COST facts and threshold-sensitive, non-independent analytical perspectives.'),
        ('Lab 20', 'Project 2 checkout', 'Reproduction, changed-input analysis and remaining human evidence boundaries.'),
        ('Project 2 prep', 'Decision and controls', 'Proposed mandate, committee memo, fee stress, signal card, validation and submission records.'),
    ]
    st.dataframe(
        pd.DataFrame(rows, columns=['Source', 'Contribution', 'How it is used here']),
        hide_index=True,
        width='stretch',
    )
    st.info(
        'Lab 13 has been recovered and its personal-client section is the pilot source. '
        'The proposed mandate is available under Project 2 preparation.'
    )

    st.subheader('Evidence browser')
    evidence_docs = {
        'Lab 13 mandate source': 'evidence/Lab 13/Lab13.md',
        'Proposed educational mandate': 'docs/proposed-mandate.md',
        'Committee decision memo': 'docs/decision-memo.md',
        'Week 12 model-risk response': 'docs/week12-prework.md',
        'Signal data card': 'docs/signal-data-card.md',
        'Operating-fee data card': 'docs/cost-data-card.md',
        'Local requirement audit': 'docs/local-audit.md',
        'Validation and AI-use record': 'docs/validation-and-ai-use.md',
        'Lab 14 mandate evidence': 'evidence/Lab14/lab14.md',
        'Lab 15 fund analysis': 'evidence/lab 15/lab15.md',
        'Lab 16 as-of test': 'evidence/Lab 16/asof_results.md',
        'Lab 17 data admission': 'evidence/Lab 17/Project2_data_admission.md',
        'Lab 18 SEC screening workflow': 'evidence/Lab 18/README.txt',
        'Lab 19 research panel': 'evidence/Lab 19/README.md',
        'Lab 20 Project 2 checkout': 'evidence/lab 20/lab20.md',
    }
    selected_doc = st.selectbox('Choose a saved lab or prep record', list(evidence_docs), key='evidence_document')
    st.markdown(read_markdown(evidence_docs[selected_doc]))


def render_validation(results):
    st.subheader('Validation and reproducibility')
    render_mason_record(ROOT)
    from chronological import run as chronological_run
    with st.expander('Data integrity and chronological robustness', expanded=True):
        try:
            audited = verify_frozen(ROOT)
            st.success('Frozen source hashes, recorded timing and raw-to-monthly transformations verified.')
            st.caption(audited['limitation'])
            diagnostic = chronological_run(audited['prices'])
            if diagnostic['constrained_evaluation'] is None:
                st.warning(diagnostic['status'])
            else:
                st.write(diagnostic['status'])
            st.caption(diagnostic['limitations'])
            st.json(diagnostic)
        except (OSError,ValueError,KeyError,TypeError) as error:
            st.error(f'STOP: validation unavailable: {error}')
    with st.expander('Blank human validation templates'):
        for label,name in [('Your AI-off Locked Changed-Input Record','templates/AI_OFF_LOCKED_CHANGED_INPUT.md'),
                           ('Independent partner cold run','templates/PARTNER_COLD_RUN.md')]:
            st.download_button(label,(ROOT/name).read_bytes(),Path(name).name,'text/markdown')
        st.caption('Unfilled templates only. No input selection, prediction, human completion or independent run is supplied by the assistant.')
    with st.expander('Validation controls, source recheck and limitations'):
        st.markdown(read_markdown('docs/validation-controls.md'))
    all_checks = ROOT/'outputs/all-tests.json'
    if all_checks.exists():
        all_record = json.loads(all_checks.read_text(encoding='utf-8'))
        st.write('Latest automated suite status: ' + all_record['status'])
        st.caption(all_record['scope'])
        st.dataframe([{'Suite':r['suite'],'Status':r['status'],'Exit code':r['exit_code']} for r in all_record['results']], hide_index=True)
    verification_path = ROOT / 'outputs' / 'prep-verification.json'
    if verification_path.exists():
        verification = json.loads(verification_path.read_text(encoding='utf-8'))
        summary = st.columns(3)
        summary[0].metric('App/package checks', str(len(verification['app_checks'])))
        summary[1].metric('Local links checked', str(verification['local_document_links_checked']))
        summary[2].metric('Latest saved verification', verification['date'])
        st.dataframe(
            pd.DataFrame({'Verified check': verification['app_checks']}),
            hide_index=True,
            width='stretch',
        )
        st.caption(verification['scope'])
    else:
        st.warning('No saved verification record is available. Run `uv run --locked python verify_prework.py`.')

    st.subheader('Validation limits that govern the recommendation')
    st.markdown(
        '- Same-sample baselines and arithmetic reproduction are implementation checks, not predictive validation.\n'
        '- No untouched holdout or prospective return history is available; trading costs use an assumed 25 bp annual stress.\n'
        '- The volatility limit and mandate are illustrative until the student/client approves them.\n'
        '- Company-screening views do not provide independent validation of the ETF model.\n'
        '- A passing estimate is not proof of future performance; keep the recommendation simulation-only.'
    )
    st.subheader('Archived AI-assisted locked test — not your AI-off record')
    st.json(json.loads((ROOT / 'docs/locked-input.json').read_text()))
    receipt = ROOT / 'docs/locked-commit.json'
    outcome = ROOT / 'outputs/locked-result.json'
    if receipt.exists():
        st.json(json.loads(receipt.read_text()))
    else:
        st.warning('Pending GitHub pre-run commit. Locked test has not been executed.')
    if outcome.exists():
        st.json(json.loads(outcome.read_text()))
    st.caption('AI-assisted locked prediction, as authorized; no AI-off authorship claimed.')
    with st.expander('Saved model-run metadata and full scenario output'):
        st.json(results)
    with st.expander('Validation record and limitations'):
        st.markdown(read_markdown('docs/validation-and-ai-use.md'))


try:
    # Keep section navigation available for repair/inspection when a sealed input fails.
    # Portfolio sections enforce the shared gate below; research evidence stays accessible.
    results = None
    prices = pd.read_csv(ROOT / 'prices.csv', index_col=0)
    source = json.loads((ROOT / 'data_sources.json').read_text(encoding='utf-8'))

    section = st.sidebar.radio('App section', [
        'Committee dashboard',
        'Mandate reconciliation',
        'Interactive portfolio model',
        'Data & timing',
        'Company research & labs',
        'Validation',
    ], key='app_section')
    if section in ('Committee dashboard','Mandate reconciliation','Validation','Data & timing'):
        results = load_committee(ROOT)
    if section == 'Committee dashboard':
        show_portfolio_summary(results)
        st.caption('PASS/FAIL above covers the proposed numerical pilot only. Open Mandate reconciliation for every original Lab 13 requirement and unresolved controls.')
    elif section == 'Mandate reconciliation':
        render_reconciliation(results)
    elif section == 'Interactive portfolio model':
        render_portfolio()
    elif section == 'Data & timing':
        show_market_data_and_timing(prices, source, results)
    elif section == 'Company research & labs':
        render_company_panel()
        st.divider()
        render_lab_timeline()
    else:
        render_validation(results)
except (OSError, ValueError, KeyError, TypeError) as error:
    st.error(f'Unable to load the saved Project 2 evidence: {error}')
