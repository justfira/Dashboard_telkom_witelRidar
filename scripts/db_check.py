import sys
import os

# Ensure project root is on sys.path so `utils` package imports correctly
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from utils.db import run_query

tables = ["failed_jobs", "obs", "jobs_batches", "workorders", "etl_logs"]

for t in tables:
    try:
        rows = run_query(f"SELECT COUNT(*) AS c FROM {t}")
        c = rows[0]["c"] if rows else 0
        print(f"{t}: {c}")
    except Exception as e:
        print(f"{t}: ERROR: {e}")
