"""Verify packaging separately from any required independent partner review."""
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import hashlib
import numpy as np
import pandas as pd
import audit_controls as controls
import portfolio as engine
from urllib.parse import unquote

from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parent


def main():
    # Same installed environment, fresh directory: this is not a clean-machine test.
    fresh = Path(tempfile.mkdtemp(prefix='project2-prep-'))
    target = fresh / 'Project2'
    shutil.copytree(ROOT, target, ignore=shutil.ignore_patterns('.venv', '__pycache__', '*.pyc'))
    result = subprocess.run([sys.executable, str(target / 'run.py')], cwd=fresh,
                            capture_output=True, text=True, encoding='utf-8', errors='replace')
    if result.returncode:
        raise RuntimeError(result.stdout + '\n' + result.stderr)
    actual = json.loads((target / 'outputs/results.json').read_text(encoding='utf-8'))
    assert actual['scenarios']['Constrained baseline']['weights'] == [.65, 0, 0, .35]
    assert actual['scenarios']['Reoptimized stress']['weights'] == [.6, 0, 0, .4]
    assert actual['scenarios']['Reoptimized fee stress']['weights'] == [.6, 0, 0, .4]
    fixed = actual['scenarios']['Fixed baseline under fee stress']
    assert not fixed['mandate_pass']
    np.testing.assert_allclose(fixed['return'], .06493754902889966, atol=1e-12, rtol=0)
    assert abs(fixed['incremental_fee_stress_annual_dollars_per_10000'] - 17.05) < 1e-12
    # Independent September/August formula, provenance gate, and fee subtraction.
    prices = pd.read_csv(ROOT / 'prices.csv', index_col=0)
    pit = controls.signal()
    np.testing.assert_allclose(list(pit['simple_returns'].values()),
                               prices.iloc[-1] / prices.iloc[-2] - 1, atol=1e-12, rtol=0)
    assert not controls.signal('2026-09-30T23:59:59Z')['available']
    assert not controls.signal('2026-10-22T21:27:42.703541Z')['available']
    assert controls.signal('2026-10-22T21:27:42.703542Z')['available']
    assert not controls.signal(verified_local=False)['available']
    assets, corr = engine.estimate_from_csv(ROOT / 'prices.csv')
    for asset in assets:
        asset['reserve_eligible'] = asset['name'] == 'SGOV'
    stressed = controls.fee_stressed(assets)
    np.testing.assert_allclose([a['return'] - b['return'] for a, b in zip(assets, stressed)],
                               list(controls.FEES.values()), atol=1e-12, rtol=0)
    assert controls.search(assets, corr, ceiling=.05) is None
    baseline = actual['scenarios']['Constrained baseline']
    assert controls.evaluate(baseline['weights'], assets, corr, ceiling=.05)['checks']['volatility_at_most_6_5_percent'] is False
    for filename, expected in json.loads((ROOT / 'outputs/preserved-input-hashes.json').read_text()).items():
        assert hashlib.sha256((ROOT / filename).read_bytes()).hexdigest() == expected, filename

    # AppTest shares this process's module cache; bind the imported helper to
    # the copied package so source-integrity tests exercise copied inputs.
    controls.ROOT = target
    app = AppTest.from_file(str(target / 'app.py'), default_timeout=30).run()
    assert not app.exception, app.exception
    dashboard = next(
        d.value for d in app.dataframe
        if 'Scenario' in d.value.columns and 'Mandate verdict' in d.value.columns
    )
    assert dashboard.loc[
        dashboard['Scenario'] == 'Constrained baseline', 'Mandate verdict'
    ].iloc[0] == 'PASS'
    assert sum(element.type == 'vega_lite_chart' for element in app) == 3
    app.radio[0].set_value('Company research & labs').run()
    assert not app.exception, app.exception
    assert sum(element.type == 'vega_lite_chart' for element in app) == 2
    company_data = next(d.value for d in app.dataframe if 'Fiscal year end' in d.value.columns)
    assert len(company_data) == 5
    next(
        selector for selector in app.selectbox
        if selector.label == 'Saved company case'
    ).select('COST').run()
    assert not app.exception, app.exception
    cost_company_data = next(d.value for d in app.dataframe if 'Fiscal year end' in d.value.columns)
    assert cost_company_data['R&D / revenue (%)'].isna().all()
    next(
        slider for slider in app.slider
        if slider.label == 'Wood-style revenue CAGR screen (%)'
    ).set_value(5).run()
    assert next(
        metric for metric in app.metric
        if metric.label == 'Revenue growth threshold check'
    ).value == 'PASS'
    assert next(
        metric for metric in app.metric
        if metric.label == 'Latest R&D threshold check'
    ).value == 'NOT KNOWN'
    assert sum(element.type == 'vega_lite_chart' for element in app) == 2
    next(
        selector for selector in app.selectbox
        if selector.label == 'Saved company case'
    ).select('AAPL').run()
    assert not app.exception, app.exception
    app.radio[0].set_value('Interactive portfolio model').run()
    assert not app.exception, app.exception
    assert sum(element.type == 'vega_lite_chart' for element in app) == 2
    assert app.table[0].value.iloc[-1]['Weight (%)'] == '35.00'
    comparison = next(d.value for d in app.dataframe if 'Portfolio' in d.value.columns).set_index('Portfolio')
    for label in ('Equal weight', 'Inverse volatility', 'Constrained portfolio'):
        saved_label = 'Constrained baseline' if label == 'Constrained portfolio' else label
        saved = actual['scenarios'][saved_label]
        assert abs(comparison.loc[label, 'Return (%)'] - saved['return'] * 100) < 1e-10
        assert comparison.loc[label, 'Return rule'] == ('PASS' if saved['checks']['return_at_least_6_5_percent'] else 'FAIL')
        assert comparison.loc[label, 'Reserve rule'] == 'PASS'
        assert comparison.loc[label, 'Risk rule'] == 'PASS'
    cost_table = next(
        d.value for d in app.dataframe
        if 'Scenario' in d.value.columns and 'Verdict' in d.value.columns
    ).set_index('Scenario')
    assert cost_table.loc['Fixed current allocation', 'Verdict'] == 'FAIL'
    assert cost_table.loc['Reoptimized fee stress', 'Verdict'] == 'PASS'
    np.testing.assert_allclose(
        cost_table.loc['Fixed current allocation', 'Incremental annual dollars per $10,000'],
        17.05, atol=1e-10)
    np.testing.assert_allclose(
        cost_table.loc['Reoptimized fee stress', 'Incremental annual dollars per $10,000'],
        18.20, atol=1e-10)
    np.testing.assert_allclose(cost_table.loc['Reoptimized fee stress', 'Stressed return (%)'],
                               actual['scenarios']['Reoptimized fee stress']['return'] * 100, atol=1e-10)
    assert any('STOP live allocation' in item.value for item in app.error)
    assert any('Transaction costs unresolved' in item.value for item in app.warning)
    next(control for control in app.checkbox if control.label == 'Use last 36 months').check().run()
    assert not app.exception, app.exception
    assert app.table[0].value.iloc[-1]['Weight (%)'] == '15.00'
    next(control for control in app.checkbox if control.label == 'Use last 36 months').uncheck().run()
    acwi = next(control for control in app.number_input if control.label == 'ACWI expected return (%)')
    acwi.set_value(11.141317140920848).run()
    assert not app.exception, app.exception
    assert app.table[0].value.iloc[-1]['Weight (%)'] == '40.00'
    next(control for control in app.number_input if control.label == 'Reserve minimum (%)').set_value(100).run()
    assert not app.exception, app.exception
    assert any('no mix meets the objective' in warning.value for warning in app.warning)

    dataset_selector = next(
        selector for selector in app.selectbox
        if selector.label == 'Dataset (when no upload)'
    )
    dataset_selector.select('Meridian training').run()
    assert not app.exception, app.exception
    assert any('Signal unavailable' in warning.value for warning in app.warning)
    next(
        selector for selector in app.selectbox
        if selector.label == 'Dataset (when no upload)'
    ).select('Project 2: local prices.csv').run()
    assert not app.exception, app.exception
    next(control for control in app.number_input if control.label == 'Reserve minimum (%)').set_value(3).run()
    next(control for control in app.number_input if control.label == 'Expected return objective (%)').set_value(100).run()
    assert not app.exception, app.exception
    assert any('no mix meets the objective' in warning.value for warning in app.warning)
    # Verify source/price gates on the copied package; originals remain untouched.
    original_prices = (target / 'prices.csv').read_bytes()
    (target / 'prices.csv').write_bytes(original_prices + b'\n')
    next(control for control in app.number_input if control.label == 'Expected return objective (%)').set_value(6.5).run()
    assert not app.exception, app.exception
    assert any('hash differs: prices.csv' in item.value for item in app.error)
    assert not app.table  # stronger gate stops before any allocation is calculated
    (target / 'prices.csv').write_bytes(original_prices)
    original_metadata = (target / 'data_sources.json').read_bytes()
    (target / 'data_sources.json').write_bytes(original_metadata + b'\n')
    app.run()
    assert not app.exception, app.exception
    assert any('hash differs: data_sources.json' in item.value for item in app.error)
    assert not app.table
    app.radio[0].set_value('Data & timing').run()
    assert not app.exception, app.exception
    assert sum(element.type == 'vega_lite_chart' for element in app) == 0
    assert any('hash differs' in item.value for item in app.error)
    (target / 'data_sources.json').write_bytes(original_metadata)
    app.radio[0].set_value('Data & timing').run()
    assert not app.exception, app.exception
    assert sum(element.type == 'vega_lite_chart' for element in app) == 2
    assert any('match the verified snapshot hashes' in item.value for item in app.success)
    app.radio[0].set_value('Validation').run()
    assert not app.exception, app.exception

    checked = 0
    for file in [ROOT / 'README.md', *sorted((ROOT / 'docs').glob('*.md'))]:
        for link in re.findall(r'\]\(([^)]+)\)', file.read_text(encoding='utf-8')):
            if '://' in link or link.startswith('#'):
                continue
            local = (file.parent / unquote(link.split('#')[0])).resolve()
            assert local.exists(), f'Broken local link in {file.name}: {link}'
            checked += 1
    record = {
        'date': '2026-11-23',
        'fresh_directory': str(target),
        'fresh_directory_command': 'Installed Python executable + copied run.py; working directory outside package',
        'fresh_directory_exit_code': result.returncode,
        'environment_limit': 'Same installed dependencies; no independent partner or clean-machine claim',
        'app_checks': ['Integrated dashboard renders risk-return, return-comparison, and allocation charts',
                       'Data page renders price-history and fund risk-return charts',
                       'Company page renders five-year financial-trend charts',
                       'Integrated committee dashboard matches saved model scenarios',
                       'Company-screen view retains missing COST R&D facts and responds to threshold changes',
                       'Default ACWI weight 35%', 'Reduced-return ACWI weight 40%',
                       'Same-sample baseline returns and rule verdicts match runner',
                       'Last-36-month ACWI weight 15%; all-month controls restored',
                       '100% reserves is infeasible without relaxing return objective',
                       'Fee stress fixed/reoptimized verdicts agree with runner; no double deduction',
                       'PIT formula and strict timestamp boundary verified; Meridian unavailable',
                       'Changed snapshot/provenance hashes stop all local portfolio calculation in copied app',
                       'Illustrative risk ceiling rejects infeasible risk without relaxing rules',
                       'Preserved engine, prices, provenance and all evidence hashes unchanged',
                       'Live-use stop and unmodelled transaction costs displayed',
                       '100% objective shows no mix meets the objective'],
        'local_document_links_checked': checked,
        'scope': 'Assistant-run numerical, packaging, and Streamlit AppTest checks; no partner or clean-machine run',
    }
    (ROOT / 'outputs/prep-verification.json').write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(record, indent=2))
    # Keep the fresh copy for inspection; no recursive deletion is performed.


if __name__ == '__main__':
    main()
