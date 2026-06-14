from utils.db import run_query

r = run_query("""
    SELECT nik_teknisi,
           TRIM(SUBSTRING_INDEX(nik_teknisi, ' - ', -1)) AS nama_parsed,
           mitra, korlap, komandan_team,
           COUNT(*) AS total_wo,
           SUM(is_sla_tercapai) AS sla_ok,
           ROUND(SUM(is_sla_tercapai)*100.0/COUNT(*),2) AS pct_sla,
           ROUND(AVG(durasi_hari),2) AS avg_durasi,
           SUM(is_workfail) AS work_fail
    FROM workorders
    WHERE nik_teknisi IS NOT NULL AND nik_teknisi != ''
    GROUP BY nik_teknisi, mitra, korlap, komandan_team
    ORDER BY total_wo DESC
    LIMIT 5
""")
for row in r:
    print(row)
