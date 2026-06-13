"""
ETL Load Module
Menyimpan DataFrame yang sudah di-transform ke MySQL.
Mendukung upsert (skip duplikat berdasarkan wo_id).
"""
import pandas as pd
from datetime import datetime
from sqlalchemy import text
from utils.db import get_engine


def load_to_db(df: pd.DataFrame, source_file: str = "", log_id: int = None) -> dict:
    """
    Load DataFrame ke tabel workorders.

    Returns:
        dict: { inserted, skipped, failed, total }
    """
    engine = get_engine()
    total = len(df)
    inserted = 0
    skipped = 0
    failed = 0
    errors = []

    if total == 0:
        return {"inserted": 0, "skipped": 0, "failed": 0, "total": 0}

    with engine.connect() as conn:
        for _, row in df.iterrows():
            try:
                # Cek duplikat berdasarkan wo_id
                wo_id = row.get("wo_id")
                if wo_id and str(wo_id) not in ("nan", "None", ""):
                    existing = conn.execute(
                        text("SELECT id FROM workorders WHERE wo_id = :wo_id LIMIT 1"),
                        {"wo_id": str(wo_id)}
                    ).fetchone()
                    if existing:
                        skipped += 1
                        continue

                # Build insert
                row_dict = {k: (None if pd.isna(v) else v) for k, v in row.items()
                            if not isinstance(v, type(pd.NaT))}

                # Pastikan tipe data datetime
                for date_col in ["tanggal", "tanggal_order", "tanggal_komitmen",
                                  "tgl_input_hd_gdocs", "imported_at"]:
                    if date_col in row_dict and row_dict[date_col] is not None:
                        val = row_dict[date_col]
                        if hasattr(val, "to_pydatetime"):
                            row_dict[date_col] = val.to_pydatetime()
                        elif isinstance(val, str) and val not in ("nan", "None", ""):
                            try:
                                row_dict[date_col] = pd.to_datetime(val).to_pydatetime()
                            except Exception:
                                row_dict[date_col] = None

                cols = list(row_dict.keys())
                placeholders = ", ".join([f":{c}" for c in cols])
                col_list = ", ".join([f"`{c}`" for c in cols])

                conn.execute(
                    text(f"INSERT INTO workorders ({col_list}) VALUES ({placeholders})"),
                    row_dict
                )
                inserted += 1

            except Exception as e:
                failed += 1
                errors.append(str(e)[:200])
                continue

        conn.commit()

    # Update ETL log jika ada
    if log_id:
        _update_etl_log(log_id, inserted, skipped, failed,
                        "; ".join(set(errors[:5])) if errors else None)

    return {
        "inserted": inserted,
        "skipped": skipped,
        "failed": failed,
        "total": total,
        "errors": errors[:10],
    }


def create_etl_log(etl_name: str, source_file: str) -> int:
    """Buat record ETL log baru dan kembalikan ID-nya."""
    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute(
            text("""
                INSERT INTO etl_logs (etl_name, source_file, status, started_at)
                VALUES (:name, :file, 'running', NOW())
            """),
            {"name": etl_name, "file": source_file}
        )
        conn.commit()
        return result.lastrowid


def finish_etl_log(log_id: int, status: str, total: int, inserted: int,
                   skipped: int, failed: int, error_msg: str = None):
    """Selesaikan record ETL log."""
    engine = get_engine()
    with engine.connect() as conn:
        conn.execute(
            text("""
                UPDATE etl_logs
                SET status = :status,
                    total_records = :total,
                    inserted_records = :inserted,
                    skipped_records = :skipped,
                    failed_records = :failed,
                    error_message = :error,
                    finished_at = NOW(),
                    duration_seconds = TIMESTAMPDIFF(SECOND, started_at, NOW())
                WHERE id = :id
            """),
            {
                "status": status, "total": total, "inserted": inserted,
                "skipped": skipped, "failed": failed,
                "error": error_msg, "id": log_id
            }
        )
        conn.commit()


def _update_etl_log(log_id: int, inserted: int, skipped: int, failed: int,
                    error_msg: str = None):
    """Update partial log progress."""
    engine = get_engine()
    with engine.connect() as conn:
        conn.execute(
            text("""
                UPDATE etl_logs
                SET inserted_records = :inserted,
                    skipped_records = :skipped,
                    failed_records = :failed,
                    error_message = :error
                WHERE id = :id
            """),
            {"inserted": inserted, "skipped": skipped,
             "failed": failed, "error": error_msg, "id": log_id}
        )
        conn.commit()
