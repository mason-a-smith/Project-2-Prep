AI use: OpenAI Codex assisted with code, analysis, documentation and verification.

The analysis and decision are mine (Mason Smith); education, not investment advice.

# Project 2 — portfolio decision studio

Personal confirmation pending: Mason must review and confirm the opening ownership statement before submission. Material assistance and limitations are in [validation-and-ai-use.md](docs/validation-and-ai-use.md).

**Committee decision: simulation-only pilot; defer live capital.** Intended user: Mason and the fictional foundation committee. The original horizon is seven years with annual rebalancing; monthly review is a proposed monitoring cadence.

## Start from the repository

Repository: https://github.com/mason-a-smith/Project-2-Prep

Use **Code → Download ZIP**, extract the complete repository, and open a terminal in the folder containing app.py, pyproject.toml and uv.lock. The smaller Mason hand-in ZIP is evidence only, not a runnable copy. Git cloning is an alternative.

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) if needed. From the repository root:

~~~powershell
uv run --locked python run.py
uv run --locked python -m streamlit run app.py
~~~

The first command reproduces outputs/VISIBLE_OUTPUT.md and outputs/results.json; the second starts the web app. Open the localhost URL printed by Streamlit, normally http://localhost:8501. Stop with Ctrl+C. For a busy port, append --server.port 8520. First setup needs internet for Python/dependencies; uv selects compatible Python 3.11–3.14. Calculations then use bundled data without API keys. Preserve source bytes: a corrupted sealed input stops the app; restore the reviewed repository rather than bypassing hashes.

Run every current application suite:

~~~powershell
uv run --locked python verify_all.py
~~~

The [final audit](docs/final-audit.md) distinguishes a repository-download/new-virtual-environment check from a human partner cold run. No public deployment is required or claimed.

## App and repository map

The six sidebar sections retain the dashboard, mandate reconciliation, interactive model, data/timing, separate company research, and validation. Filter the reconciliation by source/status; unsupported requirements remain **NOT TESTED**. Interactive controls/uploads are hypothetical and never amend the sealed committee snapshot. Validation shows the chronological diagnostic and Mason's locked record.

| Files | Purpose |
| --- | --- |
| app.py, portfolio_view.py | Web interface |
| portfolio.py, audit_controls.py | Preserved original engine/control evidence |
| current_rules.py, data_integrity.py | Actual-input labels and safe stops |
| prices.csv, data_sources.json, integrity-manifest.json | Frozen data and hashes |
| reconciliation.py, chronological.py | Mandate/loss/36-24 diagnostics |
| [Memo](docs/decision-memo.md), [validation record](docs/validation-and-ai-use.md) | Authoritative written drafts |
| [Manifest](docs/submission-manifest.md), [scripts](docs/video-preparation.md) | Locations and missing human materials |
| [Visible output](outputs/VISIBLE_OUTPUT.md), [snapshot](outputs/committee_snapshot.json) | Executed evidence readable without running code |

## Mandate, results and limits

Original [Lab 13](evidence/Lab%2013/Lab13.md): $100m foundation; $750,000 quarterly payouts; $3m twelve-month reserves; seven years; CPI+4% net over rolling five years; 60/40 global-equity/US-investment-grade reference and operational limits. The four ETFs, SGOV proxy, 5% grid, 6.5% arithmetic-return proxy and 6.5% volatility ceiling are later provisional AI-assisted choices, not client approval. Exact 4% real growth at assumed 2.5% inflation requires 6.6% nominal. Volatility is not a maximum drawdown or annual-loss cap.

Yahoo adjusted closes were downloaded October 22, 2026; 61 prices through September 2026 give 60 returns. Local source hashes/transformations are verified, not provider authenticity or earlier vintages. See [signal](docs/signal-data-card.md) and [cost](docs/cost-data-card.md) cards.

Baseline 65/0/0/35: 6.6643% estimated return, 5.2807% volatility. Conditional full-window scenario endpoints span 60–65% SGOV / 35–40% ACWI, with zero VGIT/VCIT; this is not a confidence interval. The 36-month search instead selects 85/0/0/15. The retrospective first-36/next-24 diagnostic stops for training infeasibility; previously examined data are not an untouched holdout. Annual-reset historical maximum month-end drawdown is −8.5576%; worst complete calendar-year return is −5.4078% (2022), excluding foundation payouts/full implementation costs and intramonth troughs.

Mason's [locked change](docs/mason-locked-submission.md), committed before execution, produces 55/10/10/25: **5.113379% return, 4.795116% volatility, 55% reserves; FAIL return**. Reject it under his rule; retain the original only conditionally for simulation. Prediction preparation is self-reported AI-off; execution was AI-assisted, a disclosed qualification against the shared course AI-closed-run wording.

Stop/reopen for failed selected limits, less than $3m approved reserves, infeasibility, corrupted/mistimed inputs, unsupported costs or unresolved original controls. Estimate, window, fee, assumed 25 bp trading-cost and constraint stresses are separate. No live capital is authorized.

[Hand-in evidence ZIP](outputs/Mason_Locked_Changed_Input_Submission.zip) preserves the historical locked run. Videos, corrected transcripts, partner evidence, personal confirmation and Brightspace receipt remain outstanding. Exact rubric scoring is pending the unavailable scoring anchors; no grade is invented.
