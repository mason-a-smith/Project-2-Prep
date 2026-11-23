"""Keyless SEC 10-K extraction. No market data and no model arithmetic."""
import argparse
import hashlib
import json
import os
import re
import time
import urllib.request
from datetime import date, datetime, timezone
from decimal import Decimal
from pathlib import Path

TAGS = {
    'revenue': ['RevenueFromContractWithCustomerExcludingAssessedTax', 'Revenues'],
    'net_income': ['NetIncomeLoss'],
    'operating_cash_flow': ['NetCashProvidedByUsedInOperatingActivities'],
    'capital_spending': ['PaymentsToAcquirePropertyPlantAndEquipment', 'PaymentsToAcquireProductiveAssets'],
    'equity': ['StockholdersEquity'],
    'liabilities': ['Liabilities'],
}
FLOW = {'revenue', 'net_income', 'operating_cash_flow', 'capital_spending'}
MISSING = 'not found'
UNKNOWN = 'not known'
NUMBER = re.compile(r'(?<!\d)[-+]?\d+(?:,\d{3})*(?:\.\d+)?(?:[eE][+-]?\d+)?(?:\s*%)?')


def fetch(url, path, user_agent):
    if not re.search(r'[^\s@]+@[^\s@]+\.[^\s@]+', user_agent) or 'Mason Smith' not in user_agent:
        raise ValueError('SEC User-Agent must name Mason Smith and include your real email.')
    request = urllib.request.Request(url, headers={'User-Agent': user_agent, 'Accept-Encoding': 'identity'})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                raw = response.read()
            data = json.loads(raw)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)
            time.sleep(0.15)  # comfortably below SEC request limit
            return data, {'url': url, 'downloaded_utc': datetime.now(timezone.utc).isoformat(),
                          'sha256': hashlib.sha256(raw).hexdigest(), 'file': path.name}
        except Exception:
            if attempt == 2:
                raise
            time.sleep(2 ** attempt)


def annual_ends(submissions):
    recent = submissions['filings']['recent']
    ends = {end for form, end in zip(recent['form'], recent['reportDate']) if form == '10-K' and end}
    if len(ends) < 5:
        raise ValueError('Fewer than five 10-K fiscal ends in submissions history.')
    return sorted(ends)[-5:]


def select_fact(facts, metric, end):
    """Tag priority first; newest 10-K for that period within the chosen tag."""
    gaap = facts.get('facts', {}).get('us-gaap', {})
    for tag in TAGS[metric]:
        candidates = []
        for fact in gaap.get(tag, {}).get('units', {}).get('USD', []):
            if fact.get('form') != '10-K' or fact.get('end') != end:
                continue
            if metric in FLOW:
                if not fact.get('start'):
                    continue
                days = (date.fromisoformat(end) - date.fromisoformat(fact['start'])).days + 1
                if not 350 <= days <= 380:  # 52/53-week years; excludes quarters and YTD
                    continue
            elif fact.get('start'):
                continue  # balance-sheet instant only
            candidates.append(fact)
        if candidates:
            chosen = max(candidates, key=lambda f: (f.get('filed', ''), f.get('accn', '')))
            return chosen['val'], {'tag': 'us-gaap:' + tag, **{
                k: chosen.get(k) for k in ('start', 'end', 'filed', 'accn', 'form')}}
    return MISSING, {'tag': MISSING, 'searched_tags': ['us-gaap:' + t for t in TAGS[metric]]}


def year_row(facts, end):
    """Explain this function line by line for the classroom exercise."""
    row = {'fiscal_year_end': end, 'evidence': {}}
    for metric in TAGS:
        row[metric], row['evidence'][metric] = select_fact(facts, metric, end)
    ni, eq = row['net_income'], row['equity']
    row['roe'] = UNKNOWN if not isinstance(eq, (int, float)) or eq <= 0 or not isinstance(ni, (int, float)) else ni / eq
    ocf, capex = row['operating_cash_flow'], row['capital_spending']
    row['owner_earnings'] = ocf - capex if all(isinstance(v, (int, float)) for v in (ocf, capex)) else MISSING
    debt = row['liabilities']
    row['liabilities_to_equity'] = debt / eq if isinstance(eq, (int, float)) and eq > 0 and isinstance(debt, (int, float)) else UNKNOWN
    row['evidence']['roe'] = {'tag': 'derived: NetIncomeLoss / StockholdersEquity'}
    row['evidence']['owner_earnings'] = {'tag': 'derived: operating_cash_flow - capital_spending; see input tags'}
    row['evidence']['liabilities_to_equity'] = {'tag': 'derived: Liabilities / StockholdersEquity'}
    return row


