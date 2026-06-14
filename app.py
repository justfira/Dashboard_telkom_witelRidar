"""
Dashboard BI Monitoring Work Order Telkom Ridar
Main Entry Point
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
from utils.db import get_cached_engine, init_database
from utils.theme import get_theme_css

# ── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="BI Dashboard | Telkom Ridar",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Apply Global Theme ─────────────────────────────────────────────────────────
st.markdown(get_theme_css(), unsafe_allow_html=True)

# ── Database Init ──────────────────────────────────────────────────────────────
@st.cache_resource
def init_db():
    try:
        engine = get_cached_engine()
        with engine.connect() as conn:
            conn.execute(__import__("sqlalchemy").text(
                "CREATE DATABASE IF NOT EXISTS bi_support_telkom_ridar "
                "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            ))
            conn.commit()
        init_database()
        return True, None
    except Exception as e:
        return False, str(e)

db_ok, db_err = init_db()

# ── Sidebar Branding ───────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 20px 0 10px 0;">
        <div style="font-size: 2.5rem; margin-bottom: 8px;">📡</div>
        <div style="font-size: 1.1rem; font-weight: 800; color: #2C1810; letter-spacing: 1.5px;">TELKOM RIDAR</div>
        <div style="font-size: 0.7rem; color: #9B7B75; margin-top: 4px; font-weight: 600; letter-spacing: 1px;">BI MONITORING</div>
        <div style="height: 2px; background: #F5C8BC; margin: 16px 0;"></div>
    </div>
    """, unsafe_allow_html=True)

    if db_ok:
        st.markdown('<div style="text-align:center; padding: 10px; background: #E8F5E8; border-radius: 8px; color: #2E7D4F; font-size: 0.8rem; font-weight: 600;">🟢 Database Connected</div>', unsafe_allow_html=True)
    else:
        st.error(f"❌ DB Error: {db_err}")

# ── Landing Page ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header" style="text-align: center; border: none; background: transparent; box-shadow: none;">
    <div style="font-size: 3.5rem; margin-bottom: 10px;">📡</div>
    <h1 style="font-size: 2.5rem; font-weight: 800; color: #2C1810;">Selamat Datang di BI Dashboard</h1>
    <p style="color: #9B7B75; font-size: 1.1rem; margin-top: 10px;">Monitoring Work Order & Service Connectivity · Telkom Ridar</p>
</div>
""", unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

# Menggunakan class "custom-card" yang sudah kita definisikan di theme.py
cards = [
    ("📊", "Dashboard Utama", "Ringkasan KPI, SLA, Work Fail, dan Rata-rata durasi."),
    ("🔄", "Upload & ETL", "Upload file Excel/CSV, proses ETL, dan log monitoring."),
    ("📈", "Analisis Lengkap", "Trend, SLA, STO, Teknisi, Kendala, & Durasi."),
]

for col, (icon, title, desc) in zip([col1, col2, col3], cards):
    col.markdown(f"""
    <div class="custom-card" style="height: 200px; display: flex; flex-direction: column; align-items: center; justify-content: center;">
        <div style="font-size: 2.5rem; margin-bottom: 15px;">{icon}</div>
        <div style="font-weight: 800; font-size: 1.1rem; color: #2C1810; margin-bottom: 10px;">{title}</div>
        <div style="color: #4A2C20; font-size: 0.9rem; text-align: center; padding: 0 10px;">{desc}</div>
    </div>
    """, unsafe_allow_html=True)

# ── Quick Stats ────────────────────────────────────────────────────────────────
if db_ok:
    try:
        from utils.queries import get_kpi_summary
        kpi = get_kpi_summary()
        if kpi and kpi.get("total_wo"):
            st.markdown("<br><br><br>", unsafe_allow_html=True)
            st.markdown('<p class="section-header">📊 Ringkasan Data Saat Ini</p>', unsafe_allow_html=True)
            
            # Menggunakan component metric bawaan Streamlit agar lebih rapi
            c1, c2, c3, c4, c5 = st.columns(5)
            total = int(kpi.get("total_wo", 0) or 0)
            c1.metric("Total WO", f"{total:,}")
            c2.metric("WO Selesai", f"{int(kpi.get('wo_selesai', 0) or 0):,}")
            c3.metric("SLA Tercapai", f"{((kpi.get('sla_tercapai', 0) or 0) / max(total, 1) * 100):.1f}%")
            c4.metric("Work Fail", f"{((kpi.get('work_fail', 0) or 0) / max(total, 1) * 100):.1f}%")
            c5.metric("Avg Durasi", f"{kpi.get('avg_durasi', 0) or 0:.1f} Hari")
    except Exception:
        pass