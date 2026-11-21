"""Step 9: the longest-living users (meeting 2026-10-19: "take the top 10% by lifetime and see what changes").

Population = the H4 landmark population (commenters whose first comment is in [2013-07, 2022-04) and who are
still active 30 days later). Lifetime = last activity - first comment, so it is right-censored at 2022-07-01.
Groups (compared with everyone else in the population):
  top10_all     lifetime in the top 10% of the whole population
  top10_cohort  lifetime in the top 10% within the entry-year cohort (removes the "older cohorts had more time" effect)
  gt2y, gt3y    lifetime above 2 / 3 years
Questions (same as for the whole population):
  a) Negativity in replies: early (first 30 days) hostile/friendly replies sent and received, downvote share received.
  b) Does early negativity predict being in the long-lived group? Logit with cohort fixed effects.
  c) Within the group, does negativity relate to how long they stay? Spearman with lifetime.
  d) Whole-life stance by tenure: downvote/upvote share of replies written and received, long-lived vs rest.
"""
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy.stats import spearmanr

from common import DERIVED, RESULTS, Step, connect, log
from h4 import h4_frame
from plotstyle import ALT, NULL, OBS, plt

d = DERIVED.as_posix()
con = connect()
PCT = plt.matplotlib.ticker.PercentFormatter(1.0)

with Step("population"):
    h, Z, info = h4_frame(con, window_days=30)
    h = h.reset_index(drop=True)
    h["life_years"] = h.T_years + 30 / 365.25  # from first comment
    h["top10_all"] = h.life_years >= h.life_years.quantile(0.9)
    h["top10_cohort"] = h.life_years >= h.groupby("cohort").life_years.transform(lambda s: s.quantile(0.9))
    h["gt2y"] = h.life_years >= 2
    h["gt3y"] = h.life_years >= 3
    GROUPS = ["top10_all", "top10_cohort", "gt2y", "gt3y"]
    log(f"[pop] n={len(h):,}; 90th pct lifetime = {h.life_years.quantile(0.9):.2f} y; "
        + "; ".join(f"{g}: {int(h[g].sum()):,} ({h[g].mean():.1%}), censored {h.loc[h[g], 'E'].eq(0).mean():.0%}" for g in GROUPS))

# ---------------- a) early profile ----------------
def profile(g):
    """Pooled early-window rates and user-level medians for one grouping column."""
    rows = []
    for flag, sub in h.groupby(g):
        rows.append(dict(
            group=g, long_lived=bool(flag), n=len(sub), median_life_years=sub.life_years.median(),
            median_early_comments=sub.n_comments.median(), p_got_any_reply=sub.got_any_reply.mean(),
            downvote_share_recv=sub.rneg.sum() / (sub.rpos.sum() + sub.rneg.sum()),
            upvote_share_recv=sub.rpos.sum() / (sub.rpos.sum() + sub.rneg.sum()),
            hostile_reply_share_recv=sub.n_recv_hostile.sum() / sub.n_recv.sum(),
            friendly_reply_share_recv=sub.n_recv_friendly.sum() / sub.n_recv.sum(),
            hostile_reply_share_sent=sub.n_sent_hostile.sum() / sub.n_sent.sum(),
            friendly_reply_share_sent=sub.n_sent_friendly.sum() / sub.n_sent.sum()))
    return rows


prof = pd.DataFrame([r for g in GROUPS for r in profile(g)])
prof.to_csv(RESULTS / "09_top_decile_early_profile.csv", index=False)
log("[a] early profile:\n" + prof.round(3).T.to_string(header=False))

# ---------------- b) early negativity -> being long-lived ----------------
with Step("logit"):
    F = ["downvote_share_recv", "hostile_reply_share_recv", "hostile_reply_share_sent",
         "friendly_reply_share_recv", "friendly_reply_share_sent", "got_any_reply", "log_comments"]
    D = h[F + ["cohort"]].copy()
    for c in F:
        if c != "got_any_reply":
            D[c] = (D[c] - D[c].mean()) / D[c].std()
    rows = []
    for g in ["top10_cohort", "gt2y"]:
        D["y"] = h[g].astype(int)
        # cohorts that cannot reach 2y (entered after 2020-07) are dropped for the fixed threshold
        sub = D if g == "top10_cohort" else D[D.cohort <= 2020]
        m = smf.logit("y ~ " + " + ".join(F) + " + C(cohort)", sub).fit(disp=0)
        ci = np.exp(m.conf_int())
        for c in F:
            rows.append(dict(outcome=g, covariate=c, odds_ratio=np.exp(m.params[c]), lo=ci.loc[c, 0], hi=ci.loc[c, 1], p=m.pvalues[c], n=int(m.nobs)))
    logit = pd.DataFrame(rows)
    logit.to_csv(RESULTS / "09_top_decile_logit.csv", index=False)
    log("[b] odds ratios per SD of being long-lived:\n" + logit.round(3).to_string(index=False))

