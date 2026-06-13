"""
ETL Orchestrator
Menjalankan full pipeline: Extract → Transform → Load
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from etl.extract import extract_from_file, normalize_columns
from etl.transform import transform
from etl.load import load_to_db, create_etl_log, finish_etl_log


def run_etl(file_obj, filename: str = "upload") -> dict:
    """
    Full ETL pipeline dari file ke database.

    Returns:
        dict: Statistik ETL { success, total, inserted, skipped, failed, errors }
    """
    log_id = None
    try:
        # Buat log entry
        log_id = create_etl_log(
            etl_name=f"ETL Upload - {filename}",
            source_file=filename
        )

        # 1. EXTRACT
        raw_df = extract_from_file(file_obj, filename)
        if raw_df is None or len(raw_df) == 0:
            finish_etl_log(log_id, "failed", 0, 0, 0, 0, "File kosong atau tidak terbaca")
            return {"success": False, "error": "File kosong atau tidak dapat dibaca"}

        # Normalisasi nama kolom
        df = normalize_columns(raw_df)

        # 2. TRANSFORM
        df_transformed = transform(df, source_file=filename)

        if len(df_transformed) == 0:
            finish_etl_log(log_id, "failed", 0, 0, 0, 0, "Tidak ada data setelah transform")
            return {"success": False, "error": "Tidak ada data valid setelah transformasi"}

        # 3. LOAD
        result = load_to_db(df_transformed, source_file=filename, log_id=log_id)

        # Selesaikan log
        finish_etl_log(
            log_id=log_id,
            status="success" if result["failed"] == 0 else "failed",
            total=result["total"],
            inserted=result["inserted"],
            skipped=result["skipped"],
            failed=result["failed"],
            error_msg="; ".join(result.get("errors", [])[:3])
        )

        return {
            "success": True,
            "total": result["total"],
            "inserted": result["inserted"],
            "skipped": result["skipped"],
            "failed": result["failed"],
            "errors": result.get("errors", []),
            "log_id": log_id,
        }

    except Exception as e:
        error_msg = str(e)
        if log_id:
            finish_etl_log(log_id, "failed", 0, 0, 0, 0, error_msg[:500])
        return {"success": False, "error": error_msg}
