# Local requirement audit — November 23, 2026

OpenAI Codex implemented the newly authorized educational mandate, descriptive fund signal and incremental operating-fee sensitivity. Student ownership remains unresolved. Education, not investment advice.

Scope remains the existing must-fix list. The original model decision is November 17; the frozen prices were downloaded October 22 and end September 2026. No evidence file, portfolio engine, price or provenance input was edited. All protected SHA-256 hashes are checked against [preserved hashes](../outputs/preserved-input-hashes.json). No Git repository or commit was created.

| Requirement | Local disposition |
| --- | --- |
| Proposed mandate | Lab 14 objective/benchmark, Lab 15 universe/grid/reserves and user-authorized illustrative 6.5% risk ceiling; client approval remains unresolved |
| Baselines and risk verdicts | Same-sample equal weight and inverse volatility beside constrained portfolio; inherited reference benchmark also displayed; return/reserve/risk checks |
| PIT signal/card | Lab 16 simple-return method on frozen September/August funds; Lab 17 strict download gate; descriptive only; uploads/Meridian unavailable without verified timestamp |
| Estimates/window | Existing ACWI one-point stress preserved; last-36-month result reproduced |
| Fees | One additional issuer ratio subtracted from already-net returns; fixed/reoptimized checks and dollars per $10,000; later sensitivity overlay, not transaction costs |
| Constraints/stop | Risk ceiling enforced through minimum-volatility result; reserve/return infeasibility and tighter risk ceiling stop without rule relaxation |
| Human/institutional | Student ownership/client approval, AI-off record/pre-run commit, partner cold run/rehearsal, GitHub publication/access, videos/transcripts and submission unresolved |

The benchmark fails reserve and risk (11.493085% volatility). Equal weight and inverse volatility fail return. The original mix passes; its estimate stress and fee stress each fail at fixed weights, then pass at 60%/40% after separate reoptimization. The 36-month mix is 85%/15%, return 6.849566%, volatility 1.762095%. These separate scenarios are not combined stresses or performance forecasts.

Verification: `uv run --locked python run.py` and `uv run --locked python verify_prework.py`. The latter checks copied-directory execution, Streamlit controls, independent signal formula/timing boundaries, incremental fee deduction, fixed/reoptimized agreement, risk infeasibility, protected hashes and local links. See [verification JSON](../outputs/prep-verification.json). Same installed environment, not a partner/clean-machine or visual browser review. A stdin documentation helper hit uv cache permissions; file-based scripts succeeded.

November 23 authorized update: the [proposed educational mandate](proposed-mandate.md) uses the Lab 14 6.5% objective (2.5% CPI estimate + 4% real objective), inherited provisional 40% VCIT / 60% ACWI reference benchmark, Lab 15 four-fund universe, long-only fully invested 5% grid and >=3% SGOV reserves. The 6.5% annualized sample-volatility ceiling is an AI-assisted illustrative proposal made at the user's request, above the existing 6.0178% ACWI stress; it is not client-validated risk appetite and requires Mason's review.

The [descriptive fund signal](signal-data-card.md) applies the Lab 16 September/August simple-return formula to the frozen local fund prices under the Lab 17 strict post-download gate. No threshold or optimizer predictor is added; DGS10 remains optional context. Uploads/Meridian without verified timestamps show unavailable. Stop historical-as-of claims at/before the October 22 download because Yahoo vintages are unavailable.

The [operating-fee card](cost-data-card.md) records ratios read from official issuer pages and their date basis. Historical adjusted returns already reflect fund expenses. Hypothetical doubling subtracts only one additional current ratio. Fixed 65% SGOV / 35% ACWI: $17.05 incremental annual expense per $10,000 and 6.493755% estimated return (FAIL return). Reoptimized 60% / 40%: $18.20, 6.903567% return, 6.017830% volatility (PASS proposed rules). This is illustrative, not a fee forecast or transaction-cost evidence. Bid/ask spreads and commissions remain unmodelled; missing Vanguard spread evidence is not invented. November 23 fee/mandate overlays are not asserted known on the November 17 model decision.

Stop on infeasibility, failed rules, unavailable/altered inputs or unsupported historical-as-of claims; never relax objectives or constraints automatically. Defer live capital pending client approval, trading-cost evidence and human validation. Student ownership, AI-off prediction/pre-run GitHub commit, partner cold run/rehearsal, GitHub URL/publication/access, videos/transcripts and Brightspace submission remain unresolved. No repository or commit was created. See [local audit](local-audit.md).
