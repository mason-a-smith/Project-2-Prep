"""Shared SEC facts; deterministic checks; separately authored persona memos."""
import argparse
import importlib.util
import json
import math
import os
from pathlib import Path

BASE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('sec_facts', BASE / 'buffett-sec/scripts/sec_facts.py')
sec = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sec)
sec.TAGS['research_and_development'] = ['ResearchAndDevelopmentExpense']
sec.FLOW.add('research_and_development')
UNKNOWN = sec.UNKNOWN


def numeric(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def revenue_growth(rows):
    if len(rows) != 5:
        return UNKNOWN
    first, last = rows[0]['revenue'], rows[-1]['revenue']
    return (last / first) ** (1 / 4) - 1 if numeric(first) and first > 0 and numeric(last) and last >= 0 else UNKNOWN


def cathie_checks(rows, growth_threshold=.15):
    growth = revenue_growth(rows)
    growth_check = ('pass' if growth >= growth_threshold else 'fail') if numeric(growth) else UNKNOWN
    latest = rows[-1] if len(rows) == 5 else {}
    revenue, research = latest.get('revenue'), latest.get('research_and_development')
    ratio = research / revenue if numeric(research) and numeric(revenue) and revenue > 0 else UNKNOWN
    research_check = ('pass' if ratio >= .05 else 'fail') if numeric(ratio) else UNKNOWN
    return {f'Revenue CAGR >= {growth_threshold:.0%} first to last': growth_check,
            'Latest R&D / revenue >= 5%': research_check}


def burry_checks(rows):
    complete = len(rows) == 5 and all(numeric(r.get(k)) for r in rows for k in ('operating_cash_flow', 'net_income'))
    cash = ('pass' if all(r['operating_cash_flow'] >= r['net_income'] for r in rows) else 'fail') if complete else UNKNOWN
    ratio = rows[-1].get('liabilities_to_equity') if len(rows) == 5 else UNKNOWN
    return {'Operating cash flow >= net income every year': cash,
            'Latest liabilities / equity <= 2': ('pass' if ratio <= 2 else 'fail') if numeric(ratio) else UNKNOWN}


def enrich(result, threshold=.15):
    for row in result['rows']:
        research, revenue = row['research_and_development'], row['revenue']
        row['research_to_revenue'] = research / revenue if numeric(research) and numeric(revenue) and revenue > 0 else UNKNOWN
    result['revenue_cagr'] = revenue_growth(result['rows'])
    result['growth_threshold'] = threshold
    result['panel'] = {'Buffett': sec.checks(result['rows']), 'Cathie Wood': cathie_checks(result['rows'], threshold), 'Burry': burry_checks(result['rows'])}
    return result


def printed_table(result):
    text = sec.printed_table(result)
    text += '\n## Additional panel facts\n\n| Fiscal year end | R&D USD millions | R&D / revenue |\n|---|---|---|\n'
    for row in result['rows']:
        ratio = row['research_to_revenue']
        text += f"| {row['fiscal_year_end']} | {sec.display_value('research', row['research_and_development'])} | {ratio:.2%} |\n" if numeric(ratio) else f"| {row['fiscal_year_end']} | {sec.display_value('research', row['research_and_development'])} | {ratio} |\n"
    growth = result['revenue_cagr']
    text += '\nRevenue CAGR = (last revenue / first revenue)^(1/4) - 1: ' + (f'{growth:.2%}' if numeric(growth) else growth) + '\n'
    text += '\n## Panel\n\n| Investor | Check | Result |\n|---|---|---|\n'
    for investor, checks in result['panel'].items():
        for check, status in checks.items():
            text += f'| {investor} | {check} | {status} |\n'
    for investor, checks in result['panel'].items():
        text += f"\n{investor}: {list(checks.values()).count('pass')} of {len(checks)} checks pass.\n"
    return text


def unsupported_numbers(memo, result):
    allowed = {sec.numeric_key(m.group()) for m in sec.NUMBER.finditer(printed_table(result))}
    return sorted({m.group() for m in sec.NUMBER.finditer(memo) if sec.numeric_key(m.group()) not in allowed})


def memo_flags(memos, result):
    return {investor: unsupported_numbers(memo, result) for investor, memo in memos.items()}


def save(result, root):
    target = Path(root) / result['ticker']
    target.mkdir(parents=True, exist_ok=True)
    (target / 'analysis.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    (target / 'numbers.md').write_text(printed_table(result), encoding='utf-8')


def download(ticker, root, ua, threshold=.15):
    result = enrich(sec.download(ticker, root, ua), threshold)
    save(result, root)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('ticker')
    parser.add_argument('--output', default=str(BASE / 'results'))
    parser.add_argument('--growth-threshold', type=float, default=.15)
    args = parser.parse_args()
    print(printed_table(download(args.ticker, args.output, os.getenv('SEC_USER_AGENT', ''), args.growth_threshold)))
