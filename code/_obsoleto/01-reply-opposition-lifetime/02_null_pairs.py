"""Step 2: co-present null target for every reply edge.

For reply A->B posted at position k (by time) among the eligible comments of its article, the null
target is the author of a uniformly random earlier eligible comment (positions 1..k-1) whose author
is not A. Same article, same moment, same exposure; only "who was chosen" is randomised.
Up to 5 deterministic hash draws per reply; replies with no valid draw get no null (logged).
"""
from common import DERIVED, Step, connect, log

d = DERIVED.as_posix()
con = connect()
SEED = 20261006
DRAWS = 5

with Step("null_edges"):
    con.execute(f"""
    CREATE TEMP TABLE pos AS
      SELECT comment_id, author_id, article_id,
             row_number() OVER (PARTITION BY article_id ORDER BY ts, comment_id) AS k
      FROM '{d}/comments.parquet'
      WHERE author_id IS NOT NULL
        AND comment_id NOT IN (SELECT comment_id FROM '{d}/inconsistent.parquet');
    CREATE TEMP TABLE e AS
      SELECT r.comment_id, r.a, r.b, r.article_id, p.k
      FROM '{d}/reply_edges.parquet' r JOIN pos p USING (comment_id);
    CREATE TEMP TABLE cand AS
      SELECT e.comment_id, e.a, e.b, e.article_id, draw,
             1 + floor((hash(e.comment_id, {SEED} + draw) / 18446744073709551616.0) * (e.k - 1))::BIGINT AS k_null
      FROM e, range({DRAWS}) t(draw)
      WHERE e.k > 1;
    COPY (
      SELECT c.comment_id, c.a, c.b AS b_true, p.author_id AS b_null, p.comment_id AS null_comment_id, c.draw
      FROM cand c JOIN pos p ON p.article_id = c.article_id AND p.k = c.k_null
      WHERE p.author_id <> c.a
      QUALIFY row_number() OVER (PARTITION BY c.comment_id ORDER BY c.draw) = 1
    ) TO '{d}/null_edges.parquet' (FORMAT parquet, COMPRESSION zstd)
    """)

log("[check] null_edges: " + str(con.sql(f"""
  SELECT (SELECT count(*) FROM '{d}/reply_edges.parquet') AS replies,
         count(*) AS with_null,
         count(*) FILTER (WHERE b_null = b_true) AS null_equals_true_target,
         count(*) FILTER (WHERE b_null = a) AS null_is_self,
         avg(draw) AS mean_draw
  FROM '{d}/null_edges.parquet'""").df().to_dict('records')[0]))
log("[check] null comment earlier & same article: " + str(con.sql(f"""
  SELECT count(*) AS n, count(*) FILTER (WHERE cn.ts > cr.ts) AS null_after_reply,
         count(*) FILTER (WHERE cn.article_id <> cr.article_id) AS diff_article
  FROM '{d}/null_edges.parquet' n
  JOIN '{d}/comments.parquet' cr ON cr.comment_id = n.comment_id
  JOIN '{d}/comments.parquet' cn ON cn.comment_id = n.null_comment_id""").fetchall()))
