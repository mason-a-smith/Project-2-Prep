# Lab 15: What did the data say on the trading day?

The data supported a conditional portfolio choice, not a promise of future returns. Using the full historical window, our model selected 65% SGOV and 35% ACWI. Using only the latest 36 months, it selected 85% SGOV and 15% ACWI. That 20 percentage point difference in equity exposure showed how strongly the answer depended on the history we chose.

There is no executed trade or explicit trading date recorded in the lab files. For this answer, I assume a hypothetical trade on October 23, 2026, after the recorded data download on October 22 at 21:27 UTC. An earlier hypothetical trade requires a separate check of what was available then.

## What was available for that decision?

Our saved dataset contains 61 month-end adjusted prices from September 30, 2021, through September 30, 2026, producing 60 monthly returns from October 2021 through September 2026. October 2026 was incomplete and excluded. Thus, on the assumed trading day, the model described completed history through September; it did not include October market performance or the prices at which we could actually execute the trade. [Sources: metadata](data_sources.json), [prices](prices.csv).

The historical estimates were:

| Asset | Annualized mean, all 60 months | Annualized mean, last 36 months |
| --- | ---: | ---: |
| SGOV | 3.72% | 4.44% |
| VGIT | -0.29% | 3.52% |
| VCIT | 0.64% | 5.77% |
| ACWI | 12.14% | 20.50% |

These are arithmetic monthly means multiplied by 12, not forecasts or compound annual growth rates. The recent window showed much stronger stock and bond returns. It also showed lower ACWI volatility: 11.53% versus 14.89% over the full window. Stocks and bonds had positive historical correlations in both samples, so the data did not support assuming bonds would reliably offset equity losses. [Source: saved historical analysis](lab15.md).

Given the provisional 6.5% return objective, 3% reserve minimum, and SGOV-only reserve eligibility, the lowest-volatility portfolios on our 5 percentage point grid were:

| Estimation window | SGOV / VGIT / VCIT / ACWI | Historical return estimate | Estimated annual volatility |
| --- | --- | ---: | ---: |
| All 60 months | 65% / 0% / 0% / 35% | 6.66% | 5.28% |
| Last 36 months | 85% / 0% / 0% / 15% | 6.85% | 1.76% |

The recent sample let the optimizer assign less to equities because their historical mean was higher. That was an assumption-sensitive model result, not evidence that 15% equities would actually deliver the target. The objective and reserve rules were editable lab defaults; the original Meridian training assumptions and manually edited return boxes were also assumptions, not observed market evidence. [Sources: saved results](optimization_results.json), [application](app.py), [engine](portfolio.py).

## How much of what we see now came later?

For the assumed October 23 trade, **none of the saved monthly return observations covers a later period**: all end by September 30. However, that does not prove every historical adjusted price matches the value published on its original date. We have one recorded download vintage, October 22, rather than archived downloads from each historical trading day.

The lab explicitly notes that Yahoo may revise adjusted prices after subsequent distributions. An adjusted close is a retrospectively adjusted series, not necessarily the price a trader saw or could execute at the time. A later adjustment does not automatically change the monthly return: a common scaling of both endpoints cancels in the price ratio. With only one saved vintage, we cannot measure whether revisions changed our returns, estimates, or allocations. **The revision contribution is unknown, not demonstrably zero.** [Sources: lab documentation](lab15.md), [download method](download_prices.py).

If the intended trade was October 1, the October 22 download came later, even though all observation dates preceded the trade. If the trade was before September 30's close, the full saved sample also includes information from after that decision. A valid historical simulation would restrict each calculation to observations available before execution and, where possible, use the data vintage available then. Comparing our 60-month and 36-month windows does not measure later information: both end in September 2026.

My conclusion is that the lab demonstrated how historical estimates and portfolio weights change with the sample. It did not establish future performance or reconstruct an earlier trader's exact information set. The saved files contain no post-trade performance and no second data vintage, so neither subsequent investment success nor the numerical effect of later revisions can be established from this lab.
