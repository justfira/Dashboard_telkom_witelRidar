"""
Page 2: Upload Data & ETL Process
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
import time
from etl.run_etl import run_etl
from etl.extract import extract_from_file, normalize_columns, COLUMN_MAPPING
from etl.transform import transform
from utils.theme import get_theme_css

st.set_page_config(page_title="Upload & ETL | BI Ridar", page_icon="📥", layout="wide")
st.markdown(get_theme_css(), unsafe_allow_html=True)

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
    <div style="display:flex; align-items:center; gap:16px;">
        <div style="font-size:2.2rem;">📥</div>
        <div>
            <h1 style="margin:0; font-size:1.7rem; font-weight:800; color:#2C1810;">Upload Data & ETL</h1>
            <p style="margin:4px 0 0 0; color:#9B7B75; font-size:0.9rem; font-weight:500;">
                Upload file Excel/CSV → Extract → Transform → Load ke Database
            </p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── How to use ──────────────────────────────────────────────────────────────────
with st.expander("📖 Cara Penggunaan & Format Data", expanded=False):
    st.markdown("**Format File yang Didukung:** `.xlsx`, `.xls`, `.csv`")
    st.markdown("**Kolom Excel yang dikenali secara otomatis:**")
    mapping_display = {
        "Kolom Excel": list(COLUMN_MAPPING.keys())[:30],
        "Kolom Database": list(COLUMN_MAPPING.values())[:30],
    }
    st.dataframe(pd.DataFrame(mapping_display), use_container_width=True, height=280)
    st.info("""
**Catatan:**
- Nama kolom Excel bisa huruf besar/kecil — sistem otomatis mengenali
- Data duplikat (berdasarkan WO ID) akan dilewati otomatis
- Kolom tanggal akan diparse otomatis
- Flag SLA dihitung otomatis: selesai ≤ 3 hari = SLA Tercapai
    """)

st.markdown("---")

# ── Upload ──────────────────────────────────────────────────────────────────────
st.markdown('<p class="section-header">📂 Upload File Work Order</p>', unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Drag & drop file Excel atau CSV di sini",
    type=["xlsx", "xls", "csv"],
    help="Format: Excel (.xlsx/.xls) atau CSV (.csv)"
)

if uploaded_file:
    filename = uploaded_file.name
    st.success(f"✅ File diterima: **{filename}** ({uploaded_file.size / 1024:.1f} KB)")

    # ── Preview ─────────────────────────────────────────────────────────────────
    st.markdown('<p class="section-header">👁️ Preview Data Mentah</p>', unsafe_allow_html=True)
    try:
        uploaded_file.seek(0)
        raw_df  = extract_from_file(uploaded_file, filename)
        df_norm = normalize_columns(raw_df)

        col_info1, col_info2, col_info3 = st.columns(3)
        col_info1.metric("📊 Total Baris",    f"{len(raw_df):,}")
        col_info2.metric("📋 Kolom Ditemukan", f"{len(raw_df.columns):,}")

        recognized_cols = [c for c in df_norm.columns if c in [
            "wo_id", "tanggal", "sto", "nama_teknisi", "status_wo",
            "durasi_hari", "kendala_pt1", "is_sla_tercapai"
        ]]
        col_info3.metric("🎯 Kolom Dikenali", f"{len(recognized_cols)}")

        st.dataframe(raw_df.head(10), use_container_width=True, height=250)

        with st.expander("🔄 Preview Setelah Transformasi"):
            uploaded_file.seek(0)
            raw_df2  = extract_from_file(uploaded_file, filename)
            df_norm2 = normalize_columns(raw_df2)
            df_trans = transform(df_norm2, source_file=filename)
            st.dataframe(df_trans.head(10), use_container_width=True, height=250)

    except Exception as e:
        st.error(f"❌ Gagal membaca file: {e}")

    # ── ETL Button ───────────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown('<p class="section-header">🔄 Jalankan Proses ETL</p>', unsafe_allow_html=True)

    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    with col_btn2:
        run_btn = st.button("🚀 Mulai Proses ETL", type="primary", use_container_width=True)

    if run_btn:
        with st.status("⏳ Memproses ETL...", expanded=True) as status:
            st.write("📥 Extract: Membaca file...")
            time.sleep(0.3)
            st.write("🔄 Transform: Membersihkan dan memetakan data...")
            time.sleep(0.3)
            st.write("💾 Load: Menyimpan ke database...")

            uploaded_file.seek(0)
            result = run_etl(uploaded_file, filename)

            if result.get("success"):
                status.update(label="✅ ETL Selesai!", state="complete")
            else:
                status.update(label="❌ ETL Gagal", state="error")

        if result.get("success"):
            st.balloons()
            st.markdown("---")
            st.markdown('<p class="section-header">📊 Hasil ETL</p>', unsafe_allow_html=True)

            r1, r2, r3, r4 = st.columns(4)
            r1.metric("📋 Total Record",         f"{result.get('total', 0):,}")
            r2.metric("✅ Berhasil Disimpan",    f"{result.get('inserted', 0):,}")
            r3.metric("⏭️ Dilewati (Duplikat)",  f"{result.get('skipped', 0):,}")
            r4.metric("❌ Gagal",                f"{result.get('failed', 0):,}")

            if result.get("errors"):
                with st.expander("⚠️ Detail Error"):
                    for err in result["errors"][:10]:
                        st.code(err)

            st.success(f"✅ ETL berhasil! **{result.get('inserted', 0):,}** record baru ditambahkan ke database.")
        else:
            st.error(f"❌ ETL Gagal: {result.get('error', 'Unknown error')}")

else:
    st.markdown("""
    <div class="custom-card" style="text-align:center; padding:48px 24px;">
        <div style="font-size:3rem; margin-bottom:12px;">📂</div>
        <div style="color:#9B7B75; font-size:1rem; font-weight:500;">Belum ada file yang diupload</div>
        <div style="color:#C4A99F; font-size:0.85rem; margin-top:6px;">
            Upload file Excel Work Order di atas untuk memulai
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── ETL Logs ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown('<p class="section-header">📋 Riwayat ETL Terakhir</p>', unsafe_allow_html=True)
try:
    from utils.queries import get_etl_logs
    logs = get_etl_logs(limit=10)
    if logs:
        df_logs = pd.DataFrame(logs)
        display_cols = ["id", "etl_name", "source_file", "status",
                        "total_records", "inserted_records", "skipped_records",
                        "duration_seconds", "started_at"]
        display_cols = [c for c in display_cols if c in df_logs.columns]
        st.dataframe(df_logs[display_cols], use_container_width=True, height=250)
    else:
        st.info("💡 Belum ada riwayat ETL.")
except Exception as e:
    st.info(f"💡 Riwayat ETL belum tersedia: {e}")