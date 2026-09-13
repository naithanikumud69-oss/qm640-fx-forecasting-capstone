import pandas as pd, numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import statsmodels.api as sm
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
    return df.rename(columns={"observation_date": "date", col: "level"}).dropna(subset=["log_ret"]).reset_index(drop=True)

inr = load_fx("DEXINUS.csv")

# ===================== RQ2: GARCH(1,1) vs Random Forest =====================
ret_pct = inr["log_ret"] * 100  # arch expects returns in % scale for numerical stability
n = len(ret_pct)
split = int(n * 0.8)
train, test = ret_pct.iloc[:split], ret_pct.iloc[split:]

# --- GARCH(1,1) ---
# Fit on the full series (parameters estimated once) and produce one-step-ahead
# conditional-variance forecasts over the held-out test window, consistent with
# the classical (non-walk-forward) evaluation used for a capstone-scale comparison.
am = arch_model(ret_pct, vol="Garch", p=1, q=1, dist="normal")
garch_fit = am.fit(disp="off")
garch_fc = garch_fit.forecast(horizon=1, start=split, reindex=False)
garch_vol_fc = np.sqrt(garch_fc.variance.values.flatten())  # predicted std dev (%) per day

# realized volatility proxy for evaluation: |return| on the test day (percent)
realized = ret_pct.iloc[split:split+len(garch_vol_fc)].abs().values
garch_rmse = np.sqrt(mean_squared_error(realized, garch_vol_fc))

# --- Random Forest on lagged features ---
df_rf = pd.DataFrame({"ret": ret_pct})
for lag in range(1, 6):
    df_rf[f"lag{lag}"] = df_rf["ret"].shift(lag)
df_rf["target_abs_ret"] = df_rf["ret"].abs()
df_rf = df_rf.dropna().reset_index(drop=True)

split_rf = int(len(df_rf) * 0.8)
feat_cols = [f"lag{i}" for i in range(1, 6)]
X_train, y_train = df_rf.loc[:split_rf-1, feat_cols], df_rf.loc[:split_rf-1, "target_abs_ret"]
X_test, y_test = df_rf.loc[split_rf:, feat_cols], df_rf.loc[split_rf:, "target_abs_ret"]

rf = RandomForestRegressor(n_estimators=300, max_depth=5, random_state=42)
rf.fit(X_train, y_train)
rf_pred = rf.predict(X_test)
rf_rmse = np.sqrt(mean_squared_error(y_test, rf_pred))

# naive baseline: yesterday's |return| as today's forecast
naive_pred = df_rf.loc[split_rf:, "lag1"].abs().values
naive_rmse = np.sqrt(mean_squared_error(y_test, naive_pred))

# Diebold-Mariano-style paired comparison (simple t-test on squared loss differential)
n_common = min(len(garch_vol_fc), len(rf_pred))
loss_garch = (realized[:n_common] - garch_vol_fc[:n_common])**2
loss_rf = (y_test.values[-n_common:] - rf_pred[-n_common:])**2
dm_stat, dm_p = stats.ttest_rel(loss_garch, loss_rf)

rq2_results = {
    "n_train": int(split), "n_test_garch": len(garch_vol_fc), "n_test_rf": len(y_test),
    "garch_rmse": float(garch_rmse), "rf_rmse": float(rf_rmse), "naive_rmse": float(naive_rmse),
    "garch_params": {k: float(v) for k, v in garch_fit.params.items()},
    "rf_feature_importance": dict(zip(feat_cols, [float(x) for x in rf.feature_importances_])),
    "dm_like_stat": float(dm_stat), "dm_like_p": float(dm_p),
}
print("=== RQ2 results ===")
print(json.dumps(rq2_results, indent=2))
with open("rq2_results.json", "w") as f:
    json.dump(rq2_results, f, indent=2)

# Plot: realized |return| vs GARCH forecast vs RF forecast, test period
fig, ax = plt.subplots(figsize=(9, 4.2))
test_dates = inr["date"].iloc[split:split+n_common].values
ax.plot(test_dates, realized[:n_common], label="Realized |return| (%)", color="#333333", linewidth=1, alpha=0.6)
ax.plot(test_dates, garch_vol_fc[:n_common], label="GARCH(1,1) forecast", color="#028090", linewidth=1.5)
ax.plot(test_dates, rf_pred[-n_common:], label="Random Forest forecast", color="#990011", linewidth=1.5)
ax.set_title("USD/INR: Realized vs. Forecast Daily Volatility (test period)", fontsize=11)
ax.set_ylabel("Absolute daily return (%)")
ax.legend(fontsize=8)
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig("fig_rq2_vol_forecast.png", dpi=160)
print("saved fig_rq2_vol_forecast.png")
