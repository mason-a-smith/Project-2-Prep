# Illustrative operating-fee stress data card

| Fund | Current annual expense ratio | Annual dollars per $10,000 | Official issuer source | Date basis |
| --- | ---: | ---: | --- | --- |
| SGOV | 0.09% | $9.00 | [iShares SGOV](https://www.ishares.com/us/products/314116/ishares-0-3-month-treasury-bond-etf) | Retrieved November 23, 2026; page market spread data as of November 20, 2026 |
| VGIT | 0.03% | $3.00 | [Vanguard VGIT](https://investor.vanguard.com/investment-products/etfs/profile/vgit) | expenseRatioAsOfDate December 19, 2025 |
| VCIT | 0.03% | $3.00 | [Vanguard VCIT](https://investor.vanguard.com/investment-products/etfs/profile/vcit) | expenseRatioAsOfDate December 19, 2025 |
| ACWI | 0.32% | $32.00 | [iShares ACWI](https://www.ishares.com/us/products/239600/ishares-msci-acwi-etf) | Retrieved November 23, 2026; page market spread data as of November 20, 2026 |

Expense ratios were read from the linked official issuer pages on November 23, 2026. Vanguard's embedded profile data dates these ratios to December 19, 2025. iShares pages also reported 30-day market spreads as of November 20, 2026; those spread observations are not used in the stress. Expense ratios are not bid/ask spreads. No historical fee schedule is inferred.

Historical adjusted-price returns already reflect fund operating expenses. Do **not** deduct current expenses again as a baseline cost. Model a hypothetical doubling of current expense ratios by subtracting **one additional current ratio** from each annual historical net expected-return input. Hold covariance and mandate rules fixed, evaluate the original weights, then reoptimize. Current weighted fee exposure and incremental stress dollars are numerically equal under this assumption: `sum(weight × ratio) × $10,000` annually on constant capital. These are annualized approximations, not separate cash invoices or an execution simulation.

For 65% SGOV / 35% ACWI, the incremental stress is 0.1705% ($17.05 per $10,000 annually), reducing estimated return to 6.49375490%, failing 6.5%. The conditional 60% / 40% mix has a 0.1820% increment ($18.20 per $10,000), 6.90356738% estimated return and 6.01782969% volatility. The runner verifies the reoptimized result.

This is an **illustrative operating-fee stress**, not a fee forecast or transaction-cost evidence. Bid/ask spreads, commissions, taxes, turnover and execution timing remain unmodelled; missing Vanguard spread evidence is not replaced by invented values. Fees retrieved November 23 are a later sensitivity overlay, not information asserted available at the November 17 model decision. The frozen return snapshot is unchanged.

## Additional transaction-cost scenario

Assume 25% one-way annual turnover, defined as half the absolute weight changes, and 100 bp all-in cost per dollar traded: 0.25 × 0.01 = 0.0025, or 25 bp annual NAV drag ($25 per $10,000). This deliberately adverse educational assumption includes spreads/slippage/commissions without claiming observed quotes. Subtract 0.0025 from each annual asset return; fixed weights lose 25 bp; covariance is unchanged. Reoptimize separately. This scenario is separate from doubled operating fees and does not double-count baseline fund expenses. Initial funding costs, taxes and actual execution are not estimated.
