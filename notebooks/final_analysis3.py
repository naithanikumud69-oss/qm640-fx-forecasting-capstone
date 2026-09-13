import pandas as pd, numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats
import json

def load_fx(f):
    df = pd.read_csv(f, parse_dates=["observation_date"])
    col = df.columns[1]
    df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=[col]).reset_index(drop=True)
    df["log_ret"] = np.log(df[col]).diff()
    df["abs_ret"] = df["log_ret"].abs() * 100
    return df.rename(columns={"observation_date": "date", col: "level"}).dropna(subset=["log_ret"]).reset_index(drop=True)

inr = load_fx("DEXINUS.csv")
inr = inr.set_index("date")

# Real, verified FOMC rate-decision dates (second day of each 2-day meeting),
# 2018-2026, confirmed via federalreserve.gov (2021-2026) and press-release/
# historical records (2018-2020). Includes the two unscheduled emergency cuts
# in March 2020.
fomc_dates = [
    # 2018
    "2018-01-31","2018-03-21","2018-05-02","2018-06-13","2018-08-01","2018-09-26","2018-11-08","2018-12-19",
    # 2019
    "2019-01-30","2019-03-20","2019-05-01","2019-06-19","2019-07-31","2019-09-18","2019-10-30","2019-12-11",
    # 2020 (incl. 2 emergency meetings)
    "2020-01-29","2020-03-03","2020-03-15","2020-03-18","2020-04-29","2020-06-10","2020-07-29","2020-09-16","2020-11-05","2020-12-16",
    # 2021
    "2021-01-27","2021-03-17","2021-04-28","2021-06-16","2021-07-28","2021-09-22","2021-11-03","2021-12-15",
    # 2022
    "2022-01-26","2022-03-16","2022-05-04","2022-06-15","2022-07-27","2022-09-21","2022-11-02","2022-12-14",
    # 2023
    "2023-02-01","2023-03-22","2023-05-03","2023-06-14","2023-07-26","2023-09-20","2023-11-01","2023-12-13",
    # 2024
    "2024-01-31","2024-03-20","2024-05-01","2024-06-12","2024-07-31","2024-09-18","2024-11-07","2024-12-18",
    # 2025
    "2025-01-29","2025-03-19","2025-05-07","2025-06-18","2025-07-30","2025-09-17","2025-10-29","2025-12-10",
    # 2026 (through the data cutoff of Aug 1, 2026)
    "2026-01-28","2026-03-18","2026-04-29","2026-06-17","2026-07-29",
]
fomc_dates = pd.to_datetime(fomc_dates)
fomc_dates = fomc_dates[fomc_dates <= inr.index.max()]

pre_window, post_window = 5, 1  # trading days
pre_vals, post_vals, matched_events = [], [], []
for d in fomc_dates:
    idx = inr.index.searchsorted(d)
    if idx >= len(inr) or idx < pre_window + 5:
        continue
    # actual matched trading day at/after the event date
    event_loc = idx if inr.index[idx] == d else idx  # nearest trading day on/after event
    pre = inr["abs_ret"].iloc[event_loc - pre_window - 5:event_loc - 5].mean()  # baseline, days -10 to -6
    post = inr["abs_ret"].iloc[event_loc:event_loc + post_window + 1].mean()   # event day + next day
    if not (np.isnan(pre) or np.isnan(post)):
        pre_vals.append(pre)
        post_vals.append(post)
        matched_events.append(str(d.date()))

pre_vals, post_vals = np.array(pre_vals), np.array(post_vals)
n_events = len(pre_vals)

t_stat, t_p = stats.ttest_rel(post_vals, pre_vals)
w_stat, w_p = stats.wilcoxon(post_vals, pre_vals)

rq4_results = {
    "n_fomc_dates_total": len(fomc_dates),
    "n_events_matched": n_events,
    "mean_pre_event_abs_ret_pct": float(pre_vals.mean()),
    "mean_post_event_abs_ret_pct": float(post_vals.mean()),
    "pct_increase": float((post_vals.mean() - pre_vals.mean()) / pre_vals.mean() * 100),
    "paired_t_stat": float(t_stat), "paired_t_p": float(t_p),
    "wilcoxon_stat": float(w_stat), "wilcoxon_p": float(w_p),
}
print("=== RQ4 event-study results (USD/INR) ===")
print(json.dumps(rq4_results, indent=2))
with open("rq4_results.json", "w") as f:
    json.dump(rq4_results, f, indent=2)

# Plot: pre vs post box/violin-like comparison
fig, ax = plt.subplots(figsize=(6.5, 4.2))
bp = ax.boxplot([pre_vals, post_vals], labels=["Pre-announcement\n(days -10 to -6)", "Announcement window\n(day 0 to +1)"],
                 patch_artist=True, widths=0.5)
for patch, color in zip(bp["boxes"], ["#028090", "#990011"]):
    patch.set_facecolor(color)
    patch.set_alpha(0.55)
ax.set_ylabel("Mean absolute daily return (%)")
ax.set_title(f"USD/INR Volatility Around FOMC Announcements (n={n_events} events, 2018-2026)", fontsize=10)
ax.grid(alpha=0.3, axis="y")
fig.tight_layout()
fig.savefig("fig_rq4_event_study.png", dpi=160)
print("saved fig_rq4_event_study.png, n_events=", n_events)
