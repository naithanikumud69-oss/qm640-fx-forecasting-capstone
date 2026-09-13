import pandas as pd, numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from arch import arch_model
from scipy import stats
import json, warnings
warnings.filterwarnings("ignore")

def load_fx(f):
    df = pd.read_csv(f, parse_dates=["observation_date"])
    col = df.columns[1]
    df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=[col]).reset_index(drop=True)
    df["log_ret"] = np.log(df[col]).diff()
    return df.rename(columns={"observation_date": "date", col: "level"})

def load_series(f, name):
    df = pd.read_csv(f, parse_dates=["observation_date"])
    df.columns = ["date", name]
    df[name] = pd.to_numeric(df[name], errors="coerce")
    return df.dropna()

pairs = {"USD/INR": "DEXINUS.csv", "EUR/USD": "DEXUSEU.csv", "GBP/USD": "DEXUSUK.csv", "USD/JPY": "DEXJPUS.csv"}
fx = {k: load_fx(v) for k, v in pairs.items()}

# ---- Interest rates (monthly) ----
us_rate = load_series("DFF.csv", "us_rate")
us_rate_m = us_rate.set_index("date")["us_rate"].resample("MS").mean().reset_index()
in_rate = load_series("IRSTCI01INM156N.csv", "in_rate")
ez_rate = load_series("IRSTCI01EZM156N.csv", "ez_rate")
uk_rate = load_series("IUDSOIA.csv", "uk_rate").set_index("date")["uk_rate"].resample("MS").mean().reset_index()
jp_rate = load_series("IRSTCI01JPM156N.csv", "jp_rate")

# ---- CPI (monthly, YoY inflation) ----
us_cpi = load_series("CPIAUCSL.csv", "us_cpi")
us_cpi["us_infl"] = us_cpi["us_cpi"].pct_change(12) * 100
in_cpi = load_series("INDCPIALLMINMEI.csv", "in_cpi")
in_cpi["in_infl"] = in_cpi["in_cpi"].pct_change(12) * 100
ez_cpi = load_series("CP0000EZ19M086NEST.csv", "ez_cpi")
ez_cpi["ez_infl"] = ez_cpi["ez_cpi"].pct_change(12) * 100
uk_cpi = load_series("GBRCPIALLMINMEI.csv", "uk_cpi")
uk_cpi["uk_infl"] = uk_cpi["uk_cpi"].pct_change(12) * 100

# ---- Build monthly FX return per pair ----
def monthly_ret(df):
    m = df.set_index("date")["level"].resample("MS").last()
    return np.log(m).diff().reset_index().rename(columns={"level": "ret", 0: "ret"})

results = {}

# ===== RQ1: multi-predictor OLS per pair =====
rq1_results = {}

# USD/INR: interest_rate_diff + inflation_diff
m = fx["USD/INR"].set_index("date")["level"].resample("MS").last()
ret = np.log(m).diff().rename("ret").reset_index()
df1 = ret.merge(in_rate, on="date").merge(us_rate_m, on="date").merge(in_cpi[["date","in_infl"]], on="date").merge(us_cpi[["date","us_infl"]], on="date")
df1["rate_diff"] = df1["in_rate"] - df1["us_rate"]
df1["infl_diff"] = df1["in_infl"] - df1["us_infl"]
df1 = df1.dropna()
df1["rate_diff_lag1"] = df1["rate_diff"].shift(1)
df1["infl_diff_lag1"] = df1["infl_diff"].shift(1)
df1 = df1.dropna()
X = sm.add_constant(df1[["rate_diff_lag1", "infl_diff_lag1"]])
model1 = sm.OLS(df1["ret"], X).fit()
vif = [variance_inflation_factor(X.values, i) for i in range(1, X.shape[1])]
rq1_results["USD/INR"] = {"n": int(model1.nobs), "r2": model1.rsquared, "adj_r2": model1.rsquared_adj,
                            "params": model1.params.to_dict(), "pvalues": model1.pvalues.to_dict(), "vif": vif}

