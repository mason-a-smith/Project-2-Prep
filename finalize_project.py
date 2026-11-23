"""Update the educational package from recovered Lab 13 evidence."""
from pathlib import Path
import json, hashlib, shutil
from datetime import datetime, timezone
R = Path(__file__).resolve().parent
disclosure = 'AI use: OpenAI Codex assisted with code, analysis, documentation and verification.\n\nThe analysis and decision are mine (Mason Smith); education, not investment advice.\n\n'
(R/'evidence/Lab 13').mkdir(exist_ok=True)
shutil.copy2(R.parent/'Lab 13/Lab13.md', R/'evidence/Lab 13/Lab13.md')
readme = '''# Portfolio decision studio

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
'''
(R/'README.md').write_text(disclosure+readme, encoding='utf-8')
f=R/'docs/proposed-mandate.md'
s=f.read_text(encoding='utf-8').replace('from preserved Labs 14–17', 'from recovered Lab 13 and preserved Labs 14–17')
s += '\nRecovered source: [Lab 13 personal-client mandate](../evidence/Lab%2013/Lab13.md). Its personal-client section supplies the four-fund pilot rules. Original Meridian operational requirements remain separate: annual rebalancing; <=25% annual turnover absent approval; >=90% five-day liquidity; <=8% company issuer exposure with diversified-fund exemptions. ETF liquidity is an implementation assumption requiring verification. No guarantee of a <=10% calendar-year loss is claimed.\n'
f.write_text(s, encoding='utf-8')
f=R/'docs/cost-data-card.md'
f.write_text(f.read_text(encoding='utf-8')+'\n## Additional transaction-cost scenario\n\nAssume 25% one-way annual turnover, defined as half the absolute weight changes, and 100 bp all-in cost per dollar traded: 0.25 × 0.01 = 0.0025, or 25 bp annual NAV drag ($25 per $10,000). This deliberately adverse educational assumption includes spreads/slippage/commissions without claiming observed quotes. Subtract 0.0025 from each annual asset return; fixed weights lose 25 bp; covariance is unchanged. Reoptimize separately. This scenario is separate from doubled operating fees and does not double-count baseline fund expenses. Initial funding costs, taxes and actual execution are not estimated.\n', encoding='utf-8')
f=R/'docs/decision-memo.md'
s=f.read_text(encoding='utf-8'); s=s[s.index('# Decision memo'):]; s=s.split('## Authorized educational overlay')[0]
s=s.replace('No untouched', 'No untouched')
s += '\n## Completed application update\n\nLab 13 has been recovered and is bundled. Its personal-client section supplies the pilot mandate; operational approval and the original loss promise remain unresolved. The app now exposes failed rules and estimate, window, operating-fee, transaction-cost and constraint scenarios. The implementation-cost scenario assumes 25 bp/year; it is not a quote. The 5% volatility-ceiling stress stops as infeasible. The locked 70% reserve test is separate; consult its commit receipt and actual result in Validation. Monitor monthly: estimated return <6.5%, annual volatility >6.5%, SGOV reserve <3%, projected annual turnover >25%, changed hashes or unavailable source timestamps trigger STOP/review. Any unsupported guarantee of a 10% maximum annual loss also stops live adoption.\n'
(R/'docs/decision-memo.md').write_text(disclosure+s, encoding='utf-8')
scripts='''# Video recording scripts

These are scripts for Mason to review and record; no recording or transcript is claimed.

## Video 1: research development (under 3 minutes)

OPENING

{opening}
Show Lab 13, Lab 14, Lab 15 and the app. Explain the foundation objective and the distinction between the original loss promise and the modeled volatility limit. Lab 14 uses training assumptions; Lab 15 supplies actual fund history. Labs 16–17 require information availability before the decision. The result is conditional: 65% SGOV and 35% ACWI passes numerical rules, but an equity-return haircut reverses that verdict. Explain why you endorse simulation rather than live deployment.

## Video 2: technical walkthrough (under 5 minutes)

OPENING

{opening}
Run the README commands and show the app. Trace adjusted prices to monthly returns, arithmetic annual mean, sample covariance times 12, grid search, and verdict checks. Explain equal weight and inverse volatility (inverse sigma normalized to sum to one). Show all four stress dimensions, including fixed versus reoptimized outcomes. Open the signal card and demonstrate rejection before download. Show the locked prediction, its GitHub commit before execution, then the result, reporting its actual status honestly.

## Video 3: committee recommendation (under 5 minutes)

OPENING

{opening}
Open with the app running. Recommend simulation only: conditional 60–65% SGOV and 35–40% ACWI, no VGIT/VCIT in these scenarios, no live capital. Compare both baselines and their failed return rule. Show the estimate and cost stresses, then tighten risk to an infeasible level. Explain that 36-month estimates select 85/15, showing window instability. Monitor return below 6.5%, risk above 6.5%, reserves below 3%, turnover above 25%, and source availability. Stop rather than weaken rules. Ask the committee to approve a paper pilot and resolve live operational requirements.
'''.format(opening=disclosure)
(R/'docs/video-preparation.md').write_text(disclosure+scripts, encoding='utf-8')
f=R/'app.py'; s=f.read_text(encoding='utf-8')
s=s.replace("'Last 36 months',\n    ]", "'Last 36 months',\n        'Fixed baseline last 36 months',\n        'Fixed baseline at 5% risk ceiling',\n        'Fixed baseline transaction cost stress',\n        'Reoptimized transaction cost stress',\n    ]")
s=s.replace('    rows = []\n    allocation_rows', '    for name in display_names:\n        chart_labels.setdefault(name, name)\n    rows = []\n    allocation_rows',1)
s=s.replace("'Annual incremental fee per $10,000': (", "'Failed rules': ', '.join(k for k, v in scenario['checks'].items() if not v) or 'None',\n            'Annual incremental fee per $10,000': (")
s=s.replace('Original Lab 13 mandate not found; AI-assisted proposal is awaiting student review.', 'Recovered personal-client mandate; see bundled Lab 13 evidence.')
s=s.replace("'Lab 13 is listed as a gap, not represented by invented student-authored material. '", "'Lab 13 has been recovered and its personal-client section is the pilot source. '")
s=s.replace("'Proposed educational mandate': 'docs/proposed-mandate.md',", "'Lab 13 mandate source': 'evidence/Lab 13/Lab13.md',\n        'Proposed educational mandate': 'docs/proposed-mandate.md',")
start=s.index('    st.warning(\n',s.index("st.subheader('Locked Changed-Input Record')")); end=s.index('    with st.expander',start)
s=s[:start]+'''    st.json(json.loads((ROOT / 'docs/locked-input.json').read_text()))
    receipt = ROOT / 'docs/locked-commit.json'
    outcome = ROOT / 'outputs/locked-result.json'
    if receipt.exists():
        st.json(json.loads(receipt.read_text()))
    else:
        st.warning('Pending GitHub pre-run commit. Locked test has not been executed.')
    if outcome.exists():
        st.json(json.loads(outcome.read_text()))
    st.caption('AI-assisted locked prediction, as authorized; no AI-off authorship claimed.')
'''+s[end:]
s=s.replace('Lower and farther right means more estimated return per unit of risk;', 'Up and left indicates higher estimated return and lower estimated risk;')
s=s.replace("    st.subheader('Committee decision')", "    with st.expander('Mandate: objective, universe, benchmark, risk and limits'):\n        st.markdown(read_markdown('docs/proposed-mandate.md'))\n    st.subheader('Committee decision')",1)
f.write_text(s, encoding='utf-8')
record={'record_id':'RESERVE70-2026-11-23','prepared_at_utc':datetime.now(timezone.utc).isoformat(),
 'AI_use':'OpenAI Codex drafted this prediction under user authorization; not AI-off.',
 'change':'Only reserve minimum: 0.03 to 0.70; SGOV remains sole eligible fund.',
 'unchanged':'Frozen data, 60-return window, 6.5% return target, 6.5% volatility cap, long-only fully invested 5% grid; no added cost stress.',
 'prediction':'65/35 fails reserve; no feasible optimized portfolio. With at least 70% SGOV, even the highest-return remainder in ACWI cannot meet 6.5%. STOP, do not relax rules.',
 'success_criterion':'Fixed allocation fails reserve and optimizer returns None; otherwise report prediction incorrect.',
 'input_sha256':{n:hashlib.sha256((R/n).read_bytes()).hexdigest() for n in ['prices.csv','data_sources.json','portfolio.py','audit_controls.py','locked_run.py']}}
if not (R/'docs/locked-input.json').exists():
    (R/'docs/locked-input.json').write_text(json.dumps(record, indent=2)+'\n',encoding='utf-8')
