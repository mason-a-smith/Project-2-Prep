# Lab 19 — Project 2 reference

Uses only prior work from Lab14, lab 15, Lab 16, Lab 17 and Lab 18, plus this assignment and its cited sources. Partner activities are omitted as requested.

## Run

From the course workspace:

```powershell
$env:SEC_USER_AGENT = 'Mason Smith YOUR_REAL_EMAIL'
uv run python 'Lab 19/panel.py' COST
uv run python 'Lab 19/panel.py' AAPL
uv run --with streamlit python -m streamlit run 'Lab 19/app.py' --server.port 8519
uv run python 'Lab 19/test_panel.py'
uv run python 'Lab 19/verify.py'
```

Replace YOUR_REAL_EMAIL with your real contact email; no email has been invented. Downloads preserve raw SEC responses, timestamps, hashes, fact tags, periods, accessions and filing dates. Archive results before refreshing because current snapshots are overwritten. The inherited Lab 18 engine remains bundled; `panel.py` adds R&D and the two new investors. Historical availability restrictions from Labs 16–17 still apply: these latest-filing facts are not a historical decision-date vintage.

## Question and request

When three investors' skills read the same 10-K facts, where do they agree, where do they split — and would you trust the panel?

Extend my existing Lab 18 skill and Streamlit app without removing its extraction, chart, evidence, memo editing, numeric check or decision features. Use one shared five-year SEC fact set, with the same annual-period, tag-priority and latest-filing rules, plus Liabilities and ResearchAndDevelopmentExpense. Compute revenue CAGR in code as (last / first)^(1/4)-1. Add local Wood and Burry skills with the assigned checks, keep every missing value, write separate persona memos only after reading printed numbers, and check all three memos for unprinted numeric tokens. Compare the live COST output to the class reference without feeding the reference into calculations. Probe Wood at 5%, retain 15%, then analyze the largest holding of a saved Project 2 fund. Save results, bull/bear arguments and a conditional screening decision here.

## Company choice

The saved Lab 15–17 universe is SGOV/VGIT/VCIT/ACWI. ACWI is the equity fund with positive weight in the saved Lab 15 searches. The issuer's holdings CSV dated November 20, 2026 identifies Apple (AAPL) as the largest company holding, so AAPL is selected. No fund change or portfolio purchase is implied. Source: [iShares ACWI holdings CSV](https://www.ishares.com/us/products/239600/ishares-msci-acwi-etf/latest-holdings.csv), consulted November 22, 2026. Older search snippets suggesting NVIDIA were superseded by this dated file. No fallback is needed if Apple's five annual SEC filings are available.

## Threshold choice

Keep Wood's growth threshold at 15% because it preserves the assigned high-growth screen; 5% is a sensitivity probe, not evidence that the business changed. The live output must show whether COST flips and whether R&D remains not known.

## Panel interpretation

These are three educational analytical perspectives, not three independent witnesses or actual investor opinions. The shared facts reduce data inconsistency, while different predicates encode different priorities: Buffett emphasizes returns and owner earnings, Wood growth and research, Burry cash conversion and liabilities. Agreement is correlated because the inputs and much of the code are shared. Disagreement can arise from thresholds rather than arithmetic mistakes. Memos are AI judgments; check statuses are deterministic. Changing a threshold can change a screen verdict without changing any company facts.

No automatic memo generator pretends a check count is an investor's judgment. Read the printed `results/TICKER/numbers.md`, then author `memo.md`, `cathie_memo.md` and `burry_memo.md`, each labeled AI simulation and containing a verdict. Missing memos stay pending. The app displays them side by side, supports editing and saving, and flags unsupported numeric tokens across all three. Numeric matching cannot verify metric meaning or detect every unsupported qualitative claim.

## Explain `cathie_checks`

1. Compute growth through `revenue_growth`: require five observations, numeric endpoint revenues and positive starting revenue; otherwise return not known.
2. If growth is numeric, compare it with the selected threshold, inclusively. Return pass or fail. Missing growth stays not known.
3. Select the latest row only if the five-year set is complete; otherwise use an empty mapping.
4. Read latest revenue and exact-tag R&D; neither is guessed.
5. Divide only when both are numeric and revenue is positive. Otherwise the ratio is not known.
6. Compare a numeric ratio inclusively against 5%; preserve not known otherwise.
7. Return both labeled checks. The function does not write a memo or infer innovation quality.

## Proposed screening decision — for student review

Only with a condition: use the panel to prioritize further research after checking source periods and missing facts, and require valuation, risks and decision-date availability before any Project 2 allocation.

This is an AI draft, not a claim that Mason personally made this decision. Completed company-specific agreement, split, bull and bear appear in [submission.md](submission.md), based on downloaded SEC output.

## Verification and checkout

`verification.txt` records the comparison with the supplied COST answer, including discrepancies. Synthetic tests exercise threshold changes, missing inputs, exact boundaries and the number flag in each memo; synthetic data never populate live company results. COST has not matched merely because the reference was transcribed into the verification code.

No GitHub repository destination has been established or files published. Local checkout files are `README.md`, `app.py`, `panel.py`, `test_panel.py`, `verify.py`, the three skill folders, and actual results when downloaded. A GitHub URL must come from a real repository upload; none is fabricated. Brightspace quiz access and submission remain the student's responsibility.

## Sources

- [Wood source page](https://github.com/CinderZhang/FAskills/blob/main/financial-researcher/experts/cathie_wood.md): innovation and long-horizon perspective; course thresholds override the broader workflow.
- [Burry source page](https://github.com/CinderZhang/FAskills/blob/main/financial-researcher/experts/michael_burry.md): skeptical accounting and bear-case perspective; no inference of actual trades.
- [Streamlit columns](https://docs.streamlit.io/develop/api-reference/layout/st.columns): side-by-side memo layout.
- [SEC API documentation](https://www.sec.gov/search-filings/edgar-application-programming-interfaces): company facts and submissions.
- `project2_reference.txt` and the Lab 14–18 originals preserve prior methodology.

The pasted sell-off figures are a classroom scenario, not a verified current market observation. A Wood-inspired interpretation would reconsider whether the innovation thesis survives; a Burry-inspired interpretation would inspect cash conversion, leverage and footnotes before treating a decline as an opportunity. Neither implies a particular actual trade.

## Startup debug record

Command: `uv run --with streamlit python -m streamlit run 'Lab 18/app.py' --server.headless true --server.address 127.0.0.1 --server.port 8518`

Exact initial error:

```text
error: Failed to initialize cache at `C:\Users\mason\AppData\Local\uv\cache`
  Caused by: failed to open file `C:\Users\mason\AppData\Local\uv\cache\sdists-v9\.git`: Access is denied. (os error 5)
```

The approved retry started the server at http://127.0.0.1:8518. The browser connector reported `No browser is available`; server startup alone does not establish a visual inspection. The original Lab 18 app has no saved COST extraction; completed COST and AAPL downloads and memos are saved in Lab 19/results. The Lab 19 panel runs on port 8519.
