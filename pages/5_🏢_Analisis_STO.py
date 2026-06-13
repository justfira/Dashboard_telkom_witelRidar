"""
Page 5: Analisis STO
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from utils.queries import get_wo_per_sto, get_filter_options
from utils.theme import get_theme_css, apply_plotly_defaults, COLORS

st.set_page_config(page_title="Analisis STO | BI Ridar", page_icon="🏢", layout="wide")
st.markdown(get_theme_css(), unsafe_allow_html=True)

st.markdown("""
<div class="page-header">
    <div style="display:flex; align-items:center; gap:16px;">
        <div style="font-size:2.2rem;">🏢</div>
        <div>
            <h1 style="margin:0; font-size:1.7rem; font-weight:800; color:#2C1810;">Analisis STO</h1>
            <p style="margin:4px 0 0 0; color:#9B7B75; font-size:0.9rem; font-weight:500;">
                Performa Work Order per Sentral Telepon Otomat
            </p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Filters ─────────────────────────────────────────────────────────────────────
try:
    opts = get_filter_options()
    with st.expander("🔽 Filter Data", expanded=False):
        fc1, fc2 = st.columns(2)
        sel_tahun  = fc1.multiselect("📅 Tahun", opts["years"],
            default=opts["years"][:2] if len(opts["years"]) >= 2 else opts["years"], key="sto_tahun")
        sel_status = fc2.multiselect("📌 Status WO", opts["statuses"], key="sto_status")
    filters = {}
    if sel_tahun:  filters["tahun"]     = sel_tahun
    if sel_status: filters["status_wo"] = sel_status
except Exception:
    filters = {}

