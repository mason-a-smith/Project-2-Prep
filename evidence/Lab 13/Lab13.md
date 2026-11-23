# Lab 13 — Meridian Foundation mandate

Mason Smith | November 23, 2026

AI disclosure: OpenAI Codex drafted the analysis, assumptions, code and verification under my instruction. This is AI-assisted coursework. The quiz response and actual partner exchange are not represented as completed human work.

## Decision

**A passes every rule the checker tests. B fails three rules and C fails one.** This permits A to advance to further review; it does not establish full mandate compliance or authorize investment. S1 implementation, S2 performance, S5 instrument restrictions, S7 turnover and S9 loss policy require additional evidence or clarification. No portfolio is optimized here.

Before optimization, the CIO must specify what the pilot should optimize and how the loss restriction should be measured and enforced. The CPI + 4% target alone does not define an optimization criterion.

## Sort S1–S10 and map to an investment policy statement

An investment policy statement (IPS) records the client's purpose, return and risk objectives, binding limits, implementation rules and oversight responsibilities. It works by defining feasible investments and how decisions will be evaluated before portfolio construction; constraints screen candidates, and an agreed objective ranks feasible choices.

| Statement | Primary type | One-line reason / IPS role |
| --- | --- | --- |
| S1: Horizon seven years; annual rebalancing. | Hard constraint | Sets the planning horizon and implementation schedule; current weights alone cannot prove future adherence. |
| S2: CPI + 4% a year, net of costs, over rolling five-year periods. | Objective | Defines a real return target and measurement period, but not the pilot's ranking criterion or a guaranteed outcome. |
| S3: $0.75m quarterly payouts; twelve months in cash or daily-liquid government securities. | Hard constraint | Requires a funded distribution reserve of $3m, or 3% of the initial $100m portfolio. |
| S4: Benchmark 60% global equities / 40% U.S. investment-grade bonds. | Preference | Supplies the policy reference for comparison; no tracking-error limit or requirement to replicate it is stated. |
| S5: Long-only; no borrowing, shorts or derivatives. | Hard constraint | Limits positions and financing; the script tests nonnegative weights, while the provided holdings are assumed to meet instrument restrictions. |
| S6: No single issuer above 8%. | Hard constraint | Caps aggregated company exposure with the stated exemptions for cash, Treasury and diversified funds. |
| S7: Annual turnover at most 25% without committee approval. | Hard constraint | Requires a trading-history check or approval; candidate weights alone cannot measure turnover. |
| S8: At least 90% redeemable within five business days. | Hard constraint | Sets a minimum liquidity share using the supplied redemption times. |
| S9: Cannot have a calendar-year loss greater than 10%; no measure or breach rule. | Unverifiable promise | An absolute future loss promise cannot be established by allocation weights; risk definition and breach actions are absent. |
| S10: No sector, ESG, tax or home-bias preference; no pilot optimization criterion. | Missing | Confirms no additional stated preferences but leaves the criterion for ranking feasible portfolios unspecified. |

S4 is the classification I was least sure of: an IPS benchmark is an evaluation reference, not literally an allocation preference. Within the assignment's five categories, preference is the closest fit because no binding deviation limit is supplied. S10 combines explicit absence of preferences with a missing decision; missing is its primary classification.

## Mandate assumptions

- Values and redemption times are taken from the fictional case, not market data. Weights are percentages of the initial $100m reserve, and payouts are USD millions.
- Four quarterly payouts must be available at the initial review: `4 × 0.75 / 100 × 100 = 3.0%`. No extra buffer, inflation escalation or transaction cost is invented.
- Reserve eligibility follows the supplied table exactly, including the 10-year Treasury note. Daily liquidity does not mean stable market value; the note's price risk is outside the reserve-eligibility check.
- Liquidity means the supplied business days to redeem, with the five-day boundary included. No unstated settlement, gating or market-stress adjustment is assumed.
- Acme bonds and stock share one issuer. Cash, Treasury and diversified funds are exempt, with no fund look-through required by this case.
- Weights must sum to 100%; comparisons use unrounded values with a tiny numerical tolerance except that any negative weight fails long-only. Display rounding is to one decimal.
- No initial holdings or trade history are supplied, so annual rebalancing does not establish compliance with the 25% turnover limit. Committee approval is not assumed.
- CPI series, net-cost methodology, five-year compounding conventions and risk-policy definitions remain for CIO approval. No return forecast or loss guarantee is fabricated.

## Checker and verified results

From this folder run `python mandate.py`. The file uses only Python's standard library. Run `python verify_mandate.py` to reproduce the known-answer assertions, temporary probe and saved evidence. The verification script restores candidate A in memory and never edits its saved inputs.

| Rule / measured value (%) | A | B | C | D |
| --- | --- | --- | --- | --- |
| Weights sum to 100 | 100.0 pass | 100.0 pass | 100.0 pass | 100.0 pass |
| Lowest weight >= 0 | 0.0 pass | 0.0 pass | 0.0 pass | 0.0 pass |
| Reserve >= 3.0 | 14.0 pass | 1.0 FAIL | 2.0 FAIL | 100.0 pass |
| Redeemable within five days >= 90 | 100.0 pass | 85.0 FAIL | 100.0 pass | 100.0 pass |
| Largest single company <= 8 | 0.0 pass | 9.0 FAIL | 8.0 pass | 0.0 pass |
| Calendar-year loss | requires CIO clarification | requires CIO clarification | requires CIO clarification | requires CIO clarification |
| Verdict | passes every checkable rule | fails 3 rule(s) | fails 1 rule(s) | passes every checkable rule |

