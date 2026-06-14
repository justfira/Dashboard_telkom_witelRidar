import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from utils.db import run_query

print('ETL logs for data_bi.xlsx (latest 10):')
logs = run_query("SELECT id, status, total_records, inserted_records, skipped_records, failed_records, source_file, started_at, finished_at, error_message FROM etl_logs WHERE source_file LIKE '%data_bi%' ORDER BY started_at DESC LIMIT 10")
for row in logs:
    print(row)

print('\nWorkorder source_file counts:')
counts = run_query("SELECT source_file, COUNT(*) AS c FROM workorders GROUP BY source_file ORDER BY c DESC")
for row in counts[:20]:
    print(row)

print('\nWorkorders with same wo_id and multiple track_id (sample):')
rows = run_query("SELECT wo_id, COUNT(DISTINCT track_id) AS track_count FROM workorders WHERE wo_id IS NOT NULL AND wo_id != '' GROUP BY wo_id HAVING track_count > 1 ORDER BY track_count DESC LIMIT 20")
for row in rows:
    print(row)

print('\nWorkorders distribution by track_id blankness for source data_bi.xlsx:')
print(run_query("SELECT SUM(CASE WHEN track_id IS NULL OR track_id = '' THEN 1 ELSE 0 END) AS blank_track, SUM(CASE WHEN track_id IS NOT NULL AND track_id != '' THEN 1 ELSE 0 END) AS has_track, COUNT(*) AS total FROM workorders WHERE source_file LIKE '%data_bi%'")[0])
