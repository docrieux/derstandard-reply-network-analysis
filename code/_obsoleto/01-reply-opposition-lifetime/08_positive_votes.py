"""Step 8: positive-vote mirror of H1, H2, H3-stance and H4 (meeting 2026-10-19: "results should also cover positive votes").

Same levels, same data and same specifications as the negative-vote analysis (04, 05, 06, 07):
H1  comment level: P(upvote | replier) vs other voters on the same comment, Mantel-Haenszel OR.
    (For one 2x2 table per comment, OR_up = 1 / OR_down exactly; reported for readability.)
H2  dyad level: positive-edge share (E[p] > 0.6) and upvote share, replied-to user vs co-present null,
    plus the 24-specification multiverse.
H3  stance by faction relation: P(A upvoted parent) same vs cross faction.
H4  early-life exposure to positive replies/votes and exit hazard (landmark Cox).
"""
import itertools

import numpy as np
import pandas as pd
from lifelines import CoxPHFitter

from common import DERIVED, RESULTS, Step, connect, log
from h4 import h4_frame
from plotstyle import ALT, NULL, OBS, plt

d = DERIVED.as_posix()
con = connect()
rng = np.random.default_rng(20261019)
ALPHA, BETA = 1, 2
PCT = plt.matplotlib.ticker.PercentFormatter(1.0)

# ---------------- H1 mirror ----------------
def mh(t: pd.DataFrame):
    """Mantel-Haenszel OR with Robins-Breslow-Greenland CI (same as 04_h1_comment_level.py)."""
    n = t.a + t.b + t.c + t.d_
    R, S = t.a * t.d_ / n, t.b * t.c / n
    P, Q = (t.a + t.d_) / n, (t.b + t.c) / n
    sR, sS = R.sum(), S.sum()
    or_ = sR / sS
    var = (P * R).sum() / (2 * sR**2) + ((P * S) + (Q * R)).sum() / (2 * sR * sS) + (Q * S).sum() / (2 * sS**2)
    se = np.sqrt(var)
    return or_, np.exp(np.log(or_) - 1.96 * se), np.exp(np.log(or_) + 1.96 * se)


with Step("h1_pos"):
    con.execute(f"""
    CREATE TEMP TABLE repl AS SELECT DISTINCT parent_id AS cid, a FROM '{d}/reply_edges.parquet';
    CREATE TEMP TABLE strata AS
      SELECT v.comment_id AS cid,
             count(*) FILTER (WHERE r.a IS NOT NULL AND v.sign = -1) AS a,
             count(*) FILTER (WHERE r.a IS NOT NULL AND v.sign = 1) AS b,
             count(*) FILTER (WHERE r.a IS NULL AND v.sign = -1) AS c,
             count(*) FILTER (WHERE r.a IS NULL AND v.sign = 1) AS d_
      FROM '{d}/votes_clean/*/*.parquet' v
      SEMI JOIN (SELECT DISTINCT cid FROM repl) p ON v.comment_id = p.cid
      LEFT JOIN repl r ON r.cid = v.comment_id AND r.a = v.voter_id
      GROUP BY 1
      HAVING (a + b) > 0 AND (c + d_) > 0;
    """)
    t = con.sql(f"""
      SELECT s.*, year(to_timestamp(c.ts)) AS year, c.depth
      FROM strata s JOIN '{d}/comments.parquet' c ON c.comment_id = s.cid""").df()
    # Swap the roles of up and down: "a" = replied & UP, "b" = replied & DOWN, etc.
    t = t.rename(columns={"a": "b", "b": "a", "c": "d_", "d_": "c"})
    t["depth_bin"] = t.depth.clip(upper=5).map(lambda x: f"{x}" if x < 5 else "5+")
    rows = []
    for g, sub_all in [("all", [("all", t)]), ("year", list(t.groupby("year"))), ("depth_bin", list(t.groupby("depth_bin")))]:
        for lvl, sub in sub_all:
            o, lo, hi = mh(sub)
            rows.append(dict(group=g, level=lvl, strata=len(sub),
                             p_up_repliers=sub.a.sum() / (sub.a.sum() + sub.b.sum()),
                             p_up_nonrepliers=sub.c.sum() / (sub.c.sum() + sub.d_.sum()),
                             or_up_mh=o, ci_lo=lo, ci_hi=hi))
    h1 = pd.DataFrame(rows)
    h1.to_csv(RESULTS / "08_h1_positive.csv", index=False)
    r0 = h1.iloc[0]
    log(f"[h1+] P(up|replier)={r0.p_up_repliers:.3f} P(up|non-replier)={r0.p_up_nonrepliers:.3f} "
        f"OR_up={r0.or_up_mh:.2f} [{r0.ci_lo:.2f}, {r0.ci_hi:.2f}] over {int(r0.strata):,} comments")

