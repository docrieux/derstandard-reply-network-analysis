"""Step 0: convert raw TSVs to typed Parquet (hex ids -> UBIGINT, NA -> NULL).

Moved from code/_obsoleto/01-reply-opposition-lifetime/ on 2026-11-21. Run from tfg/code:
  uv run python dataset-prep/00_to_parquet.py

Each output is skipped if it already exists; delete it to rebuild.
"""
from prep_common import DERIVED, RAW, Step, connect, hexid, log

con = connect()
csv = "delim='\t', header=true, nullstr='NA', all_varchar=true"
src = lambda pattern: f"read_csv('{(RAW / pattern).as_posix()}', {csv}, filename=true)"
out = lambda name: (DERIVED / name).as_posix()

JOBS = {
    # 259,521 comment rows appear twice with identical content -> DISTINCT
    "comments.parquet": f"""
      SELECT DISTINCT {hexid('Comment_Id')} AS comment_id,
             {hexid('Author_Id')} AS author_id,
             Is_Reply::BOOLEAN AS is_reply,
             {hexid('Parent_Id')} AS parent_id,
             Thread_Level::INTEGER AS depth,
             {hexid('Origin_Parent_Id')} AS root_id,
             Timestamp::BIGINT AS ts,
             Article_Id::BIGINT AS article_id,
             Votes_Pos::INTEGER AS votes_pos,
             Votes_Neg::INTEGER AS votes_neg
      FROM {src('comments_files/*.tsv')}
      ORDER BY article_id, ts""",
    # month/year taken from file name votes_file_MM_YY.tsv (votes carry no timestamp)
    "votes": f"""
      SELECT {hexid('Comment_Id')} AS comment_id,
             {hexid('Voter_Id')} AS voter_id,
             {hexid('Author_Id')} AS author_id,
             (Pos::TINYINT - Neg::TINYINT) AS sign,
             2000 + regexp_extract(filename, 'votes_file_(\\d\\d)_(\\d\\d)', 2)::INTEGER AS year,
             regexp_extract(filename, 'votes_file_(\\d\\d)_(\\d\\d)', 1)::INTEGER AS month
      FROM {src('votes_files/*.tsv')}""",
    # One vote per (comment, voter): drop deleted voters (NULL id), collapse exact duplicates,
    # and drop pairs recorded with both signs (safety net: 0 such pairs once NULL voters are excluded).
    "votes_clean": f"""
      SELECT comment_id, voter_id, any_value(author_id) AS author_id, min(sign) AS sign,
             min(year) AS year, min(month) AS month
      FROM '{out('votes')}/*/*.parquet'
      WHERE voter_id IS NOT NULL
      GROUP BY comment_id, voter_id
      HAVING count(DISTINCT sign) = 1""",
    "users.parquet": f"""
      SELECT {hexid('User_Id')} AS user_id, N_comments::INTEGER AS n_comments,
             NULLIF(First_Comment::BIGINT, 0) AS first_comment, NULLIF(Last_Comment::BIGINT, 0) AS last_comment,
             R_pos::BIGINT AS r_pos, R_neg::BIGINT AS r_neg, G_pos::BIGINT AS g_pos, G_neg::BIGINT AS g_neg,
             NULLIF(First_vote::BIGINT, 0) AS first_vote, NULLIF(Last_vote::BIGINT, 0) AS last_vote
      FROM {src('users_files/users_file')}""",
    "articles.parquet": f"""
      SELECT Article_Id::BIGINT AS article_id, Topic_1 AS topic1, Topic_2 AS topic2, Topic_3 AS topic3,
             Timestamp::BIGINT AS ts
      FROM {src('articles_files/*.tsv')}""",
    "factions.parquet": f"""
      SELECT {hexid('userid')} AS user_id, membership::INTEGER AS faction
      FROM {src('summary_files/faction_users.tsv')}""",
    "inconsistent.parquet": f"""
      SELECT {hexid('Comment_Id')} AS comment_id, Inconsistency_type AS kind
      FROM {src('summary_files/inconsistent_comment_metadata.tsv')}""",
}

for name, query in JOBS.items():
    if (DERIVED / name).exists():
        log(f"[{name}] exists, skipping")
        continue
    opts = "FORMAT parquet, COMPRESSION zstd"
    if not name.endswith(".parquet"):
        opts += ", PARTITION_BY (year)"
    with Step(name):
        con.execute(f"COPY ({query}) TO '{out(name)}' ({opts})")

d = DERIVED.as_posix()
for name, q in {
    "comments": f"SELECT count(*), count(DISTINCT comment_id), count(*) FILTER (WHERE is_reply), count(*) FILTER (WHERE author_id IS NULL) FROM '{d}/comments.parquet'",
    "votes": f"SELECT count(*), count(*) FILTER (WHERE sign = 1), count(*) FILTER (WHERE sign = -1), count(*) FILTER (WHERE sign = 0) FROM '{d}/votes/*/*.parquet'",
    "votes_raw_null_voter": f"SELECT count(*) FROM '{d}/votes/*/*.parquet' WHERE voter_id IS NULL",
    "votes_clean": f"SELECT count(*), count(*) FILTER (WHERE sign = 1), count(*) FILTER (WHERE sign = -1), count(author_id) FROM '{d}/votes_clean/*/*.parquet'",
    "users": f"SELECT count(*), count(first_comment), count(first_vote) FROM '{d}/users.parquet'",
    "articles": f"SELECT count(*) FROM '{d}/articles.parquet'",
    "factions": f"SELECT faction, count(*) FROM '{d}/factions.parquet' GROUP BY 1 ORDER BY 1",
    "inconsistent": f"SELECT kind, count(*) FROM '{d}/inconsistent.parquet' GROUP BY 1",
}.items():
    log(f"[check] {name}: {con.sql(q).fetchall()}")
