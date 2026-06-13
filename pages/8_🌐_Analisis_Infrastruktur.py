"""
Page 8: Analisis Infrastruktur
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from utils.queries import get_infrastruktur_stats, get_filter_options, _build_where
from utils.db import run_query
from utils.theme import get_theme_css, apply_plotly_defaults, COLORS, PALETTE

st.set_page_config(page_title="Analisis Infrastruktur | BI Ridar", page_icon="🌐", layout="wide")
st.markdown(get_theme_css(), unsafe_allow_html=True)

st.markdown("""
<div class="page-header">
    <div style="display:flex; align-items:center; gap:16px;">
        <div style="font-size:2.2rem;">🌐</div>
        <div>
            <h1 style="margin:0; font-size:1.7rem; font-weight:800; color:#2C1810;">Analisis Infrastruktur</h1>
            <p style="margin:4px 0 0 0; color:#9B7B75; font-size:0.9rem; font-weight:500;">
                Distribusi Penggunaan Infrastruktur Jaringan — FTTH, GPON, ODP, OLT
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
        sel_tahun = fc1.multiselect("📅 Tahun", opts["years"],
            default=opts["years"][:2] if len(opts["years"]) >= 2 else opts["years"], key="infra_tahun")
        sel_sto   = fc2.multiselect("🏢 STO", opts["stos"], key="infra_sto")
    filters = {}
    if sel_tahun: filters["tahun"] = sel_tahun
    if sel_sto:   filters["sto"]   = sel_sto
except Exception:
    filters = {}

INFRA_COLORS = {
    "ODP": COLORS["primary"], "ODC": COLORS["warning"],
    "GPON": COLORS["info"],   "Feeder": COLORS["purple"],
    "Distribusi": COLORS["success"],
}

try:
    infra_data = get_infrastruktur_stats(filters)
    df_infra   = pd.DataFrame(infra_data)

    if df_infra.empty:
        st.info("💡 Belum ada data. Upload file Excel via halaman Upload & ETL.")
    else:
        # ── KPI ──────────────────────────────────────────────────────────────────
        cols = st.columns(len(df_infra))
        for i, (_, row) in enumerate(df_infra.iterrows()):
            cols[i].metric(f"🔌 {row['infra']}", f"{int(row['jumlah']):,}")

        st.markdown("---")

        # ── Bar Chart ─────────────────────────────────────────────────────────────
        st.markdown('<p class="section-header">📊 Jumlah WO per Infrastruktur</p>', unsafe_allow_html=True)
        colors_list = [INFRA_COLORS.get(r["infra"], COLORS["muted"]) for _, r in df_infra.iterrows()]
        fig_bar = go.Figure(go.Bar(
            x=df_infra["infra"],
            y=df_infra["jumlah"],
            marker=dict(color=colors_list, line=dict(width=0)),
            text=df_infra["jumlah"],
            textposition="outside",
            width=0.5,
        ))
        apply_plotly_defaults(fig_bar, height=380)
        fig_bar.update_layout(
            yaxis=dict(title="Jumlah Record"),
            showlegend=False,
            margin=dict(l=0, r=0, t=30, b=20),
        )
        st.plotly_chart(fig_bar, use_container_width=True)

        st.markdown("---")
        col_l, col_r = st.columns(2)

        # ── Pie Chart ─────────────────────────────────────────────────────────────
        with col_l:
            st.markdown('<p class="section-header">🥧 Proporsi Infrastruktur</p>', unsafe_allow_html=True)
            fig_pie = go.Figure(go.Pie(
                labels=df_infra["infra"],
                values=df_infra["jumlah"],
                hole=0.45,
                marker=dict(colors=colors_list, line=dict(color="#fff", width=2)),
                textinfo="percent+label",
                textfont=dict(size=12),
            ))
            apply_plotly_defaults(fig_pie, height=350)
            fig_pie.update_layout(showlegend=True)
            st.plotly_chart(fig_pie, use_container_width=True)

        # ── ODP per STO ───────────────────────────────────────────────────────────
        with col_r:
            st.markdown('<p class="section-header">🔴 Top ODP & GPON per STO</p>', unsafe_allow_html=True)
            try:
                where, params = _build_where(filters)
                odp_data = run_query(f"""
                    SELECT sto,
                           COUNT(CASE WHEN odp  IS NOT NULL AND odp  != '' THEN 1 END) AS odp_count,
                           COUNT(CASE WHEN gpon IS NOT NULL AND gpon != '' THEN 1 END) AS gpon_count
                    FROM workorders
                    {where}
                    GROUP BY sto
                    ORDER BY odp_count DESC
                    LIMIT 15
                """, params)
                df_odp = pd.DataFrame(odp_data)
                if not df_odp.empty:
                    df_odp = df_odp.sort_values("odp_count", ascending=True)
                    fig_odp = go.Figure()
                    fig_odp.add_trace(go.Bar(
                        y=df_odp["sto"], x=df_odp["odp_count"],
                        name="ODP", orientation="h",
                        marker=dict(color=COLORS["primary"])
                    ))
                    fig_odp.add_trace(go.Bar(
                        y=df_odp["sto"], x=df_odp["gpon_count"],
                        name="GPON", orientation="h",
                        marker=dict(color=COLORS["info"])
                    ))
                    fig_odp.update_layout(barmode="group")
                    apply_plotly_defaults(fig_odp, height=350)
                    fig_odp.update_layout(
                        xaxis=dict(title="Jumlah"),
                        legend=dict(orientation="h", y=-0.15),
                    )
                    st.plotly_chart(fig_odp, use_container_width=True)
            except Exception:
                st.info("Data ODP per STO tidak tersedia.")

        # ── Top ODP ───────────────────────────────────────────────────────────────
        st.markdown("---")
        st.markdown('<p class="section-header">📍 Top 20 ODP Terbanyak Digunakan</p>', unsafe_allow_html=True)
        try:
            where, params = _build_where(filters)
            top_odp = run_query(f"""
                SELECT odp, COUNT(*) AS jumlah_wo, sto
                FROM workorders
                WHERE odp IS NOT NULL AND odp != ''
                {(' AND ' + where[7:]) if where else ''}
                GROUP BY odp, sto
                ORDER BY jumlah_wo DESC
                LIMIT 20
            """, params)
            df_top_odp = pd.DataFrame(top_odp)
            if not df_top_odp.empty:
                fig_odp2 = go.Figure(go.Bar(
                    x=df_top_odp["odp"],
                    y=df_top_odp["jumlah_wo"],
                    marker=dict(
                        color=df_top_odp["jumlah_wo"],
                        colorscale=[[0, COLORS["info"]], [1, COLORS["primary"]]],
                        showscale=True,
                        colorbar=dict(title="Jumlah WO"),
                    ),
                    text=df_top_odp["jumlah_wo"],
                    textposition="outside",
                    customdata=df_top_odp["sto"],
                    hovertemplate="<b>%{x}</b><br>WO: %{y}<br>STO: %{customdata}<extra></extra>"
                ))
                apply_plotly_defaults(fig_odp2, height=400)
                fig_odp2.update_layout(
                    xaxis=dict(tickangle=-45),
                    yaxis=dict(title="Jumlah WO"),
                    showlegend=False,
                    margin=dict(l=0, r=60, t=30, b=130),
                )
                st.plotly_chart(fig_odp2, use_container_width=True)
        except Exception:
            pass

except Exception as e:
    if "no such table" in str(e).lower() or "doesn't exist" in str(e).lower():
        st.info("💡 Belum ada data. Upload file Excel via halaman Upload & ETL.")
    else:
        st.error(f"❌ Error: {e}")