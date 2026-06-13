"""
Page 3: Trend Work Order
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from utils.queries import get_trend_monthly, get_trend_weekly, get_filter_options
from utils.theme import get_theme_css, apply_plotly_defaults, COLORS

st.set_page_config(page_title="Trend WO | BI Ridar", page_icon="📈", layout="wide")
st.markdown(get_theme_css(), unsafe_allow_html=True)

st.markdown("""
<div class="page-header">
    <div style="display:flex; align-items:center; gap:16px;">
        <div style="font-size:2.2rem;">📈</div>
        <div>
            <h1 style="margin:0; font-size:1.7rem; font-weight:800; color:#2C1810;">Trend Work Order</h1>
            <p style="margin:4px 0 0 0; color:#9B7B75; font-size:0.9rem; font-weight:500;">Analisis tren WO per bulan dan minggu</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Filters ─────────────────────────────────────────────────────────────────────
try:
    opts = get_filter_options()
    with st.expander("🔽 Filter Data", expanded=False):
        fc1, fc2, fc3 = st.columns(3)
        sel_tahun   = fc1.multiselect("📅 Tahun", opts["years"],
            default=opts["years"][:2] if len(opts["years"]) >= 2 else opts["years"], key="trend_tahun")
        sel_sto     = fc2.multiselect("🏢 STO", opts["stos"], key="trend_sto")
        sel_segment = fc3.multiselect("👤 Segment", opts["segments"], key="trend_segment")
    filters = {}
    if sel_tahun:   filters["tahun"]   = sel_tahun
    if sel_sto:     filters["sto"]     = sel_sto
    if sel_segment: filters["segment"] = sel_segment
except Exception:
    filters = {}

# ── Monthly Trend ───────────────────────────────────────────────────────────────
try:
    monthly  = get_trend_monthly(filters)
    df_m     = pd.DataFrame(monthly)

    if df_m.empty:
        st.info("💡 Belum ada data. Upload file Excel terlebih dahulu.")
    else:
        df_m["label"] = df_m.apply(
            lambda r: f"{str(r.get('nama_bulan',''))[:3]} {r.get('tahun','')}", axis=1)

        c1, c2, c3, c4 = st.columns(4)
        total = df_m["total_wo"].sum()
        sla_pct = df_m["sla_ok"].sum() / total * 100 if total > 0 else 0
        c1.metric("📋 Total WO",      f"{total:,}")
        c2.metric("🎯 SLA Tercapai",  f"{df_m['sla_ok'].sum():,}")
        c3.metric("❌ Work Fail",     f"{df_m['work_fail'].sum():,}")
        c4.metric("📊 SLA Rate",      f"{sla_pct:.1f}%")

        st.markdown("---")

        # ── Line Chart ──────────────────────────────────────────────────────────
        st.markdown('<p class="section-header">📈 Trend WO per Bulan</p>', unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_m["label"], y=df_m["total_wo"],
            name="Total WO", mode="lines+markers+text",
            text=df_m["total_wo"], textposition="top center",
            textfont=dict(color=COLORS["primary"], size=10),
            line=dict(color=COLORS["primary"], width=3),
            marker=dict(size=10, color=COLORS["primary"], line=dict(width=2, color="#fff"))
        ))
        fig.add_trace(go.Scatter(
            x=df_m["label"], y=df_m["sla_ok"],
            name="SLA Tercapai", mode="lines+markers",
            line=dict(color=COLORS["success"], width=2, dash="dot"),
            marker=dict(size=8, color=COLORS["success"])
        ))
        fig.add_trace(go.Scatter(
            x=df_m["label"], y=df_m["work_fail"],
            name="Work Fail", mode="lines+markers",
            line=dict(color=COLORS["warning"], width=2),
            marker=dict(size=8, color=COLORS["warning"]),
            fill="tozeroy", fillcolor="rgba(212,131,42,0.06)"
        ))
        apply_plotly_defaults(fig, height=400)
        fig.update_layout(
            xaxis=dict(tickangle=-30, title="Bulan"),
            yaxis=dict(title="Jumlah WO"),
            legend=dict(orientation="h", y=-0.2),
            hovermode="x unified"
        )
        st.plotly_chart(fig, use_container_width=True)

        # ── Stacked Bar ─────────────────────────────────────────────────────────
        st.markdown('<p class="section-header">📊 Proporsi Status per Bulan</p>', unsafe_allow_html=True)
        sla_not = (df_m["total_wo"] - df_m["sla_ok"] - df_m["work_fail"]).clip(0)
        fig_area = go.Figure()
        fig_area.add_trace(go.Bar(x=df_m["label"], y=df_m["sla_ok"],
            name="SLA OK", marker_color=COLORS["success"]))
        fig_area.add_trace(go.Bar(x=df_m["label"], y=df_m["work_fail"],
            name="Work Fail", marker_color=COLORS["primary"]))
        fig_area.add_trace(go.Bar(x=df_m["label"], y=sla_not,
            name="Proses / Lainnya", marker_color=COLORS["info"]))
        fig_area.update_layout(barmode="stack")
        apply_plotly_defaults(fig_area, height=360)
        fig_area.update_layout(xaxis=dict(tickangle=-30), legend=dict(orientation="h", y=-0.2))
        st.plotly_chart(fig_area, use_container_width=True)

        # ── Table ────────────────────────────────────────────────────────────────
        st.markdown('<p class="section-header">📋 Data Trend Bulanan</p>', unsafe_allow_html=True)
        df_display = df_m[["label", "total_wo", "sla_ok", "work_fail"]].copy()
        df_display.columns = ["Periode", "Total WO", "SLA Tercapai", "Work Fail"]
        df_display["SLA Rate (%)"] = (df_display["SLA Tercapai"] / df_display["Total WO"] * 100).round(1)
        df_display["WF Rate (%)"]  = (df_display["Work Fail"]    / df_display["Total WO"] * 100).round(1)
        st.dataframe(df_display, use_container_width=True, height=300)

