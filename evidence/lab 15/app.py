"""Lab 15 interface. Portfolio calculations live exclusively in portfolio.py."""
from copy import deepcopy
from io import BytesIO
from pathlib import Path
import importlib.util
import streamlit as st

# Load fresh on every rerun, including edits made to Meridian correlations.
spec = importlib.util.spec_from_file_location('portfolio_engine', Path(__file__).with_name('portfolio.py'))
engine = importlib.util.module_from_spec(spec)
spec.loader.exec_module(engine)

st.set_page_config(page_title='Lowest-risk portfolio', layout='wide')
st.title('Which mix carries the least risk?')
st.caption('Built with AI help, a learning demonstration, not investment advice.')
objective = st.sidebar.number_input('Expected return objective (%)', value=6.5, step=0.1) / 100
minimum = st.sidebar.number_input('Reserve minimum (%)', min_value=0.0, max_value=100.0, value=3.0, step=1.0) / 100
upload = st.sidebar.file_uploader('Upload prices.csv', type='csv')
dataset = st.sidebar.selectbox('Dataset (when no upload)', ['Project 2: local prices.csv', 'Meridian training'])
recent = st.sidebar.checkbox('Use last 36 months', value=False)
st.sidebar.button('Refresh engine', help='Rerun after saving changes to portfolio.py.')

try:
    if upload is None and dataset == 'Meridian training':
        baseline_sleeves, baseline_corr = deepcopy(engine.SLEEVES), deepcopy(engine.CORRELATIONS)
        sleeves, corr = deepcopy(baseline_sleeves), deepcopy(baseline_corr)
        source_key = 'meridian'
        st.caption('Meridian training estimates. The 36-month switch applies to uploaded prices only.')
    else:
        data = upload.getvalue() if upload is not None else Path(__file__).with_name('prices.csv').read_bytes()
        import hashlib
        source_key = hashlib.sha256(data).hexdigest()
        baseline_sleeves, baseline_corr = engine.estimate_from_csv(BytesIO(data))
        sleeves, corr = engine.estimate_from_csv(BytesIO(data), recent)
        for item in baseline_sleeves + sleeves:
            item['reserve_eligible'] = item['name'] == 'SGOV'
        st.caption('Return estimates: historical arithmetic monthly mean × 12; not a forecast. '
                   'Volatility: sample monthly standard deviation × √12. '
                   'SGOV is selected for the provisional reserve rule. VGIT eligibility is unconfirmed.')
        import pandas as pd
        with st.expander('Historical estimates, correlations, and annualized covariance'):
            names = [s['name'] for s in sleeves]
            st.dataframe(pd.DataFrame([{'Ticker': s['name'], 'Historical return (%)': s['return'] * 100,
                                       'Annual volatility (%)': s['volatility'] * 100} for s in sleeves]), hide_index=True)
            st.write('Correlation matrix')
            st.dataframe(pd.DataFrame(corr, index=names, columns=names))
            st.write('Annualized covariance matrix (decimal return squared)')
            st.dataframe(pd.DataFrame(engine.covariance_matrix(sleeves, corr), index=names, columns=names).style.format('{:.8f}'))
    st.subheader('Edit expected returns and reserve eligibility')
    for i, sleeve in enumerate(sleeves):
        left, right = st.columns([3, 1])
        sleeve['return'] = left.number_input(
            f"{sleeve['name']} expected return (%)", value=sleeve['return'] * 100,
            step=0.1, key=f'{source_key}_{recent}_{i}_return') / 100
        eligible = right.checkbox('Reserve-eligible', value=sleeve['reserve_eligible'],
                                  key=f'{source_key}_{i}_reserve')
        sleeve['reserve_eligible'] = eligible
        baseline_sleeves[i]['reserve_eligible'] = eligible
    baseline = engine.search_portfolio(baseline_sleeves, baseline_corr, objective, minimum)
    result = engine.search_portfolio(sleeves, corr, objective, minimum)

    def display(column, title, answer):
        column.subheader(title)
        if answer is None:
            column.warning('no mix meets the objective')
            return
        column.table([{'Asset': s['name'], 'Weight (%)': f'{w * 100:.2f}'}
                      for s, w in zip(sleeves, answer['weights'])])
        column.metric('Expected return', f"{answer['return']:.2%}")
        column.metric('Volatility', f"{answer['volatility']:.2%}")
        column.metric('Reserve-eligible weight', f"{answer['reserve_weight']:.2%}")

    a, b = st.columns(2)
    display(a, 'Current inputs — lowest-risk mix', result)
    display(b, 'As loaded — all months, original returns', baseline)
    st.caption('Both answers use the current objective, reserve minimum, and eligibility selections. '
               'Search: fully invested, long-only, 5 percentage point increments.')
    if result is not None and baseline is not None:
        change = max(abs(a - b) for a, b in zip(result['weights'], baseline['weights'])) * 100
        st.metric('Largest weight change (percentage points)', f'{change:.2f}')
    else:
        st.info('Largest weight change unavailable unless both cases have a mix.')
except (ValueError, TypeError, KeyError, OSError) as error:
    st.error(str(error))
