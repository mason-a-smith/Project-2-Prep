---
name: buffett-sec
description: Analyze a ticker's business using five years of SEC 10-K facts, deterministic Buffett checks, and a short qualitative memo. Use for Lab 18 or a Buffett business-quality review without price data.
---

Run bundled `scripts/sec_facts.py TICKER --output OUTPUT` with `SEC_USER_AGENT` naming Mason Smith and his real email. Ask for that email if absent; never invent it. Use keyless SEC EDGAR only. Never install FAskills or query its paid sources.

The script prints the latest five fiscal-year-end dates from 10-K submissions. Flows require an annual period (350–380 inclusive days accommodates 52/53-week years); balances are year-end instants. Filter form exactly 10-K. For a given tag and period choose the latest filing. Revenue tag priority: RevenueFromContractWithCustomerExcludingAssessedTax, Revenues. Net income: NetIncomeLoss. Operating cash flow: NetCashProvidedByUsedInOperatingActivities. Capex priority: PaymentsToAcquirePropertyPlantAndEquipment, PaymentsToAcquireProductiveAssets. Equity: StockholdersEquity. Preserve tags, periods, accessions, filing dates, raw snapshots and download metadata.

Code computes ROE = net income / year-end equity; owner earnings = operating cash flow - capex. Missing facts print `not found`. ROE and liabilities/equity with nonpositive or absent equity print `not known`. Any check with missing inputs prints `not known`. The three checks are ROE >= 15% every year, positive owner earnings every year, and owner earnings higher in the last year than the first. Never substitute an estimate, alternate bank capex, or the class answer key for SEC facts. Report discrepancies explicitly.

Read the script output before writing `OUTPUT/TICKER/memo.md`. Write a short first-person Buffett-inspired educational memo, clearly labeled AI simulation, choosing **own the business**, **watch it**, or **pass**. This is the model's judgment, not a verdict hardcoded from check results. Use only numbers printed in `numbers.md`; no arithmetic in prose. Explain evidence and limits. Do not infer a moat, honest management, or future durability from ratios alone. Missing owner earnings must explicitly prevent judging owner earnings. Never use prices, price targets, fair value, or a buy recommendation this week. Validate the memo with `unsupported_numbers`; revise unsupported numbers. This is a numeric provenance check, not proof that each claim uses its number correctly.

Read [philosophy notes](references/philosophy.md). Course rules override any conflicting philosophy formula, especially this simplified owner-earnings definition. Save the student's trust decision separately below the memo; do not claim the AI's opinion is the student's.