# EUR/USD: interest_rate_diff + inflation_diff (full range)
m = fx["EUR/USD"].set_index("date")["level"].resample("MS").last()
ret = np.log(m).diff().rename("ret").reset_index()
df2 = ret.merge(ez_rate, on="date").merge(us_rate_m, on="date").merge(ez_cpi[["date","ez_infl"]], on="date").merge(us_cpi[["date","us_infl"]], on="date")
df2["rate_diff"] = df2["ez_rate"] - df2["us_rate"]
df2["infl_diff"] = df2["ez_infl"] - df2["us_infl"]
df2 = df2.dropna()
df2["rate_diff_lag1"] = df2["rate_diff"].shift(1)
df2["infl_diff_lag1"] = df2["infl_diff"].shift(1)
df2 = df2.dropna()
X = sm.add_constant(df2[["rate_diff_lag1", "infl_diff_lag1"]])
model2 = sm.OLS(df2["ret"], X).fit()
vif2 = [variance_inflation_factor(X.values, i) for i in range(1, X.shape[1])]
rq1_results["EUR/USD"] = {"n": int(model2.nobs), "r2": model2.rsquared, "adj_r2": model2.rsquared_adj,
                            "params": model2.params.to_dict(), "pvalues": model2.pvalues.to_dict(), "vif": vif2}

# GBP/USD: interest_rate_diff + inflation_diff
m = fx["GBP/USD"].set_index("date")["level"].resample("MS").last()
ret = np.log(m).diff().rename("ret").reset_index()
df3 = ret.merge(uk_rate, on="date").merge(us_rate_m, on="date").merge(uk_cpi[["date","uk_infl"]], on="date").merge(us_cpi[["date","us_infl"]], on="date")
df3["rate_diff"] = df3["uk_rate"] - df3["us_rate"]
df3["infl_diff"] = df3["uk_infl"] - df3["us_infl"]
df3 = df3.dropna()
df3["rate_diff_lag1"] = df3["rate_diff"].shift(1)
df3["infl_diff_lag1"] = df3["infl_diff"].shift(1)
df3 = df3.dropna()
X = sm.add_constant(df3[["rate_diff_lag1", "infl_diff_lag1"]])
model3 = sm.OLS(df3["ret"], X).fit()
vif3 = [variance_inflation_factor(X.values, i) for i in range(1, X.shape[1])]
rq1_results["GBP/USD"] = {"n": int(model3.nobs), "r2": model3.rsquared, "adj_r2": model3.rsquared_adj,
                            "params": model3.params.to_dict(), "pvalues": model3.pvalues.to_dict(), "vif": vif3}

# USD/JPY: interest_rate_diff only (inflation unavailable - confirmed discontinued)
m = fx["USD/JPY"].set_index("date")["level"].resample("MS").last()
ret = np.log(m).diff().rename("ret").reset_index()
df4 = ret.merge(jp_rate, on="date").merge(us_rate_m, on="date")
df4["rate_diff"] = df4["jp_rate"] - df4["us_rate"]
df4 = df4.dropna()
df4["rate_diff_lag1"] = df4["rate_diff"].shift(1)
df4 = df4.dropna()
X = sm.add_constant(df4[["rate_diff_lag1"]])
model4 = sm.OLS(df4["ret"], X).fit()
rq1_results["USD/JPY"] = {"n": int(model4.nobs), "r2": model4.rsquared, "adj_r2": model4.rsquared_adj,
                            "params": model4.params.to_dict(), "pvalues": model4.pvalues.to_dict(), "vif": None,
                            "note": "inflation differential excluded - Japan CPI series confirmed discontinued on FRED since Jun 2021"}

print("=== RQ1 multi-predictor results ===")
for k, v in rq1_results.items():
    print(k, {kk: (round(vv,4) if isinstance(vv,(int,float)) else vv) for kk,vv in v.items() if kk not in ("params","pvalues")})
    print("  params:", {kk: round(vv,5) for kk,vv in v["params"].items()})
    print("  pvalues:", {kk: round(vv,4) for kk,vv in v["pvalues"].items()})

with open("rq1_results.json", "w") as f:
    json.dump(rq1_results, f, indent=2, default=str)
