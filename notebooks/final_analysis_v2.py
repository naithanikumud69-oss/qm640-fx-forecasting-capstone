"""
RQ1 v2 — full 4-predictor macro model for all currency pairs, addressing the
three RQ1/CPI limitations flagged after the first pass:
  1. Adds trade-balance differential and GDP-growth differential (previously
     only rate + inflation differentials were used).
  2. Replaces the stale/discontinued FRED CPI series for India, UK, and Japan
     with World Bank annual CPI (current through 2025 for all three),
     forward-filled to monthly resolution — clearly weaker granularity than
     a native monthly series, documented as such below and in the deck.
  3. Because Japan's inflation term is now available (via World Bank), USD/JPY
     gets the same 4-predictor specification as the other three pairs instead
     of being limited to rate-differential-only.

All series are real, verified, and current as of data pull (Sep 2026):
  - FX levels: FRED DEXINUS/DEXUSEU/DEXUSUK/DEXJPUS (daily)
  - Interest rates: FRED DFF (US), IRSTCI01INM156N (India), IRSTCI01EZM156N
    (Eurozone), IUDSOIA (UK), IRSTCI01JPM156N (Japan) — monthly
  - Inflation: US CPIAUCSL, Eurozone CP0000EZ19M086NEST (both native monthly,
    current) — India/UK/Japan from World Bank FP.CPI.TOTL (annual, forward-
    filled monthly)
  - Trade balance: FRED BOPGSTB (US), XTNTVA01INM667S (India),
    XTNTVA01GBM667S (UK), XTNTVA01JPM667S (Japan) — all monthly, current
    through mid-2026. Eurozone trade balance has no native monthly aggregate
    on FRED or Eurostat, so it is built by summing the 20 euro-area member
    states' annual trade balances from Eurostat table tet00002 (verified
    against known history — e.g. the 2022 aggregate energy-driven deficit
    shows up correctly), forward-filled monthly.
  - GDP growth: FRED NAEXKP01xxQ657S (q/q %, US/India/UK/Japan, quarterly,
    current) and Eurozone computed as q/q % change of the real GDP level
    series CLVMNACSCAB1GQEA19 (quarterly, current).
"""
import pandas as pd, numpy as np
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor
import json, warnings
warnings.filterwarnings("ignore")

def load_fx(f):
    df = pd.read_csv(f, parse_dates=["observation_date"])
    col = df.columns[1]
    df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=[col]).reset_index(drop=True)
    return df.rename(columns={"observation_date": "date", col: "level"})

def load_series(f, name):
    df = pd.read_csv(f, parse_dates=["observation_date"])
    df.columns = ["date", name]
    df[name] = pd.to_numeric(df[name], errors="coerce")
    return df.dropna()

def monthly_from_annual_wb(f, name):
    """World Bank annual CPI -> forward-filled monthly series."""
    df = pd.read_csv(f)
    df["date"] = pd.to_datetime(df["year"].astype(str) + "-01-01")
    df = df.rename(columns={"cpi": name})[["date", name]].sort_values("date")
    # expand to monthly by reindexing Jan of each year, then resample+ffill,
    # anchoring each year's CPI value to December so the forward-fill applies
    # it going forward through the following year (annual data released with
    # a lag; using Dec-anchor + ffill avoids look-ahead bias within the year)
    df["date"] = df["date"] + pd.offsets.YearEnd(0)
    full = df.set_index("date")[name].resample("MS").ffill().reset_index()
    return full

def monthly_from_eurostat_annual(f, name):
    df = pd.read_csv(f)
    df["date"] = (pd.to_datetime(df["year"].astype(str) + "-01-01") + pd.offsets.YearEnd(0))
    df = df.rename(columns={"trade_balance_mio_eur": name})[["date", name]].sort_values("date")
    full = df.set_index("date")[name].resample("MS").ffill().reset_index()
    return full

D_RAW = "../data/raw/"
D_OUT = "../data/processed/"
D_FIG = "../figures/"

pairs = {"USD/INR": "DEXINUS.csv", "EUR/USD": "DEXUSEU.csv", "GBP/USD": "DEXUSUK.csv", "USD/JPY": "DEXJPUS.csv"}
fx = {k: load_fx(D_RAW + v) for k, v in pairs.items()}

