"""
ETL Extract Module
Membaca file Excel/CSV Work Order dan mengembalikan raw DataFrame.
"""
import pandas as pd
import io


# Mapping nama kolom Excel → nama kolom DB
# Kunci = nama kolom Excel (case-insensitive strip)
# Value = nama kolom di tabel workorders
COLUMN_MAPPING = {
    # Waktu
    "bulan": "nama_bulan",
    "tanggal": "tanggal",

    # Identitas WO
    "wo / sc id": "wo_id",
    "wo/sc id": "wo_id",
    "sc id": "sc_id",
    "track id": "track_id",
    "track id baru": "track_id",
    "tanggal order": "tanggal_order",
    "tanggal komitmen ps completed": "tanggal_komitmen",
    "tanggal komitmen": "tanggal_komitmen",

    # STO
    "sto": "sto",
    "branch": "branch",
    "sektor": "sektor",
    "hsa": "hsa",
    "sto input": "sto_input",

    # Teknisi
    "nik teknisi": "nik_teknisi",
    "nama teknisi": "nama_teknisi",
    "mitra": "mitra",
    "korlap": "korlap",
    "komandan team": "komandan_team",
    "komandan team/pic team": "komandan_team",
    "cp": "cp",
    "k-contact": "cp",
    "spv": "spv",

    # Pelanggan
    "nama pelanggan": "nama_pelanggan",
    "nama contact": "nama_contact",
    "uic": "uic",
    "segment": "segment",
    "layanan": "layanan",
    "alamat instalasi": "alamat_instalasi",
    "koordinat pelanggan": "koordinat_lat",

    # Kendala
    "kendala pt1": "kendala_pt1",
    "kategori roc": "kategori_roc",
    "kategori solusi": "kategori_solusi",
    "solusi kendala": "solusi_kendala",
    "keterangan": "keterangan",
    "solusi maintenance": "solusi_maintenance",
    "solusi optima": "solusi_optima",
    "solusi sdi & daman": "solusi_sdi_daman",
    "solusi sdi daman": "solusi_sdi_daman",

    # Infrastruktur
    "odp": "odp",
    "odc": "odc",
    "gpon": "gpon",
    "feeder": "feeder",
    "distribusi": "distribusi",
    "core distribusi": "core_distribusi",
    "datek1": "datek1",
    "datek inputan": "datek_inputan",
    "datek real": "datek_real",
    "base tray odc": "base_tray_odc",
    "port base tray odc": "port_base_tray_odc",
    "hasil ukur odp": "hasil_ukur_odp",
    "hasil ukur distribusi": "hasil_ukur_distribusi",
    "hasil ukur feeder": "hasil_ukur_feeder",

    # Status
    "status": "status_wo",
    "status wo": "status_wo",
    "status sc": "status_sc",
    "status final": "status_final",

    # Durasi
    "durasi (hari)": "durasi_hari",
    "durasi hari": "durasi_hari",
    "durasi pengerjaan kendala": "durasi_pengerjaan_menit",
    "durasi grup": "durasi_grup",
    "durasi grup pengerjaan kendala teknis": "durasi_grup_pengerjaan",
    "durasi manja": "durasi_manja",
    "durasi": "durasi_hari",

    # Monitoring
    "tgl input hd gdocs": "tgl_input_hd_gdocs",
}


def extract_from_file(file_obj, filename: str = "") -> pd.DataFrame:
    """
    Baca file Excel atau CSV dan kembalikan sebagai DataFrame mentah.
    
    Args:
        file_obj: File-like object (bisa dari st.file_uploader)
        filename: Nama file untuk deteksi ekstensi
    
    Returns:
        pd.DataFrame: Data mentah
    """
    ext = filename.lower().split(".")[-1] if filename else "xlsx"

    if ext in ("xlsx", "xls"):
        # Coba baca sheet pertama yang punya data
        try:
            xl = pd.ExcelFile(file_obj)
            df = None
            for sheet in xl.sheet_names:
                candidate = pd.read_excel(xl, sheet_name=sheet, header=0)
                if len(candidate) > 0 and len(candidate.columns) > 5:
                    df = candidate
                    break
            if df is None:
                df = pd.read_excel(file_obj, header=0)
        except Exception:
            df = pd.read_excel(file_obj, header=0)
    elif ext == "csv":
        try:
            df = pd.read_csv(file_obj, encoding="utf-8-sig", low_memory=False)
        except UnicodeDecodeError:
            df = pd.read_csv(file_obj, encoding="latin-1", low_memory=False)
    else:
        raise ValueError(f"Format file tidak didukung: {ext}")

    return df


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Rename kolom Excel ke nama kolom DB berdasarkan COLUMN_MAPPING.
    Kolom yang tidak dikenali dibiarkan.
    """
    rename_map = {}
    for col in df.columns:
        normalized = str(col).strip().lower()
        # Hapus newline dan spasi berlebih
        normalized = " ".join(normalized.split())
        if normalized in COLUMN_MAPPING:
            target = COLUMN_MAPPING[normalized]
            # Hindari duplikat
            if target not in rename_map.values():
                rename_map[col] = target

    df = df.rename(columns=rename_map)
    return df