# ---------------- H2 mirror ----------------
def stance_cols(pos, neg, tag):
    e = f"(({pos}) + {ALPHA}) / (({pos}) + ({neg}) + {ALPHA + BETA})"
    v = f"({e}) * (1 - {e}) / (({pos}) + ({neg}) + {ALPHA + BETA} + 1)"
    return f"""
      ({pos}) + ({neg}) AS tot_{tag}, ({pos}) AS pos_{tag},
      (({pos}) + ({neg}) > 0)::INT AS any_{tag},
      CASE WHEN ({pos}) + ({neg}) > 0 THEN {e} END AS ep_{tag},
      (({pos}) + ({neg}) >= 5 AND {e} > 0.6)::INT AS posedge5_{tag},
      (({pos}) + ({neg}) >= 5 AND ({e} < 0.4 OR {e} > 0.6))::INT AS defedge5_{tag},
      ({e} > 0.6 AND {v} < 1e-4)::INT AS posedgeF_{tag},
      (({e} < 0.4 OR {e} > 0.6) AND {v} < 1e-4)::INT AS defedgeF_{tag}"""


with Step("h2_pos"):
    ex_t = "(vote_true = 1)::INT", "(vote_true = -1)::INT"
    ex_n = "(vote_null = 1)::INT", "(vote_null = -1)::INT"
    con.execute(f"""
    CREATE TEMP TABLE m AS SELECT a, year, depth,
      {stance_cols(f'pos_ab - coalesce({ex_t[0]},0)', f'neg_ab - coalesce({ex_t[1]},0)', 'true_excl')},
      {stance_cols(f'pos_anull - coalesce({ex_n[0]},0)', f'neg_anull - coalesce({ex_n[1]},0)', 'null_excl')}
    FROM '{d}/edges_stance.parquet' WHERE b_null IS NOT NULL
    """)
    METRICS = ["tot", "pos", "any", "posedge5", "defedge5", "posedgeF", "defedgeF"]
    cols = []
    for side in ["true", "null"]:
        for k in METRICS:
            cols.append(f"sum({k}_{side}_excl) AS {k}_{side}")
        cols.append(f"sum(coalesce(ep_{side}_excl, 0)) AS ep_{side}")
    per_a = con.sql(f"SELECT a, count(*) AS n, {', '.join(cols)} FROM m GROUP BY a").df()

    def summarise(w):
        s = lambda c: (w * per_a[c].to_numpy(float)).sum()
        out = {}
        for side in ["true", "null"]:
            out[f"pos_share_{side}"] = s(f"pos_{side}") / s(f"tot_{side}")
            out[f"mean_Ep_{side}"] = s(f"ep_{side}") / s(f"any_{side}")
            out[f"p_posedge5_{side}"] = s(f"posedge5_{side}") / s(f"defedge5_{side}")
            out[f"p_posedgeF_{side}"] = s(f"posedgeF_{side}") / s(f"defedgeF_{side}")
        return out

    point = summarise(np.ones(len(per_a)))
    boots = pd.DataFrame([summarise(rng.poisson(1.0, len(per_a))) for _ in range(200)])
    rows = []
    for k in ["pos_share", "mean_Ep", "p_posedge5", "p_posedgeF"]:
        diff = boots[f"{k}_true"] - boots[f"{k}_null"]
        rows.append(dict(variant="excl", metric=k, true=point[f"{k}_true"], null=point[f"{k}_null"],
                         diff=point[f"{k}_true"] - point[f"{k}_null"], diff_lo=diff.quantile(0.025), diff_hi=diff.quantile(0.975),
                         n_repliers=len(per_a)))
    h2 = pd.DataFrame(rows)
    h2.to_csv(RESULTS / "08_h2_positive.csv", index=False)
    log("[h2+] " + h2.round(4).to_string(index=False).replace("\n", " | "))

    by = con.sql("""
      SELECT 'depth' AS grp, least(depth, 6)::VARCHAR AS level, count(*) AS n,
             sum(pos_true_excl) / sum(tot_true_excl) AS pos_share_true, sum(pos_null_excl) / sum(tot_null_excl) AS pos_share_null
      FROM m GROUP BY 2
      UNION ALL
      SELECT 'year', year::VARCHAR, count(*), sum(pos_true_excl) / sum(tot_true_excl), sum(pos_null_excl) / sum(tot_null_excl)
      FROM m GROUP BY 2 ORDER BY 1, 2""").df()
    by.to_csv(RESULTS / "08_h2_positive_by_depth_year.csv", index=False)

