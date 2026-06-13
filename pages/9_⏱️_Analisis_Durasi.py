"""
Page 9: Analisis Durasi Pengerjaan
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from utils.queries import get_durasi_distribution, get_durasi_grup, get_filter_options
from utils.theme import get_theme_css, apply_plotly_defaults, COLORS

st.set_page_config(page_title="Analisis Durasi | BI Ridar", page_icon="⏱️", layout="wide")
st.markdown(get_theme_css(), unsafe_allow_html=True)

st.markdown("""
<div class="page-header">
    <div style="display:flex; align-items:center; gap:16px;">
        <div style="font-size:2.2rem;">⏱️</div>
        <div>
            <h1 style="margin:0; font-size:1.7rem; font-weight:800; color:#2C1810;">Analisis Durasi Pengerjaan</h1>
            <p style="margin:4px 0 0 0; color:#9B7B75; font-size:0.9rem; font-weight:500;">
                Distribusi & Outlier Durasi Penyelesaian Work Order
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
        sel_tahun  = fc1.multiselect("📅 Tahun", opts["years"],
            default=opts["years"][:2] if len(opts["years"]) >= 2 else opts["years"], key="dur_tahun")
        sel_sto    = fc2.multiselect("🏢 STO", opts["stos"], key="dur_sto")
        sel_status = fc3.multiselect("📌 Status WO", opts["statuses"], key="dur_status")
    filters = {}
    if sel_tahun:  filters["tahun"]     = sel_tahun
    if sel_sto:    filters["sto"]       = sel_sto
    if sel_status: filters["status_wo"] = sel_status
except Exception:
    filters = {}

