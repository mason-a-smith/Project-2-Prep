AI use: OpenAI Codex assisted with the reconciliation, code and verification.

The analysis and decision are mine (Mason Smith); education, not investment advice.

# Lab 13 mandate reconciliation methods and change record

The original source is `evidence/Lab 13/Lab13.md`, statements S1–S10 and its later proposed personal-client section. The separate original `Lab 13/mandate.py` supplies fictional case redemption times, issuer exemptions, $100m initial value and $0.75m payouts. Those redemption times describe case holdings; they are not verified metadata for SGOV, VGIT, VCIT or ACWI. The table preserves each original requirement separately from the later educational pilot.

PASS means the specific labeled calculation passes, subject to its stated scope. FAIL identifies a demonstrated breach in that calculation. NOT TESTED identifies missing evidence, approvals, or a future condition that history cannot establish. A historical diagnostic PASS is not a full-mandate PASS. The table covers all S1–S10, separates target weights from instrument restrictions, and separates the historical loss observation from the future loss promise.

## Return and risk measures

The existing engine is preserved: monthly arithmetic mean times 12 estimates annual returns; annualized monthly covariance determines volatility. The 6.5% return target is a later planning proxy, adding 2.5% assumed inflation to four percentage points. It is neither observed inflation nor an exact 4% real-return hurdle: `(1.025 × 1.04) − 1 = 6.6%`. Original S2 leaves the compounding interpretation for approval. Real CAGR would be `[(portfolio ending wealth / starting wealth) / (CPI ending index / starting index)]^(1/5) − 1`, after approved treatment of all costs. No CPI series or full-cost schedule is supplied, so S2 remains NOT TESTED. The 60-return data set supports only one full five-year interval, not repeated independent five-year evidence.

Annual volatility measures dispersion of returns, not a loss cap. Maximum drawdown is the most negative `wealth / running maximum wealth − 1`. The initial wealth of one is included in the peak series so a loss in the first month is counted. Calendar-year return compounds exactly January–December returns; partial 2021 and 2026 years are excluded. Rolling 12-month return can cross calendar boundaries and cannot substitute for S9. Worst month is a separate measure. Signed loss values are displayed as negative returns. The 6.5% volatility ceiling was a later illustrative overlay, not a Lab 13 replacement for S9 and not evidence of approved client risk appetite.

## Historical reconstruction

New `reconciliation.py` is additive and does not alter `portfolio.py`, the frozen price/provenance files, `audit_controls.py`, or the pre-run locked record. It reconstructs historical holdings from each saved comparison portfolio's target weights. Annual mode rebalances to those fixed targets after each December return, effective for January; buy-and-hold mode allows weights to drift without resets. No future optimized weights are inserted. The targets were fitted using the same full sample: this is an ex-post diagnostic, not a point-in-time strategy backtest, holdout test or actual account history. Adjusted prices reflect reinvested fund distributions and fund expenses; trading/advisory costs and taxes are excluded. Foundation distributions are external flows and are not treated as investment losses.

The full period is September 2021–September 2026: 61 prices, 60 returns. Monthly observations cannot detect intramonth drawdowns. Historical evidence does not guarantee future results, as explained in the [SEC performance-claims bulletin](https://www.investor.gov/introduction-investing/general-resources/news-alerts/alerts-bulletins/investor-bulletins-47). Missing full costs matter to net performance; see the [SEC fees bulletin](https://www.sec.gov/files/ib_fees_expenses.pdf).

## Cash flows, reserves and operational requirements

Four $750,000 payouts require $3m over 12 months, 3% of the initial $100m. Twenty-eight fixed nominal quarterly payouts total $21m over seven years. No inflation escalation, terminal wealth target, exact payment dates or reserve-replenishment policy is invented. Initial SGOV coverage is a conditional pilot proxy; an ETF holding is not automatically client-approved reserve eligibility. The annual reserve dollar obligation remains $3m even when NAV changes, so a static 3% floor is insufficient if NAV falls below $100m. No payout simulation is labeled compliant without a withdrawal and replenishment policy.

Original S6 exempts diversified funds: nonexempt single-company exposure is therefore 0% at the four-fund sleeve level. This is a case-specific exemption, not zero underlying concentration or a look-through audit. Original issuer exemption does not establish reserve eligibility.

Simulated one-way turnover at each annual reset is `0.5 × sum(abs(target − drifted weights))`. It excludes initial funding, payouts, replenishment and other trades. A reset above 25% demonstrates a diagnostic breach; one below 25% does not establish actual annual turnover compliance. Original annual turnover convention and approval records remain missing. Liquidity requires verified ability to redeem/sell the required weight within five business days; no assumed ETF days are inserted.

## Changes and verification

Added a dedicated app section with portfolio/rebalancing selectors, status filters, requirement search, downloadable table, source evidence, loss metrics, drawdown chart, complete-year table and turnover diagnostics. Dashboard numerical verdicts are explicitly scoped to the pilot. Added `verify_reconciliation.py` with known-answer loss, compounding, annual-reset/turnover, partial-year and invalid-input tests; it also exercises UI selectors and filters and preserves frozen evidence hashes. `verify_final.py` remains the original broader app regression check. Executed evidence is saved in `outputs/reconciliation-verification.json`; the baseline table and summary are exported there for review.

Run `uv run --locked python verify_reconciliation.py` and `uv run --locked python verify_final.py`. In the app select **Mandate reconciliation**. No existing locked prediction or recorded result is rewritten or reclassified.
