"""Step 6 / Objective 2: user lifetime, and H4 (early opposition -> earlier exit).

Lifetime = last activity (comment or vote) - first activity. Right-censored if last activity >= 2022-07-01
(user may still be active); left-censored if first activity < 2013-07-01 (may predate the dataset).
H4 (commenters, landmark design): entry t0 = first comment; exposures measured in [t0, t0+30d];
survival counted from the day-30 landmark, among users still active after it. Cox PH stratified by cohort year.
"""
import numpy as np
import pandas as pd
from lifelines import CoxPHFitter, KaplanMeierFitter

from common import DERIVED, LEFT_CENSOR, RESULTS, RIGHT_CENSOR, T_START, Step, connect, log
from h4 import X, h4_frame
from plotstyle import ALT, NULL, OBS, plt

d = DERIVED.as_posix()
con = connect()
DAY = 86400

# ---------------- Descriptives ----------------
u = con.sql(f"""
  SELECT user_id, n_comments,
         -- 21 users have votes dated 2007-2012 (old articles still open); clip to the dataset start
         greatest({T_START}, least(coalesce(first_comment, first_vote), coalesce(first_vote, first_comment))) AS first_ts,
         greatest(coalesce(last_comment, last_vote), coalesce(last_vote, last_comment)) AS last_ts,
         first_comment IS NOT NULL AS commenter
  FROM '{d}/users.parquet'""").df()
u["life_days"] = (u.last_ts - u.first_ts) / DAY
u["censored"] = u.last_ts >= RIGHT_CENSOR
u["left_censored"] = u.first_ts < LEFT_CENSOR
u["cohort"] = pd.to_datetime(u.first_ts, unit="s").dt.year
desc = dict(
    users=len(u), commenters=int(u.commenter.sum()), voter_only=int((~u.commenter).sum()),
    share_right_censored=u.censored.mean(), share_left_censored=u.left_censored.mean(),
    share_lifetime_lt_1day=(u.life_days < 1).mean(), share_lifetime_lt_30days=(u.life_days < 30).mean(),
    median_life_days_raw=u.life_days.median(), share_single_comment=(u.n_comments == 1).mean(),
)
pd.DataFrame([desc]).to_csv(RESULTS / "06_lifetime_descriptives.csv", index=False)
log(f"[life] {desc}")

fig, axes = plt.subplots(1, 2, figsize=(11, 3.8))
# CCDF of lifetime (days), uncensored-and-not-left-censored vs all
for mask, lab, col in [(np.ones(len(u), bool), "All users", OBS), (u.commenter.to_numpy(), "Commenters", ALT)]:
    x = np.sort(u.life_days[mask].to_numpy() + 1)
    axes[0].loglog(x, 1 - np.arange(len(x)) / len(x), color=col, label=lab)
axes[0].set_xlabel("Lifetime + 1 (days)")
axes[0].set_ylabel("P(lifetime ≥ x)")
axes[0].set_title("Lifetime distribution (CCDF)")
axes[0].legend()

km_rows = []
cohort_users = u[~u.left_censored & u.commenter]
kmf = KaplanMeierFitter()
cmap = plt.get_cmap("Blues")
cohorts = list(range(2014, 2023, 2))
for i, c in enumerate(cohorts):
    g = cohort_users[cohort_users.cohort == c]
    kmf.fit(g.life_days / 365.25, event_observed=~g.censored, label=str(c))
    kmf.plot_survival_function(ax=axes[1], ci_show=False, color=cmap(0.35 + 0.6 * i / (len(cohorts) - 1)))
    km_rows.append(dict(cohort=c, n=len(g), median_years=kmf.median_survival_time_,
                        surv_1y=float(kmf.predict(1.0)), surv_3y=float(kmf.predict(3.0))))
axes[1].set_xlabel("Years since first activity")
axes[1].set_ylabel("Share still active")
axes[1].set_title("Kaplan–Meier survival of commenters, by entry cohort")
axes[1].yaxis.set_major_formatter(plt.matplotlib.ticker.PercentFormatter(1.0))
axes[1].legend(title="Entry year", ncols=2)
fig.tight_layout()
fig.savefig(RESULTS / "06_lifetime_ccdf_km.png")
pd.DataFrame(km_rows).to_csv(RESULTS / "06_km_by_cohort.csv", index=False)
log(f"[life] KM: {pd.DataFrame(km_rows).to_dict('records')}")

