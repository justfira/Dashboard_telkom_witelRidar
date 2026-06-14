import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from etl.run_etl import run_etl
from utils.db import run_query

sample_path = os.path.join(ROOT, 'scripts', 'sample_upload.csv')
# Create sample CSV with columns matching mapping
csv_content = '''wo / sc id,tanggal,sto,nama teknisi,status,durasi (hari),kendala pt1
WO_TEST_001,2026-06-01,STO001,12345 - Budi,Close,1,Kabel putus
WO_TEST_002,2026-06-02,STO002,67890 - Ani,Open,4,ODP rusak
'''
with open(sample_path, 'w', encoding='utf-8') as f:
    f.write(csv_content)

print('Running ETL for sample_upload.csv...')
res = run_etl(sample_path, filename='sample_upload.csv')
print('ETL result:', res)

# Verify DB counts for inserted sample WO
rows = run_query("SELECT COUNT(*) AS c FROM workorders WHERE wo_id LIKE 'WO_TEST_%'")
print('Inserted sample rows:', rows[0]['c'] if rows else 0)

# Show latest ETL log
logs = run_query("SELECT id, status, total_records, inserted_records, failed_records, error_message, started_at FROM etl_logs ORDER BY started_at DESC LIMIT 5")
for l in logs:
    print(l)
