# Validation and AI use

**Preparation review: November 23, 2026.** The model decision record remains November 17, 2026. The results use the October 22 snapshot and are not a current-market update.

## Inputs and boundary

[data_sources.json](../data_sources.json) identifies Yahoo Finance adjusted closes and the exact download timestamp. The 61 month-end observations produce 60 returns ending September 2026. [results.json](../outputs/results.json) preserves source/code SHA-256 hashes, execution time and dependency versions. [uv.lock](../uv.lock) fixes the environment resolved during preparation.

The saved history is acceptable for reproducing estimates after download, subject to the [data-admission conditions](../evidence/Lab%2017/Project2_data_admission.md). It cannot demonstrate what an earlier trader knew without the earlier vintage. The [DGS10 card](../evidence/Lab%2017/DGS10_data_card.md) is archived context, not a fund-return input or a connected allocation signal. Later company-filing screens in Labs 18–19 do not feed this portfolio.

## Checks executed during preparation

From the package root, run `uv run --locked python run.py`.

| Check | Evidence and result |
| --- | --- |
| Baseline replication | Weights, return, volatility and reserves match the archived Lab 15 all-month JSON within 1e-12. |
| Covariance reconciliation | Engine covariance matches a separate pandas sample monthly covariance calculation multiplied by 12, within 1e-12. |
| Allocation accounting | All displayed scenario allocations are nonnegative and sum to one. |
| Mandate checks | Equal weight and inverse volatility fail return; constrained baseline passes return and reserves. |
| Single-input stress | ACWI annual estimate 12.14131714% to 11.14131714%; original mix fails return; reoptimized mix passes. |
| Infeasibility | A 100% annual return objective returns no feasible mix instead of relaxing the objective. |

Numerical output is in [VISIBLE_OUTPUT.md](../outputs/VISIBLE_OUTPUT.md). These checks establish internal consistency and reproduction, not independent predictive validation. No outcome performance, holdout results, transaction-cost study or client-approved risk ceiling is asserted.

The [preparation verification record](../outputs/prep-verification.json) also confirms a fresh-directory run with exit code 0 using the already installed environment. Streamlit AppTest verifies the committee scenario table against saved results, the AAPL/COST company views (including missing R&D remaining not known), threshold changes, the default 35% equity allocation, the stressed 40% allocation, and an infeasible-objective warning. A local Streamlit server health check and browser view were also completed. Local-link counts are recorded in the verification JSON. These checks are not a partner cold run or an independent clean-machine test. Reproduce the automated checks with `uv run --locked python verify_prework.py`.

## Material AI use and disposition

| Date | Tool and exposed model | Material use | Check and disposition |
| --- | --- | --- | --- |
| November 17, 2026 | OpenAI Codex; exact model/version not retained in the earlier artifact | Lab 20 report, reproduction script and one-input sensitivity example | Reproduced the archived allocation; retained the arithmetic and explicitly qualified the incomplete partner/human evidence. |
| November 22, 2026 | OpenAI Codex; exact runtime model/version not exposed in this session | Read course instructions; organized existing files; drafted README, memo, risk response and studio records; added an output runner | Checked against existing data, engine and archived JSON; verified covariance independently; retained simulation-only draft and unresolved requirements. |
| November 23, 2026 | OpenAI Codex CLI, model `gpt-6.1-sol`; Copilot SDK assistant | Codex implemented the user-authorized mandate proposal, baseline/risk verdicts, descriptive Lab 16/17 signal, issuer-fee stress, cards, tests and documentation; Copilot coordinated scope and reviewed source evidence and changes. | Runner and AppTest checks passed, including fee arithmetic, signal timing/hash gates, risk infeasibility and local links; protected engine/input/evidence hashes remained unchanged. This is assistant work, not student AI-off prediction or client approval. |
| November 23, 2026 | Copilot SDK assistant | Replaced the single-purpose Lab 15 page with an integrated committee dashboard, portfolio controls, frozen-data/timing analysis, saved Lab 18–19 company screens, Lab 14–20 evidence browser and validation page. | Runner and expanded AppTest passed; local Streamlit health/browser check completed. SEC/company views remain separate from ETF optimization; missing values are preserved. No new market download, personal data or client mandate was added. |
| November 23, 2026 | Copilot SDK assistant | Added dashboard risk/return, scenario-return and allocation charts; added interactive portfolio comparison charts, fund risk/return plot, and five-year company financial trend graphs. | AppTest confirms the chart elements render across dashboard, data, company, and interactive portfolio views; local browser visually checked the scenario charts. All plotted values use saved estimates and retain the simulation-only/non-advice limitations. |
| Prior labs | Prior records state AI assistance; exact dates and versions are not reconstructed here | Portfolio app/engine, provenance exercises and SEC screening materials | Original files are preserved under `evidence/`; earlier verification statements remain historical records rather than newly rerun claims. |

