"""Step 1: reply edges A (replier) -> B (author of the parent comment).

Moved from code/_obsoleto/01-reply-opposition-lifetime/ on 2026-11-21. Run from tfg/code:
  uv run python dataset-prep/01_reply_edges.py

Exclusions (logged): child or parent flagged in inconsistent_comment_metadata, parent missing
from the dataset, NULL (deleted) author on either side, self-replies.
"""
from prep_common import DERIVED, RESULTS, Step, connect, log

d = DERIVED.as_posix()
con = connect()

with Step("reply_edges"):
    con.execute(f"""
    CREATE TEMP TABLE bad AS SELECT comment_id FROM '{d}/inconsistent.parquet';
    CREATE TEMP TABLE c AS SELECT * FROM '{d}/comments.parquet';
    CREATE TEMP TABLE raw AS
      SELECT r.comment_id, r.author_id AS a, p.author_id AS b, r.parent_id, r.root_id,
             r.article_id, r.ts, r.depth, p.ts AS parent_ts,
             p.comment_id IS NULL AS parent_missing,
             (r.comment_id IN (SELECT comment_id FROM bad) OR r.parent_id IN (SELECT comment_id FROM bad)) AS inconsistent
      FROM c r LEFT JOIN c p ON r.parent_id = p.comment_id
      WHERE r.is_reply;
    """)
    funnel = con.sql("""
      SELECT count(*) AS replies,
             count(*) FILTER (WHERE inconsistent) AS inconsistent,
             count(*) FILTER (WHERE NOT inconsistent AND parent_missing) AS parent_missing,
             count(*) FILTER (WHERE NOT inconsistent AND NOT parent_missing AND (a IS NULL OR b IS NULL)) AS deleted_author,
             count(*) FILTER (WHERE NOT inconsistent AND NOT parent_missing AND a = b) AS self_reply
      FROM raw""").df()
    log(f"[funnel] {funnel.to_dict('records')[0]}")
    funnel.to_csv(RESULTS / "01_reply_funnel.csv", index=False)

    # tenure = time since the user's first observed activity (comment or vote)
    con.execute(f"""
    CREATE TEMP TABLE first_seen AS
      SELECT user_id, least(coalesce(first_comment, first_vote), coalesce(first_vote, first_comment)) AS first_ts
      FROM '{d}/users.parquet';
    COPY (
      SELECT e.*, (e.ts - fa.first_ts) / 86400.0 AS tenure_a_days, (e.ts - fb.first_ts) / 86400.0 AS tenure_b_days,
             year(to_timestamp(e.ts)) AS year
      FROM (SELECT * EXCLUDE (parent_missing, inconsistent) FROM raw
            WHERE NOT inconsistent AND NOT parent_missing AND a IS NOT NULL AND b IS NOT NULL AND a <> b) e
      LEFT JOIN first_seen fa ON e.a = fa.user_id
      LEFT JOIN first_seen fb ON e.b = fb.user_id
    ) TO '{d}/reply_edges.parquet' (FORMAT parquet, COMPRESSION zstd)
    """)

log("[check] reply_edges: " + str(con.sql(f"""
  SELECT count(*) AS n, count(DISTINCT a) AS repliers, count(DISTINCT b) AS targets,
         count(*) FILTER (WHERE parent_ts > ts) AS parent_after_reply,
         count(*) FILTER (WHERE tenure_a_days IS NULL OR tenure_b_days IS NULL) AS no_tenure,
         min(year), max(year)
  FROM '{d}/reply_edges.parquet'""").df().to_dict('records')[0]))
