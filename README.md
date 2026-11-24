AI use: OpenAI Codex assisted with code, analysis, documentation and verification.

The analysis and decision are mine (Mason Smith); education, not investment advice.

# Portfolio decision studio

Current correction: intended user is Mason and the fictional foundation committee; investment horizon is seven years. The committee decision is a paper pilot, with no live capital authorized. [Edition A versus Edition B](docs/edition-and-decision.md) compares the archived prior AI-assisted app with the current corrections. Selected return, reserve and volatility limits now appear accurately in current views; the historical engine and locked evidence remain preserved. See [corrections and verification](docs/application-corrections.md).

New: select **Mandate reconciliation** for the complete original Lab 13 S1–S10 review, separate pilot rules, searchable/filterable status table, CSV export, annual-rebalanced or buy-and-hold historical drawdown, worst month, rolling 12-month loss and complete calendar-year losses. The original mandate is not fully tested by the dashboard's numerical pilot PASS. See [methods and change record](docs/mandate-reconciliation.md) and [executed verification](outputs/reconciliation-verification.json). Run `uv run --locked python verify_reconciliation.py` for the added checks.

Start in this Project2 folder with Python 3.11–3.14 and uv installed:

```powershell
uv run --locked python run.py
uv run --locked python -m streamlit run app.py
```

Open http://localhost:8501 (or the URL printed by Streamlit). First setup downloads locked dependencies; later calculations use bundled data without credentials. Stop the server with Ctrl+C. If the port is busy, append `--server.port 8520` to the app command. Without uv: create a virtual environment, install numpy, pandas and streamlit, then run `python -m streamlit run app.py`; uv is preferred for exact reproduction.

The dashboard compares equal weight, inverse volatility and the constrained portfolio, with PASS/FAIL and each failed numerical rule. Use Interactive portfolio model to change estimates, window and constraints. Data & timing shows the frozen point-in-time signal and its data card. Validation contains the locked record and result. The source evidence remains bundled.

Mandate recovered from [Lab 13](evidence/Lab%2013/Lab13.md): fictional $100m foundation, seven years, $0.75m quarterly payouts, CPI+4% rolling-five-year aspiration. The educational pilot minimizes sample annual volatility subject to a 6.5% annual return proxy, 3% SGOV reserves, 6.5% annual volatility ceiling, long-only fully invested SGOV/VGIT/VCIT/ACWI, on a 5% grid. Reference benchmark: 60% ACWI / 40% VCIT, a proxy for global equity / US investment-grade bonds. The risk ceiling is a proposed modeling rule; it cannot guarantee a calendar-year loss below 10%. The modeled return proxy does not prove the rolling-five-year net objective.

Recommendation: simulation only, 60–65% SGOV / 35–40% ACWI, 0% VGIT/VCIT across the baseline and specified estimate/cost cases; 0% live capital authorized. These are conditional scenario endpoints, not a confidence interval. The 36-month search separately selects 85% SGOV / 15% ACWI, illustrating instability rather than expanding the recommendation. Review estimates, reserve funding, risk, costs and data at each month-end; annual rebalancing, maximum 25% annual turnover absent approval. Stop for failed rules, no feasible allocation, changed/missing snapshots, unavailable point-in-time evidence, or required operational approvals absent.

Stress coverage: ACWI return minus 1 percentage point; 60 versus 36 monthly returns; doubled fund expenses; assumed 25 bp annual implementation drag; risk ceiling tightened from 6.5% to 5%. Fixed and reoptimized results are separated. The tightened ceiling is infeasible. Costs are scenario assumptions, not measured execution estimates. See [cost card](docs/cost-data-card.md).

[Executed results](outputs/VISIBLE_OUTPUT.md), [memo](docs/decision-memo.md), [mandate](docs/proposed-mandate.md), [signal data card](docs/signal-data-card.md), [locked prediction](docs/locked-input.json), [video scripts](docs/video-preparation.md).

The locked test changes only the SGOV minimum from 3% to 70%. `uv run --locked python locked_run.py` refuses to run without a GitHub precommit receipt. Its prediction is AI-assisted under the user's instruction; no AI-off or independent human prediction is claimed. Prior ACWI sensitivity results are not presented as new predictions. Publication and execution status appear in Validation.

Verification: `uv run --locked python verify_final.py`. This checks actual app views and financial behaviors; it is not a partner cold run. Videos are supplied as recording scripts, not invented recordings. Client approval, realized performance and verified execution liquidity remain outside this educational model.
