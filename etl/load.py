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
                    # Cek duplikat berdasarkan wo_id + track_id, atau hanya wo_id jika track_id kosong
                wo_id = row.get("wo_id")
                track_id = row.get("track_id")
                sc_id = row.get("sc_id")
                if wo_id and str(wo_id) not in ("nan", "None", ""):
                    if track_id and str(track_id).strip() not in ("nan", "None", ""):
                        existing = conn.execute(
                            text("SELECT id FROM workorders WHERE wo_id = :wo_id AND track_id = :track_id LIMIT 1"),
                            {"wo_id": str(wo_id), "track_id": str(track_id)}
                        ).fetchone()
                    elif sc_id and str(sc_id).strip() not in ("nan", "None", ""):
                        existing = conn.execute(
                            text("SELECT id FROM workorders WHERE wo_id = :wo_id AND sc_id = :sc_id LIMIT 1"),
                            {"wo_id": str(wo_id), "sc_id": str(sc_id)}
                        ).fetchone()
                    else:
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
                
                # Populasikan ke star-schema dimension & fact tables
                try:
                    _load_star_schema_row(conn, row_dict, log_id)
                except Exception as star_err:
                    # Log star schema error but don't fail flat table load
                    errors.append(f"Star schema err: {str(star_err)[:150]}")

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


