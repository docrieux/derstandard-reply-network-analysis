"""Step 5 / H2 + H3 + reply-back + faction projection.

H2: is A's overall vote stance toward the user they reply to (B) more negative than toward a co-present
    null target (random earlier commenter in the same article)? Paired per reply edge.
    Variants: "all" = every A->B vote; "excl" = minus A's vote on the specific comment (parent / null comment).
    Bootstrap: Poisson weights clustered by replier A.
H3: cross-faction share of replies (FAULTANA factions) vs null and vs random mixing by faction size.
    Then the same with projected factions for (almost) all users.
Reply-back: P(B replies to A's reply) by A's stance toward B.
"""
import numpy as np
import pandas as pd

from common import DERIVED, RESULTS, Step, connect, log
from plotstyle import NULL, OBS, plt

d = DERIVED.as_posix()
con = connect()
rng = np.random.default_rng(20261006)
ALPHA, BETA = 1, 2  # FAULTANA prior (slightly favours negative)


def stance_cols(pos, neg, tag):
    """SQL for per-edge stance indicators from pos/neg counts."""
    e = f"(({pos}) + {ALPHA}) / (({pos}) + ({neg}) + {ALPHA + BETA})"
    v = f"({e}) * (1 - {e}) / (({pos}) + ({neg}) + {ALPHA + BETA} + 1)"
    return f"""
      ({pos}) + ({neg}) AS tot_{tag}, ({neg}) AS neg_{tag},
      (({pos}) + ({neg}) > 0)::INT AS any_{tag},
      CASE WHEN ({pos}) + ({neg}) > 0 THEN {e} END AS ep_{tag},
      (({pos}) + ({neg}) >= 5 AND {e} < 0.4)::INT AS negedge5_{tag},
      (({pos}) + ({neg}) >= 5 AND ({e} < 0.4 OR {e} > 0.6))::INT AS defedge5_{tag},
      ({e} < 0.4 AND {v} < 1e-4)::INT AS negedgeF_{tag},
      (({e} < 0.4 OR {e} > 0.6) AND {v} < 1e-4)::INT AS defedgeF_{tag}"""


with Step("h2_edge_metrics"):
    excl_t = "(vote_true = 1)::INT", "(vote_true = -1)::INT"
    excl_n = "(vote_null = 1)::INT", "(vote_null = -1)::INT"
    con.execute(f"""
    CREATE TEMP TABLE m AS SELECT a, year, depth,
      {stance_cols('pos_ab', 'neg_ab', 'true_all')},
      {stance_cols('pos_anull', 'neg_anull', 'null_all')},
      {stance_cols(f'pos_ab - coalesce({excl_t[0]},0)', f'neg_ab - coalesce({excl_t[1]},0)', 'true_excl')},
      {stance_cols(f'pos_anull - coalesce({excl_n[0]},0)', f'neg_anull - coalesce({excl_n[1]},0)', 'null_excl')}
    FROM '{d}/edges_stance.parquet' WHERE b_null IS NOT NULL
    """)

