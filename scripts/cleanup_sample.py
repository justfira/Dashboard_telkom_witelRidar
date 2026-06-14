import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from utils.db import run_query, get_cached_engine
from sqlalchemy import text

# Temukan etl_log untuk sample_upload.csv
logs = run_query("SELECT id FROM etl_logs WHERE source_file = 'sample_upload.csv' ORDER BY started_at DESC LIMIT 1")
log_id = logs[0]['id'] if logs else None

engine = get_cached_engine()
with engine.connect() as conn:
    if log_id:
        print('Found log_id =', log_id)
        # Hapus fact_kendalateknis, fact_workorder, dim_infrastruktur yang berhubungan
        try:
            conn.execute(text("DELETE FROM fact_kendalateknis WHERE etl_log_id = :id"), {'id': log_id})
            conn.execute(text("DELETE FROM fact_workorder WHERE etl_log_id = :id"), {'id': log_id})
            conn.execute(text("DELETE FROM dim_infrastruktur WHERE etl_log_id = :id"), {'id': log_id})
            conn.execute(text("DELETE FROM etl_logs WHERE id = :id"), {'id': log_id})
            conn.commit()
            print('Deleted fact and etl_logs related to sample')
        except Exception as e:
            print('Error deleting fact/etl_logs:', e)
    else:
        print('No etl_log found for sample_upload.csv')

    # Hapus workorders dengan wo_id sample
    try:
        res = conn.execute(text("DELETE FROM workorders WHERE wo_id LIKE 'WO_TEST_%'"))
        conn.commit()
        print('Deleted sample workorders')
    except Exception as e:
        print('Error deleting sample workorders:', e)

# Hapus file sample CSV jika ada
sample_path = os.path.join(ROOT, 'scripts', 'sample_upload.csv')
if os.path.exists(sample_path):
    try:
        os.remove(sample_path)
        print('Removed sample_upload.csv')
    except Exception as e:
        print('Error removing sample file:', e)
else:
    print('No sample file to remove')
