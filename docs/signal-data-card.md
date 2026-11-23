# Frozen fund signal data card

Source: [local provenance](../data_sources.json), Yahoo Finance via yfinance, adjusted close (USD), sampled at the last trading observation in each completed calendar month without filling. Universe: SGOV / VGIT / VCIT / ACWI. Frozen download: **2026-10-22T21:27:42.703541Z**. Latest saved completed month: September 30, 2026; preceding month: August 31, 2026.

Lab 16 method: `signal = September adjusted close / August adjusted close - 1`. This is a unitless simple monthly return, displayed as a percentage. It is descriptive context only: no threshold, trading rule or optimizer predictor is added. Synthetic AAA/BBB/CCC results are not fund observations. DGS10 remains optional context, not a fund-return proxy.

| Fund | September simple return |
| --- | ---: |
| SGOV | +0.29586681% |
| VGIT | -2.31707976% |
| VCIT | -3.02167087% |
| ACWI | -1.18869087% |

Lab 17 admission rule: use this frozen snapshot only for decisions **strictly after** its recorded download. The November 17 model decision is after that cutoff. Load no later publications or updated prices; retrieval establishes availability of this snapshot, not historical availability on the measured dates. Yahoo adjusted-price vintages are unavailable: stop historical-as-of claims at or before download rather than infer availability from month labels. Revisions/distributions can affect adjusted history. Missing/changed frozen hashes stop signal use. Uploads and Meridian training without verified timestamps show signal unavailable, even if uploaded bytes resemble the local file.

The signal uses the saved final month even when the estimation window switches to 36 months or expected-return estimates are edited. It does not use those edited estimates. Source links and sampling details remain in the preserved provenance and [Lab 17 admission record](../evidence/Lab%2017/Project2_data_admission.md).