METRICS = ["tot", "neg", "any", "negedge5", "defedge5", "negedgeF", "defedgeF"]
rows = []
for variant in ["all", "excl"]:
    cols = []
    for side in ["true", "null"]:
        for k in METRICS:
            cols.append(f"sum({k}_{side}_{variant}) AS {k}_{side}")
        cols.append(f"sum(coalesce(ep_{side}_{variant}, 0)) AS ep_{side}")
    per_a = con.sql(f"SELECT a, count(*) AS n, {', '.join(cols)} FROM m GROUP BY a").df()

    def summarise(w):
        s = lambda c: (w * per_a[c].to_numpy(float)).sum()
        out = {}
        for side in ["true", "null"]:
            out[f"p_any_{side}"] = s(f"any_{side}") / s("n")
            out[f"neg_share_{side}"] = s(f"neg_{side}") / s(f"tot_{side}")
            out[f"mean_Ep_{side}"] = s(f"ep_{side}") / s(f"any_{side}")
            out[f"p_negedge5_{side}"] = s(f"negedge5_{side}") / s(f"defedge5_{side}")
            out[f"p_negedgeF_{side}"] = s(f"negedgeF_{side}") / s(f"defedgeF_{side}")
            out[f"n_defedgeF_{side}"] = s(f"defedgeF_{side}")
        return out

    point = summarise(np.ones(len(per_a)))
    boots = pd.DataFrame([summarise(rng.poisson(1.0, len(per_a))) for _ in range(200)])
    for k in ["p_any", "neg_share", "mean_Ep", "p_negedge5", "p_negedgeF"]:
        diff = boots[f"{k}_true"] - boots[f"{k}_null"]
        rows.append(dict(variant=variant, metric=k, true=point[f"{k}_true"], null=point[f"{k}_null"],
                         diff=point[f"{k}_true"] - point[f"{k}_null"],
                         diff_lo=diff.quantile(0.025), diff_hi=diff.quantile(0.975),
                         n_edges=int(per_a.n.sum()), n_repliers=len(per_a)))
    log(f"[h2:{variant}] " + ", ".join(f"{k}={point[f'{k}_true']:.3f} vs {point[f'{k}_null']:.3f}"
                                      for k in ["p_any", "neg_share", "mean_Ep", "p_negedge5", "p_negedgeF"])
        + f" | FAULTANA-defined edges true={point['n_defedgeF_true']:.0f} null={point['n_defedgeF_null']:.0f}")
h2 = pd.DataFrame(rows)
h2.to_csv(RESULTS / "05_h2_dyad.csv", index=False)

# H2 by depth (escalation) and year, "excl" variant, pooled negative share
by = con.sql("""
  SELECT 'depth' AS grp, least(depth, 6)::VARCHAR AS level, count(*) AS n,
         sum(neg_true_excl) / sum(tot_true_excl) AS neg_share_true, sum(neg_null_excl) / sum(tot_null_excl) AS neg_share_null
  FROM m GROUP BY 2
  UNION ALL
  SELECT 'year', year::VARCHAR, count(*),
         sum(neg_true_excl) / sum(tot_true_excl), sum(neg_null_excl) / sum(tot_null_excl)
  FROM m GROUP BY 2 ORDER BY 1, 2""").df()
by.to_csv(RESULTS / "05_h2_by_depth_year.csv", index=False)

# ---------------- H3: factions ----------------
with Step("h3_factions"):
    f = con.sql(f"""
      WITH e AS (SELECT a, b, b_null FROM '{d}/edges_stance.parquet' WHERE b_null IS NOT NULL),
           F AS (SELECT * FROM '{d}/factions.parquet')
      SELECT 'true' AS side, fa.faction AS fa, fb.faction AS fb, count(*) AS n
        FROM e JOIN F fa ON fa.user_id = e.a JOIN F fb ON fb.user_id = e.b GROUP BY ALL
      UNION ALL
      SELECT 'null', fa.faction, fb.faction, count(*)
        FROM e JOIN F fa ON fa.user_id = e.a JOIN F fb ON fb.user_id = e.b_null GROUP BY ALL""").df()
    sizes = con.sql(f"SELECT faction, count(*) n FROM '{d}/factions.parquet' GROUP BY 1").df().set_index("faction").n
    p1 = sizes[1] / sizes.sum()
    h3 = []
    for side, g in f.groupby("side"):
        cross = g[g.fa != g.fb].n.sum() / g.n.sum()
        h3.append(dict(side=side, n_edges=int(g.n.sum()), cross_share=cross,
                       cross_from_F1=g[(g.fa == 1) & (g.fb == 2)].n.sum() / g[g.fa == 1].n.sum(),
                       cross_from_F2=g[(g.fa == 2) & (g.fb == 1)].n.sum() / g[g.fa == 2].n.sum()))
    h3.append(dict(side="random_mixing_by_size", cross_share=2 * p1 * (1 - p1), cross_from_F1=1 - p1, cross_from_F2=p1))
    h3 = pd.DataFrame(h3)
    h3.to_csv(RESULTS / "05_h3_factions.csv", index=False)
    log("[h3] " + h3.to_string(index=False).replace("\n", " | "))

    # Stance by faction relation: P(A downvoted parent) and dyad neg share, same vs cross faction
    sf = con.sql(f"""
      SELECT (fa.faction <> fb.faction) AS cross_faction, count(*) AS n,
             avg((vote_true = -1)::INT) FILTER (WHERE vote_true IS NOT NULL) AS p_down_parent,
             sum(neg_ab) / nullif(sum(pos_ab + neg_ab), 0) AS dyad_neg_share
      FROM '{d}/edges_stance.parquet' e
      JOIN '{d}/factions.parquet' fa ON fa.user_id = e.a JOIN '{d}/factions.parquet' fb ON fb.user_id = e.b
      GROUP BY 1 ORDER BY 1""").df()
    sf.to_csv(RESULTS / "05_h3_stance_by_faction_relation.csv", index=False)
    log("[h3] stance by faction relation: " + sf.to_string(index=False).replace("\n", " | "))

