import pandas as pd
from utils.db import run_query


# ── KPI Utama ──────────────────────────────────────────────────────────────────

def get_kpi_summary(filters: dict = None) -> dict:
    where, params = _build_where(filters)
    rows = run_query(f"""
        SELECT
            COUNT(*)                                        AS total_wo,
            SUM(CASE WHEN LOWER(status_wo) IN ('close','closed','selesai','ps') THEN 1 ELSE 0 END) AS wo_selesai,
            SUM(is_sla_tercapai)                            AS sla_tercapai,
            SUM(is_workfail)                                AS work_fail,
            ROUND(AVG(durasi_hari), 2)                      AS avg_durasi,
            SUM(is_unsc)                                    AS unsc,
            COUNT(DISTINCT nama_teknisi)                    AS jumlah_teknisi,
            COUNT(DISTINCT sto)                             AS jumlah_sto
        FROM workorders
        {where}
    """, params)
    return rows[0] if rows else {}


def get_kpi_monthly_comparison(filters: dict = None) -> list:
    where, params = _build_where(filters)
    return run_query(f"""
        SELECT tahun, bulan, nama_bulan,
               COUNT(*) AS total_wo,
               SUM(is_sla_tercapai) AS sla_ok,
               SUM(is_workfail) AS work_fail,
               ROUND(AVG(durasi_hari),2) AS avg_durasi
        FROM workorders
        {where}
        GROUP BY tahun, bulan, nama_bulan
        ORDER BY tahun, bulan
    """, params)


# ── Trend WO ──────────────────────────────────────────────────────────────────

def get_trend_monthly(filters: dict = None) -> list:
    where, params = _build_where(filters)
    return run_query(f"""
        SELECT tahun, bulan, nama_bulan,
               COUNT(*) AS total_wo,
               SUM(is_sla_tercapai) AS sla_ok,
               SUM(is_workfail) AS work_fail
        FROM workorders
        {where}
        GROUP BY tahun, bulan, nama_bulan
        ORDER BY tahun, bulan
    """, params)


def get_trend_weekly(filters: dict = None) -> list:
    where, params = _build_where(filters)
    return run_query(f"""
        SELECT
            tahun,
            WEEK(tanggal, 1) AS minggu,
            MIN(tanggal) AS tanggal_awal,
            COUNT(*) AS total_wo,
            SUM(is_sla_tercapai) AS sla_ok
        FROM workorders
        {where}
        GROUP BY tahun, WEEK(tanggal, 1)
        ORDER BY tahun, minggu
    """, params)


# ── SLA ───────────────────────────────────────────────────────────────────────

def get_sla_summary(filters: dict = None) -> list:
    where, params = _build_where(filters)
    return run_query(f"""
        SELECT
            SUM(is_sla_tercapai) AS sla_ok,
            COUNT(*) - SUM(is_sla_tercapai) AS sla_not_ok,
            COUNT(*) AS total,
            ROUND(SUM(is_sla_tercapai) * 100.0 / COUNT(*), 2) AS pct_sla
        FROM workorders
        {where}
    """, params)


def get_sla_per_sto(filters: dict = None) -> list:
    where, params = _build_where(filters)
    return run_query(f"""
        SELECT sto,
               COUNT(*) AS total_wo,
               SUM(is_sla_tercapai) AS sla_ok,
               ROUND(SUM(is_sla_tercapai) * 100.0 / COUNT(*), 2) AS pct_sla
        FROM workorders
        {where}
        GROUP BY sto
        ORDER BY pct_sla DESC
        LIMIT 30
    """, params)


# ── STO ───────────────────────────────────────────────────────────────────────

def get_wo_per_sto(filters: dict = None) -> list:
    where, params = _build_where(filters)
    return run_query(f"""
        SELECT sto,
               COUNT(*) AS total_wo,
               SUM(is_sla_tercapai) AS sla_ok,
               SUM(is_workfail) AS work_fail,
               ROUND(AVG(durasi_hari), 2) AS avg_durasi,
               ROUND(SUM(is_sla_tercapai) * 100.0 / COUNT(*), 2) AS pct_sla
        FROM workorders
        {where}
        GROUP BY sto
        ORDER BY total_wo DESC
        LIMIT 30
    """, params)


