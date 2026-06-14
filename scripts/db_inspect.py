import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
from utils.db import run_query

for t in ["failed_jobs"]:
    try:
        rows = run_query(f"SHOW CREATE TABLE {t}")
        print(f"SHOW CREATE TABLE {t}:")
        print(rows)
    except Exception as e:
        print(f"{t}: ERROR: {e}")