try:
    dist_data = get_durasi_distribution(filters)
    df        = pd.DataFrame(dist_data)

    if df.empty:
        st.info("💡 Belum ada data. Upload file Excel via halaman Upload & ETL.")
    else:
        df["durasi_hari"] = pd.to_numeric(df["durasi_hari"], errors="coerce")
        df = df.dropna(subset=["durasi_hari"])
        df = df[df["durasi_hari"] >= 0]

        q3           = df["durasi_hari"].quantile(0.75)
        iqr          = q3 - df["durasi_hari"].quantile(0.25)
        outlier_count = len(df[df["durasi_hari"] > q3 + 1.5 * iqr])

        # ── KPI ──────────────────────────────────────────────────────────────────
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("📊 Total Record",  f"{len(df):,}")
        c2.metric("📈 Avg Durasi",    f"{df['durasi_hari'].mean():.1f} Hari")
        c3.metric("📉 Min Durasi",    f"{df['durasi_hari'].min():.1f} Hari")
        c4.metric("📈 Max Durasi",    f"{df['durasi_hari'].max():.1f} Hari")
        c5.metric("⚠️ Outlier",       f"{outlier_count:,}",
                  f"{outlier_count/len(df)*100:.1f}%", delta_color="inverse")

        st.markdown("---")

        # ── Boxplot per STO ───────────────────────────────────────────────────────
        st.markdown('<p class="section-header">📦 Boxplot Distribusi Durasi per STO</p>', unsafe_allow_html=True)
        df_valid   = df[df["sto"].notna() & (df["sto"] != "")]
        sto_groups = df_valid.groupby("sto")["durasi_hari"].count().sort_values(ascending=False)
        top_stos   = sto_groups.head(15).index.tolist()
        df_top     = df_valid[df_valid["sto"].isin(top_stos)]

        if not df_top.empty:
            from utils.theme import PALETTE
            fig_box = go.Figure()
            for i, sto in enumerate(top_stos):
                data_sto = df_top[df_top["sto"] == sto]["durasi_hari"]
                fig_box.add_trace(go.Box(
                    y=data_sto,
                    name=sto,
                    marker=dict(color=PALETTE[i % len(PALETTE)]),
                    line=dict(color=PALETTE[i % len(PALETTE)]),
                    boxpoints="outliers",
                    jitter=0.3,
                ))
            fig_box.add_hline(y=3, line=dict(color=COLORS["success"], width=2, dash="dot"),
                              annotation_text="SLA 3 Hari",
                              annotation_font=dict(color=COLORS["success"], size=11))
            apply_plotly_defaults(fig_box, height=460)
            fig_box.update_layout(
                xaxis=dict(tickangle=-30),
                yaxis=dict(title="Durasi (Hari)"),
                showlegend=False,
                margin=dict(l=0, r=0, t=10, b=90),
            )
            st.plotly_chart(fig_box, use_container_width=True)

        st.markdown("---")
        col_l, col_r = st.columns(2)

        # ── Histogram ─────────────────────────────────────────────────────────────
        with col_l:
            st.markdown('<p class="section-header">📊 Histogram Distribusi Durasi</p>', unsafe_allow_html=True)
            clip_val = df["durasi_hari"].quantile(0.99)
            fig_hist = go.Figure(go.Histogram(
                x=df["durasi_hari"].clip(0, clip_val),
                nbinsx=40,
                marker=dict(color=COLORS["info"],
                            line=dict(color=COLORS["info"], width=1)),
                opacity=0.75,
            ))
            fig_hist.add_vline(x=3, line=dict(color=COLORS["success"], width=2, dash="dot"),
                               annotation_text="SLA 3 Hari",
                               annotation_font=dict(color=COLORS["success"], size=11))
            fig_hist.add_vline(x=df["durasi_hari"].mean(),
                               line=dict(color=COLORS["warning"], width=2, dash="dash"),
                               annotation_text=f"Avg {df['durasi_hari'].mean():.1f}",
                               annotation_font=dict(color=COLORS["warning"], size=11))
            apply_plotly_defaults(fig_hist, height=380)
            fig_hist.update_layout(
                xaxis=dict(title="Durasi (Hari)"),
                yaxis=dict(title="Frekuensi"),
                showlegend=False,
            )
            st.plotly_chart(fig_hist, use_container_width=True)

        # ── Grup Durasi ───────────────────────────────────────────────────────────
        with col_r:
            st.markdown('<p class="section-header">📊 WO per Grup Durasi</p>', unsafe_allow_html=True)
            try:
                grup_data = get_durasi_grup(filters)
                df_grup   = pd.DataFrame(grup_data)
                if not df_grup.empty:
                    order = ["< 1 Hari", "1-3 Hari", "4-7 Hari", "8-14 Hari", "> 14 Hari", "Tidak Diketahui"]
                    df_grup["sort_key"] = df_grup["durasi_grup"].apply(
                        lambda x: order.index(x) if x in order else 99)
                    df_grup = df_grup.sort_values("sort_key")

                    grup_colors = {
                        "< 1 Hari":       COLORS["success"],
                        "1-3 Hari":       COLORS["info"],
                        "4-7 Hari":       COLORS["warning"],
                        "8-14 Hari":      COLORS["secondary"],
                        "> 14 Hari":      COLORS["primary"],
                        "Tidak Diketahui": COLORS["muted"],
                    }
                    bar_colors = [grup_colors.get(g, COLORS["muted"]) for g in df_grup["durasi_grup"]]
                    fig_grup = go.Figure(go.Bar(
                        x=df_grup["durasi_grup"],
                        y=df_grup["jumlah"],
                        marker=dict(color=bar_colors),
                        text=df_grup["jumlah"],
                        textposition="outside",
                    ))
                    apply_plotly_defaults(fig_grup, height=380)
                    fig_grup.update_layout(
                        xaxis=dict(tickangle=-20),
                        yaxis=dict(title="Jumlah WO"),
                        showlegend=False,
                        margin=dict(l=0, r=0, t=10, b=70),
                    )
                    st.plotly_chart(fig_grup, use_container_width=True)
            except Exception:
                pass

        # ── Box SLA vs Non-SLA ────────────────────────────────────────────────────
        st.markdown("---")
        st.markdown('<p class="section-header">🎯 Durasi: SLA Tercapai vs Tidak Tercapai</p>', unsafe_allow_html=True)
        df_sla = df[df["is_sla_tercapai"].notna()]
        if not df_sla.empty:
            fig_sla_box = go.Figure()
            fig_sla_box.add_trace(go.Box(
                y=df_sla[df_sla["is_sla_tercapai"] == 1]["durasi_hari"],
                name="SLA Tercapai",
                marker=dict(color=COLORS["success"]),
                line=dict(color=COLORS["success"]),
                boxpoints="outliers",
            ))
            fig_sla_box.add_trace(go.Box(
                y=df_sla[df_sla["is_sla_tercapai"] == 0]["durasi_hari"],
                name="SLA Tidak Tercapai",
                marker=dict(color=COLORS["primary"]),
                line=dict(color=COLORS["primary"]),
                boxpoints="outliers",
            ))
            apply_plotly_defaults(fig_sla_box, height=380)
            fig_sla_box.update_layout(
                yaxis=dict(title="Durasi (Hari)"),
                legend=dict(orientation="h", y=-0.15),
            )
            st.plotly_chart(fig_sla_box, use_container_width=True)

except Exception as e:
    if "no such table" in str(e).lower() or "doesn't exist" in str(e).lower():
        st.info("💡 Belum ada data. Upload file Excel via halaman Upload & ETL.")
    else:
        st.error(f"❌ Error: {e}")