# ---- multiverse for H2+ ----
with Step("multiverse_h2_pos"):
    con.execute(f"CREATE TEMP TABLE es AS SELECT * FROM '{d}/edges_stance.parquet' WHERE b_null IS NOT NULL")
    rows = []
    for (al, be), thr, mn, excl in itertools.product([(1, 2), (1, 1)], [0.6, 0.7], [1, 5, 20], [False, True]):
        def side(pos, neg, vote):
            if excl:
                pos, neg = f"({pos} - coalesce(({vote} = 1)::INT, 0))", f"({neg} - coalesce(({vote} = -1)::INT, 0))"
            e = f"(({pos}) + {al}) / (({pos}) + ({neg}) + {al + be})"
            n = f"(({pos}) + ({neg}))"
            return (f"sum(({n} >= {mn} AND {e} > {thr})::INT)",
                    f"sum(({n} >= {mn} AND ({e} < {1 - thr} OR {e} > {thr}))::INT)")
        tn, td = side("pos_ab", "neg_ab", "vote_true")
        nn, nd = side("pos_anull", "neg_anull", "vote_null")
        r = con.sql(f"SELECT {tn} / {td} AS t, {nn} / {nd} AS n, {td} AS t_def, {nd} AS n_def FROM es").fetchone()
        rows.append(dict(prior=f"({al},{be})", threshold=f"{thr}/{1 - thr:.1f}", min_votes=mn, excl_specific_vote=excl,
                         pos_edge_share_true=r[0], pos_edge_share_null=r[1], diff=r[0] - r[1], n_def_true=r[2], n_def_null=r[3]))
    mv = pd.DataFrame(rows)
    mv.to_csv(RESULTS / "08_multiverse_h2_positive.csv", index=False)
    log(f"[mv-h2+] {len(mv)} specs; diff range [{mv['diff'].min():.3f}, {mv['diff'].max():.3f}]; all < 0: {(mv['diff'] < 0).all()}; all > 0: {(mv['diff'] > 0).all()}")

# ---------------- H3 stance by faction relation (positive) ----------------
with Step("h3_pos"):
    sf = con.sql(f"""
      SELECT (fa.faction <> fb.faction) AS cross_faction, count(*) AS n,
             avg((vote_true = 1)::INT) FILTER (WHERE vote_true IS NOT NULL) AS p_up_parent,
             sum(pos_ab) / nullif(sum(pos_ab + neg_ab), 0) AS dyad_pos_share
      FROM '{d}/edges_stance.parquet' e
      JOIN '{d}/factions.parquet' fa ON fa.user_id = e.a JOIN '{d}/factions.parquet' fb ON fb.user_id = e.b
      GROUP BY 1 ORDER BY 1""").df()
    sf.to_csv(RESULTS / "08_h3_positive_by_faction_relation.csv", index=False)
    log("[h3+] " + sf.round(4).to_string(index=False).replace("\n", " | "))

