"""Reconcile live results to instructor fixture; never change SEC data to match."""
import importlib.util
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('engine', BASE / 'buffett-sec/scripts/sec_facts.py')
e = importlib.util.module_from_spec(spec)
spec.loader.exec_module(e)


def verify():
    report = ['Lab 18 acceptance checks', '']
    cost_path = BASE / 'results/COST/analysis.json'
    if cost_path.exists():
        actual = json.loads(cost_path.read_text(encoding='utf-8'))
        fixture = json.loads((BASE / 'known_answer.json').read_text())
        by_end = {r['fiscal_year_end']: r for r in actual['rows']}
        mismatches = []
        for values in fixture['rows']:
            expected = dict(zip(fixture['columns'], values))
            end = expected['fiscal_year_end']
            if end not in by_end:
                mismatches.append(f'{end}: fiscal year absent from latest five SEC 10-Ks')
                continue
            for key in fixture['columns'][1:]:
                value = by_end[end][key]
                converted = round(value*100, 1) if key == 'roe' and isinstance(value, (int,float)) else value/1e6 if isinstance(value, (int,float)) else value
                if converted != expected[key]:
                    mismatches.append(f'{end} {key}: SEC {converted}; class {expected[key]}')
        report += ['COST: ' + ('MATCH' if not mismatches else 'DISCREPANCIES'), *mismatches]
        report += [f'{key}: {value}' for key, value in actual['checks'].items()]
        assert e.unsupported_numbers('40.0%', actual), '40.0% was not flagged'
        report.append('Hand-typed 40.0%: flagged')
        memo_path = cost_path.parent / 'memo.md'
        report.append('COST memo: ' + (str(e.unsupported_numbers(memo_path.read_text(encoding='utf-8'), actual)) + ' unsupported numbers' if memo_path.exists() else 'pending AI judgment'))
    else:
        report.append('COST: PENDING live SEC download; no fixture substituted')
    jpm_path = BASE / 'results/JPM/analysis.json'
    if jpm_path.exists():
        jpm = json.loads(jpm_path.read_text(encoding='utf-8'))
        missing = all(r['capital_spending'] == 'not found' and r['owner_earnings'] == 'not found' for r in jpm['rows'])
        unknown = all(v == 'not known' for k,v in jpm['checks'].items() if k.startswith('Owner'))
        report.append(f'JPM missing capex/owner earnings: {missing}; unknown owner-earnings checks: {unknown}')
        report.append('JPM memo: ' + ('saved' if (jpm_path.parent/'memo.md').exists() else 'pending AI judgment'))
    else:
        report.append('JPM: PENDING live SEC download')
    report.append('Student trust decision: ' + ('saved' if (BASE/'results/COST/decision.txt').exists() else 'awaiting Mason'))
    text = '\n'.join(report) + '\n'
    (BASE / 'verification.txt').write_text(text, encoding='utf-8')
    print(text)


if __name__ == '__main__':
    verify()
