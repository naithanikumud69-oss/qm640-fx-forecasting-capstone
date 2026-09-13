"""
RQ2 v2 — true walk-forward GARCH(1,1) re-estimation, replacing the single
in-sample fit used previously (flagged limitation: "GARCH evaluated with a
single in-sample fit rather than full walk-forward re-estimation").

Methodology: refit GARCH(1,1) every REFIT_EVERY trading days using only data
available up to that point (no look-ahead), then forecast one step ahead for
each day until the next refit. This is the standard walk-forward protocol for
volatility-model backtests and is materially more expensive than a single fit
(N/REFIT_EVERY refits instead of 1) but gives an honest out-of-sample RMSE.
"""
import pandas as pd, numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from arch import arch_model
from scipy import stats
import json, warnings, time
warnings.filterwarnings("ignore")

D_RAW = "../data/raw/"
D_OUT = "../data/processed/"
D_FIG = "../figures/"

def load_fx(f):
    df = pd.read_csv(f, parse_dates=["observation_date"])
    col = df.columns[1]
    df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=[col]).reset_index(drop=True)
    df["log_ret"] = np.log(df[col]).diff()
    return df.rename(columns={"observation_date": "date", col: "level"}).dropna(subset=["log_ret"]).reset_index(drop=True)

inr = load_fx(D_RAW + "DEXINUS.csv")
ret_pct = inr["log_ret"] * 100
n = len(ret_pct)
split = int(n * 0.8)

REFIT_EVERY = 20  # ~1 trading month; re-estimate GARCH params this often

t0 = time.time()
garch_vol_fc = []
n_refits = 0
i = split
while i < n:
    train_slice = ret_pct.iloc[:i]  # everything up to (not including) day i — no look-ahead
    am = arch_model(train_slice, vol="Garch", p=1, q=1, dist="normal")
    fit = am.fit(disp="off")
    n_refits += 1
    horizon = min(REFIT_EVERY, n - i)
    fc = fit.forecast(horizon=horizon, reindex=False)
    step_vols = np.sqrt(fc.variance.values.flatten())
    garch_vol_fc.extend(step_vols.tolist())
    i += horizon
garch_vol_fc = np.array(garch_vol_fc[:n - split])
elapsed = time.time() - t0

realized = ret_pct.iloc[split:split + len(garch_vol_fc)].abs().values
garch_rmse_wf = np.sqrt(mean_squared_error(realized, garch_vol_fc))

print(f"Walk-forward GARCH: {n_refits} refits every {REFIT_EVERY} days, {elapsed:.1f}s, RMSE={garch_rmse_wf:.4f}")

# --- Single-fit GARCH (previous method) for direct comparison ---
am_single = arch_model(ret_pct, vol="Garch", p=1, q=1, dist="normal")
single_fit = am_single.fit(disp="off")
single_fc = single_fit.forecast(horizon=1, start=split, reindex=False)
garch_vol_single = np.sqrt(single_fc.variance.values.flatten())
garch_rmse_single = np.sqrt(mean_squared_error(realized[:len(garch_vol_single)], garch_vol_single))

# --- Random Forest (unchanged from v1, already out-of-sample) ---
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
naive_pred = df_rf.loc[split_rf:, "lag1"].abs().values
naive_rmse = np.sqrt(mean_squared_error(y_test, naive_pred))

n_common = min(len(garch_vol_fc), len(rf_pred))
loss_garch_wf = (realized[:n_common] - garch_vol_fc[:n_common])**2
loss_rf = (y_test.values[-n_common:] - rf_pred[-n_common:])**2
dm_stat, dm_p = stats.ttest_rel(loss_garch_wf, loss_rf)

rq2_v2 = {
    "method": f"walk-forward refit every {REFIT_EVERY} trading days ({n_refits} refits)",
    "n_train_initial": int(split), "n_test": len(garch_vol_fc), "n_test_rf": len(y_test),
    "garch_rmse_walkforward": float(garch_rmse_wf),
    "garch_rmse_single_fit_previous": float(garch_rmse_single),
    "rf_rmse": float(rf_rmse), "naive_rmse": float(naive_rmse),
    "dm_like_stat_wf_vs_rf": float(dm_stat), "dm_like_p_wf_vs_rf": float(dm_p),
}
print(json.dumps(rq2_v2, indent=2))
with open(D_OUT + "rq2_results_v2.json", "w") as f:
    json.dump(rq2_v2, f, indent=2)

# Plot: realized vs walk-forward GARCH vs single-fit GARCH vs RF
fig, ax = plt.subplots(figsize=(9, 4.2))
test_dates = inr["date"].iloc[split:split+n_common].values
ax.plot(test_dates, realized[:n_common], label="Realized |return| (%)", color="#333333", linewidth=1, alpha=0.5)
ax.plot(test_dates, garch_vol_fc[:n_common], label=f"GARCH walk-forward ({n_refits} refits)", color="#028090", linewidth=1.6)
ax.plot(test_dates, garch_vol_single[:n_common], label="GARCH single-fit (previous)", color="#028090", linewidth=1, linestyle="--", alpha=0.6)
ax.plot(test_dates, rf_pred[-n_common:], label="Random Forest forecast", color="#990011", linewidth=1.5)
ax.set_title("USD/INR: Walk-Forward vs. Single-Fit GARCH vs. RF (test period)", fontsize=11)
ax.set_ylabel("Absolute daily return (%)")
ax.legend(fontsize=7.5)
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(D_FIG + "fig_rq2_vol_forecast_v2.png", dpi=160)
print("saved fig_rq2_vol_forecast_v2.png")
