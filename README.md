# Forecasting Short-Term Exchange Rate Movements and Volatility Using Macroeconomic Indicators and Machine Learning

QM640 Data Analytics Capstone — Walsh College, Fall 2026
**Author:** Kumud Naithani · **Mentor:** Abhay Poddar · **Group 8**

This repository contains the full data, code, and deliverables for a capstone project comparing
macroeconomic-regression, machine-learning, and event-study approaches to forecasting short-term
direction and volatility for four currency pairs (USD/INR, EUR/USD, GBP/USD, USD/JPY), using
exclusively free, public, non-Kaggle data sources (FRED, World Bank, Eurostat, and the official
FOMC policy calendar).

See [`reports/QM640_Final_Report_Group8.pdf`](reports/QM640_Final_Report_Group8.pdf) for the full
write-up — background, literature review, methodology, results, limitations, and bibliography.

## Repository structure

```
data/
  raw/                        Original downloaded source data (FX levels, rates, CPI, trade
                              balance, GDP), pulled directly from FRED / World Bank / Eurostat.
  raw/superseded_stale_mirrors/
                              Earlier FRED CPI mirrors for India/UK/Japan that turned out to be
                              stale or discontinued (documented in the report, Table 4) — kept
                              here for provenance, not used in the final models.
  processed/                  Model outputs (rq1/rq2/rq4 results as JSON), plus the ADF
                              stationarity test and RQ1 predictor descriptive statistics.
notebooks/                    The three core analysis scripts, referenced as Appendix A/B/C in
                              the final report, plus their earlier (v1/pilot) versions for
                              history. Fully reproducible — see "Reproducing the results" below.
figures/                      All figures embedded in the final report and presentation.
build_scripts/                The reportlab scripts that generate the final report PDF and the
                              final presentation PDF directly from the processed results.
reports/                      Final deliverables: the final report and final presentation PDFs.
```

## Reproducing the results

Requires Python 3.11+ with `pandas`, `numpy`, `statsmodels`, `scikit-learn`, `arch`, `scipy`, and
`matplotlib`. From the `notebooks/` directory:

```bash
python3 final_analysis_v2.py    # RQ1 — four-predictor OLS regression, all four currency pairs
python3 final_analysis2_v2.py   # RQ2 — walk-forward GARCH(1,1) vs. Random Forest volatility forecast
python3 final_analysis3_v2.py   # RQ4 — FOMC event study, conditioned on policy-surprise magnitude
```

Each script reads its inputs from `../data/raw/`, writes its results to `../data/processed/`, and
(for RQ2 and RQ4) regenerates the corresponding figure into `../figures/`. Re-running them against
the committed raw CSVs reproduces every number and figure in the final report exactly — this was
verified by re-running all three scripts from a clean checkout of this repository before publishing.

## Key findings (see the final report for full detail)

- **RQ1** (macro regression): EUR/USD is the one pair where the full four-predictor model reaches
  statistical significance (R² = 12.4%, three of four coefficients significant at p < .05); the
  other three pairs fail to reject the null — consistent with, but not universally confirming,
  the Meese-Rogoff puzzle.
- **RQ2** (volatility forecasting): under genuine walk-forward re-estimation, both GARCH(1,1) and
  Random Forest cut RMSE by roughly 22–25% versus a naive baseline, with no significant difference
  between the two models.
- **RQ3** (news sentiment): architected but not yet executed — see the report's Limitations section.
- **RQ4** (FOMC event study): no significant average volatility spike across 71 meetings, but
  splitting on policy-surprise magnitude (proxied by 3-month T-bill yield changes) shows the
  theoretically expected direction, though the halved subsample is underpowered.

## Data sources

FRED (`fred.stlouisfed.org`), World Bank Open Data (`data.worldbank.org`), Eurostat
(`ec.europa.eu/eurostat`), and the official FOMC meeting calendar (`federalreserve.gov`). Full
source-by-variable attribution is in the final report's Data Dictionary (Table 2).
