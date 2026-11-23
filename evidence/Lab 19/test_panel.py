"""Synthetic edge cases only; never company evidence."""
import copy
import unittest
import panel


class Checks(unittest.TestCase):
    def setUp(self):
        self.rows = [dict(fiscal_year_end=f'{2020+i}-12-31', revenue=100 * 1.1**i,
            research_and_development='not found', operating_cash_flow=20, net_income=15,
            equity=100, liabilities=150, liabilities_to_equity=1.5, capital_spending=5,
            owner_earnings=15+i, roe=.15, evidence={}) for i in range(5)]

    def test_threshold_probe_and_missing(self):
        self.assertEqual(list(panel.cathie_checks(self.rows).values()), ['fail', 'not known'])
        self.assertEqual(list(panel.cathie_checks(self.rows, .05).values()), ['pass', 'not known'])
        self.rows[0]['revenue'] = 'not found'
        self.assertEqual(list(panel.cathie_checks(self.rows).values()), ['not known', 'not known'])

    def test_cash_and_equity_gaps(self):
        self.assertEqual(list(panel.burry_checks(self.rows).values()), ['pass', 'pass'])
        self.rows[0]['operating_cash_flow'] = 'not found'
        self.rows[-1]['liabilities_to_equity'] = 'not known'
        self.assertEqual(list(panel.burry_checks(self.rows).values()), ['not known', 'not known'])

    def test_boundaries(self):
        self.rows[-1]['research_and_development'] = self.rows[-1]['revenue'] * .05
        self.assertEqual(list(panel.cathie_checks(self.rows).values())[-1], 'pass')
        self.rows[-1]['liabilities_to_equity'] = 2
        self.assertEqual(list(panel.burry_checks(self.rows).values())[-1], 'pass')
        self.rows[-1]['liabilities_to_equity'] = 2.001
        self.assertEqual(list(panel.burry_checks(self.rows).values())[-1], 'fail')

    def test_flag_all_memos(self):
        result = panel.enrich(dict(ticker='TEST', company='Synthetic test', rows=self.rows, checks=panel.sec.checks(self.rows)))
        for investor in ['Buffett', 'Cathie Wood', 'Burry']:
            memos = {name: 'No unsupported numbers.' for name in ['Buffett', 'Cathie Wood', 'Burry']}
            memos[investor] = 'Unsupported 987654321.123%'
            self.assertTrue(panel.memo_flags(memos, result)[investor])


if __name__ == '__main__':
    unittest.main()
