"""Compare live extraction with supplied class reference; never feeds extraction."""
import json
from pathlib import Path
import panel

root = Path(__file__).resolve().parent
path = root / 'results/COST/analysis.json'
if not path.exists():
    report = 'PENDING: no live COST SEC extraction. Class reference is not a data source.\n'
else:
    result = panel.enrich(json.loads(path.read_text(encoding='utf-8')))
    dates = ['2022-08-28', '2023-09-03', '2024-09-01', '2025-08-31', '2026-08-30']
    ratios = ['2.11', '1.75', '1.96', '1.64', '1.49']
    expected = ['pass', 'pass', 'pass', 'fail', 'not known', 'pass', 'pass']
    comparisons = {
        'Fiscal ends': ([r['fiscal_year_end'] for r in result['rows']], dates),
        'Liabilities / equity': ([panel.sec.display_value('liabilities_to_equity', r['liabilities_to_equity']) for r in result['rows']], ratios),
        'R&D missing': ([r['research_and_development'] for r in result['rows']], ['not found'] * 5),
        'Revenue CAGR': (f"{result['revenue_cagr']:.2%}" if panel.numeric(result['revenue_cagr']) else result['revenue_cagr'], '7.51%'),
        'Panel': ([v for checks in result['panel'].values() for v in checks.values()], expected),
        'Threshold probe': (list(panel.cathie_checks(result['rows'], .05).values()), ['pass', 'not known']),
    }
    report = '\n'.join(f"{'MATCH' if actual == wanted else 'DISCREPANCY'} {name}: actual={actual}; class={wanted}" for name, (actual, wanted) in comparisons.items()) + '\n'
(root / 'verification.txt').write_text(report, encoding='utf-8')
print(report)
