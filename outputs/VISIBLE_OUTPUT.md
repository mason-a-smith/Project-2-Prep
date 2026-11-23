# Executed portfolio output

AI assistance: OpenAI Codex packaged and checked the existing model; the Copilot SDK assistant reviewed the package. Education, not investment advice.

Pilot in simulation only; defer capital allocation pending confirmed mandate and validation.

Model decision: November 17, 2026. Preparation review: November 23, 2026. Frozen prices downloaded October 22, 2026; returns October 2021–September 2026. This run does not update the market data.

Proposed educational rules: return >=6.5%, SGOV reserves >=3%, volatility <=6.5%. Weights follow SGOV / VGIT / VCIT / ACWI.

| Scenario | Weights (%) | Return (%) | Volatility (%) | Reserves (%) | Risk rule | Mandate verdict | Current fee exposure $/10,000/year | Incremental fee $/10,000/year |
| --- | --- | ---: | ---: | ---: | --- | --- | ---: | ---: |
| Equal weight | 25.0000 / 25.0000 / 25.0000 / 25.0000 | 4.051003 | 6.466667 | 25.0000 | PASS | FAIL: return_at_least_6_5_percent | 11.75 | Not applied |
| Inverse volatility | 84.0458 / 7.7447 / 5.3927 / 2.8167 | 3.476161 | 1.327369 | 84.0458 | PASS | FAIL: return_at_least_6_5_percent | 8.86 | Not applied |
| Constrained baseline | 65.0000 / 0.0000 / 0.0000 / 35.0000 | 6.664255 | 5.280674 | 65.0000 | PASS | PASS | 17.05 | Not applied |
| Fixed baseline under stress | 65.0000 / 0.0000 / 0.0000 / 35.0000 | 6.314255 | 5.280674 | 65.0000 | PASS | FAIL: return_at_least_6_5_percent | 17.05 | Not applied |
| Reoptimized stress | 60.0000 / 0.0000 / 0.0000 / 40.0000 | 6.685567 | 6.017830 | 60.0000 | PASS | PASS | 18.20 | Not applied |
| Fixed baseline under fee stress | 65.0000 / 0.0000 / 0.0000 / 35.0000 | 6.493755 | 5.280674 | 65.0000 | PASS | FAIL: return_at_least_6_5_percent | 17.05 | 17.05 |
| Reoptimized fee stress | 60.0000 / 0.0000 / 0.0000 / 40.0000 | 6.903567 | 6.017830 | 60.0000 | PASS | PASS | 18.20 | 18.20 |
| Inherited reference benchmark | 0.0000 / 0.0000 / 40.0000 / 60.0000 | 7.541771 | 11.493085 | 0.0000 | FAIL | FAIL: reserve_at_least_3_percent, volatility_at_most_6_5_percent | 20.40 | Not applied |
| Last 36 months | 85.0000 / 0.0000 / 0.0000 / 15.0000 | 6.849566 | 1.762095 | 85.0000 | PASS | PASS | 12.45 | Not applied |
| Fixed baseline last 36 months | 65.0000 / 0.0000 / 0.0000 / 35.0000 | 10.062376 | 4.056380 | 65.0000 | PASS | PASS | 17.05 | Not applied |
| Fixed baseline at 5% risk ceiling | 65.0000 / 0.0000 / 0.0000 / 35.0000 | 6.664255 | 5.280674 | 65.0000 | FAIL | FAIL: volatility_at_most_6_5_percent | 17.05 | Not applied |
| Fixed baseline transaction cost stress | 65.0000 / 0.0000 / 0.0000 / 35.0000 | 6.414255 | 5.280674 | 65.0000 | PASS | FAIL: return_at_least_6_5_percent | 17.05 | Not applied |
| Reoptimized transaction cost stress | 60.0000 / 0.0000 / 0.0000 / 40.0000 | 6.835567 | 6.017830 | 60.0000 | PASS | PASS | 18.20 | Not applied |

Changed input: ACWI annual return estimate 12.14131714% to 11.14131714%. Volatilities, correlations, objective, and eligibility stay fixed.

The fixed allocation loses 0.35 percentage point of return. Reoptimization increases equity by 5 percentage points. These are conditional model estimates; no realized performance or historical point-in-time backtest is established.

## Verification

- Matches archived all-month result to 1e-12
- Covariance matches independent pandas sample covariance annualized by 12
- All allocations are long-only and fully invested
- Fee stress fails fixed weights and passes after reoptimization
- 5% volatility ceiling stops without relaxing return or reserve rules
- Signal unavailable at/before snapshot and for unverified sources
- Impossible 100% annual objective returns no feasible mix
- Stress fails at fixed weights and passes after reoptimization

Detailed inputs, source hashes, dependency versions, and execution timestamp: [results.json](results.json).


## Descriptive point-in-time signal

September 2026 versus August 2026; snapshot available only after October 22 download. No historical Yahoo vintage claim; not an optimizer input.

- SGOV: 0.29586681%
- VGIT: -2.31707976%
- VCIT: -3.02167087%
- ACWI: -1.18869087%

Historical adjusted-price returns already reflect operating expenses. The illustrative fee stress subtracts only one additional current ratio. Fee sources retrieved November 23 are a later sensitivity overlay, not November 17 information. Spreads and commissions remain unmodelled. See [cost card](../docs/cost-data-card.md).

The 6.5% volatility ceiling is an AI-assisted illustrative choice made at user request, chosen above the existing 6.0178% stressed volatility; it is not validated client risk appetite. The inherited 40% VCIT / 60% ACWI benchmark is provisional. STOP on infeasibility, unavailable inputs, a rule failure or unsupported historical-as-of claim. Live allocation remains deferred pending client approval and validation.