# ---------------- H4 mirror ----------------
with Step("h4_pos"):
    h, Z, info = h4_frame(con, window_days=30)
    h = h.loc[Z.index]
    Xpos = ["upvote_share_recv", "friendly_reply_share_recv", "friendly_reply_share_sent", "got_any_reply", "log_comments"]
    Xjoint = ["downvote_share_recv", "hostile_reply_share_recv", "hostile_reply_share_sent",
              "friendly_reply_share_recv", "friendly_reply_share_sent", "got_any_reply", "log_comments"]
    Zp = h[Xpos + ["T_years", "E", "cohort"]].copy()
    Zj = h[Xjoint + ["T_years", "E", "cohort"]].copy()
    for frame, xs in [(Zp, Xpos), (Zj, Xjoint)]:
        for c in xs:
            if c != "got_any_reply":
                frame[c] = (frame[c] - frame[c].mean()) / frame[c].std()
    out = []
    for name, frame in [("positive_only", Zp), ("joint_pos_and_neg", Zj)]:
        s = CoxPHFitter(penalizer=0.001).fit(frame, "T_years", "E", strata=["cohort"]).summary
        s = s[["exp(coef)", "exp(coef) lower 95%", "exp(coef) upper 95%", "p"]].assign(model=name)
        out.append(s)
        log(f"[h4+:{name}] n={len(frame):,}\n" + s.drop(columns="model").round(4).to_string())
    pd.concat(out).to_csv(RESULTS / "08_h4_positive_cox.csv")

# ---------------- Figure ----------------
fig, axes = plt.subplots(1, 3, figsize=(11, 3.4))
yr = h1[(h1.group == "year") & (h1.strata >= 10_000)].sort_values("level")
axes[0].plot(yr.level, yr.p_up_repliers, "o-", color=OBS, label="Repliers")
axes[0].plot(yr.level, yr.p_up_nonrepliers, "o-", color=NULL, label="Other voters")
axes[0].yaxis.set_major_formatter(PCT)
axes[0].set_title(f"H1 · Upvote share (OR_up = {r0.or_up_mh:.2f})", fontsize=10)
axes[0].legend()
ex = h2.set_index("metric")
vals = [ex.loc["pos_share", "true"], ex.loc["pos_share", "null"]]
bars = axes[1].bar(["Replied-to user", "Co-present null"], vals, color=[OBS, NULL], width=0.55)
axes[1].bar_label(bars, labels=[f"{v:.1%}" for v in vals], padding=2)
axes[1].yaxis.set_major_formatter(PCT)
axes[1].set_ylim(0, 1)
axes[1].set_title("H2 · Upvote share of A's votes to target", fontsize=10)
g = h4_pos = pd.concat(out)
g = g[g.model == "positive_only"].loc[Xpos[:3]]
yy = np.arange(len(g))[::-1]
axes[2].errorbar(g["exp(coef)"], yy, xerr=[g["exp(coef)"] - g["exp(coef) lower 95%"], g["exp(coef) upper 95%"] - g["exp(coef)"]],
                 fmt="o", color=OBS, capsize=0)
axes[2].axvline(1, color=NULL, lw=1)
axes[2].set_yticks(yy, ["Upvote share received", "Friendly replies received", "Friendly replies written"])
axes[2].set_xlabel("HR of leaving (per SD)")
axes[2].set_title("H4 · Early positive exposure", fontsize=10)
axes[2].grid(axis="y", visible=False)
fig.tight_layout()
fig.savefig(RESULTS / "08_positive_votes.png")
log("[figs] wrote 08_positive_votes.png")