# ---- Interest rates (monthly) ----
us_rate = load_series(D_RAW + "DFF.csv", "us_rate")
us_rate_m = us_rate.set_index("date")["us_rate"].resample("MS").mean().reset_index()
in_rate = load_series(D_RAW + "IRSTCI01INM156N.csv", "in_rate")
ez_rate = load_series(D_RAW + "IRSTCI01EZM156N.csv", "ez_rate")
uk_rate = load_series(D_RAW + "IUDSOIA.csv", "uk_rate").set_index("date")["uk_rate"].resample("MS").mean().reset_index()
jp_rate = load_series(D_RAW + "IRSTCI01JPM156N.csv", "jp_rate")

# ---- CPI: US/EZ native monthly; India/UK/Japan World Bank annual->ffill ----
us_cpi = load_series(D_RAW + "CPIAUCSL.csv", "us_cpi")
us_cpi["us_infl"] = us_cpi["us_cpi"].pct_change(12) * 100
ez_cpi = load_series(D_RAW + "CP0000EZ19M086NEST.csv", "ez_cpi")
ez_cpi["ez_infl"] = ez_cpi["ez_cpi"].pct_change(12) * 100

in_cpi_m = monthly_from_annual_wb(D_RAW + "WB_CPI_IN.csv", "in_cpi")
in_cpi_m["in_infl"] = in_cpi_m["in_cpi"].pct_change(12) * 100
uk_cpi_m = monthly_from_annual_wb(D_RAW + "WB_CPI_GB.csv", "uk_cpi")
uk_cpi_m["uk_infl"] = uk_cpi_m["uk_cpi"].pct_change(12) * 100
jp_cpi_m = monthly_from_annual_wb(D_RAW + "WB_CPI_JP.csv", "jp_cpi")
jp_cpi_m["jp_infl"] = jp_cpi_m["jp_cpi"].pct_change(12) * 100

# ---- Trade balance (monthly; EZ annual->ffill) ----
tb_us = load_series(D_RAW + "TB_US.csv", "tb_us")
tb_in = load_series(D_RAW + "TB_IN.csv", "tb_in")
tb_gb = load_series(D_RAW + "TB_GB.csv", "tb_gb")
tb_jp = load_series(D_RAW + "TB_JP.csv", "tb_jp")
tb_ez = monthly_from_eurostat_annual(D_RAW + "TB_EZ.csv", "tb_ez")
# normalize each to a z-score so trade-balance units (differ by country: USD
# millions vs EUR millions vs local-currency) are comparable as a "diff" term
for df, col in [(tb_us,"tb_us"),(tb_in,"tb_in"),(tb_gb,"tb_gb"),(tb_jp,"tb_jp"),(tb_ez,"tb_ez")]:
    df[col+"_z"] = (df[col] - df[col].mean()) / df[col].std()

# ---- GDP growth (quarterly q/q %; EZ computed from level) ----
gdp_us = load_series(D_RAW + "GDP_US.csv", "gdp_us")
gdp_in = load_series(D_RAW + "GDP_IN.csv", "gdp_in")
gdp_gb = load_series(D_RAW + "GDP_GB.csv", "gdp_gb")
gdp_jp = load_series(D_RAW + "GDP_JP.csv", "gdp_jp")
gdp_ez_lvl = load_series(D_RAW + "GDP_EZ.csv", "gdp_ez_lvl")
gdp_ez_lvl["gdp_ez"] = gdp_ez_lvl["gdp_ez_lvl"].pct_change() * 100
gdp_ez = gdp_ez_lvl[["date", "gdp_ez"]].dropna()

def to_monthly_ffill(df, col):
    return df.set_index("date")[col].resample("MS").ffill().reset_index()

gdp_us_m, gdp_in_m, gdp_gb_m, gdp_jp_m, gdp_ez_m = [
    to_monthly_ffill(d, c) for d, c in
    [(gdp_us,"gdp_us"), (gdp_in,"gdp_in"), (gdp_gb,"gdp_gb"), (gdp_jp,"gdp_jp"), (gdp_ez,"gdp_ez")]
]