# ---------------- Faction projection to all users ----------------
with Step("faction_projection"):
    # score = Beta-mean approval of F1 authors - Beta-mean approval of F2 authors (votes cast by u)
    con.execute(f"""
    CREATE TEMP TABLE proj AS
      WITH agg AS (
        SELECT v.voter_id AS user_id, f.faction,
               count(*) FILTER (WHERE sign = 1) AS pos, count(*) FILTER (WHERE sign = -1) AS neg
        FROM '{d}/votes_clean/*/*.parquet' v JOIN '{d}/factions.parquet' f ON f.user_id = v.author_id
        WHERE v.voter_id <> v.author_id
        GROUP BY ALL)
      SELECT user_id,
             coalesce(max(pos) FILTER (WHERE faction = 1), 0) AS pos1, coalesce(max(neg) FILTER (WHERE faction = 1), 0) AS neg1,
             coalesce(max(pos) FILTER (WHERE faction = 2), 0) AS pos2, coalesce(max(neg) FILTER (WHERE faction = 2), 0) AS neg2
      FROM agg GROUP BY 1;
    CREATE TEMP TABLE proj2 AS
      SELECT *, (pos1 + 1.0) / (pos1 + neg1 + 2) - (pos2 + 1.0) / (pos2 + neg2 + 2) AS score,
             pos1 + neg1 + pos2 + neg2 AS n_votes
      FROM proj;
    """)
    val = con.sql(f"""SELECT p.score, p.n_votes, f.faction FROM proj2 p JOIN '{d}/factions.parquet' f USING (user_id)""").df()
    from scipy.stats import mannwhitneyu
    y = (val.faction == 1).astype(int)
    auc = mannwhitneyu(val.score[y == 1], val.score[y == 0]).statistic / (y.sum() * (1 - y).sum())
    acc = ((val.score > 0).astype(int) == y).mean()
    log(f"[proj] in-sample validation on {len(val):,} labelled users: AUC={auc:.3f}, accuracy(score>0)={acc:.3f}")
    # confident projection: >= 20 votes to faction members and |score| >= 0.2
    con.execute(f"""
    COPY (
      SELECT p.user_id, p.score, p.n_votes,
             coalesce(f.faction, CASE WHEN n_votes >= 20 AND score >= 0.2 THEN 1
                                      WHEN n_votes >= 20 AND score <= -0.2 THEN 2 END) AS faction_proj,
             f.faction IS NOT NULL AS labelled
      FROM proj2 p LEFT JOIN '{d}/factions.parquet' f USING (user_id)
    ) TO '{d}/factions_projected.parquet' (FORMAT parquet)""")
    cov = con.sql(f"SELECT faction_proj, labelled, count(*) FROM '{d}/factions_projected.parquet' GROUP BY ALL ORDER BY ALL").fetchall()
    log(f"[proj] coverage (faction_proj, labelled, n): {cov}")
    pd.DataFrame([dict(auc=auc, accuracy=acc, n_labelled=len(val))]).to_csv(RESULTS / "05_projection_validation.csv", index=False)

    fp = con.sql(f"""
      WITH e AS (SELECT a, b, b_null FROM '{d}/edges_stance.parquet' WHERE b_null IS NOT NULL),
           F AS (SELECT user_id, faction_proj AS faction FROM '{d}/factions_projected.parquet' WHERE faction_proj IS NOT NULL)
      SELECT 'true' AS side, avg((fa.faction <> fb.faction)::INT) AS cross_share, count(*) AS n
        FROM e JOIN F fa ON fa.user_id = e.a JOIN F fb ON fb.user_id = e.b
      UNION ALL
      SELECT 'null', avg((fa.faction <> fb.faction)::INT), count(*)
        FROM e JOIN F fa ON fa.user_id = e.a JOIN F fb ON fb.user_id = e.b_null""").df()
    fp.to_csv(RESULTS / "05_h3_projected_factions.csv", index=False)
    log("[h3-proj] " + fp.to_string(index=False).replace("\n", " | "))