# ── Teknisi ───────────────────────────────────────────────────────────────────

def get_teknisi_performance(filters: dict = None) -> list:
    where, params = _build_where(filters)
    return run_query(f"""
        SELECT nama_teknisi,
               COUNT(*) AS total_wo,
               SUM(is_sla_tercapai) AS sla_ok,
               ROUND(SUM(is_sla_tercapai) * 100.0 / COUNT(*), 2) AS pct_sla,
               ROUND(AVG(durasi_hari), 2) AS avg_durasi,
               SUM(is_workfail) AS work_fail,
               mitra
        FROM workorders
        WHERE nama_teknisi IS NOT NULL AND nama_teknisi != ''
        {(' AND ' + where[7:]) if where else ''}
        GROUP BY nama_teknisi, mitra
        ORDER BY total_wo DESC
        LIMIT 30
    """, params)


# ── Kendala ───────────────────────────────────────────────────────────────────

def get_kendala_top(filters: dict = None, top_n: int = 10) -> list:
    where, params = _build_where(filters)
    return run_query(f"""
        SELECT kendala_pt1,
               COUNT(*) AS jumlah
        FROM workorders
        WHERE kendala_pt1 IS NOT NULL AND kendala_pt1 != ''
        {(' AND ' + where[7:]) if where else ''}
        GROUP BY kendala_pt1
        ORDER BY jumlah DESC
        LIMIT {top_n}
    """, params)


def get_kendala_kategori(filters: dict = None) -> list:
    where, params = _build_where(filters)
    return run_query(f"""
        SELECT kategori_roc,
               COUNT(*) AS jumlah
        FROM workorders
        WHERE kategori_roc IS NOT NULL AND kategori_roc != ''
        {(' AND ' + where[7:]) if where else ''}
        GROUP BY kategori_roc
        ORDER BY jumlah DESC
        LIMIT 20
    """, params)


# ── Infrastruktur ─────────────────────────────────────────────────────────────

def get_infrastruktur_stats(filters: dict = None) -> list:
    where, params = _build_where(filters)
    return run_query(f"""
        SELECT
            'ODP'   AS infra, COUNT(CASE WHEN odp   IS NOT NULL AND odp   != '' THEN 1 END) AS jumlah FROM workorders {where}
        UNION ALL
        SELECT
            'ODC'   AS infra, COUNT(CASE WHEN odc   IS NOT NULL AND odc   != '' THEN 1 END) FROM workorders {where}
        UNION ALL
        SELECT
            'GPON'  AS infra, COUNT(CASE WHEN gpon  IS NOT NULL AND gpon  != '' THEN 1 END) FROM workorders {where}
        UNION ALL
        SELECT
            'Feeder' AS infra, COUNT(CASE WHEN feeder IS NOT NULL AND feeder != '' THEN 1 END) FROM workorders {where}
        UNION ALL
        SELECT
            'Distribusi' AS infra, COUNT(CASE WHEN distribusi IS NOT NULL AND distribusi != '' THEN 1 END) FROM workorders {where}
    """, {**params, **params, **params, **params, **params})


# ── Durasi ────────────────────────────────────────────────────────────────────

def get_durasi_distribution(filters: dict = None) -> list:
    where, params = _build_where(filters)
    return run_query(f"""
        SELECT durasi_hari, sto, nama_teknisi, status_wo, is_sla_tercapai
        FROM workorders
        WHERE durasi_hari IS NOT NULL AND durasi_hari >= 0
        {(' AND ' + where[7:]) if where else ''}
        LIMIT 5000
    """, params)


def get_durasi_grup(filters: dict = None) -> list:
    where, params = _build_where(filters)
    return run_query(f"""
        SELECT durasi_grup,
               COUNT(*) AS jumlah,
               ROUND(AVG(durasi_hari), 2) AS avg_durasi
        FROM workorders
        WHERE durasi_grup IS NOT NULL AND durasi_grup != ''
        {(' AND ' + where[7:]) if where else ''}
        GROUP BY durasi_grup
        ORDER BY jumlah DESC
    """, params)


# ── ETL Logs ──────────────────────────────────────────────────────────────────

