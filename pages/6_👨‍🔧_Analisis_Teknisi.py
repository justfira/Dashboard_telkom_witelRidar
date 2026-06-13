"""
Page 6: Analisis Teknisi
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from utils.queries import get_teknisi_performance, get_filter_options
from utils.theme import get_theme_css, apply_plotly_defaults, COLORS

st.set_page_config(page_title="Analisis Teknisi | BI Ridar", page_icon="👨‍🔧", layout="wide")
st.markdown(get_theme_css(), unsafe_allow_html=True)

st.markdown("""
<div class="page-header">
    <div style="display:flex; align-items:center; gap:16px;">
        <div style="font-size:2.2rem;">👨‍🔧</div>
        <div>
            <h1 style="margin:0; font-size:1.7rem; font-weight:800; color:#2C1810;">Analisis Teknisi</h1>
            <p style="margin:4px 0 0 0; color:#9B7B75; font-size:0.9rem; font-weight:500;">
                Produktivitas & Performa Teknisi Lapangan
            </p>
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
            default=opts["years"][:2] if len(opts["years"]) >= 2 else opts["years"], key="tek_tahun")
        sel_sto   = fc2.multiselect("🏢 STO", opts["stos"], key="tek_sto")
        top_n     = fc3.selectbox("🔢 Tampilkan Top N", [10, 20, 30], key="tek_topn")
    filters = {}
    if sel_tahun: filters["tahun"] = sel_tahun
    if sel_sto:   filters["sto"]   = sel_sto
except Exception:
    filters = {}
    top_n   = 20

