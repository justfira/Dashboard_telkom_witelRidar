import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path: sys.path.insert(0, ROOT)

import pandas as pd
from etl.run_etl import run_etl
from utils.db import run_query

sample_path = os.path.join(ROOT, 'scripts', 'duplicate_test.csv')
rows = [
    {'wo / sc id': 'WO1001 / SC2001', 'tanggal': '2026-06-01', 'sto': 'STO1', 'nama teknisi': '123 - Tono', 'status': 'Closed', 'durasi (hari)': 1, 'track id': 'T001'},
    {'wo / sc id': 'WO1001 / SC2001', 'tanggal': '2026-06-01', 'sto': 'STO1', 'nama teknisi': '123 - Tono', 'status': 'Closed', 'durasi (hari)': 1, 'track id': 'T001'},
    {'wo / sc id': 'WO1001 / SC2002', 'tanggal': '2026-06-02', 'sto': 'STO1', 'nama teknisi': '123 - Tono', 'status': 'Open', 'durasi (hari)': 2, 'track id': 'T002'},
    {'wo / sc id': 'WO1002 / SC2003', 'tanggal': '2026-06-03', 'sto': 'STO2', 'nama teknisi': '456 - Budi', 'status': 'Closed', 'durasi (hari)': 3, 'track id': 'T003'},
]
df = pd.DataFrame(rows)
df.to_csv(sample_path, index=False)
print('Running ETL on duplicate test sample...')
res = run_etl(sample_path, filename='duplicate_test.csv')
print(res)
print('Workorders inserted count (wo_id WO1001, WO1002):', run_query("SELECT wo_id, track_id, COUNT(*) AS c FROM workorders WHERE wo_id IN ('WO1001','WO1002') GROUP BY wo_id, track_id"))
