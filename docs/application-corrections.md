AI use: OpenAI Codex assisted with implementation, financial checks and documentation.

The analysis and decision are mine (Mason Smith); education, not investment advice.

# Application corrections and verification

This is an additive correction of the existing app. No page, company screen, chart, training dataset, upload, signal, stress, download or historical evidence is removed. `portfolio.py`, `audit_controls.py`, `prices.csv`, provenance, and the locked prediction/result remain unchanged. Edition A is the fixed prior GitHub commit linked in [version comparison](edition-and-decision.md). Edition B is the current corrected application; both are AI-assisted.

| Correction | Reason and resulting behavior |
| --- | --- |
| Dynamic rules in `current_rules.py` | Frozen check keys named 6.5%/3% could misdescribe nondefault inputs, including the saved 5% ceiling stress. Current displayed labels carry actual return, reserve and risk limits. The historical control module is retained byte-for-byte for the locked test. |
| Editable volatility ceiling | All interactive searches, comparisons and fee stresses use the selected cap. Finite rule inputs and a positive-semidefinite covariance are validated. No limit is silently weakened to obtain feasibility. |
| Clear authority and investment horizon | Original Lab 13 requirements are distinguished from later provisional AI-assisted rules. Seven years is the investment horizon; monthly is review cadence. Original requirements lacking evidence remain NOT TESTED. |
| Decision and version explanation | Named user and committee ask, Edition A archive versus Edition B corrections, and feasibility versus live authorization are visible without changing the app layout. |
| Historical losses surfaced | Dashboard shows maximum month-end drawdown and worst full calendar-year return; interactive targets expose the same annual-reset diagnostic where price history exists. Full reconciliation retains all loss periods, charts and filters. No estimates-only training loss path is fabricated. |
| Allocation range and reversal | Conditional full-window endpoints are separated from the 85/15 result under 36-month estimates. Threshold breaches, infeasibility, source issues and unresolved original controls reopen or stop the decision. |
| Correct saved stress presentation | Saved legacy output remains evidence; current UI re-labels its actual scenario limits, including 5% risk. Downloads of old audit results remain available as historical records. |

## Material calculation verification

`verify_improvements.py` independently recomputes monthly returns, arithmetic annual means, sample annual covariance, equal and inverse-volatility weights, all saved scenario returns/risks/reserves, expense and implementation-cost effects, and the complete four-asset 5% allocation grid using a separate enumeration. It checks minimum-volatility feasibility for both windows, haircut/cost cases and infeasible tighter constraints. Exact real-return compounding, payout arithmetic, signal values and availability gate are also checked. Historical path calculations are covered by known-answer loss/rebalancing tests in `verify_reconciliation.py`; buy-and-hold is independently matched to normalized fund prices.

UI tests exercise all six sections, editable return/reserve/risk limits, changed windows, training data, original mandate source classifications and the absence of live authorization. Frozen artifact hashes are checked before/after. Test results and independently recomputed scenarios are saved to `outputs/improvements-verification.json`. The older broad checks `verify_final.py` and `verify_prework.py` are retained and run as regression tests; `verify_final.py`'s label expectation now tests human-readable actual limits. They are implementation checks, not a partner cold run, actual investment performance or client approval.

Historical reconstruction is fitted with hindsight and excludes foundation withdrawals and full implementation costs; incomplete calendar years are excluded. Annual volatility is not maximum drawdown or calendar-year loss. Expense-ratio stress subtracts one additional ratio from already-net fund returns. The separate trading stress is assumed 25% turnover × 100 bp per traded dollar = 25 bp of annual NAV, not observed execution evidence. Current sources and rules do not prove the original CPI+4% net objective or future maximum-loss promise.

Verification executed successfully: `verify_improvements.py` (13 scenarios, 1,771 independently enumerated grid points, changed-input UI tests), `verify_reconciliation.py` (known-answer history and reconciliation interactions), `verify_final.py` (all six app sections), and `verify_prework.py` (fresh copied-directory run, charts, uploads/training controls, signal corruption gates, company screens and 76 local document links). These runs preserve the original engine/data/locked hashes. Historical raw SEC archives remain local as previously documented; the published app does not require them for its saved company views.
