"""Offline edge cases; these synthetic facts are never used as company results."""
import copy
import importlib.util
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location('engine', Path(__file__).parent / 'buffett-sec/scripts/sec_facts.py')
e = importlib.util.module_from_spec(spec)
spec.loader.exec_module(e)


def fact(val, filed='2025-10-01', form='10-K', start='2023-09-04', end='2024-09-01'):
    item = dict(val=val, filed=filed, form=form, end=end, accn='example-' + filed)
    if start:
        item['start'] = start
    return item


class EngineTests(unittest.TestCase):
    def setUp(self):
        self.facts = {'facts': {'us-gaap': {}}}
        for metric, tags in e.TAGS.items():
            self.facts['facts']['us-gaap'][tags[0]] = {'units': {'USD': [fact(100, start=None if metric not in e.FLOW else '2023-09-04')]}}

    def test_latest_annual_not_quarter_or_10q(self):
        values = self.facts['facts']['us-gaap'][e.TAGS['revenue'][0]]['units']['USD']
        values.extend([fact(120, filed='2026-10-01'), fact(999, filed='2026-11-01', form='10-Q'), fact(888, filed='2026-11-01', start='2024-06-01')])
        value, ev = e.select_fact(self.facts, 'revenue', '2024-09-01')
        self.assertEqual(value, 120)
        self.assertEqual(ev['filed'], '2026-10-01')

    def test_priority_and_fallback(self):
        gaap = self.facts['facts']['us-gaap']
        gaap['Revenues'] = {'units': {'USD': [fact(200)]}}
        self.assertEqual(e.select_fact(self.facts, 'revenue', '2024-09-01')[0], 100)
        del gaap[e.TAGS['revenue'][0]]
        self.assertEqual(e.select_fact(self.facts, 'revenue', '2024-09-01')[0], 200)

    def test_missing_capex_and_nonpositive_equity(self):
        gaap = self.facts['facts']['us-gaap']
        del gaap[e.TAGS['capital_spending'][0]]
        gaap['StockholdersEquity']['units']['USD'][0]['val'] = 0
        row = e.year_row(self.facts, '2024-09-01')
        self.assertEqual(row['capital_spending'], 'not found')
        self.assertEqual(row['owner_earnings'], 'not found')
        self.assertEqual(row['roe'], 'not known')
        self.assertEqual(row['liabilities_to_equity'], 'not known')
        self.assertTrue(all(v == 'not known' for v in e.checks([row]*5).values()))

    def test_checks_and_numeric_probe(self):
        rows = []
        for i in range(5):
            row = e.year_row(self.facts, '2024-09-01')
            row.update(roe=.283, owner_earnings=3501000000+i*1000000)
            rows.append(row)
        result = dict(ticker='TEST', company='Synthetic', rows=rows, checks=e.checks(rows))
        self.assertTrue(all(v == 'pass' for v in result['checks'].values()))
        self.assertEqual(e.unsupported_numbers('ROE 28.3%; owner earnings 3,501.', result), [])
        for text in ['ROE 40.0%', 'ROE 40.0 %', 'claim 9e12', 'FY2099']:
            self.assertTrue(e.unsupported_numbers(text, result), text)
        rows[2]['owner_earnings'] = 'not found'
        self.assertEqual(e.checks(rows)['Owner earnings grew first to last'], 'not known')


if __name__ == '__main__':
    unittest.main()