def get_etl_logs(limit: int = 50) -> list:
    return run_query(f"""
        SELECT id, etl_name, source_file, status,
               total_records, inserted_records, skipped_records, failed_records,
               error_message, started_at, finished_at, duration_seconds
        FROM etl_logs
        ORDER BY started_at DESC
        LIMIT {limit}
    """)


def get_etl_summary() -> list:
    return run_query("""
        SELECT
            status,
            COUNT(*) AS total_runs,
            SUM(total_records) AS total_records,
            SUM(inserted_records) AS inserted,
            MAX(started_at) AS last_run
        FROM etl_logs
        GROUP BY status
    """)


# ── Filter Options ────────────────────────────────────────────────────────────

def get_filter_options() -> dict:
    years = run_query("SELECT DISTINCT tahun FROM workorders WHERE tahun IS NOT NULL ORDER BY tahun DESC")
    months = run_query("SELECT DISTINCT bulan, nama_bulan FROM workorders WHERE bulan IS NOT NULL ORDER BY bulan")
    stos = run_query("SELECT DISTINCT sto FROM workorders WHERE sto IS NOT NULL ORDER BY sto")
    statuses = run_query("SELECT DISTINCT status_wo FROM workorders WHERE status_wo IS NOT NULL ORDER BY status_wo")
    teknisi = run_query("SELECT DISTINCT nama_teknisi FROM workorders WHERE nama_teknisi IS NOT NULL ORDER BY nama_teknisi")
    segment = run_query("SELECT DISTINCT segment FROM workorders WHERE segment IS NOT NULL ORDER BY segment")
    return {
        "years": [r["tahun"] for r in years],
        "months": [(r["bulan"], r["nama_bulan"]) for r in months],
        "stos": [r["sto"] for r in stos],
        "statuses": [r["status_wo"] for r in statuses],
        "teknisi": [r["nama_teknisi"] for r in teknisi],
        "segments": [r["segment"] for r in segment],
    }


# ── Internal Helpers ──────────────────────────────────────────────────────────

def _build_where(filters: dict) -> tuple:
    """Build WHERE clause and params dict from filter dict."""
    if not filters:
        return "", {}

    clauses = []
    params = {}

    if filters.get("tahun"):
        tahun = filters["tahun"]
        if isinstance(tahun, list) and tahun:
            placeholders = ",".join([f":tahun_{i}" for i in range(len(tahun))])
            clauses.append(f"tahun IN ({placeholders})")
            for i, y in enumerate(tahun):
                params[f"tahun_{i}"] = y
        elif not isinstance(tahun, list):
            clauses.append("tahun = :tahun")
            params["tahun"] = tahun

    if filters.get("bulan"):
        bulan = filters["bulan"]
        if isinstance(bulan, list) and bulan:
            placeholders = ",".join([f":bulan_{i}" for i in range(len(bulan))])
            clauses.append(f"bulan IN ({placeholders})")
            for i, m in enumerate(bulan):
                params[f"bulan_{i}"] = m
        elif not isinstance(bulan, list):
            clauses.append("bulan = :bulan")
            params["bulan"] = bulan

    if filters.get("sto"):
        sto_list = filters["sto"]
        if isinstance(sto_list, list) and sto_list:
            placeholders = ",".join([f":sto_{i}" for i in range(len(sto_list))])
            clauses.append(f"sto IN ({placeholders})")
            for i, s in enumerate(sto_list):
                params[f"sto_{i}"] = s

    if filters.get("status_wo"):
        st_list = filters["status_wo"]
        if isinstance(st_list, list) and st_list:
            placeholders = ",".join([f":status_{i}" for i in range(len(st_list))])
            clauses.append(f"status_wo IN ({placeholders})")
            for i, s in enumerate(st_list):
                params[f"status_{i}"] = s

    if filters.get("segment"):
        seg_list = filters["segment"]
        if isinstance(seg_list, list) and seg_list:
            placeholders = ",".join([f":segment_{i}" for i in range(len(seg_list))])
            clauses.append(f"segment IN ({placeholders})")
            for i, s in enumerate(seg_list):
                params[f"segment_{i}"] = s

    where = ("WHERE " + " AND ".join(clauses)) if clauses else ""
    return where, params
