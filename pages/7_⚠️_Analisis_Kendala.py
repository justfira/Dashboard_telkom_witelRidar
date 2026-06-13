"""
Page 7: Analisis Kendala
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from utils.queries import get_kendala_top, get_kendala_kategori, get_filter_options
from utils.theme import get_theme_css, apply_plotly_defaults, COLORS, PALETTE

st.set_page_config(page_title="Analisis Kendala | BI Ridar", page_icon="⚠️", layout="wide")
st.markdown(get_theme_css(), unsafe_allow_html=True)

st.markdown("""
<div class="page-header">
    <div style="display:flex; align-items:center; gap:16px;">
        <div style="font-size:2.2rem;">⚠️</div>
        <div>
            <h1 style="margin:0; font-size:1.7rem; font-weight:800; color:#2C1810;">Analisis Kendala</h1>
            <p style="margin:4px 0 0 0; color:#9B7B75; font-size:0.9rem; font-weight:500;">
                Pareto Analysis — Identifikasi Akar Masalah Dominan
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
            default=opts["years"][:2] if len(opts["years"]) >= 2 else opts["years"], key="kend_tahun")
        sel_sto   = fc2.multiselect("🏢 STO", opts["stos"], key="kend_sto")
        top_n     = fc3.selectbox("🔢 Top Kendala", [10, 15, 20], key="kend_topn")
    filters = {}
    if sel_tahun: filters["tahun"] = sel_tahun
    if sel_sto:   filters["sto"]   = sel_sto
except Exception:
    filters = {}
    top_n   = 10

try:
    kendala_data  = get_kendala_top(filters, top_n=top_n)
    df            = pd.DataFrame(kendala_data)

    if df.empty:
        st.info("💡 Belum ada data. Upload file Excel via halaman Upload & ETL.")
    else:
        total_kendala = df["jumlah"].sum()
        top_kendala   = str(df.iloc[0]["kendala_pt1"]) if not df.empty else "-"

        c1, c2, c3 = st.columns(3)
        c1.metric("⚠️ Jenis Kendala Unik",    f"{len(df):,}")
        c2.metric("📋 Total Kejadian Kendala", f"{total_kendala:,}")
        c3.metric("🔴 Kendala Terbanyak",      top_kendala[:30] if len(top_kendala) > 30 else top_kendala)

        st.markdown("---")
        st.markdown(f'<p class="section-header">📊 Pareto Chart — Top {top_n} Kendala</p>', unsafe_allow_html=True)

        df = df.sort_values("jumlah", ascending=False)
        df["pct"]            = df["jumlah"] / df["jumlah"].sum() * 100
        df["cumulative_pct"] = df["pct"].cumsum()
        df["label"]          = df["kendala_pt1"].astype(str).str[:40]

        # gradient color dari primary ke warning
        n = len(df)
        bar_colors = [PALETTE[i % len(PALETTE)] for i in range(n)]

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df["label"], y=df["jumlah"],
            name="Jumlah Kendala",
            marker=dict(color=bar_colors, line=dict(width=0)),
            text=df["jumlah"],
            textposition="outside",
            yaxis="y",
            customdata=df["pct"],
            hovertemplate="<b>%{x}</b><br>Jumlah: %{y:,}<br>%{customdata:.1f}% dari total<extra></extra>"
        ))
        fig.add_trace(go.Scatter(
            x=df["label"], y=df["cumulative_pct"],
            name="Kumulatif (%)",
            mode="lines+markers",
            line=dict(color=COLORS["warning"], width=3),
            marker=dict(size=8, color=COLORS["warning"], line=dict(color="#fff", width=2)),
            yaxis="y2",
            hovertemplate="%{x}<br>Kumulatif: %{y:.1f}%<extra></extra>"
        ))
        fig.add_hline(y=80, line=dict(color=COLORS["success"], width=1.5, dash="dot"),
                      yref="y2",
                      annotation_text="80% (Pareto Rule)",
                      annotation_font=dict(color=COLORS["success"], size=10))
        apply_plotly_defaults(fig, height=480)
        fig.update_layout(
            xaxis=dict(tickangle=-35),
            yaxis=dict(title="Jumlah Kendala"),
            yaxis2=dict(title="Kumulatif (%)", overlaying="y", side="right",
                        range=[0, 110], tickformat=".0f"),
            legend=dict(orientation="h", y=-0.25),
            margin=dict(l=0, r=50, t=30, b=130),
            barmode="overlay"
        )
        st.plotly_chart(fig, use_container_width=True)

        # ── Kategori ROC ──────────────────────────────────────────────────────────
        try:
            kat_data  = get_kendala_kategori(filters)
            df_kat    = pd.DataFrame(kat_data)
            if not df_kat.empty:
                st.markdown("---")
                col_l, col_r = st.columns(2)

                with col_l:
                    st.markdown('<p class="section-header">🗂️ Kendala per Kategori ROC</p>', unsafe_allow_html=True)
                    fig_kat = go.Figure(go.Bar(
                        x=df_kat["kategori_roc"],
                        y=df_kat["jumlah"],
                        marker=dict(color=PALETTE[:len(df_kat)]),
                        text=df_kat["jumlah"],
                        textposition="outside",
                    ))
                    apply_plotly_defaults(fig_kat, height=350)
                    fig_kat.update_layout(
                        xaxis=dict(tickangle=-30),
                        yaxis=dict(title="Jumlah"),
                        showlegend=False,
                        margin=dict(l=0, r=0, t=10, b=90),
                    )
                    st.plotly_chart(fig_kat, use_container_width=True)

                with col_r:
                    st.markdown('<p class="section-header">🥧 Proporsi Kategori</p>', unsafe_allow_html=True)
                    fig_pie = go.Figure(go.Pie(
                        labels=df_kat["kategori_roc"],
                        values=df_kat["jumlah"],
                        hole=0.4,
                        marker=dict(colors=PALETTE[:len(df_kat)],
                                    line=dict(color="#fff", width=2)),
                        textinfo="percent+label",
                        textfont=dict(size=11),
                    ))
                    apply_plotly_defaults(fig_pie, height=350)
                    fig_pie.update_layout(showlegend=False)
                    st.plotly_chart(fig_pie, use_container_width=True)
        except Exception:
            pass

        # ── Table ─────────────────────────────────────────────────────────────────
        st.markdown("---")
        st.markdown('<p class="section-header">📋 Tabel Detail Kendala</p>', unsafe_allow_html=True)
        df_table = df[["kendala_pt1", "jumlah", "pct", "cumulative_pct"]].copy()
        df_table.columns = ["Kendala", "Jumlah", "Persentase (%)", "Kumulatif (%)"]
        df_table["Persentase (%)"] = df_table["Persentase (%)"].round(2)
        df_table["Kumulatif (%)"]  = df_table["Kumulatif (%)"].round(2)
        st.dataframe(df_table, use_container_width=True, height=300)

except Exception as e:
    if "no such table" in str(e).lower() or "doesn't exist" in str(e).lower():
        st.info("💡 Belum ada data. Upload file Excel via halaman Upload & ETL.")
    else:
        st.error(f"❌ Error: {e}")