def checks(rows):
    def every(key, predicate):
        values = [r[key] for r in rows]
        if len(values) != 5 or any(not isinstance(v, (int, float)) for v in values):
            return UNKNOWN
        return 'pass' if all(predicate(v) for v in values) else 'fail'
    owner = [r['owner_earnings'] for r in rows]
    growth = UNKNOWN if len(owner) != 5 or any(not isinstance(v, (int, float)) for v in owner) else ('pass' if owner[-1] > owner[0] else 'fail')
    return {'ROE >= 15% every year': every('roe', lambda v: v >= .15),
            'Owner earnings positive every year': every('owner_earnings', lambda v: v > 0),
            'Owner earnings grew first to last': growth}


def display_value(key, value):
    if isinstance(value, str):
        return value
    if key == 'roe':
        return f'{value * 100:.1f}%'
    if key == 'liabilities_to_equity':
        return f'{value:.2f}'
    return f'{value / 1_000_000:,.0f}'


def printed_table(result):
    keys = ['revenue', 'net_income', 'operating_cash_flow', 'capital_spending', 'equity', 'roe', 'owner_earnings', 'liabilities', 'liabilities_to_equity']
    lines = [f"# {result['ticker']} — {result['company']}", '', 'USD millions; ROE percent; liabilities/equity ratio. Display rounded; checks use unrounded USD.', '',
             '| Fiscal year end | ' + ' | '.join(keys) + ' |', '|---|' + '---|' * len(keys)]
    for row in result['rows']:
        lines.append('| ' + row['fiscal_year_end'] + ' | ' + ' | '.join(display_value(k, row[k]) for k in keys) + ' |')
    lines += ['', *[f'{k}: {v}' for k, v in result['checks'].items()], '', '## XBRL tags and filing evidence']
    for row in result['rows']:
        lines.append('\nFiscal year end ' + row['fiscal_year_end'])
        for k, ev in row['evidence'].items():
            lines.append(f"- {k}: {ev['tag']}" + (f"; filed {ev['filed']}; accession {ev['accn']}; period {ev['start'] or 'instant'} to {ev['end']}" if ev.get('accn') else ''))
    return '\n'.join(lines) + '\n'


def numeric_key(token):
    return (Decimal(token.rstrip('%').replace(',', '').strip()), token.endswith('%'))


def unsupported_numbers(memo, result):
    # Permit only the numeric forms printed in the script's actual output.
    allowed = {numeric_key(m.group()) for m in NUMBER.finditer(printed_table(result))}
    return sorted({m.group() for m in NUMBER.finditer(memo) if numeric_key(m.group()) not in allowed})


def download(ticker, output, user_agent):
    ticker = ticker.strip().upper()
    if not re.fullmatch(r'[A-Z0-9.-]{1,12}', ticker):
        raise ValueError('Enter a valid ticker.')
    rawdir = Path(output) / 'raw'
    tickers, meta1 = fetch('https://www.sec.gov/files/company_tickers.json', rawdir / 'company_tickers.json', user_agent)
    entry = next((v for v in tickers.values() if v['ticker'].upper() == ticker), None)
    if entry is None:
        raise ValueError(f'Ticker {ticker} not in SEC ticker map.')
    cik = f"{entry['cik_str']:010d}"
    facts, meta2 = fetch(f'https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json', rawdir / f'{ticker}_companyfacts.json', user_agent)
    submissions, meta3 = fetch(f'https://data.sec.gov/submissions/CIK{cik}.json', rawdir / f'{ticker}_submissions.json', user_agent)
    sources = [meta1, meta2, meta3]
    recent = submissions['filings']['recent']
    # High-volume issuers may have fewer than five annual filings in recent.
    for archive in submissions['filings'].get('files', []):
        if len({end for form, end in zip(recent['form'], recent['reportDate']) if form == '10-K' and end}) >= 5:
            break
        history, metadata = fetch('https://data.sec.gov/submissions/' + archive['name'], rawdir / archive['name'], user_agent)
        sources.append(metadata)
        for key in ('form', 'reportDate'):
            recent[key].extend(history[key])
    rows = [year_row(facts, end) for end in annual_ends(submissions)]
    result = {'ticker': ticker, 'company': facts['entityName'], 'cik': cik, 'rows': rows,
              'checks': checks(rows), 'sources': sources}
    target = Path(output) / ticker
    target.mkdir(parents=True, exist_ok=True)
    (target / 'analysis.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    (target / 'numbers.md').write_text(printed_table(result), encoding='utf-8')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('ticker')
    parser.add_argument('--output', default='results')
    parser.add_argument('--user-agent', default=os.getenv('SEC_USER_AGENT', ''))
    args = parser.parse_args()
    try:
        print(printed_table(download(args.ticker, args.output, args.user_agent)))
    except Exception as exc:
        parser.exit(1, f'SEC extraction failed: {exc}\n')
