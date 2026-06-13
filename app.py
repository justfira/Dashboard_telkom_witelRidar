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
        <div style="font-size: 2.2rem; margin-bottom: 6px;">📡</div>
        <div style="font-size: 1rem; font-weight: 800; color: #2C1810;
            letter-spacing: 1.5px;">TELKOM RIDAR</div>
        <div style="font-size: 0.68rem; color: #9B7B75; margin-top: 4px;
            font-weight: 500; letter-spacing: 0.5px;">BI MONITORING DASHBOARD</div>
        <div style="height: 2px; background: linear-gradient(90deg, transparent, #D24F3C, transparent);
            margin: 14px 0;"></div>
    </div>
    """, unsafe_allow_html=True)

    # DB Status
    if db_ok:
        st.markdown(
            '<div style="text-align:center;">'
            '<span class="kpi-badge-green">🟢 Database Connected</span>'
            '</div>',
            unsafe_allow_html=True
        )
    else:
        st.error(f"❌ DB Error: {db_err}")

    st.markdown("<br>", unsafe_allow_html=True)

# ── Landing Page ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header" style="text-align: center;">
    <div style="font-size: 3rem; margin-bottom: 10px;">📡</div>
    <h1 style="font-size: 2rem; font-weight: 800; margin: 0; color: #2C1810;">
        Dashboard BI Monitoring
    </h1>
    <p style="color: #9B7B75; font-size: 1rem; margin-top: 8px; font-weight: 500;">
        Work Order & Service Connectivity · Telkom Ridar
    </p>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

cards = [
    ("📊", "Dashboard Utama",
     "KPI ringkasan, total WO, SLA, Work Fail, rata-rata durasi"),
    ("🔄", "Upload & ETL",
     "Upload Excel/CSV, proses ETL otomatis, monitoring log"),
    ("📈", "Analisis Lengkap",
     "Trend, SLA, STO, Teknisi, Kendala, Infrastruktur, Durasi"),
]
for col, (icon, title, desc) in zip([col1, col2, col3], cards):
    col.markdown(f"""
    <div class="custom-card" style="text-align: center;">
        <div style="font-size: 2rem; margin-bottom: 10px;">{icon}</div>
        <div style="font-weight: 700; font-size: 1rem; color: #2C1810;
            margin-bottom: 8px;">{title}</div>
        <div style="color: #9B7B75; font-size: 0.85rem; line-height: 1.5;">{desc}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align: center; color: #9B7B75; font-size: 0.88rem;">
    👈 <strong style="color: #D24F3C;">Gunakan menu di sidebar</strong>
    untuk navigasi antar halaman
</div>
""", unsafe_allow_html=True)

# ── Quick Stats ────────────────────────────────────────────────────────────────
if db_ok:
    try:
        from utils.queries import get_kpi_summary
        kpi = get_kpi_summary()
        if kpi and kpi.get("total_wo"):
            st.markdown("---")
            st.markdown(
                '<p class="section-header">📊 Ringkasan Cepat</p>',
                unsafe_allow_html=True
            )
            c1, c2, c3, c4, c5 = st.columns(5)
            total_wo = int(kpi.get("total_wo", 0) or 0)
            wo_selesai = int(kpi.get("wo_selesai", 0) or 0)
            sla_pct = (kpi.get("sla_tercapai", 0) or 0) / max(total_wo, 1) * 100
            wf_pct  = (kpi.get("work_fail", 0) or 0) / max(total_wo, 1) * 100
            c1.metric("📋 Total WO", f"{total_wo:,}")
            c2.metric("✅ WO Selesai", f"{wo_selesai:,}")
            c3.metric("🎯 SLA Tercapai", f"{sla_pct:.1f}%")
            c4.metric("❌ Work Fail", f"{wf_pct:.1f}%")
            c5.metric("⏱️ Avg Durasi", f"{kpi.get('avg_durasi', 0) or 0:.1f} Hari")
    except Exception:
        pass