# ---------------- Reply-back ----------------
with Step("reply_back"):
    rb = con.sql(f"""
      WITH back AS (SELECT DISTINCT parent_id AS cid, a AS replier FROM '{d}/reply_edges.parquet')
      SELECT CASE vote_true WHEN -1 THEN 'A downvoted parent' WHEN 1 THEN 'A upvoted parent' ELSE 'A did not vote' END AS a_vote,
             count(*) AS n, avg((bk.cid IS NOT NULL)::INT) AS p_b_replies_back
      FROM '{d}/edges_stance.parquet' e
      LEFT JOIN back bk ON bk.cid = e.comment_id AND bk.replier = e.b
      GROUP BY 1 ORDER BY 1""").df()
    rb.to_csv(RESULTS / "05_reply_back.csv", index=False)
    log("[reply-back] " + rb.to_string(index=False).replace("\n", " | "))

# ---------------- Figures ----------------
fig, axes = plt.subplots(1, 3, figsize=(11, 3.4))
ex = h2[h2.variant == "excl"].set_index("metric")
labels = {"neg_share": "Downvote share of\nA's votes to target", "p_negedge5": "Negative edges among\ndefined dyads (≥5 votes)"}
for ax, k in zip(axes[:2], labels):
    vals = [ex.loc[k, "true"], ex.loc[k, "null"]]
    bars = ax.bar(["Replied-to user", "Co-present null"], vals, color=[OBS, NULL], width=0.55)
    ax.bar_label(bars, labels=[f"{v:.1%}" for v in vals], color="#0b0b0b", padding=2)
    ax.set_title(labels[k], fontsize=10)
    ax.yaxis.set_major_formatter(plt.matplotlib.ticker.PercentFormatter(1.0))
    ax.set_ylim(0, max(vals) * 1.25)
dep = by[by.grp == "depth"].copy()
dep["level"] = dep.level.replace({"6": "6+"})
axes[2].plot(dep.level, dep.neg_share_true, "o-", color=OBS, label="Replied-to user")
axes[2].plot(dep.level, dep.neg_share_null, "o-", color=NULL, label="Co-present null")
axes[2].set_xlabel("Depth of the reply in the thread")
axes[2].yaxis.set_major_formatter(plt.matplotlib.ticker.PercentFormatter(1.0))
axes[2].set_title("Downvote share by thread depth", fontsize=10)
axes[2].legend()
fig.suptitle("H2 · Users reply to people they vote against (votes on the replied comment excluded)", x=0.01, ha="left", fontweight="bold")
fig.tight_layout()
fig.savefig(RESULTS / "05_h2_dyad.png")
log("[figs] wrote 05_h2_dyad.png")
