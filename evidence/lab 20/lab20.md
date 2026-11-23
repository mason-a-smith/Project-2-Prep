# Lab 20 — Project 2 completion checkout

**Mason Smith | November 17, 2026**

Built with AI assistance. This report reproduces the saved Project 2 model and records a changed-input demonstration. Partner observations, an AI-closed prediction, commits, and an oral explanation have not been supplied and are not claimed as completed.

## D — Can a stranger reach the decision, and does it survive a changed input?

The saved work supports a reproducible, conditional model decision: **65% SGOV / 0% VGIT / 0% VCIT / 35% ACWI**, using all 60 monthly returns. Its historical annualized return estimate is **6.6643%**, estimated annual volatility **5.2807%**, and reserve-eligible weight **65%**. It passes the provisional **6.5% return objective** and **3% reserve minimum**, with only SGOV eligible for reserves.

The exact allocation does **not** survive a one-percentage-point reduction in ACWI's annual return estimate. Keeping the original weights drops estimated return to **6.3143%**, below the target. Reoptimizing selects **60% SGOV / 40% ACWI**, with return **6.6856%**, volatility **6.0178%**, and reserves **60%**. A feasible portfolio survives, but the original allocation and its mandate verdict do not.

These are historical model estimates, not promised returns or an instruction to trade. The objective and reserve eligibility remain provisional lab defaults, not a confirmed committee mandate.

## R — Repository manifest

Project 2 is treated here as the portfolio work beginning in Lab 14, developed in Lab 15 and supplemented by Labs 16–17's availability and vintage work. No separate Project 2 final package or Week 12 must-fix list was found in the accessible folders.

| Required part | Evidence and readiness |
| --- | --- |
| Tool: move one control and read verdict | [Lab 15 app](../lab%2015/app.py) provides editable estimates and mandate settings. Lab 20's numerical check calls the same engine; an independent partner UI check remains outstanding. |
| README with result command | Command below reproduces the baseline and stress in one run from the repository root. Existing Lab 17 README addresses the rate-vintage app, not the portfolio decision. A repository-root README remains a final-package item. |
| Visible output | Baseline and stress numbers are readable in this file without running code. |
| Decision memo at `docs/decision-memo.md` | No Project 2 memo at that path was found. The decision line below can supply its verified numbers, dates, and conditions; the required final memo remains outstanding. |
| Baseline, mandate, stress, AI use | Reproduced below using [checkout.py](checkout.py). This is an AI-assisted check. |
| Locked Changed-Input Record | A human prediction committed and pushed before an AI-closed run is not documented. The demonstration below does not substitute for it. |
| Videos 1–3 and transcripts | Project 2 links/transcripts were not found or verified. Project 1 materials are a separate project. |
| Week 12 must-fix list | Not supplied or found; reconciliation remains outstanding. |

### Reproduce from the repository root

Prerequisite: installed `uv`; its first run may need internet access to install Python dependencies. Preserve the folders and filenames when uploading to GitHub.

```powershell
uv run --with numpy --with pandas python "lab 20/checkout.py"
```

The result prints as JSON in the terminal. No fresh market download occurs. The runner imports [the Lab 15 engine](../lab%2015/portfolio.py) and reads [the frozen monthly prices](../lab%2015/prices.csv). Uploading this Markdown alone preserves the visible report, but reproduction also requires `checkout.py` and the referenced Lab 15 files.

To open the interactive tool from the repository root:

```powershell
uv run --with streamlit python -m streamlit run "lab 15/app.py"
```

Use the local actual-price dataset and all-month window. Change the ACWI return estimate from approximately 12.1413% to 11.1413%, holding the target, reserve rule, volatilities, and correlations fixed.

## I — Cold run

**Actual check completed:** the AI-assisted reproduction command above ran successfully on November 17, 2026, exited with code 0, and reproduced the saved all-month baseline. Its built-in checks verified that baseline and stressed optimized weights sum to 100%, are nonnegative, and satisfy both numerical mandate constraints.

**Independent partner cold run: not yet recorded.** A run in this existing workspace does not establish that a stranger can reproduce it in a fresh folder.

| Partner record required | Entry |
| --- | --- |
| Partner name and repository URL | To be entered after the actual exchange |
| Exact command followed from README | To be entered by partner |
| First failure, or explicit clean run | To be entered by partner |
| Elapsed time | Not measured for a partner run |
| Where the result appeared | To be entered by partner; expected terminal JSON |
| Rerun after fix and outcome | To be entered after partner rerun |

Send only the repository link and do not coach. Any question requiring an answer should become a README instruction.

## V — Changed-input demonstration

**Status:** AI-assisted sensitivity calculation, not the required human Locked Changed-Input Record. No pre-run human prediction or prior commit/push is asserted.

Input changed: ACWI's estimated annual arithmetic return, **12.141317% to 11.141317%**, a reduction of **1.000000 percentage point per year**. All other estimated inputs and mandate settings remain fixed. This changes an estimate, not the underlying saved prices.

The reasoning to test independently with AI closed is that a lower equity estimate lowers return at the original weights. Since equity still has the largest expected return, the optimizer may need more equity to meet the unchanged target, raising modeled risk. Write your own prediction before a separate required run and commit/push it before viewing that run's output.

### Preserved before-and-after output

Weight order is SGOV / VGIT / VCIT / ACWI. Percentages below are annualized where applicable.

