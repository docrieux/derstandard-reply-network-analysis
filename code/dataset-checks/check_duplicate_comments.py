"""Check: are the duplicated comments in the raw TSVs identical in all columns?

Run from tfg/code:  uv run python dataset-checks/check_duplicate_comments.py [--buckets N]

(a) = number of distinct Comment_Id     (b) = number of distinct full rows (the 10 Codebook columns).
(b) >= (a) always. If (a) = (b), every Comment_Id has a single version of its row, so the
duplicates are identical and DISTINCT in 00_to_parquet.py loses no information.
Result (2026-10-16): (a) = (b) = 75,385,329, out of 75,644,850 raw rows (259,521 duplicates).
Rerun (2026-11-21): same result. (b) was computed with --buckets 16 because the machine had 3 GB of RAM.
--buckets N splits (b) by hash(Comment_Id) % N and adds the parts. It is exact: rows with the same
Comment_Id always fall in the same bucket, so no duplicate is split across buckets.
"""
import sys

import duckdb
from pathlib import Path

# Paths (scripts moved here from code/_obsoleto/01-reply-opposition-lifetime/ on 2026-11-21)
ROOT = Path(__file__).resolve().parents[2]  # tfg/
RAW = ROOT / "data" / "derstandard"
DERIVED = RAW / "derived"

con = duckdb.connect()
con.execute("SET memory_limit='22GB'")


def show(title, sql):
    print(f"\n--- {title}")
    print(con.sql(sql).df().to_string(index=False))  # .show() breaks on the Windows console


# 'NA' becomes NULL, as in 00_to_parquet.py. DISTINCT treats NULLs as equal.
raw = (
    f"read_csv('{(RAW / 'comments_files/*.tsv').as_posix()}', "
    "delim='\\t', header=true, nullstr='NA', all_varchar=true)"
)

show("raw rows (expected 75,644,850)", f"SELECT count(*) AS n FROM {raw}")
show("(a) distinct Comment_Id", f"SELECT count(DISTINCT comment_id) AS n FROM {raw}")
if "--buckets" in sys.argv:
    k = int(sys.argv[sys.argv.index("--buckets") + 1])
    parts = [con.sql(f"SELECT count(*) FROM (SELECT DISTINCT * FROM {raw} WHERE hash(Comment_Id) % {k} = {b})").fetchone()[0]
             for b in range(k)]
    print(f"\n--- (b) distinct full rows ({k} buckets)\n{sum(parts)}")
else:
    show("(b) distinct full rows", f"SELECT count(*) AS n FROM (SELECT DISTINCT * FROM {raw})")
