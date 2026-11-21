"""Step 4 / H1: do voters who reply to comment c downvote c more than voters who don't reply?

Within-comment design: strata = parent comments that received >= 1 reply edge and have at least one
replier-voter AND one non-replier-voter. Mantel-Haenszel pooled OR (downvote | replied) with
Robins-Breslow-Greenland 95% CI, plus a Poisson bootstrap over comments.
Heterogeneity: same OR by year, by depth of the parent comment, by Topic_1.
"""
import numpy as np
import pandas as pd

from common import DERIVED, RESULTS, Step, connect, log
from plotstyle import NULL, OBS, plt

d = DERIVED.as_posix()
con = connect()


def mh(t: pd.DataFrame):
    """t has a (replied&down), b (replied&up), c (nonreplied&down), d_ (nonreplied&up) per stratum."""
    n = t.a + t.b + t.c + t.d_
    R, S = t.a * t.d_ / n, t.b * t.c / n
    P, Q = (t.a + t.d_) / n, (t.b + t.c) / n
    sR, sS = R.sum(), S.sum()
    or_ = sR / sS
    var = (P * R).sum() / (2 * sR**2) + ((P * S) + (Q * R)).sum() / (2 * sR * sS) + (Q * S).sum() / (2 * sS**2)
    se = np.sqrt(var)
    return or_, np.exp(np.log(or_) - 1.96 * se), np.exp(np.log(or_) + 1.96 * se)


with Step("h1_strata"):
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
      SELECT s.*, year(to_timestamp(c.ts)) AS year, c.depth, coalesce(ar.topic1, 'NA') AS topic1
      FROM strata s JOIN '{d}/comments.parquet' c ON c.comment_id = s.cid
      LEFT JOIN '{d}/articles.parquet' ar ON ar.article_id = c.article_id""").df()
log(f"[h1] informative comments: {len(t):,}; replier votes {int((t.a + t.b).sum()):,}; non-replier votes {int((t.c + t.d_).sum()):,}")

rows = []
or_, lo, hi = mh(t)
p_rep = t.a.sum() / (t.a.sum() + t.b.sum())
p_non = t.c.sum() / (t.c.sum() + t.d_.sum())
rows.append(dict(group="all", level="all", strata=len(t), p_down_repliers=p_rep, p_down_nonrepliers=p_non, or_mh=or_, ci_lo=lo, ci_hi=hi))
log(f"[h1] P(down|replier)={p_rep:.3f} P(down|non-replier)={p_non:.3f} OR_MH={or_:.2f} [{lo:.2f}, {hi:.2f}]")

# Poisson bootstrap over strata (comments)
rng = np.random.default_rng(20261006)
A, B, C, D = (t[k].to_numpy(float) for k in ("a", "b", "c", "d_"))
N = A + B + C + D
boots = []
for _ in range(200):
    w = rng.poisson(1.0, len(t))
    boots.append((w * A * D / N).sum() / (w * B * C / N).sum())
blo, bhi = np.percentile(boots, [2.5, 97.5])
rows[0].update(boot_lo=blo, boot_hi=bhi)
log(f"[h1] bootstrap 95% CI over comments: [{blo:.2f}, {bhi:.2f}]")

t["depth_bin"] = t.depth.clip(upper=5).map(lambda x: f"{x}" if x < 5 else "5+")
top_topics = t.groupby("topic1").size().sort_values(ascending=False).head(12).index
for g in ["year", "depth_bin", "topic1"]:
    for lvl, sub in t.groupby(g):
        if g == "topic1" and lvl not in top_topics:
            continue
        o, l, h = mh(sub)
        rows.append(dict(group=g, level=lvl, strata=len(sub),
                         p_down_repliers=sub.a.sum() / (sub.a.sum() + sub.b.sum()),
                         p_down_nonrepliers=sub.c.sum() / (sub.c.sum() + sub.d_.sum()),
                         or_mh=o, ci_lo=l, ci_hi=h))
res = pd.DataFrame(rows)
res.to_csv(RESULTS / "04_h1_comment_level.csv", index=False)

# Figure: P(downvote) repliers vs non-repliers, by year (paired dots)
yr = res[(res.group == "year") & (res.strata >= 10_000)].sort_values("level")  # drops 2023 (422 late comments)
fig, ax = plt.subplots(figsize=(7, 3.6))
ax.plot(yr.level, yr.p_down_repliers, "o-", color=OBS, label="Voters who replied to the comment")
ax.plot(yr.level, yr.p_down_nonrepliers, "o-", color=NULL, label="Other voters on the same comment")
ax.set_ylim(0, max(0.7, yr.p_down_repliers.max() * 1.1))
ax.yaxis.set_major_formatter(plt.matplotlib.ticker.PercentFormatter(1.0))
ax.set_ylabel("Share of votes that are downvotes")
ax.set_title(f"H1 · Repliers downvote the comment they answer (pooled OR_MH = {or_:.2f})")
ax.legend(loc="lower right")
fig.savefig(RESULTS / "04_h1_by_year.png")
log("[h1] wrote 04_h1_comment_level.csv, 04_h1_by_year.png")