| Measurement | Baseline | Original weights under changed input | Reoptimized changed input |
| --- | ---: | ---: | ---: |
| Weights (%) | 65 / 0 / 0 / 35 | 65 / 0 / 0 / 35 | 60 / 0 / 0 / 40 |
| Estimated return (%) | 6.664255 | 6.314255 | 6.685567 |
| Estimated volatility (%) | 5.280674 | 5.280674 | 6.017830 |
| Reserve weight (%) | 65 | 65 | 60 |
| Return >= 6.5% | Pass | Fail | Pass |
| Reserve >= 3% | Pass | Pass | Pass |
| Combined numerical mandate | Pass | Fail | Pass |

At fixed weights, return falls by exactly **0.35 percentage point**: 35% equity weight multiplied by a one-percentage-point reduction in its return estimate. Volatility stays constant because weights and covariance stay constant. After reoptimization, equity rises five percentage points and volatility increases by about **0.7372 percentage point**. The reoptimized return slightly exceeds the baseline because the search moves in discrete five-percentage-point steps rather than choosing an exact continuous target allocation.

The changed-input result supports the directional reasoning above. It cannot be described as matching a previously locked human prediction because none is documented. Separately, the existing last-36-month analysis selects 85% SGOV / 15% ACWI, showing sensitivity to the estimation window; that experiment changes multiple estimates and is not this single-input test.

## Explain the code — preparation for the six-minute exchange

Open `search_portfolio` in [portfolio.py](../lab%2015/portfolio.py). This guide is AI-assisted preparation; the actual line-by-line explanation and partner question must happen without AI.

1. Validate the target and reserve minimum, then build covariance from correlations and annual volatilities: covariance(i,j) = correlation(i,j) × volatility(i) × volatility(j).
2. `compositions(20, len(sleeves))` generates all nonnegative allocations of 20 units across the funds. Dividing by 20 creates fully invested portfolios in 5% increments.
3. Matrix multiplication computes each portfolio's weighted expected return and reserve-eligible weight.
4. `feasible` retains portfolios satisfying both constraints, with a small floating-point tolerance. If none qualifies, return `None`.
5. `np.einsum` calculates each feasible portfolio's variance, w-transpose × covariance × w.
6. `np.argmin` selects the smallest variance. The returned dictionary includes weights, weighted return, square-root variance, and reserves.

Practice question: Why does a lower ACWI return estimate leave volatility unchanged at fixed weights but increase it after reoptimization? Answer: the first calculation changes neither weights nor covariance; the second chooses new weights with more equity exposure.

**Actual partner question and answer:** not yet recorded. **Line needing follow-up:** to be recorded during the exchange.

## E — Fix one thing

The repository review identified an entry-point problem: running `lab 15/portfolio.py` directly prints the original Meridian training portfolios, whereas Project 2's actual-price decision is calculated elsewhere. A stranger could mistake that output for the Project 2 result.

**Fix completed locally:** added `lab 20/checkout.py` and the explicit root-relative command in this report. It uses the existing engine, reproduces the frozen actual-price baseline, runs the single-input stress, and prints both outputs together. Execution succeeded with exit code 0. Earlier lab files and downloaded inputs were preserved.

This was an AI-assisted repository finding, not a failure reported by a partner. Partner rerun and GitHub push are not documented. Do not mark the required partner fix step complete until the real cold run establishes its outcome.

## Decision line

**As of November 17, 2026, retain 65% SGOV / 35% ACWI as the reproducible all-month model baseline, conditional on a confirmed 6.5% annual return objective, 3% reserve minimum, and SGOV-only reserve eligibility. Its historical return estimate is 6.6643%, estimated annual volatility 5.2807%, and reserve weight 65%. If ACWI's annual return estimate falls from 12.1413% to 11.1413%, the original mix fails the return target; the model instead selects 60% SGOV / 40% ACWI, returning an estimated 6.6856% with 6.0178% volatility and 60% reserves. Final committee approval remains pending confirmation of the mandate and completion of the repository checkout requirements.**

Data conditions: frozen Yahoo adjusted-price download dated October 22, 2026, at 21:27:42 UTC; 61 month-end prices from September 2021 through September 2026, producing 60 monthly returns from October 2021 through September 2026. This is a reproduction of that saved sample, not an updated November market assessment. Returns use arithmetic monthly mean × 12; volatility uses sample monthly standard deviation × square root of 12. No transaction costs are modeled. The minimum applies to the five-percentage-point grid, not every continuous allocation.

The [Lab 17 admission record](../Lab%2017/Project2_data_admission.md) permits the saved prices for clearly labeled estimation after their download, subject to source checks, but quarantines claims that they reconstruct information available at every historical decision date. DGS10 is optional rate context, not a substitute for ETF total returns, and is not added to this optimizer.

## Reflection and checkout status

The most useful distinction is between a feasible optimization and a robust decision. Both optimized scenarios pass the numerical rules, but the original recommendation fails after a modest change in a load-bearing estimate. A committee therefore needs the baseline, the fixed-weight failure, and the reoptimized response together. The 0.1643-percentage-point baseline return margin is small relative to estimation uncertainty.

A stranger now has a reproducible numerical path and visible output. The full submission is **not yet evidenced as complete**: record the partner cold run and rerun, perform a separate AI-closed prediction/commit/run and oral explanation, reconcile the Week 12 list, confirm the mandate, and supply the Project 2 root README, decision memo, and three video/transcript links. No grade, partner participation, successful push, or completion of those human activities is claimed here.

AI-use disclosure: AI inspected existing coursework, drafted this report, added the reproduction runner, and executed the numerical check. The changed-input example and explanation guide were produced with AI assistance. Historical sources and assumptions are documented in [Lab 15](../lab%2015/lab15.md) and [its data metadata](../lab%2015/data_sources.json).
