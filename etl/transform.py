"""
ETL Transform Module
Cleaning, type casting, dan feature engineering dari DataFrame mentah.
"""
import pandas as pd
import numpy as np
import re
from datetime import datetime


MONTH_MAP = {
    "january": 1, "februari": 2, "february": 2, "maret": 3, "march": 3,
    "april": 4, "mei": 5, "may": 5, "juni": 6, "june": 6,
    "juli": 7, "july": 7, "agustus": 8, "august": 8,
    "september": 9, "oktober": 10, "october": 10,
    "november": 11, "desember": 12, "december": 12,
    "jan": 1, "feb": 2, "mar": 3, "apr": 4,
    "jun": 6, "jul": 7, "aug": 8, "agt": 8, "sep": 9,
    "oct": 10, "okt": 10, "nov": 11, "dec": 12, "des": 12,
}

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

STATUS_SELESAI = {"close", "closed", "selesai", "ps", "completed", "done",
                  "ps completed", "close ps", "clsd"}


def transform(df: pd.DataFrame, source_file: str = "") -> pd.DataFrame:
    """
    Full transform pipeline:
    1. Bersihkan kolom teks
    2. Parse & derive tanggal
    3. Hitung durasi
    4. Flag SLA, workfail, unsc
    5. Tambah kolom ETL metadata
    """
    df = df.copy()

    # ── 1. Normalisasi nama kolom ──────────────────────────────────────────────
    df.columns = [str(c).strip() for c in df.columns]

    # ── 2. Bersihkan teks di semua kolom string ────────────────────────────────
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].astype(str).str.strip()
        df[col] = df[col].replace({"nan": None, "None": None, "": None, "NaT": None})

    # ── 3. Parse kolom tanggal ────────────────────────────────────────────────
    for date_col in ["tanggal", "tanggal_order", "tanggal_komitmen", "tgl_input_hd_gdocs"]:
        if date_col in df.columns:
            df[date_col] = df[date_col].apply(_safe_parse_date)

    # ── 4. Derive kolom waktu dari kolom tanggal ──────────────────────────────
    if "tanggal" in df.columns:
        valid_dates = df["tanggal"].dropna()

        df["bulan"] = df["tanggal"].apply(
            lambda x: x.month if pd.notna(x) else None)
        df["tahun"] = df["tanggal"].apply(
            lambda x: x.year if pd.notna(x) else None)
        df["kuartal"] = df["bulan"].apply(
            lambda m: ((m - 1) // 3 + 1) if pd.notna(m) else None)
        df["nama_bulan"] = df["bulan"].apply(
            lambda m: MONTH_NAMES_ID.get(int(m), "") if pd.notna(m) else None)
        df["nama_hari"] = df["tanggal"].apply(
            lambda x: DAY_NAMES_ID.get(x.strftime("%A"), x.strftime("%A"))
            if pd.notna(x) else None)
    elif "nama_bulan" in df.columns:
        # Fallback: derive bulan dari nama_bulan
        df["bulan"] = df["nama_bulan"].apply(_parse_month_name)
        df["tahun"] = _guess_year(df)
        df["kuartal"] = df["bulan"].apply(
            lambda m: ((int(m) - 1) // 3 + 1) if pd.notna(m) and str(m) != "None" else None)

    # ── 5. Parse durasi ────────────────────────────────────────────────────────
    if "durasi_hari" in df.columns:
        df["durasi_hari"] = pd.to_numeric(
            df["durasi_hari"].astype(str).str.replace(",", ".").str.extract(r"([\d.]+)")[0],
            errors="coerce"
        )

    if "durasi_pengerjaan_menit" in df.columns:
        df["durasi_pengerjaan_menit"] = pd.to_numeric(
            df["durasi_pengerjaan_menit"].astype(str).str.extract(r"([\d]+)")[0],
            errors="coerce"
        ).astype("Int64")

    # ── 6. Hitung grup durasi ──────────────────────────────────────────────────
    if "durasi_hari" in df.columns and "durasi_grup" not in df.columns:
        df["durasi_grup"] = df["durasi_hari"].apply(_classify_durasi)

    # ── 7. Flag SLA ────────────────────────────────────────────────────────────
    # SLA tercapai: selesai dalam ≤ 3 hari (standar Telkom) atau flag dari data
    if "is_sla_tercapai" not in df.columns:
        if "durasi_hari" in df.columns and "status_wo" in df.columns:
            df["is_sla_tercapai"] = (
                (df["durasi_hari"].fillna(999) <= 3) &
                (df["status_wo"].str.lower().isin(STATUS_SELESAI))
            ).astype(int)
        elif "durasi_hari" in df.columns:
            df["is_sla_tercapai"] = (df["durasi_hari"].fillna(999) <= 3).astype(int)
        else:
            df["is_sla_tercapai"] = 0
    else:
        df["is_sla_tercapai"] = pd.to_numeric(df["is_sla_tercapai"], errors="coerce").fillna(0).astype(int)

    # ── 8. Flag Work Fail ──────────────────────────────────────────────────────
    if "is_workfail" not in df.columns:
        if "status_wo" in df.columns:
            workfail_keywords = ["workfail", "work fail", "wf", "gagal"]
            df["is_workfail"] = df["status_wo"].str.lower().apply(
                lambda x: 1 if any(kw in str(x) for kw in workfail_keywords) else 0
            )
        else:
            df["is_workfail"] = 0
    else:
        df["is_workfail"] = pd.to_numeric(df["is_workfail"], errors="coerce").fillna(0).astype(int)

    # ── 9. Flag UNSC ───────────────────────────────────────────────────────────
    if "is_unsc" not in df.columns:
        if "status_sc" in df.columns:
            df["is_unsc"] = df["status_sc"].str.lower().apply(
                lambda x: 1 if "unsc" in str(x) else 0
            )
        else:
            df["is_unsc"] = 0

    # ── 10. Parse wo_id dari kolom wo/sc id ────────────────────────────────────
    if "wo_id" in df.columns:
        # wo_id bisa berupa "WO024928973" atau combined "WO... / SC..."
        df["wo_id"] = df["wo_id"].astype(str).apply(_parse_wo_id)
        if "sc_id" not in df.columns:
            # Coba ekstrak SC ID dari kolom yang sama
            pass

    # ── 11. Koordinat ──────────────────────────────────────────────────────────
    if "koordinat_lat" in df.columns:
        df[["koordinat_lat", "koordinat_lon"]] = df["koordinat_lat"].apply(
            _parse_koordinat).apply(pd.Series)

    # ── 12. Jumlah kendala & total eskalasi ────────────────────────────────────
    if "jumlah_kendala" not in df.columns:
        df["jumlah_kendala"] = 1

    if "total_eskalasi" not in df.columns:
        df["total_eskalasi"] = 0

    # ── 13. ETL metadata ──────────────────────────────────────────────────────
    df["source_file"] = source_file
    df["imported_at"] = datetime.now()
    df["status_etl"] = "processed"

    # ── 14. Hanya ambil kolom yang ada di tabel DB ─────────────────────────────
    db_columns = [
        "tanggal", "bulan", "nama_bulan", "tahun", "kuartal", "nama_hari",
        "wo_id", "sc_id", "track_id", "tanggal_order", "tanggal_komitmen",
        "sto", "branch", "sektor", "hsa", "sto_input",
        "nik_teknisi", "nama_teknisi", "mitra", "korlap", "komandan_team", "cp", "spv",
        "nama_pelanggan", "nama_contact", "uic", "segment", "layanan",
        "alamat_instalasi", "koordinat_lat", "koordinat_lon",
        "kendala_pt1", "kategori_roc", "kategori_solusi", "solusi_kendala", "keterangan",
        "solusi_maintenance", "solusi_optima", "solusi_sdi_daman",
        "odp", "odc", "gpon", "feeder", "distribusi", "core_distribusi",
        "datek1", "datek_inputan", "datek_real",
        "base_tray_odc", "port_base_tray_odc",
        "hasil_ukur_odp", "hasil_ukur_distribusi", "hasil_ukur_feeder",
        "status_wo", "status_sc", "status_final",
        "durasi_hari", "durasi_pengerjaan_menit", "durasi_grup",
        "durasi_grup_pengerjaan", "durasi_manja",
        "tgl_input_hd_gdocs",
        "is_sla_tercapai", "is_workfail", "is_unsc",
        "total_eskalasi", "jumlah_kendala",
        "status_etl", "source_file", "imported_at",
    ]

    # Hanya sertakan kolom yang ada di DataFrame
    existing = [c for c in db_columns if c in df.columns]
    df = df[existing]

    # Ganti nilai None/NaN dengan None (bukan string "None")
    df = df.where(pd.notna(df), None)

    return df


# ── Helpers ───────────────────────────────────────────────────────────────────

def _safe_parse_date(val):
    if val is None or str(val).strip() in ("", "nan", "None", "NaT"):
        return None
    try:
        return pd.to_datetime(val, dayfirst=True, errors="coerce")
    except Exception:
        return None


def _parse_month_name(val) -> int | None:
    if val is None:
        return None
    val_lower = str(val).strip().lower()
    return MONTH_MAP.get(val_lower, None)


def _guess_year(df: pd.DataFrame) -> pd.Series:
    """Coba ambil tahun dari kolom tanggal_order atau tanggal_komitmen."""
    for col in ["tanggal_order", "tanggal_komitmen"]:
        if col in df.columns:
            years = df[col].apply(
                lambda x: x.year if pd.notna(x) else None)
            if years.notna().sum() > 0:
                return years
    return pd.Series([datetime.now().year] * len(df))


def _classify_durasi(days) -> str:
    if pd.isna(days):
        return "Tidak Diketahui"
    days = float(days)
    if days <= 1:
        return "< 1 Hari"
    elif days <= 3:
        return "1-3 Hari"
    elif days <= 7:
        return "4-7 Hari"
    elif days <= 14:
        return "8-14 Hari"
    else:
        return "> 14 Hari"


def _parse_wo_id(val) -> str | None:
    if val is None or str(val) in ("nan", "None"):
        return None
    val = str(val).strip()
    # Ambil bagian pertama jika ada separator
    for sep in [" / ", "/", "|", " "]:
        if sep in val and val.upper().startswith("WO"):
            parts = val.split(sep)
            wo_part = next((p.strip() for p in parts if p.strip().upper().startswith("WO")), None)
            if wo_part:
                return wo_part
    return val if val else None


def _parse_koordinat(val) -> tuple:
    """Parse 'lat lon' atau 'lat,lon' string ke tuple (lat, lon)."""
    if val is None or str(val) in ("nan", "None"):
        return (None, None)
    val = str(val).strip()
    # Format: "0.50299 101.512601" atau "0.50299,101.512601"
    val = val.replace(",", " ").split()
    if len(val) >= 2:
        try:
            return (float(val[0]), float(val[1]))
        except ValueError:
            pass
    return (None, None)
