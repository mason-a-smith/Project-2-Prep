"""Streamlit view over the bundled deterministic SEC engine."""
import importlib.util
import json
import os
from pathlib import Path
import pandas as pd
import streamlit as st
import panel

BASE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('sec_facts', BASE / 'buffett-sec/scripts/sec_facts.py')
engine = panel.sec
st.set_page_config(page_title='Buffett business review', layout='wide')
st.title('Buffett business review')
st.subheader('Lab 19: Buffett / Cathie Wood / Burry panel')
st.caption('data from SEC EDGAR; built with AI help, a learning demonstration, not investment advice.')
ticker = st.text_input('Ticker', 'COST').strip().upper()
ua = st.text_input('SEC User-Agent (name and real email)', os.getenv('SEC_USER_AGENT', 'Mason Smith '))
if st.button('Download latest SEC facts'):
    try:
        with st.spinner('Downloading SEC 10-K facts…'):
            panel.download(ticker, BASE / 'results', ua)
        st.success('Saved source snapshots and results. Ask Codex to use buffett-sec to write or refresh the memo.')
    except Exception as exc:
        st.error(str(exc))
if not engine.re.fullmatch(r'[A-Z0-9.-]{1,12}', ticker):
    st.warning('Enter a ticker using letters, digits, dots or hyphens.')
    st.stop()
folder = BASE / 'results' / ticker
if not (folder / 'analysis.json').exists():
    st.info('No saved SEC results for this ticker. Enter your User-Agent and download facts.')
    st.stop()
result = json.loads((folder / 'analysis.json').read_text(encoding='utf-8'))
threshold = st.selectbox('Cathie Wood revenue growth threshold', [.15, .05], format_func=lambda v: f'{v:.0%}')
result = panel.enrich(result, threshold)
st.subheader(result['company'])
st.caption('USD millions. Checks use unrounded values. Latest available filings can revise earlier fiscal periods; this is not a historical as-of dataset.')
chart = pd.DataFrame([{'Fiscal year end': r['fiscal_year_end'],
    'Owner earnings': r['owner_earnings'] / 1e6 if isinstance(r['owner_earnings'], (int, float)) else None,
    'Net income': r['net_income'] / 1e6 if isinstance(r['net_income'], (int, float)) else None} for r in result['rows']]).set_index('Fiscal year end')
st.line_chart(chart, y_label='USD millions')
keys = ['revenue', 'net_income', 'operating_cash_flow', 'capital_spending', 'equity', 'roe', 'owner_earnings', 'liabilities', 'liabilities_to_equity']
st.dataframe(pd.DataFrame([{'Fiscal year end': r['fiscal_year_end'], **{k: engine.display_value(k, r[k]) for k in keys}} for r in result['rows']]), hide_index=True)
st.table(pd.DataFrame(result['checks'].items(), columns=['Buffett check', 'Result']))
st.subheader('Investor panel')
st.table(pd.DataFrame([{'Investor': investor, 'Check': check, 'Result': status}
    for investor, checks in result['panel'].items() for check, status in checks.items()]))
st.markdown(panel.printed_table(result).split('## Additional panel facts')[1].split('## Panel')[0])
all_memos = {}
for column, investor, filename in zip(st.columns(3), result['panel'], ['memo.md', 'cathie_memo.md', 'burry_memo.md']):
    with column:
        st.subheader(investor)
        path = folder / filename
        content = path.read_text(encoding='utf-8') if path.exists() else ''
        all_memos[investor] = st.text_area(investor + ' memo and verdict', content, height=280, key=f'{investor}_{ticker}')
        st.markdown(all_memos[investor] or 'Memo pending: read the printed facts first.')
        if investor == 'Cathie Wood':
            st.caption('Kept threshold: 15%, to preserve the assigned growth screen; 5% is a sensitivity probe only.')
        if st.button('Save ' + investor + ' memo'):
            path.write_text(all_memos[investor], encoding='utf-8')
flags = panel.memo_flags(all_memos, result)
if any(flags.values()):
    st.error('Unprinted-number flag across all memos: ' + str(flags))
else:
    st.success('Unprinted-number flag: clear for entered memos; missing memos remain pending. Numeric matching does not validate context.')
with st.expander('XBRL tags, periods, filing dates and source snapshots'):
    st.json(result)
st.subheader('Memo — AI judgment')
memo_path = folder / 'memo.md'
saved_memo = memo_path.read_text(encoding='utf-8') if memo_path.exists() else ''
memo = st.text_area('Edit memo (try typing 40.0% as a provenance probe)', saved_memo, height=240, key=f'memo_{ticker}')
bad = panel.unsupported_numbers(memo, result)
if bad:
    st.error('Numbers the script did not print: ' + ', '.join(bad))
elif memo:
    st.success('All numeric tokens appear in script output. This does not validate their meaning or context.')
else:
    st.info('Ask Codex to use buffett-sec on this ticker and save memo.md. The app does not replace AI judgment with a formula.')
if st.button('Save memo'):
    memo_path.write_text(memo, encoding='utf-8')
    st.success('Memo saved; any unsupported-number warning still applies.')
st.markdown(memo)
decision_path = folder / 'decision.txt'
decision = st.text_input('Your decision: do you trust this verdict, and why?', decision_path.read_text(encoding='utf-8') if decision_path.exists() else '', key=f'decision_{ticker}')
if st.button('Save my decision'):
    decision_path.write_text(decision, encoding='utf-8')
    st.success('Your decision saved.')
st.download_button('Download script output', panel.printed_table(result), file_name=f'{ticker}_numbers.md')