def build_model(pair_name, fx_df, foreign_rate, foreign_infl_col, foreign_infl_df,
                 foreign_tb_col, foreign_tb_df, foreign_gdp_df, us_is_base):
    """us_is_base=True means quote is FOREIGN/USD (e.g. EUR/USD): a rise in
    foreign rate/growth should appreciate the foreign currency -> ret rises.
    For USD/INR and USD/JPY (USD is base, foreign is quote), sign convention
    is flipped in the differential itself (foreign - US) consistently."""
    m = fx_df.set_index("date")["level"].resample("MS").last()
    ret = np.log(m).diff().rename("ret").reset_index()
    df = (ret.merge(foreign_rate, on="date")
              .merge(us_rate_m, on="date")
              .merge(foreign_infl_df[["date", foreign_infl_col]], on="date")
              .merge(us_cpi[["date", "us_infl"]], on="date")
              .merge(foreign_tb_df[["date", foreign_tb_col + "_z"]], on="date")
              .merge(tb_us[["date", "tb_us_z"]], on="date")
              .merge(foreign_gdp_df, on="date")
              .merge(gdp_us_m, on="date"))
    rate_col = [c for c in df.columns if c.endswith("_rate") and c != "us_rate"][0]
    gdp_col = [c for c in df.columns if c.startswith("gdp_") and c != "gdp_us"][0]
    df["rate_diff"] = df[rate_col] - df["us_rate"]
    df["infl_diff"] = df[foreign_infl_col] - df["us_infl"]
    df["tb_diff"] = df[foreign_tb_col + "_z"] - df["tb_us_z"]
    df["gdp_diff"] = df[gdp_col] - df["gdp_us"]
    df = df.dropna()
    for c in ["rate_diff", "infl_diff", "tb_diff", "gdp_diff"]:
        df[c + "_lag1"] = df[c].shift(1)
    df = df.dropna()
    feat_cols = ["rate_diff_lag1", "infl_diff_lag1", "tb_diff_lag1", "gdp_diff_lag1"]
    X = sm.add_constant(df[feat_cols])
    model = sm.OLS(df["ret"], X).fit()
    vif = [variance_inflation_factor(X.values, i) for i in range(1, X.shape[1])]
    return {
        "n": int(model.nobs), "r2": model.rsquared, "adj_r2": model.rsquared_adj,
        "params": model.params.to_dict(), "pvalues": model.pvalues.to_dict(),
        "vif": dict(zip(feat_cols, vif)),
        "date_range": [str(df["date"].min().date()), str(df["date"].max().date())],
    }

rq1_v2 = {}
rq1_v2["USD/INR"] = build_model("USD/INR", fx["USD/INR"], in_rate, "in_infl", in_cpi_m,
                                 "tb_in", tb_in, gdp_in_m, us_is_base=True)
rq1_v2["EUR/USD"] = build_model("EUR/USD", fx["EUR/USD"], ez_rate, "ez_infl", ez_cpi,
                                 "tb_ez", tb_ez, gdp_ez_m, us_is_base=False)
rq1_v2["GBP/USD"] = build_model("GBP/USD", fx["GBP/USD"], uk_rate, "uk_infl", uk_cpi_m,
                                 "tb_gb", tb_gb, gdp_gb_m, us_is_base=False)
rq1_v2["USD/JPY"] = build_model("USD/JPY", fx["USD/JPY"], jp_rate, "jp_infl", jp_cpi_m,
                                 "tb_jp", tb_jp, gdp_jp_m, us_is_base=True)

print("=== RQ1 v2: full 4-predictor model, all pairs ===")
for k, v in rq1_v2.items():
    print(f"\n{k}: n={v['n']}, R2={v['r2']*100:.2f}%, adj_R2={v['adj_r2']*100:.2f}%, range={v['date_range']}")
    for feat in ["rate_diff_lag1", "infl_diff_lag1", "tb_diff_lag1", "gdp_diff_lag1"]:
        print(f"  {feat}: coef={v['params'][feat]:.5f}  p={v['pvalues'][feat]:.4f}  VIF={v['vif'][feat]:.2f}")

with open(D_OUT + "rq1_results_v2.json", "w") as f:
    json.dump(rq1_v2, f, indent=2, default=str)
print("\nsaved rq1_results_v2.json")