AI is responsible for drafting assistance, not the student's personal attestation. Mason must review the finance interpretation and own the final recommendation. No AI-generated prose is represented as a student's unaided prediction, spoken explanation, partner observation or recorded transcript.

## Locked Changed-Input Record — unresolved

The existing ACWI sensitivity is **AI-assisted**, with before-and-after results already disclosed. It is not a compliant human locked prediction. Use a distinct student-chosen material input for the required record; do not backdate or recast this example.

Complete the prediction with AI closed, commit and push before execution, run with AI closed, and then preserve:

| Required record field | Status |
| --- | --- |
| Material input, old/new values and units | Awaiting student's separate test |
| Predicted output direction and finance reason | Awaiting student's AI-closed writing |
| Predicted decision effect | Awaiting student's AI-closed writing |
| Timestamp and immutable pre-run commit URL | Unresolved |
| AI-closed execution and before/after artifacts | Unresolved |
| Actual effect and reconciliation or failure diagnosis | Unresolved |

This blank record identifies missing evidence; it does not count as a completed test.

## Independent review and known limits

The partner cold run and sceptical committee rehearsal are to be entered in [studio-record.md](studio-record.md). An assistant-run fresh-directory check, if recorded there, verifies packaging only. It does not replace the partner exercise.

The app preserves Lab 15's controls and now displays both transparent baselines with separate return/reserve verdicts beside the constrained result. The descriptive frozen-fund signal is implemented; DGS10 is context only. Transaction costs, a client-approved risk limit and prospective validation remain absent. See [must-fix.md](must-fix.md) and the [November 23 local audit](local-audit.md).

On November 23, OpenAI Codex added these bounded app displays and extended the existing AppTest checks. The Copilot SDK assistant coordinated the Codex pass and reviewed the resulting package. The documented runner and preparation verification passed, including baseline agreement, the preserved 36-month result and reserve infeasibility. The engine, prices and evidence were not edited. Student review remains required; this does not supply human locked-test or partner evidence.

## Authorized educational overlay — November 23, 2026

November 23 authorized update: the [proposed educational mandate](proposed-mandate.md) uses the Lab 14 6.5% objective (2.5% CPI estimate + 4% real objective), inherited provisional 40% VCIT / 60% ACWI reference benchmark, Lab 15 four-fund universe, long-only fully invested 5% grid and >=3% SGOV reserves. The 6.5% annualized sample-volatility ceiling is an AI-assisted illustrative proposal made at the user's request, above the existing 6.0178% ACWI stress; it is not client-validated risk appetite and requires Mason's review.

The [descriptive fund signal](signal-data-card.md) applies the Lab 16 September/August simple-return formula to the frozen local fund prices under the Lab 17 strict post-download gate. No threshold or optimizer predictor is added; DGS10 remains optional context. Uploads/Meridian without verified timestamps show unavailable. Stop historical-as-of claims at/before the October 22 download because Yahoo vintages are unavailable.

The [operating-fee card](cost-data-card.md) records ratios read from official issuer pages and their date basis. Historical adjusted returns already reflect fund expenses. Hypothetical doubling subtracts only one additional current ratio. Fixed 65% SGOV / 35% ACWI: $17.05 incremental annual expense per $10,000 and 6.493755% estimated return (FAIL return). Reoptimized 60% / 40%: $18.20, 6.903567% return, 6.017830% volatility (PASS proposed rules). This is illustrative, not a fee forecast or transaction-cost evidence. Bid/ask spreads and commissions remain unmodelled; missing Vanguard spread evidence is not invented. November 23 fee/mandate overlays are not asserted known on the November 17 model decision.

Stop on infeasibility, failed rules, unavailable/altered inputs or unsupported historical-as-of claims; never relax objectives or constraints automatically. Defer live capital pending client approval, trading-cost evidence and human validation. Student ownership, AI-off prediction/pre-run GitHub commit, partner cold run/rehearsal, GitHub URL/publication/access, videos/transcripts and Brightspace submission remain unresolved. No repository or commit was created. See [local audit](local-audit.md).
