import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from utils.db import run_query

print('Total records:', run_query('SELECT COUNT(*) AS c FROM workorders')[0]['c'])
print('Distinct wo_id:', run_query('SELECT COUNT(DISTINCT wo_id) AS c FROM workorders')[0]['c'])
print('Distinct sc_id:', run_query('SELECT COUNT(DISTINCT sc_id) AS c FROM workorders')[0]['c'])
print('Distinct track_id:', run_query('SELECT COUNT(DISTINCT track_id) AS c FROM workorders')[0]['c'])
print('Top 20 wo_id counts:')
for row in run_query('SELECT wo_id, COUNT(*) AS c FROM workorders GROUP BY wo_id ORDER BY c DESC LIMIT 20'):
    print(row)
print('Top 20 distinct wo_id sample:')
for row in run_query('SELECT wo_id FROM workorders WHERE wo_id IS NOT NULL AND wo_id != "" GROUP BY wo_id ORDER BY wo_id LIMIT 20'):
    print(row)
