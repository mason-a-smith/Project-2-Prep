AI use: OpenAI Codex assisted with application code, financial verification and explanation.

The analysis and decision are mine (Mason Smith); education, not investment advice.

# Intended user, decision and version comparison

The intended user is Mason Smith presenting to the fictional foundation investment committee, not a retail trading client. The foundation has an original seven-year investment horizon, $100m initial assets and fixed $750,000 quarterly payouts. Monthly paper reviews are a proposed monitoring cadence. Annual rebalancing is original S1; monitoring does not authorize monthly trades. The committee question is whether to approve a simulation-only pilot and resolve the untested original requirements. A numerical feasible portfolio is not authorization to invest; live allocation under this proposal remains 0%.

## Edition A and Edition B

These names describe versions for comparison in this application. They do not claim a required course submission format, AI-off work, independent authorship, or a real committee decision.

| Version | Evidence | Scope and status |
| --- | --- | --- |
| Edition A: archived prior application | [Fixed GitHub commit b525ca3](https://github.com/mason-a-smith/Project-2-Prep/tree/b525ca3d89ca107c989c63c302066d71b418e8ac) | Prior AI-assisted app including original Lab 13 reconciliation, frozen engine/data and locked reserve test. It used hard-coded default constraint identifiers, even for the 5% risk stress. Preserved in Git history; not overwritten as a newly independent analysis. |
| Edition B: current correction | Current app; `current_rules.py`, `verify_improvements.py`, and `docs/application-corrections.md` | Same universe, price snapshot, optimizer, saved scenarios and paper-only recommendation. Dynamic labels and validation reflect selected limits; clearer audience, authority, horizon, losses and reversal conditions. AI-assisted. |
| Earlier lab evidence | `evidence/Lab14`, `evidence/lab 15`, `evidence/Lab 13` | Lab 14 training inputs are not the personal four-fund historical price dataset. They remain selectable; they are not relabeled as an independently authored Edition A. |

## Mandate authority

Original S1–S10 govern the fictional client case: seven years and annual rebalancing; CPI + four percentage points net over rolling five years; quarterly payouts and twelve-month reserve; 60/40 global equity/US investment-grade reference; instrument, issuer, turnover and liquidity restrictions; and the undefined enforcement of the 10% calendar-year loss promise. See the original source in Mandate reconciliation.

Later proposed personal-client rules, already labeled AI-assisted in Lab 13, add the SGOV/VGIT/VCIT/ACWI universe, 5% allocation grid and minimum-sample-volatility ranking. The 6.5% return proxy adds an assumed 2.5% CPI to 4 percentage points; it is not measured CPI or proof of net real five-year performance. An exact 4% real return at 2.5% inflation compounds to 6.6% nominal. Client interpretation remains unresolved. SGOV-only reserve eligibility, the VCIT benchmark proxy, 6.5% volatility ceiling and cost stresses remain provisional. The volatility ceiling is a later illustrative AI-assisted overlay, not S9 and not a loss guarantee. Changing controls explores a scenario; it does not amend the original mandate or grant committee approval.

## Recommendation, sensitivity and reversal

The 60–65% SGOV / 35–40% ACWI paper-allocation span describes paired endpoints of separate full-window baseline and return/cost scenarios. VGIT/VCIT are zero in these cases. The range is not a confidence interval, a guarantee of feasibility throughout the range, or a trading authorization. Each candidate must be checked against its scenario's assumptions.

The last-36-month estimation window instead yields 85% SGOV / 15% ACWI. That 20-point ACWI difference is outside the proposed range: it demonstrates window instability. The data sample has 60 monthly returns and one complete five-year interval, not seven years or repeated independent rolling five-year observations. No blend of windows, averaging rule or timing strategy has been approved.

At the fixed 65/35 target, an ACWI return haircut of one percentage point, doubled operating expenses, or the assumed 25 bp annual implementation drag each separately fails the return target. Reoptimization can restore numerical feasibility but does not resolve the estimate risk. A 5% volatility ceiling makes the grid infeasible at the unchanged return objective. The locked test's 70% reserve minimum also stops as infeasible. These are separate stresses; no combined-stress robustness is claimed.

Reject or reopen the recommendation for return below the selected target, volatility above the selected cap, less than $3m in approved reserves, altered source hashes, mistimed data, a different approved window/universe, or unavailable cost evidence. Resolve actual payout funding/replenishment, five-day liquidity, annual turnover/approval, fund instrument restrictions, net-real objective and loss enforcement before live use. A simulation PASS cannot establish any of those missing approvals. Historical drawdown, worst calendar-year return and volatility measure different things; none establishes a future maximum loss. See the [SEC performance-claims bulletin](https://www.investor.gov/introduction-investing/general-resources/news-alerts/alerts-bulletins/investor-bulletins-47).
