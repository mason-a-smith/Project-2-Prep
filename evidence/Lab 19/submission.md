# Lab 19 — investor panel and Project 2 reference

Built with AI help. Memos are educational AI simulations, not actual investor views. Partner activities omitted as requested.

## The question

When three investors' skills read the same 10-K facts, where do they agree, where do they split — and would you trust the panel?

## COST verification and probe

The SEC extraction matches every supplied fiscal end, liabilities/equity ratio, missing R&D value and revenue CAGR of 7.51%. Buffett passes all three checks; Wood fails growth with R&D not known; Burry passes both, with latest liabilities/equity of 1.49. See [verification](verification.txt), [printed facts](results/COST/numbers.md) and the separate memos in `results/COST/`.

The 5% probe changes COST's Wood growth check to pass while R&D remains not known. Keep 15% to preserve the assigned high-growth screen; the probe shows that a threshold can change classification without changing facts. See [probe output](results/COST/threshold_probe.md).

## Your company: AAPL

Apple is the largest holding of ACWI in the issuer's November 20, 2026 holdings file. ACWI belongs to the saved Lab 15–17 universe. Apple files annual SEC reports; no fallback was necessary. See [selection evidence](references/company_selection.md).

| Investor | Check | AAPL |
|---|---|---|
| Buffett | ROE at least 15% every year | pass |
| Buffett | Owner earnings positive every year | pass |
| Buffett | Owner earnings grew first to last | pass |
| Cathie Wood | Revenue CAGR at least 15% | fail: 4.97% |
| Cathie Wood | Latest R&D / revenue at least 5% | pass: 9.56% |
| Burry | Operating cash flow at least net income every year | fail |
| Burry | Latest liabilities/equity at most twice | fail: 2.61 |

For the fiscal year ending September 27, 2025, operating cash flow of 111,482 USD millions was below net income of 112,010 USD millions, failing the every-year test. Apple also fails Wood's growth check at the lower 5% threshold. No required AAPL inputs are missing; COST's R&D gap remains explicitly missing.

Read [printed facts](results/AAPL/numbers.md), [Buffett memo](results/AAPL/memo.md), [Wood memo](results/AAPL/cathie_memo.md) and [Burry memo](results/AAPL/burry_memo.md). Verdicts: Buffett — watch it; Wood — watch; Burry — pass pending accounting and liability review. These judgments are independently reasoned prose, not automatic translations of check counts.

## Bull case — two sentences

Apple passes all Buffett checks, with positive simplified owner earnings throughout and higher owner earnings at the end than at the start. Research intensity also passes Wood's requirement, giving a reason to investigate future earning power without assuming spending guarantees innovation.

## Bear case — two sentences

Apple fails Wood's growth screen and both Burry checks, exposing concerns that the favorable profitability checks do not resolve. Those failures justify reviewing cash timing, obligations and durability before relying on the apparent quality signaled by ROE.

## Reflection and proposed decision

The panel gives favorable evidence on owner earnings and research spending but splits on the company assessment because growth, cash conversion and liability requirements fail. Agreement is correlated because the personas share inputs and extraction code; differing priorities and thresholds cause disagreement without requiring an arithmetic error.

**Only with a condition: use the panel to prioritize research after checking source periods and missing facts, and require valuation, risk review and decision-date availability before any Project 2 allocation.**

This decision is an AI-written draft for Mason's review, not a claim that Mason made a personal decision or completed a discussion.

## What is an AI panel?

A panel gives several analytical roles common evidence and lets each apply different criteria. Here, deterministic Python functions calculate the checks, and Codex writes separate persona memos after reading the printed output. Streamlit displays the saved results; it does not execute autonomous agents or call a model API. Different goals and thresholds explain why personas can disagree about the same company.

## Provenance and limits

Raw SEC responses, retrieval timestamps, hashes, tags, periods, accessions and filing dates are saved in `results/`. All six memos passed the numeric provenance check; see [validation](memo_validation.json). Numeric matching cannot validate context or qualitative claims.

Only Lab 14 onward methodology is used. Latest filings can revise older periods, so the extraction is not a decision-date backtest. Owner earnings subtract total tagged capex; high ROE can reflect the equity base; the liability screen does not prove solvency. Preserve these limits in Project 2.

## Checkout

Use the commands in [README.md](README.md); the app runs at http://127.0.0.1:8519. COST is the default ticker; enter AAPL for the company panel. Local files and results are ready; GitHub URLs remain pending a real repository destination. No quiz or GitHub submission is claimed.
