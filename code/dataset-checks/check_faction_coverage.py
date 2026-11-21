"""Check: in how many reply edges are both users labelled in FAULTANA?

Run from tfg/code:  uv run python dataset-checks/check_faction_coverage.py

Population of the question "who replies to whom across factions": the clean reply edges
A (replier) -> B (author of the parent comment) in which both A and B have a faction label.

Inputs (made by code/dataset-prep/):
- reply_edges.parquet: one row per clean reply (44,350,672 expected, see 01_reply_funnel.csv).
- factions.parquet: one row per labelled user (14,817 expected), from summary_files/faction_users.tsv.

Output: counts and shares of reply edges by labelling status (both / only A / only B / neither),
and how many labelled users appear as A and as B. It does NOT look at which faction each user is in.

Result (2026-11-21): factions 14,817 unique users, 0 NULL; 44,350,672 edges, 0 NULL ids, 0 self-replies.
both labelled 11,302,013 (25.48%); only A 11,263,454 (25.40%); only B 10,476,843 (23.62%);
neither 11,308,362 (25.50%). Labelled users seen as replier 14,647 and as parent author 14,606 (of 14,817).
"""
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[2]  # tfg/
DERIVED = ROOT / "data" / "derstandard" / "derived"

con = duckdb.connect()
con.execute("SET memory_limit='22GB'")
d = DERIVED.as_posix()
edges = f"'{d}/reply_edges.parquet'"
fac = f"'{d}/factions.parquet'"


def show(title, sql):
    print(f"\n--- {title}")
    print(con.sql(sql).df().to_string(index=False))  # .show() breaks on the Windows console


# Sanity checks on the inputs.
show("factions: rows, distinct users, NULL ids (expected 14,817 / 14,817 / 0)",
     f"SELECT count(*) AS n, count(DISTINCT user_id) AS users, count(*) FILTER (WHERE user_id IS NULL) AS null_ids FROM {fac}")
show("reply edges: rows, NULL ids, self-replies (expected 44,350,672 / 0 / 0)",
     f"SELECT count(*) AS n, count(*) FILTER (WHERE a IS NULL OR b IS NULL) AS null_ids, count(*) FILTER (WHERE a = b) AS self FROM {edges}")

# Label status of each edge. LEFT JOIN keeps every edge; factions has one row per user, so no duplication.
status = f"""
  SELECT (fa.user_id IS NOT NULL) AS a_lab, (fb.user_id IS NOT NULL) AS b_lab
  FROM {edges} e
  LEFT JOIN {fac} fa ON e.a = fa.user_id
  LEFT JOIN {fac} fb ON e.b = fb.user_id"""

show("reply edges by labelling status",
     f"""SELECT CASE WHEN a_lab AND b_lab THEN 'both'
                     WHEN a_lab THEN 'only A (replier)'
                     WHEN b_lab THEN 'only B (parent author)'
                     ELSE 'neither' END AS status,
                count(*) AS edges,
                round(100.0 * count(*) / sum(count(*)) OVER (), 2) AS pct
         FROM ({status}) GROUP BY 1 ORDER BY 1""")

show("labelled users that appear in the reply edges",
     f"""SELECT (SELECT count(DISTINCT a) FROM {edges} SEMI JOIN {fac} f ON a = f.user_id) AS as_replier,
                (SELECT count(DISTINCT b) FROM {edges} SEMI JOIN {fac} f ON b = f.user_id) AS as_parent_author,
                (SELECT count(*) FROM {fac}) AS labelled_total""")
