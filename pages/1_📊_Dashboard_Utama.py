"""
Page 1: Dashboard Utama (Executive Summary)
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from utils.queries import get_kpi_summary, get_kpi_monthly_comparison, get_filter_options
from utils.theme import get_theme_css, apply_plotly_defaults, COLORS, PALETTE, GRID_COLOR

st.set_page_config(page_title="Dashboard Utama | BI Ridar", page_icon="📊", layout="wide")
st.markdown(get_theme_css(), unsafe_allow_html=True)

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
    <div style="display:flex; align-items:center; gap:16px;">
        <div style="font-size:2.2rem;">📊</div>
        <div>
            <h1 style="margin:0; font-size:1.7rem; font-weight:800; color:#2C1810;">Dashboard Utama</h1>
            <p style="margin:4px 0 0 0; color:#9B7B75; font-size:0.9rem; font-weight:500;">Executive Summary — Work Order Monitoring</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Filters ─────────────────────────────────────────────────────────────────────
try:
    opts = get_filter_options()
    with st.expander("🔽 Filter Data", expanded=False):
        fc1, fc2, fc3 = st.columns(3)
        sel_tahun = fc1.multiselect("📅 Tahun", opts["years"],
            default=opts["years"][:2] if len(opts["years"]) >= 2 else opts["years"])
        sel_sto   = fc2.multiselect("🏢 STO", opts["stos"])
        sel_status = fc3.multiselect("📌 Status WO", opts["statuses"])
    filters = {}
    if sel_tahun:  filters["tahun"]     = sel_tahun
    if sel_sto:    filters["sto"]       = sel_sto
    if sel_status: filters["status_wo"] = sel_status
except Exception as e:
    filters = {}
    st.warning(f"⚠️ Tidak dapat memuat filter: {e}")

# ── KPI Cards ──────────────────────────────────────────────────────────────────
try:
    kpi = get_kpi_summary(filters)
    total_wo    = int(kpi.get("total_wo", 0) or 0)
    wo_selesai  = int(kpi.get("wo_selesai", 0) or 0)
    sla_ok      = int(kpi.get("sla_tercapai", 0) or 0)
    work_fail   = int(kpi.get("work_fail", 0) or 0)
    avg_durasi  = float(kpi.get("avg_durasi", 0) or 0)
    unsc        = int(kpi.get("unsc", 0) or 0)
    jml_teknisi = int(kpi.get("jumlah_teknisi", 0) or 0)
    jml_sto     = int(kpi.get("jumlah_sto", 0) or 0)

    sla_pct     = (sla_ok / total_wo * 100)    if total_wo > 0 else 0
    wf_pct      = (work_fail / total_wo * 100)  if total_wo > 0 else 0
    selesai_pct = (wo_selesai / total_wo * 100) if total_wo > 0 else 0

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("📋 Total WO",      f"{total_wo:,}")
    c2.metric("✅ WO Selesai",    f"{wo_selesai:,}",   f"{selesai_pct:.1f}%")
    c3.metric("🎯 SLA Tercapai",  f"{sla_pct:.1f}%",   f"{sla_ok:,} WO")
    c4.metric("❌ Work Fail",     f"{wf_pct:.1f}%",    f"-{work_fail:,} WO", delta_color="inverse")
    c5.metric("⏱️ Avg Durasi",   f"{avg_durasi:.1f} Hari")

    st.markdown("<br>", unsafe_allow_html=True)
    c6, c7, c8 = st.columns(3)
    c6.metric("👨‍🔧 Jumlah Teknisi", f"{jml_teknisi:,}")
    c7.metric("🏢 Jumlah STO",      f"{jml_sto:,}")
    c8.metric("🚫 UNSC",            f"{unsc:,}",
              f"{(unsc/total_wo*100):.1f}%" if total_wo > 0 else "0%", delta_color="inverse")

except Exception as e:
    st.error(f"❌ Gagal memuat KPI: {e}")
    total_wo = 0
    sla_ok, sla_pct = 0, 0
    kpi = {}

st.markdown("---")

# ── Charts ──────────────────────────────────────────────────────────────────────
try:
    monthly   = get_kpi_monthly_comparison(filters)
    df_monthly = pd.DataFrame(monthly)

    if not df_monthly.empty and "bulan" in df_monthly.columns:
        df_monthly["label"] = df_monthly.apply(
            lambda r: f"{str(r.get('nama_bulan',''))[:3]} {r.get('tahun','')}", axis=1)

        col_left, col_right = st.columns([2, 1])

        with col_left:
            st.markdown('<p class="section-header">📈 Trend Work Order per Bulan</p>', unsafe_allow_html=True)
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df_monthly["label"], y=df_monthly["total_wo"],
                name="Total WO", mode="lines+markers",
                line=dict(color=COLORS["primary"], width=3),
                marker=dict(size=8, color=COLORS["primary"],
                            line=dict(width=2, color="#fff")),
                fill="tozeroy", fillcolor="rgba(210,79,60,0.08)"
            ))
            fig.add_trace(go.Scatter(
                x=df_monthly["label"], y=df_monthly["sla_ok"],
                name="SLA Tercapai", mode="lines+markers",
                line=dict(color=COLORS["success"], width=2, dash="dot"),
                marker=dict(size=6, color=COLORS["success"])
            ))
            fig.add_trace(go.Scatter(
                x=df_monthly["label"], y=df_monthly["work_fail"],
                name="Work Fail", mode="lines+markers",
                line=dict(color=COLORS["warning"], width=2),
                marker=dict(size=6, color=COLORS["warning"])
            ))
            apply_plotly_defaults(fig, height=320)
            fig.update_layout(
                legend=dict(orientation="h", y=-0.2, bgcolor="rgba(255,255,255,0.8)",
                            bordercolor="#F5C8BC", borderwidth=1),
                xaxis=dict(tickangle=-30),
            )
            st.plotly_chart(fig, use_container_width=True)

        with col_right:
            st.markdown('<p class="section-header">🎯 SLA Overview</p>', unsafe_allow_html=True)
            sla_not = max(total_wo - sla_ok, 0)
            fig_pie = go.Figure(data=[go.Pie(
                labels=["SLA Tercapai", "Belum Tercapai"],
                values=[sla_ok, sla_not],
                hole=0.6,
                marker=dict(colors=[COLORS["success"], COLORS["primary"]],
                            line=dict(color="#fff", width=2)),
                textinfo="percent+label",
                textfont=dict(size=11),
            )])
            fig_pie.add_annotation(
                text=f"<b>{sla_pct:.0f}%</b>",
                x=0.5, y=0.5,
                font=dict(size=28, color=COLORS["success"]),
                showarrow=False
            )
            apply_plotly_defaults(fig_pie, height=320)
            fig_pie.update_layout(showlegend=False)
            st.plotly_chart(fig_pie, use_container_width=True)

        # ── Bar chart ────────────────────────────────────────────────────────────
        st.markdown('<p class="section-header">📊 Work Order per Bulan (Detail)</p>', unsafe_allow_html=True)
        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(
            x=df_monthly["label"], y=df_monthly["total_wo"],
            name="Total WO", marker_color=COLORS["primary"],
            text=df_monthly["total_wo"], textposition="outside",
        ))
        fig_bar.add_trace(go.Bar(
            x=df_monthly["label"], y=df_monthly["sla_ok"],
            name="SLA Tercapai", marker_color=COLORS["success"],
        ))
        fig_bar.add_trace(go.Bar(
            x=df_monthly["label"], y=df_monthly["work_fail"],
            name="Work Fail", marker_color=COLORS["warning"],
        ))
        fig_bar.update_layout(barmode="group")
        apply_plotly_defaults(fig_bar, height=360)
        fig_bar.update_layout(
            xaxis=dict(tickangle=-30),
            legend=dict(orientation="h", y=-0.2),
        )
        st.plotly_chart(fig_bar, use_container_width=True)

except Exception as e:
    if "no such table" in str(e).lower() or "doesn't exist" in str(e).lower():
        st.info("💡 Belum ada data. Upload file Excel via halaman **Upload & ETL**.")
    else:
        st.error(f"❌ Error memuat chart: {e}")