except Exception as e:
    if "no such table" in str(e).lower() or "doesn't exist" in str(e).lower():
        st.info("💡 Belum ada data. Upload file Excel via halaman **Upload & ETL**.")
    else:
        st.error(f"❌ Error: {e}")

# ── Weekly Trend ────────────────────────────────────────────────────────────────
try:
    weekly = get_trend_weekly(filters)
    df_w   = pd.DataFrame(weekly)
    if not df_w.empty:
        st.markdown("---")
        st.markdown('<p class="section-header">📅 Trend WO per Minggu</p>', unsafe_allow_html=True)
        df_w["label"] = df_w.apply(
            lambda r: f"W{r.get('minggu','')}/{r.get('tahun','')}", axis=1)

        fig_w = go.Figure()
        fig_w.add_trace(go.Scatter(
            x=df_w["label"], y=df_w["total_wo"],
            name="Total WO", mode="lines+markers",
            line=dict(color=COLORS["purple"], width=2),
            marker=dict(size=7, color=COLORS["purple"]),
            fill="tozeroy", fillcolor="rgba(139,92,246,0.08)"
        ))
        fig_w.add_trace(go.Scatter(
            x=df_w["label"], y=df_w["sla_ok"],
            name="SLA Tercapai", mode="lines",
            line=dict(color=COLORS["success"], width=2, dash="dot")
        ))
        apply_plotly_defaults(fig_w, height=350)
        fig_w.update_layout(
            xaxis=dict(tickangle=-45, nticks=20, title="Minggu"),
            yaxis=dict(title="Jumlah WO"),
            legend=dict(orientation="h", y=-0.2),
            hovermode="x unified"
        )
        st.plotly_chart(fig_w, use_container_width=True)
except Exception:
    pass