def _load_star_schema_row(conn, row, log_id):
    import uuid
    # Check if wo_id is None
    wo_id = row.get("wo_id")
    if not wo_id:
        return
        
    track_id = row.get("track_id") or ""
    
    # Check duplicate fact record
    existing_fact = conn.execute(text("""
        SELECT id FROM fact_workorder WHERE wo_sc_id = :wo_id AND track_id = :track_id
    """), {"wo_id": wo_id, "track_id": track_id}).fetchone()
    if existing_fact:
        return

    # 1. dim_waktu
    tanggal = row.get("tanggal")
    if not tanggal:
        tanggal = row.get("tanggal_order") or datetime.now().date()
    
    w_row = conn.execute(text("SELECT id FROM dim_waktu WHERE tanggal = :t"), {"t": tanggal}).fetchone()
    if w_row:
        waktu_id = w_row[0]
    else:
        import pandas as pd
        dt = pd.to_datetime(tanggal)
        MONTH_NAMES_ID = {
            1: "Januari", 2: "Februari", 3: "Maret", 4: "April",
            5: "Mei", 6: "Juni", 7: "Juli", 8: "Agustus",
            9: "September", 10: "Oktober", 11: "November", 12: "Desember",
        }
        DAY_NAMES_ID = {
            "Monday": "Senin", "Tuesday": "Selasa", "Wednesday": "Rabu",
            "Thursday": "Kamis", "Friday": "Jumat", "Saturday": "Sabtu",
            "Sunday": "Minggu",
        }
        nama_bulan = MONTH_NAMES_ID.get(dt.month, "")
        nama_hari = DAY_NAMES_ID.get(dt.strftime("%A"), dt.strftime("%A"))
        w_res = conn.execute(text("""
            INSERT INTO dim_waktu (tanggal, tahun, bulan, hari, nama_bulan, nama_hari, kuartal, hari_kerja, created_at, updated_at)
            VALUES (:tanggal, :tahun, :bulan, :hari, :nama_bulan, :nama_hari, :kuartal, :hari_kerja, NOW(), NOW())
        """), {
            "tanggal": tanggal,
            "tahun": dt.year,
            "bulan": dt.month,
            "hari": dt.day,
            "nama_bulan": nama_bulan,
            "nama_hari": nama_hari,
            "kuartal": (dt.month - 1) // 3 + 1,
            "hari_kerja": 0 if dt.weekday() in (5, 6) else 1
        })
        waktu_id = w_res.lastrowid
        
    # 2. dim_sto
    sto = row.get("sto") or "Tidak Diketahui"
    sto_row = conn.execute(text("SELECT id FROM dim_sto WHERE kode_sto = :sto OR nama_sto = :sto LIMIT 1"), {"sto": sto}).fetchone()
    if sto_row:
        sto_id = sto_row[0]
    else:
        kode_sto = f"{sto}_{uuid.uuid4().hex[:4]}"
        sto_res = conn.execute(text("""
            INSERT INTO dim_sto (kode_sto, nama_sto, sto_input, branch, sektor, hsa, created_at, updated_at)
            VALUES (:kode_sto, :nama_sto, :sto_input, :branch, :sektor, :hsa, NOW(), NOW())
        """), {
            "kode_sto": kode_sto,
            "nama_sto": sto,
            "sto_input": row.get("sto_input") or sto,
            "branch": row.get("branch"),
            "sektor": row.get("sektor"),
            "hsa": row.get("hsa")
        })
        sto_id = sto_res.lastrowid
        
    # 3. dim_teknisi
    nik = row.get("nik_teknisi") or "Tidak Diketahui"
    tek_row = conn.execute(text("SELECT id FROM dim_teknisi WHERE nik_teknisi = :nik"), {"nik": nik}).fetchone()
    if tek_row:
        teknisi_id = tek_row[0]
    else:
        nama = row.get("nama_teknisi")
        if not nama:
            if " - " in nik:
                nama = nik.split(" - ", 1)[1].strip()
            else:
                nama = nik
        tek_res = conn.execute(text("""
            INSERT INTO dim_teknisi (nik_teknisi, nama_teknisi, korlap, komandan_team, mitra, spv, nama_mitra, cp, created_at, updated_at)
            VALUES (:nik, :nama, :korlap, :komandan, :mitra, :spv, :mitra, :cp, NOW(), NOW())
        """), {
            "nik": nik,
            "nama": nama,
            "korlap": row.get("korlap"),
            "komandan": row.get("komandan_team"),
            "mitra": row.get("mitra"),
            "spv": row.get("spv"),
            "cp": row.get("cp")
        })
        teknisi_id = tek_res.lastrowid
        
    # 4. dim_pelanggan
    cp = row.get("cp")
    k_contact = cp if cp and str(cp).strip() not in ("", "None") else wo_id
    pel_row = conn.execute(text("SELECT id FROM dim_pelanggan WHERE k_contact = :k"), {"k": str(k_contact)}).fetchone()
    if pel_row:
        pelanggan_id = pel_row[0]
    else:
        pel_res = conn.execute(text("""
            INSERT INTO dim_pelanggan (k_contact, nama_pelanggan, cp, segment, layanan, uic, alamat_instalasi, nama_contact, koordinat_pelanggan, koordinat_lat, koordinat_lon, created_at, updated_at)
            VALUES (:k, :nama, :cp, :segment, :layanan, :uic, :alamat, :nama_contact, :koordinat, :lat, :lon, NOW(), NOW())
        """), {
            "k": str(k_contact),
            "nama": row.get("nama_pelanggan"),
            "cp": cp,
            "segment": row.get("segment"),
            "layanan": row.get("layanan"),
            "uic": row.get("uic"),
            "alamat": row.get("alamat_instalasi"),
            "nama_contact": row.get("nama_contact"),
            "koordinat": f"{row.get('koordinat_lat') or ''} {row.get('koordinat_lon') or ''}".strip() or None,
            "lat": row.get("koordinat_lat"),
            "lon": row.get("koordinat_lon")
        })
        pelanggan_id = pel_res.lastrowid
        
    # 5. dim_status
    status = row.get("status_wo") or ""
    stat_row = conn.execute(text("SELECT id FROM dim_status WHERE status_name = :s"), {"s": status}).fetchone()
    if stat_row:
        status_id = stat_row[0]
    else:
        STATUS_SELESAI = {"close", "closed", "selesai", "ps", "completed", "done", "ps completed", "close ps", "clsd"}
        status_group = "Selesai" if status.lower() in STATUS_SELESAI else "Pending"
        stat_res = conn.execute(text("""
            INSERT INTO dim_status (status_name, status_group, aktif, status_sc, created_at, updated_at)
            VALUES (:s, :group, 1, :sc, NOW(), NOW())
        """), {
            "s": status,
            "group": status_group,
            "sc": row.get("status_sc")
        })
        status_id = stat_res.lastrowid
        
    # 6. dim_kendala
    kendala = row.get("kendala_pt1") or ""
    ken_row = conn.execute(text("SELECT id FROM dim_kendala WHERE COALESCE(kendala_pt1, '') = :k AND COALESCE(kategori_solusi, '') = :sol AND COALESCE(kategori_roc, '') = :roc LIMIT 1"), {
        "k": kendala,
        "sol": row.get("kategori_solusi") or "",
        "roc": row.get("kategori_roc") or ""
    }).fetchone()
    if ken_row:
        kendala_id = ken_row[0]
    else:
        ken_res = conn.execute(text("""
            INSERT INTO dim_kendala (kategori_solusi, kategori_roc, kendala_pt1, solusi_kendala, solusi_maintenance, solusi_optima, solusi_sdi_daman, keterangan, created_at, updated_at)
            VALUES (:solusi, :roc, :k, :sol_k, :sol_m, :sol_o, :sol_s, :ket, NOW(), NOW())
        """), {
            "solusi": row.get("kategori_solusi"),
            "roc": row.get("kategori_roc"),
            "k": kendala,
            "sol_k": row.get("solusi_kendala"),
            "sol_m": row.get("solusi_maintenance"),
            "sol_o": row.get("solusi_optima"),
            "sol_s": row.get("solusi_sdi_daman"),
            "ket": row.get("keterangan")[:499] if row.get("keterangan") else None
        })
        kendala_id = ken_res.lastrowid
        
    # 7. dim_infrastruktur
    infra_res = conn.execute(text("""
        INSERT INTO dim_infrastruktur (etl_log_id, odp, odc, gpon, feeder, distribusi, core_distribusi, datek1, datek_inputan, datek_real, hasil_ukur_odp, hasil_ukur_distribusi, hasil_ukur_feeder, base_tray_odc, port_base_tray_odc, wo_id, created_at, updated_at)
        VALUES (:log_id, :odp, :odc, :gpon, :feeder, :distribusi, :core, :d1, :d_in, :d_real, :h_odp, :h_dist, :h_feed, :bt, :pbt, :wo_id, NOW(), NOW())
    """), {
        "log_id": log_id,
        "odp": row.get("odp"),
        "odc": row.get("odc"),
        "gpon": row.get("gpon"),
        "feeder": row.get("feeder"),
        "distribusi": row.get("distribusi"),
        "core": row.get("core_distribusi"),
        "d1": row.get("datek1"),
        "d_in": row.get("datek_inputan"),
        "d_real": row.get("datek_real"),
        "h_odp": row.get("hasil_ukur_odp"),
        "h_dist": row.get("hasil_ukur_distribusi"),
        "h_feed": row.get("hasil_ukur_feeder"),
        "bt": row.get("base_tray_odc"),
        "pbt": row.get("port_base_tray_odc"),
        "wo_id": wo_id
    })
    infrastruktur_id = infra_res.lastrowid
    
    # 8. fact_workorder
    fact_res = conn.execute(text("""
        INSERT INTO fact_workorder (
            etl_log_id, dim_waktu_id, dim_sto_id, dim_teknisi_id, dim_pelanggan_id,
            dim_kendala_id, dim_infrastruktur_id, dim_status_id,
            wo_sc_id, sc_id, track_id, track_id_baru,
            tanggal_order, tanggal_komitmen, tgl_input_hd_gdocs,
            status_wo, status_sc, durasi_hari, durasi, durasi_manja,
            durasi_pengerjaan_kendala, durasi_grup, durasi_grup_kendala,
            is_sla_tercapai, is_workfail, is_unsc, keterangan, created_at, updated_at,
            durasi_pengerjaan_menit
        )
        VALUES (
            :log_id, :waktu_id, :sto_id, :teknisi_id, :pelanggan_id,
            :kendala_id, :infrastruktur_id, :status_id,
            :wo_id, :sc_id, :track_id, :track_id_baru,
            :tgl_order, :tgl_komit, :tgl_gdocs,
            :status_wo, :status_sc, :durasi_hari, :durasi, :durasi_manja,
            :durasi_pengerjaan_kendala, :durasi_grup, :durasi_grup_kendala,
            :is_sla, :is_wf, :is_unsc, :keterangan, NOW(), NOW(),
            :durasi_menit
        )
    """), {
        "log_id": log_id, "waktu_id": waktu_id, "sto_id": sto_id, "teknisi_id": teknisi_id, "pelanggan_id": pelanggan_id,
        "kendala_id": kendala_id, "infrastruktur_id": infrastruktur_id, "status_id": status_id,
        "wo_id": wo_id, "sc_id": row.get("sc_id"), "track_id": track_id, "track_id_baru": track_id,
        "tgl_order": row.get("tanggal_order"), "tgl_komit": row.get("tanggal_komitmen"), "tgl_gdocs": row.get("tgl_input_hd_gdocs"),
        "status_wo": status, "status_sc": row.get("status_sc"), "durasi_hari": row.get("durasi_hari"), "durasi": row.get("durasi_hari"), "durasi_manja": row.get("durasi_manja"),
        "durasi_pengerjaan_kendala": row.get("durasi_pengerjaan_menit"), "durasi_grup": row.get("durasi_grup"), "durasi_grup_kendala": row.get("durasi_grup_pengerjaan"),
        "is_sla": row.get("is_sla_tercapai") or 0, "is_wf": row.get("is_workfail") or 0, "is_unsc": row.get("is_unsc") or 0,
        "keterangan": row.get("keterangan"), "durasi_menit": row.get("durasi_pengerjaan_menit")
    })
    fact_workorder_id = fact_res.lastrowid
    
    # 9. fact_kendalateknis
    if kendala:
        conn.execute(text("""
            INSERT INTO fact_kendalateknis (
                etl_log_id, fact_workorder_id, dim_kendala_id, dim_teknisi_id, dim_status_id,
                keterangan, resolusi_jam, root_cause, created_at, updated_at,
                durasi_grup_pengerjaan, hasil_solusi_maintenance, hasil_solusi_optima, hasil_solusi_sdi,
                total_eskalasi, jumlah_kendala
            )
            VALUES (
                :log_id, :fact_wo_id, :kendala_id, :teknisi_id, :status_id,
                :keterangan, :resolusi, :root_cause, NOW(), NOW(),
                :durasi_grup, :sol_m, :sol_o, :sol_s,
                :total_esk, :jml_knd
            )
        """), {
            "log_id": log_id,
            "fact_wo_id": fact_workorder_id,
            "kendala_id": kendala_id,
            "teknisi_id": teknisi_id,
            "status_id": status_id,
            "keterangan": row.get("keterangan")[:499] if row.get("keterangan") else None,
            "resolusi": float(row.get("durasi_pengerjaan_menit") or 0) / 60.0 if row.get("durasi_pengerjaan_menit") else None,
            "root_cause": kendala,
            "durasi_grup": row.get("durasi_pengerjaan_menit"),
            "sol_m": row.get("solusi_maintenance"),
            "sol_o": row.get("solusi_optima"),
            "sol_s": row.get("solusi_sdi_daman"),
            "total_esk": row.get("total_eskalasi") or 0,
            "jml_knd": row.get("jumlah_kendala") or 1
        })



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
