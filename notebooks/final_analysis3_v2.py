"""
RQ4 v2 — conditions the event study on actual policy "surprise" magnitude
instead of treating every scheduled FOMC date as equivalent (flagged
limitation: "RQ4 uses scheduled dates not true consensus-vs-actual
surprises").

True Bloomberg/Reuters consensus-survey data is proprietary and unavailable
here. The standard academic proxy for the market's policy surprise — used
since Kuttner (2001) and Gurkaynak, Sack & Swanson (2005) — is the change in
a short-maturity risk-free rate around the announcement window: a rate move
close to expectations produces almost no change in the 3-month T-bill yield,
while a genuine surprise (like the March 2020 emergency cuts) produces a
large one. We use |change in DTB3 (3-month T-bill, secondary market)| over
the event window [day -1, day +1] as the surprise-magnitude proxy, then
split the 71 real FOMC dates into high-surprise vs. low-surprise halves
(median split) and re-run the pre/post volatility comparison on each half
separately. If "it's the surprise, not the schedule, that matters" (the
takeaway already stated in the deck), the high-surprise half should show a
materially larger post-announcement volatility jump than the low-surprise
half — this directly tests that claim instead of asserting it.
"""
import pandas as pd, numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats
import json

D_RAW = "../data/raw/"
D_OUT = "../data/processed/"
D_FIG = "../figures/"

def load_fx(f):
    df = pd.read_csv(f, parse_dates=["observation_date"])
    col = df.columns[1]
    df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=[col]).reset_index(drop=True)
    df["log_ret"] = np.log(df[col]).diff()
    df["abs_ret"] = df["log_ret"].abs() * 100
    return df.rename(columns={"observation_date": "date", col: "level"}).dropna(subset=["log_ret"]).reset_index(drop=True)

inr = load_fx(D_RAW + "DEXINUS.csv").set_index("date")

dtb3 = pd.read_csv(D_RAW + "DTB3.csv", parse_dates=["observation_date"])
dtb3.columns = ["date", "yield"]
dtb3["yield"] = pd.to_numeric(dtb3["yield"], errors="coerce")
dtb3 = dtb3.dropna().set_index("date")["yield"]

fomc_dates = [
    "2018-01-31","2018-03-21","2018-05-02","2018-06-13","2018-08-01","2018-09-26","2018-11-08","2018-12-19",
    "2019-01-30","2019-03-20","2019-05-01","2019-06-19","2019-07-31","2019-09-18","2019-10-30","2019-12-11",
    "2020-01-29","2020-03-03","2020-03-15","2020-03-18","2020-04-29","2020-06-10","2020-07-29","2020-09-16","2020-11-05","2020-12-16",
    "2021-01-27","2021-03-17","2021-04-28","2021-06-16","2021-07-28","2021-09-22","2021-11-03","2021-12-15",
    "2022-01-26","2022-03-16","2022-05-04","2022-06-15","2022-07-27","2022-09-21","2022-11-02","2022-12-14",
    "2023-02-01","2023-03-22","2023-05-03","2023-06-14","2023-07-26","2023-09-20","2023-11-01","2023-12-13",
    "2024-01-31","2024-03-20","2024-05-01","2024-06-12","2024-07-31","2024-09-18","2024-11-07","2024-12-18",
    "2025-01-29","2025-03-19","2025-05-07","2025-06-18","2025-07-30","2025-09-17","2025-10-29","2025-12-10",
    "2026-01-28","2026-03-18","2026-04-29","2026-06-17","2026-07-29",
]
fomc_dates = pd.to_datetime(fomc_dates)
fomc_dates = fomc_dates[fomc_dates <= inr.index.max()]

pre_window, post_window = 5, 1
records = []
for d in fomc_dates:
    idx = inr.index.searchsorted(d)
    if idx >= len(inr) or idx < pre_window + 5:
        continue
    event_loc = idx
    pre = inr["abs_ret"].iloc[event_loc - pre_window - 5:event_loc - 5].mean()
    post = inr["abs_ret"].iloc[event_loc:event_loc + post_window + 1].mean()
    if np.isnan(pre) or np.isnan(post):
        continue

    # surprise proxy: |change in DTB3| from last available yield before day-1
    # to last available yield on/after day+1 of the event
    y_idx = dtb3.index.searchsorted(d)
    if y_idx <= 1 or y_idx >= len(dtb3):
        continue
    y_before = dtb3.iloc[max(0, y_idx - 2):y_idx].iloc[-1] if y_idx >= 2 else np.nan
    post_range = dtb3.iloc[y_idx:y_idx + 3]
    y_after = post_range.iloc[-1] if len(post_range) else np.nan
    if pd.isna(y_before) or pd.isna(y_after):
        continue
    surprise = abs(y_after - y_before) * 100  # in basis points

    records.append({"date": str(d.date()), "pre": pre, "post": post, "surprise_bp": surprise})

df = pd.DataFrame(records)
n_events = len(df)
median_surprise = df["surprise_bp"].median()
high = df[df["surprise_bp"] >= median_surprise]
low = df[df["surprise_bp"] < median_surprise]

def paired_stats(sub):
    t_stat, t_p = stats.ttest_rel(sub["post"], sub["pre"])
    return {
        "n": len(sub),
        "mean_pre": float(sub["pre"].mean()), "mean_post": float(sub["post"].mean()),
        "pct_increase": float((sub["post"].mean() - sub["pre"].mean()) / sub["pre"].mean() * 100),
        "paired_t_stat": float(t_stat), "paired_t_p": float(t_p),
    }

overall_t, overall_p = stats.ttest_rel(df["post"], df["pre"])
rq4_v2 = {
    "n_events_matched": n_events,
    "median_surprise_bp": float(median_surprise),
    "overall": {
        "mean_pre": float(df["pre"].mean()), "mean_post": float(df["post"].mean()),
        "paired_t_stat": float(overall_t), "paired_t_p": float(overall_p),
    },
    "high_surprise_half": paired_stats(high),
    "low_surprise_half": paired_stats(low),
}
print("=== RQ4 v2: surprise-conditioned event study (USD/INR) ===")
print(json.dumps(rq4_v2, indent=2))
with open(D_OUT + "rq4_results_v2.json", "w") as f:
    json.dump(rq4_v2, f, indent=2)

# Plot: high-surprise vs low-surprise pre/post comparison
fig, axes = plt.subplots(1, 2, figsize=(9.5, 4.2), sharey=True)
for ax, sub, title, color in [
    (axes[0], low, f"Low-surprise half (n={len(low)})\nmedian |DTB3 change| < {median_surprise:.0f}bp", "#69A297"),
    (axes[1], high, f"High-surprise half (n={len(high)})\nmedian |DTB3 change| >= {median_surprise:.0f}bp", "#990011"),
]:
    bp = ax.boxplot([sub["pre"], sub["post"]], labels=["Pre\n(-10 to -6)", "Post\n(0 to +1)"],
                     patch_artist=True, widths=0.5)
    for patch in bp["boxes"]:
        patch.set_facecolor(color)
        patch.set_alpha(0.55)
    ax.set_title(title, fontsize=9.5)
    ax.grid(alpha=0.3, axis="y")
axes[0].set_ylabel("Mean absolute daily return (%)")
fig.suptitle("USD/INR Volatility Around FOMC: Conditioned on Surprise Magnitude (3M T-bill yield move)", fontsize=10.5)
fig.tight_layout()
fig.savefig(D_FIG + "fig_rq4_event_study_v2.png", dpi=160)
print("saved fig_rq4_event_study_v2.png")