The reserve minimum and A–C results match the assignment's known answer. B combines 5% Acme bonds and 4% Acme stock into 9%; C's 8% is allowed because the limit is inclusive.

Probe: temporarily setting A's cash to -2% and global equity to 64% leaves total weight at 100%, reserve at 10%, five-day liquidity at 100% and company exposure at 0%. Its minimum weight is -2.0%, so long-only is the only failed check. A is restored to 2% cash and 60% global equity afterward. See [results.txt](results.txt), [probe_results.txt](probe_results.txt) and [verification_log.txt](verification_log.txt) for executed evidence.

## Candidate D: attack the checker

D holds 100% cash and 0% in every other listed holding. It passes every programmed check without optimizing anything.

Two-sentence judgment: The objection holds as a suitability concern: passing allocation checks does not establish that cash will meet the real return target over rolling five-year periods. S2 supplies the reason for the CIO to reject D if its expected net real return is inadequate; the case supplies no cash-return forecast, so this is not a proven numerical return breach.

Partner exchange: no actual partner portfolio was provided, and no exchange is claimed. Illustrative peer case only: 100% Treasury bills also passes the checker; I would cite S2 and ask how its expected net return supports CPI + 4%, rather than claim the checker's pass demonstrates suitability.

## One question for the CIO

**Should the pilot minimize forecast volatility subject to CPI + 4% net of costs, and what measurable risk limit and breach action should replace the undefined 10% calendar-year loss promise?**

An answer that changes my portfolio would be: "Minimize forecast volatility subject to that return target; interpret 10% as a specified annual downside-risk constraint with an agreed probability and review process, not a guarantee." That would require estimates of net returns and downside risk before choosing weights, and could reject otherwise eligible A; if the CIO instead insists on an absolute guaranteed loss ceiling, I would stop and resolve feasibility rather than claim any candidate meets it. S10 determines the ranking criterion; S9 determines whether the intended risk restriction is testable.

## Reflection and quiz

A portfolio can pass every checkable rule and still be wrong because the checker covers static funding, weights, liquidity and issuer concentration, not the client's full return, risk and implementation needs. D demonstrates the distinction: a large reserve passes the reserve test but does not establish purchasing-power growth.

The classification I was least sure of is S4, for the benchmark-versus-binding-limit distinction explained above.

Quiz posed in chat: Why does `company_weights[issuer] = company_weights.get(issuer, 0.0) + weight` combine Acme's 5% bonds and 4% stock into 9% issuer exposure? Student response remains pending; no explanation is recorded as having followed a student answer.

## Project 2: proposed personal-client mandate

This is an AI-assisted educational assumption set, consistent with the existing [Project 2 proposal](../Project2/docs/proposed-mandate.md), not a claim of a real client's approval. Assumed client: a fictional foundation with a $100m reserve, seven-year horizon and $0.75m quarterly distributions. Work proceeds as a simulation pilot.

**Objective:** minimize annualized sample volatility among feasible allocations, subject to estimated annual return >=6.5%. The 6.5% nominal target assumes CPI of 2.5% plus a 4% real target; CPI is an explicit planning assumption. Estimated historical return is a proxy and does not establish the Meridian rolling-five-year net objective.

**Hard constraints proposed for the pilot:** use SGOV, VGIT, VCIT and ACWI only; remain long-only, fully invested and unlevered; use a five-percentage-point allocation grid; hold at least 3% in SGOV as the reserve proxy; and impose annualized sample volatility <=6.5%. The volatility ceiling is illustrative and is not equivalent to S9's 10% calendar-year loss statement. The provisional comparison benchmark is 60% ACWI / 40% VCIT, inherited from earlier coursework, rather than a claim that VCIT replicates the Meridian U.S. investment-grade benchmark exactly.

Before live use, require verified five-day liquidity >=90%, an approved annual rebalancing and reserve-replenishment process, <=25% annual turnover absent approval, and <=8% aggregated company exposure with the case's exemptions. The existing pilot does not establish all of these operational controls. Diversified funds being issuer-exempt does not automatically make them reserve-eligible: SGOV eligibility is a separate proposed client assumption. Costs and a forward-looking return/risk method must be agreed before using the model as a client decision.

**One client question:** Do you approve minimizing modeled volatility subject to the proposed 6.5% return target and illustrative 6.5% volatility ceiling, including SGOV as reserve-eligible? If the client requires a lower ceiling or excludes SGOV from eligible reserves, the feasible set and selected weights change, and the current four-fund pilot may need a different universe; I would not relax the rule to manufacture feasibility.

## Submission status

Files: [Lab13.md](Lab13.md), [mandate.py](mandate.py), [verify_mandate.py](verify_mandate.py), and execution evidence linked above. No GitHub URL is fabricated: publication requires a connected repository or destination. No partner exchange or student quiz response is claimed.