try:
    sto_data = get_wo_per_sto(filters)
    df       = pd.DataFrame(sto_data)

    if df.empty:
        st.info("💡 Belum ada data. Upload file Excel via halaman Upload & ETL.")
    else:
        # ── KPI ──────────────────────────────────────────────────────────────────
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("🏢 Total STO",    f"{len(df):,}")
        c2.metric("📋 Total WO",     f"{df['total_wo'].sum():,}")
        best_sto  = df.nlargest(1, "pct_sla")["sto"].values[0]  if not df.empty else "-"
        worst_sto = df.nsmallest(1, "pct_sla")["sto"].values[0] if not df.empty else "-"
        c3.metric("🏆 STO Terbaik",  best_sto)
        c4.metric("⚠️ STO Terburuk", worst_sto)

        st.markdown("---")

        # ── Total WO per STO ──────────────────────────────────────────────────────
        st.markdown('<p class="section-header">📊 Total Work Order per STO</p>', unsafe_allow_html=True)
        df_sorted  = df.sort_values("total_wo", ascending=False)
        colors_wo  = [COLORS["primary"] if i < 3 else COLORS["info"] if i < 10 else COLORS["muted"]
                      for i in range(len(df_sorted))]
        fig_wo = go.Figure(go.Bar(
            x=df_sorted["sto"],
            y=df_sorted["total_wo"],
            marker=dict(color=colors_wo, line=dict(width=0)),
            text=df_sorted["total_wo"],
            textposition="outside",
            hovertemplate="<b>%{x}</b><br>Total WO: %{y:,}<extra></extra>"
        ))
        apply_plotly_defaults(fig_wo, height=380)
        fig_wo.update_layout(
            xaxis=dict(tickangle=-45),
            yaxis=dict(title="Jumlah WO"),
            showlegend=False,
            margin=dict(l=0, r=0, t=30, b=90),
        )
        st.plotly_chart(fig_wo, use_container_width=True)

        st.markdown("---")
        left, right = st.columns(2)

        # ── SLA per STO ───────────────────────────────────────────────────────────
        with left:
            st.markdown('<p class="section-header">🎯 SLA Rate per STO</p>', unsafe_allow_html=True)
            df_sla    = df.sort_values("pct_sla", ascending=True)
            colors_sla = [COLORS["success"] if v >= 85 else COLORS["warning"] if v >= 70 else COLORS["primary"]
                          for v in df_sla["pct_sla"]]
            fig_sla = go.Figure(go.Bar(
                y=df_sla["sto"], x=df_sla["pct_sla"],
                orientation="h",
                marker=dict(color=colors_sla),
                text=[f"{v:.0f}%" for v in df_sla["pct_sla"]],
                textposition="outside",
            ))
            fig_sla.add_vline(x=85, line=dict(color=COLORS["accent"], width=1.5, dash="dot"),
                              annotation_text="Target 85%",
                              annotation_font=dict(color=COLORS["accent"], size=10))
            apply_plotly_defaults(fig_sla, height=460)
            fig_sla.update_layout(
                xaxis=dict(range=[0, 115], title="SLA (%)"),
                showlegend=False,
            )
            st.plotly_chart(fig_sla, use_container_width=True)

        # ── Work Fail per STO ─────────────────────────────────────────────────────
        with right:
            st.markdown('<p class="section-header">❌ Work Fail per STO</p>', unsafe_allow_html=True)
            df_wf      = df.sort_values("work_fail", ascending=False).head(20)
            colors_wf  = [COLORS["primary"] if v > 10 else COLORS["warning"] if v > 5 else COLORS["success"]
                          for v in df_wf["work_fail"]]
            fig_wf = go.Figure(go.Bar(
                x=df_wf["sto"], y=df_wf["work_fail"],
                marker=dict(color=colors_wf),
                text=df_wf["work_fail"],
                textposition="outside",
            ))
            apply_plotly_defaults(fig_wf, height=460)
            fig_wf.update_layout(
                xaxis=dict(tickangle=-45),
                yaxis=dict(title="Jumlah Work Fail"),
                showlegend=False,
                margin=dict(l=0, r=0, t=10, b=90),
            )
            st.plotly_chart(fig_wf, use_container_width=True)

        # ── Scatter ───────────────────────────────────────────────────────────────
        st.markdown("---")
        st.markdown('<p class="section-header">🔵 Pemetaan STO: Volume WO vs SLA Rate</p>', unsafe_allow_html=True)
        fig_sc = go.Figure(go.Scatter(
            x=df["total_wo"], y=df["pct_sla"],
            mode="markers+text",
            text=df["sto"],
            textposition="top center",
            textfont=dict(size=9),
            marker=dict(
                size=df["work_fail"].clip(5, 50) + 8,
                color=df["pct_sla"],
                colorscale=[[0, COLORS["primary"]], [0.5, COLORS["warning"]], [1, COLORS["success"]]],
                showscale=True,
                colorbar=dict(title="SLA %"),
                line=dict(color="#fff", width=1)
            ),
            hovertemplate="<b>%{text}</b><br>WO: %{x:,}<br>SLA: %{y:.1f}%<extra></extra>"
        ))
        fig_sc.add_hline(y=85, line=dict(color=COLORS["accent"], width=1.5, dash="dot"),
                         annotation_text="Target SLA 85%",
                         annotation_font=dict(color=COLORS["accent"], size=10))
        apply_plotly_defaults(fig_sc, height=400)
        fig_sc.update_layout(
            xaxis=dict(title="Total WO"),
            yaxis=dict(title="SLA Rate (%)"),
        )
        st.plotly_chart(fig_sc, use_container_width=True)

        # ── Table ─────────────────────────────────────────────────────────────────
        st.markdown("---")
        st.markdown('<p class="section-header">📋 Data Lengkap per STO</p>', unsafe_allow_html=True)
        df_display = df.copy()
        df_display.columns = ["STO", "Total WO", "SLA OK", "Work Fail", "Avg Durasi (Hari)", "SLA Rate (%)"]
        st.dataframe(
            df_display.sort_values("Total WO", ascending=False),
            use_container_width=True, height=350
        )

except Exception as e:
    if "no such table" in str(e).lower() or "doesn't exist" in str(e).lower():
        st.info("💡 Belum ada data. Upload file Excel via halaman Upload & ETL.")
    else:
        st.error(f"❌ Error: {e}")