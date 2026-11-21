"""Step 3: vote-based stance for every reply edge and its null counterpart.

dyads.parquet: directed vote totals voter->author (pos, neg) over the whole dataset, restricted to pairs
  that appear (in either direction) as a real or null reply edge.
edges_stance.parquet: one row per reply edge with
  - vote_true / vote_null: A's vote (+1/-1/NULL) on the parent comment / on the null comment   (H1-style)
  - pos/neg A->B_true, A->B_null, and reverse B_true->A, B_null->A                               (H2)
"""
from common import DERIVED, Step, connect, log

d = DERIVED.as_posix()
con = connect()
V = f"'{d}/votes_clean/*/*.parquet'"

with Step("dyads"):
    con.execute(f"""
    CREATE TEMP TABLE pairs AS
      SELECT DISTINCT u, v FROM (
        SELECT a AS u, b_true AS v FROM '{d}/null_edges.parquet'
        UNION ALL SELECT a, b_null FROM '{d}/null_edges.parquet'
        UNION ALL SELECT b_true, a FROM '{d}/null_edges.parquet'
        UNION ALL SELECT b_null, a FROM '{d}/null_edges.parquet'
        UNION ALL SELECT a, b FROM '{d}/reply_edges.parquet'
        UNION ALL SELECT b, a FROM '{d}/reply_edges.parquet');
    """)
    log(f"[dyads] distinct directed pairs: {con.sql('SELECT count(*) FROM pairs').fetchone()[0]:,}")
    con.execute(f"""
    COPY (
      SELECT x.voter_id AS u, x.author_id AS v,
             count(*) FILTER (WHERE sign = 1) AS pos, count(*) FILTER (WHERE sign = -1) AS neg
      FROM {V} x SEMI JOIN pairs p ON x.voter_id = p.u AND x.author_id = p.v
      GROUP BY ALL
    ) TO '{d}/dyads.parquet' (FORMAT parquet, COMPRESSION zstd)
    """)

with Step("edges_stance"):
    con.execute(f"""
    CREATE TEMP TABLE dy AS SELECT * FROM '{d}/dyads.parquet';
    CREATE TEMP TABLE vt AS
      SELECT x.comment_id, x.voter_id, x.sign FROM {V} x
      SEMI JOIN (SELECT parent_id AS cid, a FROM '{d}/reply_edges.parquet'
                 UNION ALL SELECT null_comment_id, a FROM '{d}/null_edges.parquet') q
        ON x.comment_id = q.cid AND x.voter_id = q.a;
    COPY (
      SELECT r.comment_id, r.a, r.b, r.parent_id, r.root_id, r.article_id, r.ts, r.year, r.depth,
             r.tenure_a_days, r.tenure_b_days,
             n.b_null, n.null_comment_id,
             v1.sign AS vote_true, v2.sign AS vote_null,
             coalesce(d1.pos, 0) AS pos_ab, coalesce(d1.neg, 0) AS neg_ab,
             coalesce(d2.pos, 0) AS pos_ba, coalesce(d2.neg, 0) AS neg_ba,
             coalesce(d3.pos, 0) AS pos_anull, coalesce(d3.neg, 0) AS neg_anull,
             coalesce(d4.pos, 0) AS pos_nulla, coalesce(d4.neg, 0) AS neg_nulla
      FROM '{d}/reply_edges.parquet' r
      LEFT JOIN '{d}/null_edges.parquet' n USING (comment_id)
      LEFT JOIN vt v1 ON v1.comment_id = r.parent_id AND v1.voter_id = r.a
      LEFT JOIN vt v2 ON v2.comment_id = n.null_comment_id AND v2.voter_id = r.a
      LEFT JOIN dy d1 ON d1.u = r.a AND d1.v = r.b
      LEFT JOIN dy d2 ON d2.u = r.b AND d2.v = r.a
      LEFT JOIN dy d3 ON d3.u = r.a AND d3.v = n.b_null
      LEFT JOIN dy d4 ON d4.u = n.b_null AND d4.v = r.a
    ) TO '{d}/edges_stance.parquet' (FORMAT parquet, COMPRESSION zstd)
    """)

log("[check] edges_stance: " + str(con.sql(f"""
  SELECT count(*) AS n,
         avg((vote_true IS NOT NULL)::INT) AS p_voted_parent, avg((vote_null IS NOT NULL)::INT) AS p_voted_null,
         avg((vote_true = -1)::INT) FILTER (WHERE vote_true IS NOT NULL) AS p_down_parent,
         avg((vote_null = -1)::INT) FILTER (WHERE vote_null IS NOT NULL) AS p_down_null,
         avg((pos_ab + neg_ab > 0)::INT) AS p_any_ab, avg((pos_anull + neg_anull > 0)::INT) AS p_any_anull
  FROM '{d}/edges_stance.parquet'""").df().to_dict('records')[0]))
