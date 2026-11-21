"""Check: are there self-votes (voter == author of the voted comment)?

Run from tfg/code:  uv run python dataset-checks/check_self_votes.py
Rerun 2026-11-21: same result (0 self-votes in both tables, 54,044,269 voted comments).

Both tables have: comment_id, voter_id, author_id, sign (+1 upvote / -1 downvote), year, month.
- votes:       all votes after typing (voter_id and author_id may be NULL = deleted user).
- votes_clean: one vote per (comment, voter), deleted voters dropped (see 00_to_parquet.py).
A self-vote is voter_id = author_id. If either side is NULL the comparison is NULL (not true),
so those rows are not counted.
"""
import duckdb
from pathlib import Path

# Paths (scripts moved here from code/_obsoleto/01-reply-opposition-lifetime/ on 2026-11-21)
ROOT = Path(__file__).resolve().parents[2]  # tfg/
RAW = ROOT / "data" / "derstandard"
DERIVED = RAW / "derived"

con = duckdb.connect()
con.execute("SET memory_limit='22GB'")
d = DERIVED.as_posix()
votes = f"'{d}/votes/*/*.parquet'"
votes_clean = f"'{d}/votes_clean/*/*.parquet'"


def show(title, sql):
    print(f"\n--- {title}")
    print(con.sql(sql).df().to_string(index=False))  # .show() breaks on the Windows console


# Sanity check (expected: votes_clean = 383,858,436 rows, see data-treatment.md)
show("rows", f"SELECT (SELECT count(*) FROM {votes}) AS votes, (SELECT count(*) FROM {votes_clean}) AS votes_clean")

# My prediction (before running): ...
# No self votes or all self votes

tables = {"votes": votes, "votes_clean": votes_clean}

# 1. Self-votes: count and share of all votes, in each table.
# FILTER applies the condition to one aggregate only, so the denominator count(*) stays unfiltered.
for name, t in tables.items():
    show(
        f"1. self-votes in {name}",
        f"""SELECT count(*) AS total_votes,
                   count(*) FILTER (WHERE voter_id = author_id) AS self_votes,
                   100.0 * count(*) FILTER (WHERE voter_id = author_id) / count(*) AS self_pct
            FROM {t}""",
    )

# 2. By sign: GROUP BY sign gives one row per value of sign (check for values other than +1/-1).
for name, t in tables.items():
    show(
        f"2. self-votes by sign in {name}",
        f"""SELECT sign,
                   count(*) AS votes,
                   count(*) FILTER (WHERE voter_id = author_id) AS self_votes,
                   100.0 * count(*) FILTER (WHERE voter_id = author_id) / count(*) AS self_pct_of_sign
            FROM {t}
            GROUP BY sign
            ORDER BY sign""",
    )

# 3. In how many distinct comments do self-votes appear?
show(
    "3. comments with a self-vote (votes_clean)",
    f"""SELECT count(DISTINCT comment_id) AS comments_voted,
               count(DISTINCT comment_id) FILTER (WHERE voter_id = author_id) AS comments_with_self_vote
        FROM {votes_clean}""",
)
