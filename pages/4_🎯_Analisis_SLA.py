"""
Page 4: Analisis SLA
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from utils.queries import get_sla_summary, get_sla_per_sto, get_filter_options
from utils.theme import get_theme_css, apply_plotly_defaults, COLORS

st.set_page_config(page_title="Analisis SLA | BI Ridar", page_icon="🎯", layout="wide")
st.markdown(get_theme_css(), unsafe_allow_html=True)

st.markdown("""
<div class="page-header">
    <div style="display:flex; align-items:center; gap:16px;">
        <div style="font-size:2.2rem;">🎯</div>
        <div>
            <h1 style="margin:0; font-size:1.7rem; font-weight:800; color:#2C1810;">Analisis SLA</h1>
            <p style="margin:4px 0 0 0; color:#9B7B75; font-size:0.9rem; font-weight:500;">Service Level Agreement — Pencapaian & Distribusi per STO</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

try:
    opts = get_filter_options()
    with st.expander("🔽 Filter Data", expanded=False):
        fc1, fc2 = st.columns(2)
        sel_tahun = fc1.multiselect("📅 Tahun", opts["years"],
            default=opts["years"][:2] if len(opts["years"]) >= 2 else opts["years"], key="sla_tahun")
        sel_sto   = fc2.multiselect("🏢 STO", opts["stos"], key="sla_sto")
    filters = {}
    if sel_tahun: filters["tahun"] = sel_tahun
    if sel_sto:   filters["sto"]   = sel_sto
except Exception:
    filters = {}

try:
    sla_data    = get_sla_summary(filters)
    sla_per_sto = get_sla_per_sto(filters)

    if not sla_data:
        st.info("💡 Belum ada data.")
    else:
        sla_info = sla_data[0] if sla_data else {}
        total    = int(sla_info.get("total", 0) or 0)
        sla_ok   = int(sla_info.get("sla_ok", 0) or 0)
        sla_not  = int(sla_info.get("sla_not_ok", 0) or 0)
        pct_sla  = float(sla_info.get("pct_sla", 0) or 0)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("📋 Total WO",             f"{total:,}")
        c2.metric("✅ SLA Tercapai",         f"{sla_ok:,}", f"{pct_sla:.1f}%")
        c3.metric("❌ SLA Tidak Tercapai",   f"{sla_not:,}",
                  f"-{100-pct_sla:.1f}%", delta_color="inverse")
        target_sla  = 85.0
        delta_target = pct_sla - target_sla
        c4.metric("🎯 vs Target (85%)", f"{pct_sla:.1f}%",
                  f"{'▲' if delta_target >= 0 else '▼'} {abs(delta_target):.1f}%",
                  delta_color="normal" if delta_target >= 0 else "inverse")

        st.markdown("---")
        left, right = st.columns([1, 2])

        with left:
            st.markdown('<p class="section-header">📊 SLA Achievement</p>', unsafe_allow_html=True)
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=pct_sla,
                number={"suffix": "%", "font": {"size": 36, "color": COLORS["success"]}},
                delta={"reference": target_sla,
                       "increasing": {"color": COLORS["success"]},
                       "decreasing": {"color": COLORS["primary"]}},
                gauge={
                    "axis": {"range": [0, 100]},
                    "bar":  {"color": COLORS["success"], "thickness": 0.25},
                    "bgcolor": "rgba(0,0,0,0)", "borderwidth": 0,
                    "steps": [
                        {"range": [0, 60],   "color": "rgba(210,79,60,0.12)"},
                        {"range": [60, 85],  "color": "rgba(212,131,42,0.12)"},
                        {"range": [85, 100], "color": "rgba(74,155,111,0.12)"},
                    ],
                    "threshold": {"line": {"color": COLORS["accent"], "width": 3},
                                  "thickness": 0.8, "value": target_sla},
                },
                title={"text": "SLA Achievement", "font": {"color": COLORS["muted"], "size": 13}},
            ))
            apply_plotly_defaults(fig_gauge, height=280)
            st.plotly_chart(fig_gauge, use_container_width=True)

            fig_pie = go.Figure(data=[go.Pie(
                labels=["SLA Tercapai", "SLA Tidak Tercapai"],
                values=[sla_ok, sla_not],
                hole=0.55,
                marker=dict(colors=[COLORS["success"], COLORS["primary"]],
                            line=dict(color="#fff", width=2)),
                textinfo="percent+label",
                textfont=dict(size=11),
            )])
            fig_pie.add_annotation(
                text=f"<b>{pct_sla:.0f}%</b>",
                x=0.5, y=0.5,
                font=dict(size=24, color=COLORS["success"]),
                showarrow=False
            )
            apply_plotly_defaults(fig_pie, height=260)
            fig_pie.update_layout(showlegend=True)
            st.plotly_chart(fig_pie, use_container_width=True)

        with right:
            st.markdown('<p class="section-header">📊 SLA per STO</p>', unsafe_allow_html=True)
            df_sto = pd.DataFrame(sla_per_sto)
            if not df_sto.empty:
                df_sto = df_sto.sort_values("pct_sla", ascending=True)
                colors = [COLORS["success"] if v >= 85 else COLORS["warning"] if v >= 70 else COLORS["primary"]
                          for v in df_sto["pct_sla"]]
                fig_bar = go.Figure()
                fig_bar.add_trace(go.Bar(
                    y=df_sto["sto"], x=df_sto["pct_sla"],
                    orientation="h",
                    marker=dict(color=colors),
                    text=[f"{v:.1f}%" for v in df_sto["pct_sla"]],
                    textposition="outside",
                    customdata=df_sto[["total_wo", "sla_ok"]].values,
                    hovertemplate="<b>%{y}</b><br>SLA: %{x:.1f}%<br>Total WO: %{customdata[0]}<br>SLA OK: %{customdata[1]}<extra></extra>"
                ))
                fig_bar.add_vline(x=85, line=dict(color=COLORS["accent"], width=1.5, dash="dot"),
                                  annotation_text="Target 85%",
                                  annotation_font=dict(color=COLORS["accent"], size=10))
                apply_plotly_defaults(fig_bar, height=560)
                fig_bar.update_layout(xaxis=dict(range=[0, 115], title="SLA (%)"))
                st.plotly_chart(fig_bar, use_container_width=True)

        st.markdown("---")
        st.markdown('<p class="section-header">📋 Detail SLA per STO</p>', unsafe_allow_html=True)
        if sla_per_sto:
            df_table = pd.DataFrame(sla_per_sto).sort_values("pct_sla", ascending=False)
            df_table.columns = [c.replace("_", " ").title() for c in df_table.columns]
            st.dataframe(df_table, use_container_width=True, height=300)

except Exception as e:
    if "no such table" in str(e).lower() or "doesn't exist" in str(e).lower():
        st.info("💡 Belum ada data. Upload file Excel via halaman **Upload & ETL**.")
    else:
        st.error(f"❌ Error: {e}")