# ---------------- Opposition by tenure (newcomers vs veterans) ----------------
ten = con.sql(f"""
  WITH e AS (
    SELECT CASE WHEN tenure_a_days < 30 THEN '1: <30d' WHEN tenure_a_days < 365 THEN '2: 30d-1y'
                WHEN tenure_a_days < 3 * 365 THEN '3: 1-3y' ELSE '4: 3y+' END AS replier_tenure,
           CASE WHEN tenure_b_days < 30 THEN '1: <30d' WHEN tenure_b_days < 365 THEN '2: 30d-1y'
                WHEN tenure_b_days < 3 * 365 THEN '3: 1-3y' ELSE '4: 3y+' END AS target_tenure,
           vote_true
    FROM '{d}/edges_stance.parquet' WHERE ts >= {LEFT_CENSOR + 3 * 365 * DAY})
  SELECT replier_tenure, target_tenure, count(*) AS n,
         avg((vote_true = -1)::INT) FILTER (WHERE vote_true IS NOT NULL) AS p_down_parent
  FROM e GROUP BY ALL ORDER BY ALL""").df()
ten.to_csv(RESULTS / "06_opposition_by_tenure.csv", index=False)
log("[tenure] " + ten.to_string(index=False).replace("\n", " | "))

# ---------------- H4: early opposition -> exit (landmark Cox) ----------------
with Step("h4_features"):
    h, Z, info = h4_frame(con, window_days=30)
log(f"[h4] commenters entering 2013-07..2022-04: {info['n_entered']:,}; gone before day 30: {info['share_gone_before_landmark']:.1%}")
log(f"[h4] landmark population: {info['n_landmark']:,}; events (left before 2022-07): {info['event_share']:.1%}")

with Step("h4_cox"):
    cph = CoxPHFitter(penalizer=0.001)
    cph.fit(Z, duration_col="T_years", event_col="E", strata=["cohort"])
    s = cph.summary[["exp(coef)", "exp(coef) lower 95%", "exp(coef) upper 95%", "p"]]
    s.to_csv(RESULTS / "06_h4_cox.csv")
    log("[h4] hazard ratios per SD (binary for got_any_reply):\n" + s.to_string())
    uni = {c: CoxPHFitter().fit(Z[[c, "T_years", "E", "cohort"]], "T_years", "E", strata=["cohort"]).summary["exp(coef)"].iloc[0] for c in X}
    pd.Series(uni, name="univariate_HR").to_csv(RESULTS / "06_h4_cox_univariate.csv")
    log(f"[h4] univariate HRs: { {k: round(v, 3) for k, v in uni.items()} }")
    # activity-quartile table (explains HR > 1 for early activity: burst accounts leave fast)
    q = h.assign(q=pd.qcut(h.n_comments, [0, .5, .75, .9, 1], duplicates="drop")).groupby("q", observed=True)
    q.agg(n=("E", "size"), share_left=("E", "mean"), median_T_years=("T_years", "median")).to_csv(RESULTS / "06_h4_by_early_activity.csv")
    try:
        sample = Z.sample(min(20000, len(Z)), random_state=1)
        ph = CoxPHFitter(penalizer=0.001).fit(sample, "T_years", "E", strata=["cohort"])
        from lifelines.statistics import proportional_hazard_test
        pt = proportional_hazard_test(ph, sample, time_transform="rank").summary
        pt.to_csv(RESULTS / "06_h4_ph_test.csv")
        log("[h4] PH test (20k sample):\n" + pt.to_string())
    except Exception as ex:  # diagnostic only
        log(f"[h4] PH test failed: {ex!r}")

# Forest plot
fig, ax = plt.subplots(figsize=(7, 3.4))
names = {"downvote_share_recv": "Downvote share received", "hostile_reply_share_recv": "Hostile replies received",
         "hostile_reply_share_sent": "Hostile replies written", "got_any_reply": "Got any reply (yes/no)",
         "log_comments": "Early comments (log)"}
s = s.loc[list(names)]
y = np.arange(len(s))[::-1]
ax.errorbar(s["exp(coef)"], y, xerr=[s["exp(coef)"] - s["exp(coef) lower 95%"], s["exp(coef) upper 95%"] - s["exp(coef)"]],
            fmt="o", color=OBS, ecolor=OBS, capsize=0)
ax.axvline(1, color=NULL, lw=1)
ax.set_yticks(y, [names[i] for i in s.index])
ax.set_xlabel("Hazard ratio of leaving (per SD; >1 = leaves sooner)")
ax.set_title("H4 · Early-life (first 30 days) exposures and exit hazard")
ax.grid(axis="y", visible=False)
fig.savefig(RESULTS / "06_h4_cox.png")
log("[figs] wrote 06_lifetime_ccdf_km.png, 06_h4_cox.png")