try:
    tek_data = get_teknisi_performance(filters)
    df       = pd.DataFrame(tek_data)

    if df.empty:
        st.info("💡 Belum ada data. Upload file Excel via halaman Upload & ETL.")
    else:
        df = df.head(top_n)

        # ── KPI ──────────────────────────────────────────────────────────────────
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("👨‍🔧 Total Teknisi",       f"{len(df):,}")
        c2.metric("📋 Total WO Dikerjakan",    f"{df['total_wo'].sum():,}")
        best_tek = df.nlargest(1, "total_wo")["nama_teknisi"].values[0] if not df.empty else "-"
        c3.metric("🏆 Teknisi Teraktif",       str(best_tek)[:22])
        c4.metric("🎯 Avg SLA Rate",           f"{df['pct_sla'].mean():.1f}%")

        st.markdown("---")

        df_sorted = df.sort_values("total_wo", ascending=True).tail(top_n)
        col_left, col_right = st.columns(2)

        # ── Jumlah WO ─────────────────────────────────────────────────────────────
        with col_left:
            st.markdown('<p class="section-header">📊 Jumlah WO per Teknisi</p>', unsafe_allow_html=True)
            colors_wo = [
                COLORS["primary"] if i >= len(df_sorted) - 3 else
                COLORS["info"]    if i >= len(df_sorted) - 10 else COLORS["muted"]
                for i in range(len(df_sorted))
            ]
            fig_wo = go.Figure(go.Bar(
                y=df_sorted["nama_teknisi"],
                x=df_sorted["total_wo"],
                orientation="h",
                marker=dict(color=colors_wo, line=dict(width=0)),
                text=df_sorted["total_wo"],
                textposition="outside",
                customdata=df_sorted[["mitra", "pct_sla"]].values,
                hovertemplate="<b>%{y}</b><br>WO: %{x:,}<br>Mitra: %{customdata[0]}<br>SLA: %{customdata[1]:.1f}%<extra></extra>"
            ))
            apply_plotly_defaults(fig_wo, height=560)
            fig_wo.update_layout(
                xaxis=dict(title="Jumlah WO"),
                showlegend=False,
                margin=dict(l=0, r=60, t=10, b=0),
            )
            st.plotly_chart(fig_wo, use_container_width=True)

        # ── SLA Rate ──────────────────────────────────────────────────────────────
        with col_right:
            st.markdown('<p class="section-header">🎯 SLA Rate per Teknisi</p>', unsafe_allow_html=True)
            df_sla    = df.sort_values("pct_sla", ascending=True).tail(top_n)
            colors_sla = [COLORS["success"] if v >= 85 else COLORS["warning"] if v >= 70 else COLORS["primary"]
                          for v in df_sla["pct_sla"]]
            fig_sla = go.Figure(go.Bar(
                y=df_sla["nama_teknisi"],
                x=df_sla["pct_sla"],
                orientation="h",
                marker=dict(color=colors_sla),
                text=[f"{v:.0f}%" for v in df_sla["pct_sla"]],
                textposition="outside",
            ))
            fig_sla.add_vline(x=85, line=dict(color=COLORS["accent"], width=1.5, dash="dot"),
                              annotation_text="Target 85%",
                              annotation_font=dict(color=COLORS["accent"], size=9))
            apply_plotly_defaults(fig_sla, height=560)
            fig_sla.update_layout(
                xaxis=dict(range=[0, 115], title="SLA Rate (%)"),
                showlegend=False,
                margin=dict(l=0, r=60, t=10, b=0),
            )
            st.plotly_chart(fig_sla, use_container_width=True)

        # ── Avg Durasi ────────────────────────────────────────────────────────────
        st.markdown("---")
        st.markdown('<p class="section-header">⏱️ Rata-rata Durasi per Teknisi (Hari)</p>', unsafe_allow_html=True)
        df_dur    = df.sort_values("avg_durasi", ascending=False).head(20)
        colors_dur = [COLORS["primary"] if v > 7 else COLORS["warning"] if v > 3 else COLORS["success"]
                      for v in df_dur["avg_durasi"]]
        fig_dur = go.Figure(go.Bar(
            x=df_dur["nama_teknisi"],
            y=df_dur["avg_durasi"],
            marker=dict(color=colors_dur),
            text=[f"{v:.1f}" for v in df_dur["avg_durasi"]],
            textposition="outside",
        ))
        fig_dur.add_hline(y=3, line=dict(color=COLORS["success"], width=1.5, dash="dot"),
                          annotation_text="SLA 3 Hari",
                          annotation_font=dict(color=COLORS["success"], size=10))
        apply_plotly_defaults(fig_dur, height=380)
        fig_dur.update_layout(
            xaxis=dict(tickangle=-45),
            yaxis=dict(title="Hari"),
            showlegend=False,
            margin=dict(l=0, r=0, t=30, b=110),
        )
        st.plotly_chart(fig_dur, use_container_width=True)

        # ── Bubble Chart ──────────────────────────────────────────────────────────
        st.markdown("---")
        st.markdown('<p class="section-header">🔵 Pemetaan Teknisi: WO vs SLA vs Durasi</p>', unsafe_allow_html=True)
        fig_bub = go.Figure(go.Scatter(
            x=df["total_wo"],
            y=df["pct_sla"],
            mode="markers+text",
            text=df["nama_teknisi"].str[:15],
            textposition="top center",
            textfont=dict(size=8),
            marker=dict(
                size=df["avg_durasi"].clip(2, 20) * 3 + 10,
                color=df["avg_durasi"],
                colorscale=[[0, COLORS["success"]], [0.5, COLORS["warning"]], [1, COLORS["primary"]]],
                showscale=True,
                colorbar=dict(title="Avg Durasi (Hari)"),
                line=dict(color="#fff", width=1)
            ),
            hovertemplate="<b>%{text}</b><br>WO: %{x:,}<br>SLA: %{y:.1f}%<extra></extra>"
        ))
        fig_bub.add_hline(y=85, line=dict(color=COLORS["accent"], width=1.5, dash="dot"),
                          annotation_text="Target SLA 85%",
                          annotation_font=dict(color=COLORS["accent"], size=10))
        apply_plotly_defaults(fig_bub, height=450)
        fig_bub.update_layout(
            xaxis=dict(title="Total WO"),
            yaxis=dict(title="SLA Rate (%)"),
        )
        st.plotly_chart(fig_bub, use_container_width=True)

        # ── Table ─────────────────────────────────────────────────────────────────
        st.markdown("---")
        st.markdown('<p class="section-header">📋 Data Lengkap Teknisi</p>', unsafe_allow_html=True)
        df_display = df[["nama_teknisi", "mitra", "total_wo", "pct_sla", "avg_durasi", "work_fail"]].copy()
        df_display.columns = ["Nama Teknisi", "Mitra", "Total WO", "SLA Rate (%)", "Avg Durasi (Hari)", "Work Fail"]
        st.dataframe(
            df_display.sort_values("Total WO", ascending=False),
            use_container_width=True, height=350
        )

except Exception as e:
    if "no such table" in str(e).lower() or "doesn't exist" in str(e).lower():
        st.info("💡 Belum ada data. Upload file Excel via halaman Upload & ETL.")
    else:
        st.error(f"❌ Error: {e}")