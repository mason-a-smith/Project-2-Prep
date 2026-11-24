AI use: Mason supplied the change and prediction and reports preparing them without AI. OpenAI Codex transcribed the submission, committed it before execution, implemented the app comparison and verified the calculations. AI-off authorship is self-reported, not independently verified.

The analysis and decision are mine (Mason Smith); education, not investment advice.

# Mason Smith — Locked Changed-Input Record and actual result

## Locked submission and timing

The [verbatim prediction](mason-locked-prediction.md), [numerical input specification](mason-locked-input.json) and executable runner were committed to GitHub **before** the test was run:

- Pre-run commit: [462e6e2f38e0499d78bde4eedc4f1e927bd6d210](https://github.com/mason-a-smith/Project-2-Prep/commit/462e6e2f38e0499d78bde4eedc4f1e927bd6d210).
- GitHub commit timestamp: **2026-11-24 01:24:27 UTC**.
- Actual run started: **2026-11-24 01:24:50.924398 UTC**; completed **01:24:51.062951 UTC**.
- Pre-run file hashes and receipt: [mason-locked-commit.json](mason-locked-commit.json).
- Actual machine-readable result: [mason-locked-result.json](../outputs/mason-locked-result.json).
- Saved-run hash: [mason-locked-result-receipt.json](mason-locked-result-receipt.json).

These timestamps record packaging, GitHub commitment and execution, not the time of independent human authorship. The prior AI-assisted 70% reserve test remains separate. No partner cold run is claimed.

## One change; other inputs fixed

Mason specified reallocating 20 percentage points: reduce SGOV and ACWI by 10 points each, adding 10 points each to VGIT and VCIT. The original 65/0/0/35 allocation becomes **55/10/10/25**, in SGOV/VGIT/VCIT/ACWI order. Both sum to 100%; the proposed one-way allocation change is 20%, not a claim of actual annual turnover compliance.

Frozen data: 61 monthly adjusted prices, September 2021–September 2026; 60 monthly returns. Keep expected-return estimates, covariance, SGOV-only reserve eligibility and the 6.5% return / 3% reserve / 6.5% volatility pilot limits unchanged. No reoptimization, new fees or cost stress is introduced.

## Actual model results

| Measure | Original | Revised | Change |
| --- | ---: | ---: | ---: |
| Weights: SGOV / VGIT / VCIT / ACWI | 65% / 0% / 0% / 35% | 55% / 10% / 10% / 25% | −10 / +10 / +10 / −10 percentage points |
| Estimated annual return | 6.664255% | **5.113379%** | −1.550876 percentage points (−155.0876 bp) |
| Annualized sample volatility | 5.280674% | **4.795116%** | −0.485558 percentage point |
| SGOV reserve share | 65% | **55%** | −10 percentage points |
| Return >=6.5% | PASS | **FAIL** | Revised shortfall: 1.386621 percentage points |
| Reserve >=3% | PASS | **PASS** | Initial SGOV reserve proxy only |
| Volatility <=6.5% | PASS | **PASS** | Not an annual-loss guarantee |
| Numerical pilot verdict | PASS | **FAIL: return minimum** | No live investment authorization |

All five of Mason's directional/rule predictions are supported: lower estimated return, lower annualized volatility, failed return requirement, passed reserve requirement and passed volatility requirement. Increased sleeve diversification did not make the revised allocation satisfy the return constraint. This is agreement with this model calculation, not proof of forecasting skill or independent validation.

Calculation: `expected return = weights · (monthly arithmetic mean × 12)`; `annual volatility = sqrt(weightsᵀ × (monthly sample covariance ×12) × weights)`; reserves equal SGOV weight. The runner cross-checks both allocations using direct NumPy/Pandas calculations separately from engine covariance construction. The app recalculates the values and verifies the saved result before displaying it.

## Decision and limitations

Following Mason's stated decision rule, reject the revised allocation because it fails the 6.5% minimum expected-return requirement. Retain the original target only conditionally for the simulation-only pilot while it continues to pass modeled rules; the existing estimate, window and cost sensitivity and unresolved original mandate requirements still apply. No live capital is authorized.

These are historical arithmetic estimates, not actual future or realized account results. Adjusted prices reflect fund expenses; full trading/advisory costs, foundation cash flows and inflation-adjusted net returns are not established. A lower volatility estimate neither guarantees lower drawdown nor enforces the original maximum calendar-year loss requirement. See the app's full mandate reconciliation.

## Submission contents and reproduction

Open the app's **Validation** section, or the committee dashboard's **Mason's locked allocation comparison** expander. Submit this summary with its linked pre-run prediction, input specification, commit receipt and saved result. Automated verification is recorded in [mason-locked-verification.json](../outputs/mason-locked-verification.json); a partner's independent cold run remains outstanding.

The app verifies and recalculates this saved result without overwriting the locked transcript or recorded first run. `uv run --locked python verify_mason_locked_record.py` reproduces arithmetic/record checks and app views. `uv run --locked python mason_locked_run.py` is the original runner; rerunning it overwrites its output timestamp and makes the saved-run hash fail until explicitly reviewed, so retain the recorded first-run evidence for submission.
