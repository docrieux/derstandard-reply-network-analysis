"""Shared paths and helpers for the dataset preparation scripts.

Taken from code/_obsoleto/01-reply-opposition-lifetime/common.py on 2026-11-21, keeping only what
00_to_parquet.py and 01_reply_edges.py use. Outputs of a new run go to notes/dataset/prep-results/;
the outputs of the 2026-10-06 run stay in notes/experiments/01-reply-opposition-lifetime/results/.
"""
import time
from pathlib import Path

import duckdb

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]  # tfg/
RAW = ROOT / "data" / "derstandard"
DERIVED = RAW / "derived"
RESULTS = ROOT / "notes" / "dataset" / "prep-results"
LOG = RESULTS / "run.log"

DERIVED.mkdir(parents=True, exist_ok=True)
RESULTS.mkdir(parents=True, exist_ok=True)


def hexid(col):
    """SQL expression turning a 16-hex anonymized id into UBIGINT (NULL stays NULL).
    Lossless: every id in the raw files is 16 lowercase hex characters (checked 2026-11-21)."""
    return f"('0x' || {col})::UBIGINT"


def connect():
    con = duckdb.connect()
    con.execute(f"SET temp_directory='{(DERIVED / 'duckdb_tmp').as_posix()}'")
    con.execute("SET memory_limit='22GB'")
    con.execute("SET enable_progress_bar=false")
    return con


def log(msg):
    line = f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}"
    print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


class Step:
    """Context manager that logs the start, end and duration of a pipeline step."""

    def __init__(self, name):
        self.name = name

    def __enter__(self):
        self.t0 = time.time()
        log(f"[{self.name}] start")
        return self

    def __exit__(self, *exc):
        log(f"[{self.name}] {'FAILED' if exc[0] else 'done'} in {time.time() - self.t0:.1f}s")
