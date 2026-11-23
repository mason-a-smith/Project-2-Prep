# Week 12 preparation and independent challenge

**Mason Smith | November 22, 2026 | AI-assisted preparation**

The relevant prep is complete locally: the model-risk reading has been applied to the existing portfolio, accessible coursework has been assembled, a one-command reproduction has run, and a draft mandate/memo and short review list are available. Student review, missing mandate details and the live partner activities remain separate.

## Reading response

The [Federal Reserve guidance, Section V](https://www.federalreserve.gov/frrs/guidance/supervisory-guidance-on-model-risk-management.htm) addresses three distinct questions: whether a model's construction fits its use, whether its outputs stand up against observed outcomes, and whether it remains suitable as circumstances change. Its scope excludes generative and agentic AI; the analogy here concerns the quantitative portfolio model. This reading does not certify the AI that helped build it.

**What evidence would let an independent challenger reject this model even when the output looks good?** A return target passed by in-sample arithmetic is insufficient for live adoption. This model's provisional mandate, narrow target margin, sensitivity to equity estimates, and missing prospective outcomes justify restricting use to simulation until those issues are resolved.

### Conceptual soundness applied to this portfolio

The model assumes historical arithmetic means are useful return estimates, uses a single covariance sample, minimizes volatility over a 5% grid, and labels SGOV as reserve eligible. Its purpose is constrained allocation, but the saved files do not establish a client's confirmed risk limit or reserve definition. A reviewer should reject a claim of client suitability if the actual mandate differs from these defaults. A reviewer should also reject a claim of continuous global optimality: the code searches only discrete grid points.

The price snapshot was retrieved after all measured months ended. That makes it available for this later reproduction, but does not prove the same adjusted prices were known on every past decision date. A historical strategy claim relying on those unarchived vintages should be restricted. The [Lab 17 admission record](../evidence/Lab%2017/Project2_data_admission.md) already reaches that narrower conclusion.

### Outcome analysis applied to this portfolio

The runner reproduces the archived baseline and compares two transparent baselines on the same sample. This verifies arithmetic and exposes constraint tradeoffs; it does not establish predictive performance. No untouched holdout, realized return record or after-cost implementation result is supplied. Reject any statement that the passing estimated return demonstrates the future target will be achieved.

The strongest existing challenge is the one-input stress: a one-percentage-point reduction in ACWI's annual estimate makes the original weights fail. The revised feasible weights add equity and risk. This directly qualifies the baseline recommendation without introducing another model or adding a new research question.

### Ongoing monitoring applied to this portfolio

Before each proposed monthly paper decision, archive the input vintage, record the actual information cutoff, rerun the mandate checks and baselines, and explain weight changes or overrides. Mason is the proposed monitoring owner; the arrangement needs student confirmation. Stop live use if an input is unavailable, a rule changes without approval, no feasible mix exists, or the client risk limit is undefined. Future paper outcomes should be retained separately from estimates; a favorable optimized output cannot close that evidence gap.

## Riskiest claim traced to evidence

**Claim under challenge:** the original 65% SGOV / 35% ACWI mix can meet the return objective without changing the decision when estimates weaken.

| Link in the argument | Existing evidence |
| --- | --- |
| Input source and timing | [prices.csv](../prices.csv), [download metadata](../data_sources.json), October 22, 2026 snapshot |
| Finance calculation | [portfolio.py](../portfolio.py): historical mean, covariance, constraint filter and minimum variance |
| Test | [run.py](../run.py): lower ACWI estimate by one percentage point while holding covariance and rules fixed |
| Observed result | [executed output](../outputs/VISIBLE_OUTPUT.md): original return falls from 6.6643% to 6.3143%, failing the 6.5% objective |
| Disposition | Qualify the recommendation; retain only a simulation pilot, with a conditional 60% SGOV / 40% ACWI stressed candidate |

The test checks a claim suggested in AI-assisted work. It is not a substitute for the student's own AI-closed prediction. Because this exact example has already been exposed with AI, do not relabel it later as an untouched human prediction.

## Mandate draft for student confirmation

| Field | Available record |
| --- | --- |
| Intended user and question | Educational committee: should this process be piloted under a client mandate? |
| Universe | SGOV / VGIT / VCIT / ACWI |
| Objective | Minimize estimated annual volatility subject to estimated return >=6.5% |
| Hard constraints | Long-only, fully invested, >=3% reserves; SGOV-only eligibility is provisional |
| Benchmark | Original 40% VCIT / 60% ACWI benchmark is documented; personal benchmark unconfirmed |
| Risk measure and limit | Annualized sample volatility; proposed educational ceiling 6.5%, client approval unresolved |
| Stop condition | No feasible allocation, a mandate violation, unavailable information, or unresolved live-use constraints |

No Lab 13 mandate was found. Confirming these fields is a required student decision, not a reason to invent missing preferences.

## Studio preparation

Bring the [README](../README.md), [draft memo](decision-memo.md), [must-fix list](must-fix.md), and [partner record](studio-record.md). Before the live studio discussion, write the requested decision and reversal claim without AI in your own words. The video outlines preserve separate purposes and do not claim recordings or transcripts exist.

The [Week 12 handout](https://github.com/CinderZhang/FIN43900-Fall2026/blob/main/lessons/week-12/student-handout.md) maps the mandate to Lab 13, numerical work to Labs 14–15, and timing work to Labs 16–17. Labs 18–19 are included as later supporting research. The current [Project 2 brief](https://github.com/CinderZhang/FIN43900-Fall2026/blob/main/projects/project-2-investment-management-application.md) governs the final bundle. Its Markdown rule and the [submission architecture's Project 2 rulings](https://github.com/CinderZhang/FIN43900-Fall2026/blob/main/PROJECT-SUBMISSION-ARCHITECTURE.md) mean no Edition A/B submission is required; the human locked test remains required.

## Authorized educational overlay — November 23, 2026

November 23 authorized update: the [proposed educational mandate](proposed-mandate.md) uses the Lab 14 6.5% objective (2.5% CPI estimate + 4% real objective), inherited provisional 40% VCIT / 60% ACWI reference benchmark, Lab 15 four-fund universe, long-only fully invested 5% grid and >=3% SGOV reserves. The 6.5% annualized sample-volatility ceiling is an AI-assisted illustrative proposal made at the user's request, above the existing 6.0178% ACWI stress; it is not client-validated risk appetite and requires Mason's review.

The [descriptive fund signal](signal-data-card.md) applies the Lab 16 September/August simple-return formula to the frozen local fund prices under the Lab 17 strict post-download gate. No threshold or optimizer predictor is added; DGS10 remains optional context. Uploads/Meridian without verified timestamps show unavailable. Stop historical-as-of claims at/before the October 22 download because Yahoo vintages are unavailable.

The [operating-fee card](cost-data-card.md) records ratios read from official issuer pages and their date basis. Historical adjusted returns already reflect fund expenses. Hypothetical doubling subtracts only one additional current ratio. Fixed 65% SGOV / 35% ACWI: $17.05 incremental annual expense per $10,000 and 6.493755% estimated return (FAIL return). Reoptimized 60% / 40%: $18.20, 6.903567% return, 6.017830% volatility (PASS proposed rules). This is illustrative, not a fee forecast or transaction-cost evidence. Bid/ask spreads and commissions remain unmodelled; missing Vanguard spread evidence is not invented. November 23 fee/mandate overlays are not asserted known on the November 17 model decision.

Stop on infeasibility, failed rules, unavailable/altered inputs or unsupported historical-as-of claims; never relax objectives or constraints automatically. Defer live capital pending client approval, trading-cost evidence and human validation. Student ownership, AI-off prediction/pre-run GitHub commit, partner cold run/rehearsal, GitHub URL/publication/access, videos/transcripts and Brightspace submission remain unresolved. No repository or commit was created. See [local audit](local-audit.md).
