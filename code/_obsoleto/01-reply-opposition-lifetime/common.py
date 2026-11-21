"""Shared paths and helpers for the DerStandard reply/stance/lifetime analysis."""
import time
from pathlib import Path

import duckdb

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]  # tfg/
RAW = ROOT / "data" / "derstandard"
DERIVED = RAW / "derived"
# Docs and outputs live in the vault, in the folder named like this experiment
RESULTS = ROOT / "notes" / "experiments" / HERE.name / "results"
LOG = RESULTS / "run.log"

DERIVED.mkdir(parents=True, exist_ok=True)
RESULTS.mkdir(parents=True, exist_ok=True)

# Dataset window and censoring rules (see notes/experiments/01-reply-opposition-lifetime/PLAN.md)
T_START = 1356998400  # 2013-01-01 UTC
T_END = 1672531200  # 2023-01-01 UTC
RIGHT_CENSOR = 1656633600  # 2022-07-01: last activity after this = still active
LEFT_CENSOR = 1372636800  # 2013-07-01: first activity before this = maybe older


def hexid(col):
    """SQL expression turning a 16-hex anonymized id into UBIGINT (NULL stays NULL)."""
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