# ---------------- c) within the group ----------------
rows = []
for g in ["top10_cohort", "top10_all"]:
    sub = h[h[g]]
    for c in ["downvote_share_recv", "hostile_reply_share_recv", "hostile_reply_share_sent",
              "friendly_reply_share_recv", "friendly_reply_share_sent", "log_comments"]:
        rho, p = spearmanr(sub[c], sub.life_years)
        rows.append(dict(group=g, covariate=c, spearman_rho=rho, p=p, n=len(sub)))
within = pd.DataFrame(rows)
within.to_csv(RESULTS / "09_top_decile_within_group.csv", index=False)
log("[c] within long-lived group:\n" + within.round(3).to_string(index=False))

# ---------------- d) whole-life stance by tenure ----------------
with Step("tenure"):
    con.register("grp", h[["uid", "top10_cohort", "gt3y"]])
    BIN = lambda c: (f"CASE WHEN {c} < 365 THEN '1: <1y' WHEN {c} < 2*365 THEN '2: 1-2y' "
                     f"WHEN {c} < 3*365 THEN '3: 2-3y' ELSE '4: 3y+' END")
    parts = []
    for side, who, tenure in [("written", "a", "tenure_a_days"), ("received", "b", "tenure_b_days")]:
        parts.append(con.sql(f"""
          SELECT '{side}' AS side, g.top10_cohort AS long_lived, {BIN('e.' + tenure)} AS tenure, count(*) AS n_replies,
                 avg((vote_true = -1)::INT) FILTER (WHERE vote_true IS NOT NULL) AS p_down_parent,
                 avg((vote_true = 1)::INT) FILTER (WHERE vote_true IS NOT NULL) AS p_up_parent,
                 avg((vote_true IS NOT NULL)::INT) AS p_voted_parent
          FROM '{d}/edges_stance.parquet' e JOIN grp g ON g.uid = e.{who}
          GROUP BY ALL ORDER BY ALL""").df())
    ten = pd.concat(parts)
    ten.to_csv(RESULTS / "09_top_decile_by_tenure.csv", index=False)
    log("[d] stance by tenure:\n" + ten.round(3).to_string(index=False))

# ---------------- Figure ----------------
fig, axes = plt.subplots(1, 3, figsize=(11.5, 3.5))
p = prof[prof.group == "top10_cohort"].set_index("long_lived")
labs = ["Downvote share\nreceived", "Hostile replies\nreceived", "Hostile replies\nwritten"]
cols = ["downvote_share_recv", "hostile_reply_share_recv", "hostile_reply_share_sent"]
x = np.arange(len(cols))
axes[0].bar(x - 0.2, p.loc[True, cols], 0.4, color=OBS, label="Top 10% by lifetime")
axes[0].bar(x + 0.2, p.loc[False, cols], 0.4, color=NULL, label="Rest")
axes[0].set_xticks(x, labs)
axes[0].yaxis.set_major_formatter(PCT)
axes[0].set_title("First 30 days", fontsize=10)
axes[0].legend()
for ax, side, title in [(axes[1], "written", "Replies written: downvoted the parent"), (axes[2], "received", "Replies received: replier downvoted")]:
    for flag, col, lab in [(True, OBS, "Top 10%"), (False, NULL, "Rest")]:
        g = ten[(ten.side == side) & (ten.long_lived == flag)]
        ax.plot(g.tenure, g.p_down_parent, "o-", color=col, label=lab)
    ax.yaxis.set_major_formatter(PCT)
    ax.set_xlabel("Tenure at time of reply")
    ax.set_title(title, fontsize=10)
axes[1].legend()
fig.tight_layout()
fig.savefig(RESULTS / "09_top_decile.png")
log("[figs] wrote 09_top_decile.png")
