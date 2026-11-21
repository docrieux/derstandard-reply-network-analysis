"""Step 7: multiverse-lite robustness for H2 (dyad stance) and H4 (early opposition -> exit).

H2 specs: Beta prior (1,2)/(1,1) x thresholds 0.6/0.4 | 0.7/0.3 x min votes 1/5/20 x include/exclude
          A's vote on the specific comment. Outcome: share of negative edges among defined edges, true - null.
H4 specs: churn buffer 3/6/12 months x early window 14/30/60 days x shrinkage pseudo-count 2/10.
          (Plan said "30 days vs first 10 comments"; a window grid was used instead to keep one feature builder.)
          Outcome: adjusted HR (per SD) of downvote share received and hostile replies received.
"""
import itertools

import pandas as pd
from lifelines import CoxPHFitter

from common import DERIVED, RESULTS, T_END, Step, connect, log
from h4 import h4_frame
from plotstyle import ALT, NULL, OBS, plt

d = DERIVED.as_posix()
con = connect()
con.execute(f"CREATE TEMP TABLE es AS SELECT * FROM '{d}/edges_stance.parquet' WHERE b_null IS NOT NULL")

# ---------------- H2 ----------------
rows = []
with Step("multiverse_h2"):
    for (al, be), thr, mn, excl in itertools.product([(1, 2), (1, 1)], [0.6, 0.7], [1, 5, 20], [False, True]):
        def side(pos, neg, vote):
            if excl:
                pos, neg = f"({pos} - coalesce(({vote} = 1)::INT, 0))", f"({neg} - coalesce(({vote} = -1)::INT, 0))"
            e = f"(({pos}) + {al}) / (({pos}) + ({neg}) + {al + be})"
            n = f"(({pos}) + ({neg}))"
            return (f"sum(({n} >= {mn} AND {e} < {1 - thr})::INT)",
                    f"sum(({n} >= {mn} AND ({e} < {1 - thr} OR {e} > {thr}))::INT)")
        tn, td = side("pos_ab", "neg_ab", "vote_true")
        nn, nd = side("pos_anull", "neg_anull", "vote_null")
        r = con.sql(f"SELECT {tn} / {td} AS t, {nn} / {nd} AS n, {td} AS t_def, {nd} AS n_def FROM es").fetchone()
        rows.append(dict(prior=f"({al},{be})", threshold=f"{thr}/{1 - thr:.1f}", min_votes=mn, excl_specific_vote=excl,
                         neg_edge_share_true=r[0], neg_edge_share_null=r[1], diff=r[0] - r[1], n_def_true=r[2], n_def_null=r[3]))
h2 = pd.DataFrame(rows)
h2.to_csv(RESULTS / "07_multiverse_h2.csv", index=False)
log(f"[mv-h2] {len(h2)} specs; diff range [{h2['diff'].min():.3f}, {h2['diff'].max():.3f}]; all > 0: {(h2['diff'] > 0).all()}")

# ---------------- H4 ----------------
rows = []
with Step("multiverse_h4"):
    for buf_m, win, M in itertools.product([3, 6, 12], [14, 30, 60], [2, 10]):
        right_censor = T_END - int(buf_m * 30.44 * 86400)
        h, Z, info = h4_frame(con, window_days=win, right_censor=right_censor, M=M)
        s = CoxPHFitter(penalizer=0.001).fit(Z, "T_years", "E", strata=["cohort"]).summary
        for cov in ["downvote_share_recv", "hostile_reply_share_recv", "hostile_reply_share_sent"]:
            rows.append(dict(buffer_months=buf_m, window_days=win, shrink_M=M, covariate=cov, n=info["n_landmark"],
                             hr=s.loc[cov, "exp(coef)"], lo=s.loc[cov, "exp(coef) lower 95%"], hi=s.loc[cov, "exp(coef) upper 95%"]))
h4 = pd.DataFrame(rows)
h4.to_csv(RESULTS / "07_multiverse_h4.csv", index=False)
for cov, g in h4.groupby("covariate"):
    log(f"[mv-h4] {cov}: HR range [{g.hr.min():.3f}, {g.hr.max():.3f}]; CI excludes 1 in {(g.lo > 1).sum()}/{len(g)} specs")

# ---------------- Specification-curve figure ----------------
fig, axes = plt.subplots(1, 2, figsize=(11, 3.6))
s2 = h2.sort_values("diff").reset_index(drop=True)
axes[0].scatter(s2.index, s2["diff"], color=OBS, s=22, zorder=3)
axes[0].axhline(0, color=NULL, lw=1)
axes[0].set_xlabel(f"Specification (sorted; {len(s2)} total)")
axes[0].set_ylabel("Negative-edge share: replied-to − null")
axes[0].yaxis.set_major_formatter(plt.matplotlib.ticker.PercentFormatter(1.0))
axes[0].set_title("H2 across specifications")
for cov, col, lab in [("downvote_share_recv", OBS, "Downvote share received"),
                      ("hostile_reply_share_recv", ALT, "Hostile replies received")]:
    g = h4[h4.covariate == cov].sort_values("hr").reset_index(drop=True)
    axes[1].errorbar(g.index, g.hr, yerr=[g.hr - g.lo, g.hi - g.hr], fmt="o", ms=4, color=col, label=lab, capsize=0)
axes[1].axhline(1, color=NULL, lw=1)
axes[1].set_xlabel("Specification (sorted; 18 per covariate)")
axes[1].set_ylabel("Hazard ratio of leaving (per SD)")
axes[1].set_title("H4 across specifications")
axes[1].legend()
fig.tight_layout()
fig.savefig(RESULTS / "07_multiverse.png")
log("[figs] wrote 07_multiverse.png")
