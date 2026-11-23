"""Calculate every historical estimate through the shared portfolio engine."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import portfolio as p

ROOT = Path(__file__).resolve().parent

def markdown_table(frame, digits=6):
    headers = ['Asset'] + list(frame.columns)
    lines = ['| ' + ' | '.join(headers) + ' |', '| ' + ' | '.join(['---'] * len(headers)) + ' |']
    for index, row in frame.iterrows():
        lines.append('| ' + str(index) + ' | ' + ' | '.join(f'{x:.{digits}f}' for x in row) + ' |')
    return '\n'.join(lines)

def main():
    source = json.loads((ROOT / 'data_sources.json').read_text())
    prices = pd.read_csv(ROOT / 'prices.csv', index_col=0, parse_dates=True)
    returns = prices.pct_change(fill_method=None).iloc[1:]
    returns.to_csv(ROOT / 'monthly_returns.csv', float_format='%.12f', date_format='%Y-%m-%d')
    sections = [
        '# Lab 15 — Project 2 historical estimates',
        'Built with AI help, a learning demonstration, not investment advice.',
        'Universe: SGOV / VGIT / VCIT / ACWI. Prices are actual Yahoo Finance daily adjusted closes sampled on the last trading day of each completed month. No Tuesday training assumptions are used in these historical estimates.',
        f"Downloaded: {source['downloaded_at_utc']}. Price observations: 61, September 2021–September 2026. The first price is the starting anchor, producing exactly 60 monthly returns, October 2021–September 2026. October 2026 is incomplete and excluded.",
        '## Sources',
        '\n'.join(f"- [{t} — Yahoo Finance]({url}), downloaded {source['downloaded_at_utc'][:10]}." for t, url in source['sources'].items()),
        'Raw daily downloads are retained in `raw/`. `data_sources.json` records the provider, field, retrieval timestamp, date boundaries, and yfinance version. Yahoo may revise adjusted prices after subsequent distributions.',
        '## Method',
        'Monthly return = adjusted close / prior adjusted close − 1. Historical expected-return estimate = arithmetic monthly mean × 12 (not CAGR and not a forecast). Annual volatility = sample monthly standard deviation × √12, with ddof=1. Correlation = Pearson correlation of aligned monthly returns. Annual covariance = sample monthly covariance × 12 = correlation × annual volatility_i × annual volatility_j. Covariance is in decimal-return-squared units. No missing months are filled.',
        '## Provisional optimization settings',
        'The 6.5% objective and 3% reserve minimum remain editable defaults from the lab, not confirmed personal mandate terms. Only SGOV counts toward reserves provisionally. VGIT is unchecked because its mandate eligibility is unconfirmed. Neither label is a legal eligibility determination. Searches are long-only, fully invested, on a 5 percentage point grid.',
    ]
    results = {}
    for label, recent in [('all_months', False), ('last_36', True)]:
        sleeves, corr = p.estimate_from_csv(ROOT / 'prices.csv', recent)
        names = [s['name'] for s in sleeves]
        covariance = pd.DataFrame(p.covariance_matrix(sleeves, corr), index=names, columns=names)
        correlation = pd.DataFrame(corr, index=names, columns=names)
        estimates = pd.DataFrame({'Historical expected return (%)': [s['return'] * 100 for s in sleeves],
                                  'Annual volatility (%)': [s['volatility'] * 100 for s in sleeves]}, index=names)
        estimates.index.name = correlation.index.name = covariance.index.name = 'Asset'
        estimates.to_csv(ROOT / f'estimates_{label}.csv', float_format='%.10f')
        correlation.to_csv(ROOT / f'correlations_{label}.csv', float_format='%.12f')
        covariance.to_csv(ROOT / f'covariance_{label}.csv', float_format='%.12f')
        sample = returns.tail(36) if recent else returns
        assert np.allclose(covariance, sample.cov() * 12, atol=1e-12)
        assert np.allclose(np.diag(covariance), np.square([s['volatility'] for s in sleeves]))
        assert np.linalg.eigvalsh(covariance).min() >= -1e-12
        for s in sleeves:
            s['reserve_eligible'] = s['name'] == 'SGOV'
        result = p.search_portfolio(sleeves, corr, .065, .03)
        results[label] = result
        sections += [f'## {"Last 36 monthly returns (October 2023–September 2026)" if recent else "All 60 monthly returns"}',
                     markdown_table(estimates, 4), '### Correlation', markdown_table(correlation),
                     '### Annualized covariance', markdown_table(covariance, 8)]
        if result is None:
            sections.append('Optimization: **no mix meets the objective**.')
        else:
            weights = ' / '.join(f'{w:.0%}' for w in result['weights'])
            sections.append(f"Lowest-risk mix (SGOV / VGIT / VCIT / ACWI): **{weights}**. Historical return estimate **{result['return']:.2%}**, volatility **{result['volatility']:.2%}**, reserve weight **{result['reserve_weight']:.2%}**.")
        benchmark = [0, 0, .4, .6]
        sections.append(f"40% VCIT / 60% ACWI benchmark evaluated using this same historical window: return {p.expected_return(benchmark, sleeves):.2%}, volatility {p.portfolio_volatility(benchmark, covariance.to_numpy()):.2%}. It has 0% reserve weight and fails the provisional reserve rule.")
    if all(results.values()):
        change = max(abs(a-b) for a,b in zip(results['all_months']['weights'], results['last_36']['weights'])) * 100
        sections.append(f'Largest weight change between all months and last 36: **{change:.2f} percentage points**.')
    else:
        sections.append('Largest weight change unavailable because both windows do not have a feasible mix.')
    sections += ['## Run', 'From this folder:\n\n```powershell\nuv run --with streamlit python -m streamlit run app.py\n```\n\nThe app defaults to the local actual-price dataset. Meridian is separately labeled training data. Uploading a file overrides the selected dataset. The last-36 switch recalculates from prices; edited return boxes are scenario assumptions.',
                 'Recalculate saved estimates: `uv run --with streamlit python analyze_prices.py`. Refresh actual prices from Yahoo: `uv run --with yfinance python download_prices.py`, then rerun analysis. The download script fixes this assignment window for reproducibility. `portfolio.py` still prints the original training outputs when executed directly, as required by the lab.']
    sections.append('''## Engine flowchart

```mermaid
flowchart TD
    A[Yahoo daily adjusted closes] --> B[Last actual trading day per completed month]
    B --> C[prices.csv: 61 observations, four funds]
    C --> D[Validate dates and positive aligned prices]
    D --> E[Calculate 60 monthly returns]
    E --> F{Estimation window}
    F --> G[All 60 returns]
    F --> H[Last 36 returns]
    G --> I[Historical mean times 12, sample volatility times square root of 12, correlations]
    H --> I
    I --> J[Covariance from correlation and annual volatilities]
    I --> K[Editable return scenarios and reserve eligibility]
    K --> L[Enumerate long-only fully invested 5-point mixes]
    J --> L
    L --> M[Filter by return objective and reserve minimum]
    M --> N{Feasible mix exists?}
    N -->|Yes| O[Return mix with minimum volatility]
    N -->|No| P[No mix meets the objective]
    O --> Q[App compares current mix with all-month loaded mix]
    P --> Q
```
''')
    (ROOT / 'lab15.md').write_text('\n\n'.join(sections) + '\n', encoding='utf-8')
    (ROOT / 'optimization_results.json').write_text(json.dumps(results, indent=2) + '\n')
    print('Saved lab15.md, monthly returns, estimates, correlations, covariance, and optimization results.')
    print(json.dumps(results, indent=2))

if __name__ == '__main__':
    main()
