"""
Page 10: Monitoring ETL
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from utils.queries import get_etl_logs, get_etl_summary
from utils.theme import get_theme_css, apply_plotly_defaults, COLORS

st.set_page_config(page_title="Monitoring ETL | BI Ridar", page_icon="🔄", layout="wide")
st.markdown(get_theme_css(), unsafe_allow_html=True)

st.markdown("""
<div class="page-header">
    <div style="display:flex; align-items:center; gap:16px;">
        <div style="font-size:2.2rem;">🔄</div>
        <div>
            <h1 style="margin:0; font-size:1.7rem; font-weight:800; color:#2C1810;">Monitoring ETL</h1>
            <p style="margin:4px 0 0 0; color:#9B7B75; font-size:0.9rem; font-weight:500;">Status & Riwayat Proses Extract-Transform-Load</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

col_btn, _ = st.columns([1, 5])
if col_btn.button("🔄 Refresh", type="primary"):
    st.rerun()

try:
    summary  = get_etl_summary()
    df_sum   = pd.DataFrame(summary)

    if not df_sum.empty:
        total_runs    = int(df_sum["total_runs"].sum())
        success_runs  = int(df_sum[df_sum["status"] == "success"]["total_runs"].sum()) if "success" in df_sum["status"].values else 0
        failed_runs   = int(df_sum[df_sum["status"] == "failed"]["total_runs"].sum())  if "failed"  in df_sum["status"].values else 0
        total_records = int(df_sum["total_records"].fillna(0).sum())
        total_inserted= int(df_sum["inserted"].fillna(0).sum())

        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("🔄 Total Runs",              f"{total_runs:,}")
        c2.metric("✅ Sukses",                  f"{success_runs:,}",
                  f"{success_runs/total_runs*100:.0f}%" if total_runs > 0 else "0%")
        c3.metric("❌ Gagal",                   f"{failed_runs:,}",
                  f"-{failed_runs/total_runs*100:.0f}%" if total_runs > 0 else "0%", delta_color="inverse")
        c4.metric("📋 Total Record Diproses",   f"{total_records:,}")
        c5.metric("💾 Total Inserted",          f"{total_inserted:,}")

        st.markdown("---")
        col_gauge, col_bar = st.columns([1, 2])

        with col_gauge:
            st.markdown('<p class="section-header">🎯 ETL Health</p>', unsafe_allow_html=True)
            success_rate = (success_runs / total_runs * 100) if total_runs > 0 else 0
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=success_rate,
                number={"suffix": "%", "font": {"size": 32, "color": COLORS["success"]}},
                delta={"reference": 90,
                       "increasing": {"color": COLORS["success"]},
                       "decreasing": {"color": COLORS["primary"]}},
                gauge={
                    "axis": {"range": [0, 100]},
                    "bar":  {"color": COLORS["success"], "thickness": 0.3},
                    "bgcolor": "rgba(0,0,0,0)", "borderwidth": 0,
                    "steps": [
                        {"range": [0, 50],   "color": "rgba(210,79,60,0.12)"},
                        {"range": [50, 85],  "color": "rgba(212,131,42,0.12)"},
                        {"range": [85, 100], "color": "rgba(74,155,111,0.12)"},
                    ],
                    "threshold": {"line": {"color": COLORS["accent"], "width": 2},
                                  "thickness": 0.8, "value": 90},
                },
                title={"text": "Success Rate", "font": {"color": COLORS["muted"], "size": 13}},
            ))
            apply_plotly_defaults(fig_gauge, height=260)
            st.plotly_chart(fig_gauge, use_container_width=True)

        with col_bar:
            st.markdown('<p class="section-header">📊 Distribusi Status ETL</p>', unsafe_allow_html=True)
            status_counts = df_sum.set_index("status")["total_runs"].to_dict()
            colors_map = {"success": COLORS["success"], "failed": COLORS["primary"], "running": COLORS["warning"]}
            fig_status = go.Figure(go.Bar(
                x=list(status_counts.keys()),
                y=list(status_counts.values()),
                marker=dict(color=[colors_map.get(k, COLORS["muted"]) for k in status_counts]),
                text=list(status_counts.values()),
                textposition="outside",
                width=0.4,
            ))
            apply_plotly_defaults(fig_status, height=260)
            fig_status.update_layout(yaxis=dict(title="Jumlah Run"))
            st.plotly_chart(fig_status, use_container_width=True)

    else:
        st.info("💡 Belum ada riwayat ETL. Upload file Excel untuk memulai.")

    # ── Log Table ────────────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown('<p class="section-header">📋 Riwayat ETL Detail</p>', unsafe_allow_html=True)

    logs = get_etl_logs(limit=50)
    if logs:
        df_logs = pd.DataFrame(logs)
        display_cols = {
            "id": "ID", "etl_name": "Nama ETL", "source_file": "File Sumber",
            "status": "Status", "total_records": "Total Record",
            "inserted_records": "Inserted", "skipped_records": "Skipped",
            "failed_records": "Failed", "duration_seconds": "Durasi (detik)",
            "started_at": "Mulai", "finished_at": "Selesai",
        }
        df_display = df_logs[[c for c in display_cols if c in df_logs.columns]].copy()
        df_display = df_display.rename(columns=display_cols)

        def highlight_status(val):
            v = str(val).lower()
            if v == "success": return "background-color:#E8F5EE; color:#2E7D4F; font-weight:600"
            if v == "failed":  return "background-color:#FEF0EE; color:#C0392B; font-weight:600"
            if v == "running": return "background-color:#FEF7E8; color:#D4832A; font-weight:600"
            return ""

        if "Status" in df_display.columns:
            st.dataframe(
                df_display.style.applymap(highlight_status, subset=["Status"]),
                use_container_width=True, height=400
            )
        else:
            st.dataframe(df_display, use_container_width=True, height=400)

        failed_logs = df_logs[df_logs["status"] == "failed"] if "status" in df_logs.columns else pd.DataFrame()
        if not failed_logs.empty:
            st.markdown("---")
            st.markdown('<p class="section-header">❌ Detail Error ETL Gagal</p>', unsafe_allow_html=True)
            for _, row in failed_logs.head(5).iterrows():
                with st.expander(f"ETL #{row.get('id')} — {row.get('etl_name','')} ({row.get('started_at','')})"):
                    st.code(row.get("error_message", "Tidak ada detail error"), language="text")
    else:
        st.info("💡 Belum ada riwayat ETL.")

    # ── DB Stats ─────────────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown('<p class="section-header">🗄️ Statistik Database</p>', unsafe_allow_html=True)
    try:
        from utils.db import run_query
        db_stats = run_query("""
            SELECT COUNT(*) AS total_records,
                   COUNT(DISTINCT sto) AS total_sto,
                   COUNT(DISTINCT nama_teknisi) AS total_teknisi,
                   MIN(tanggal) AS tanggal_awal,
                   MAX(tanggal) AS tanggal_akhir
            FROM workorders
        """)
        if db_stats:
            stats = db_stats[0]
            cs1, cs2, cs3, cs4 = st.columns(4)
            cs1.metric("📋 Total Record di DB", f"{int(stats.get('total_records', 0) or 0):,}")
            cs2.metric("🏢 Total STO",          f"{int(stats.get('total_sto', 0) or 0):,}")
            cs3.metric("👨‍🔧 Total Teknisi",   f"{int(stats.get('total_teknisi', 0) or 0):,}")
            date_range = f"{stats.get('tanggal_awal','-')} s/d {stats.get('tanggal_akhir','-')}"
            cs4.metric("📅 Rentang Data", str(date_range)[:22])
    except Exception as e:
        st.info(f"Tidak dapat mengambil statistik DB: {e}")

except Exception as e:
    if "no such table" in str(e).lower() or "doesn't exist" in str(e).lower():
        st.info("💡 Tabel ETL log belum ada. Upload file Excel untuk memulai.")
    else:
        st.error(f"❌ Error: {e}")