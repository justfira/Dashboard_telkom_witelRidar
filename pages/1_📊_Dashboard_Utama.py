"""
Page 3: Analisis Lengkap
Gabungan: Trend WO · Analisis SLA · Analisis STO · Analisis Teknisi · Analisis Kendala · Analisis Infrastruktur · Analisis Durasi
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import plotly.graph_objects as go
import pandas as pd

from utils.queries import (
    get_trend_monthly, get_trend_weekly,
    get_sla_summary, get_sla_per_sto,
    get_wo_per_sto,
    get_teknisi_performance,
    get_kendala_top, get_kendala_kategori,
    get_infrastruktur_stats,
    get_durasi_distribution, get_durasi_grup,
    get_filter_options, _build_where,
)
from utils.db import run_query
from utils.theme import get_theme_css, apply_plotly_defaults, COLORS, PALETTE

st.set_page_config(page_title="Analisis Lengkap | BI Ridar", page_icon="📈", layout="wide")
st.markdown(get_theme_css(), unsafe_allow_html=True)

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
    <div style="display:flex; align-items:center; gap:16px;">
        <div style="font-size:2.2rem;">📈</div>
        <div>
            <h1 style="margin:0; font-size:1.7rem; font-weight:800; color:#2C1810;">Analisis Lengkap</h1>
            <p style="margin:4px 0 0 0; color:#9B7B75; font-size:0.9rem; font-weight:500;">
                Trend · SLA · STO · Teknisi · Kendala · Infrastruktur · Durasi
            </p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Shared Filters ─────────────────────────────────────────────────────────────
try:
    opts = get_filter_options()
    with st.expander("🔽 Filter Data (berlaku untuk semua tab)", expanded=False):
        fc1, fc2, fc3, fc4 = st.columns(4)
        sel_tahun   = fc1.multiselect("📅 Tahun",    opts["years"],
            default=opts["years"][:2] if len(opts["years"]) >= 2 else opts["years"], key="al_tahun")
        sel_sto     = fc2.multiselect("🏢 STO",      opts["stos"],     key="al_sto")
        sel_status  = fc3.multiselect("📌 Status WO", opts["statuses"], key="al_status")
        sel_segment = fc4.multiselect("👤 Segment",  opts["segments"], key="al_segment")
    filters = {}
    if sel_tahun:   filters["tahun"]     = sel_tahun
    if sel_sto:     filters["sto"]       = sel_sto
    if sel_status:  filters["status_wo"] = sel_status
    if sel_segment: filters["segment"]   = sel_segment
except Exception as e:
    filters = {}
    st.warning(f"⚠️ Tidak dapat memuat filter: {e}")

# ── Tabs ───────────────────────────────────────────────────────────────────────
tabs = st.tabs([
    "📈 Trend WO",
    "🎯 SLA",
    "🏢 STO",
    "👨‍🔧 Teknisi",
    "⚠️ Kendala",
    "🌐 Infrastruktur",
    "⏱️ Durasi",
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — TREND WORK ORDER
# ══════════════════════════════════════════════════════════════════════════════
with tabs[0]:
    try:
        monthly   = get_trend_monthly(filters)
        df_m      = pd.DataFrame(monthly)

        if df_m.empty:
            st.info("💡 Belum ada data. Upload file Excel terlebih dahulu.")
        else:
            df_m["label"] = df_m.apply(
                lambda r: f"{str(r.get('nama_bulan',''))[:3]} {r.get('tahun','')}", axis=1)

            total   = df_m["total_wo"].sum()
            sla_pct = df_m["sla_ok"].sum() / total * 100 if total > 0 else 0
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("📋 Total WO",     f"{total:,}")
            c2.metric("🎯 SLA Tercapai", f"{df_m['sla_ok'].sum():,}")
            c3.metric("❌ Work Fail",    f"{df_m['work_fail'].sum():,}")
            c4.metric("📊 SLA Rate",     f"{sla_pct:.1f}%")

            st.markdown("---")

            # Line chart
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

            # Stacked bar
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

            # Table bulanan
            st.markdown('<p class="section-header">📋 Data Trend Bulanan</p>', unsafe_allow_html=True)
            df_display = df_m[["label", "total_wo", "sla_ok", "work_fail"]].copy()
            df_display.columns = ["Periode", "Total WO", "SLA Tercapai", "Work Fail"]
            df_display["SLA Rate (%)"] = (df_display["SLA Tercapai"] / df_display["Total WO"] * 100).round(1)
            df_display["WF Rate (%)"]  = (df_display["Work Fail"]    / df_display["Total WO"] * 100).round(1)
            st.dataframe(df_display, use_container_width=True, height=280)

    except Exception as e:
        st.error(f"❌ Error: {e}") if "no such table" not in str(e).lower() else \
        st.info("💡 Belum ada data. Upload file Excel via halaman Upload & ETL.")

    # Weekly trend
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


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — ANALISIS SLA
# ══════════════════════════════════════════════════════════════════════════════
with tabs[1]:
    try:
        sla_data    = get_sla_summary(filters)
        sla_per_sto = get_sla_per_sto(filters)

        if not sla_data:
            st.info("💡 Belum ada data.")
        else:
            sla_info  = sla_data[0] if sla_data else {}
            total     = int(sla_info.get("total", 0) or 0)
            sla_ok    = int(sla_info.get("sla_ok", 0) or 0)
            sla_not   = int(sla_info.get("sla_not_ok", 0) or 0)
            pct_sla   = float(sla_info.get("pct_sla", 0) or 0)
            target_sla = 85.0
            delta_target = pct_sla - target_sla

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("📋 Total WO",           f"{total:,}")
            c2.metric("✅ SLA Tercapai",        f"{sla_ok:,}", f"{pct_sla:.1f}%")
            c3.metric("❌ SLA Tidak Tercapai",  f"{sla_not:,}",
                      f"-{100-pct_sla:.1f}%", delta_color="inverse")
            c4.metric("🎯 vs Target (85%)",     f"{pct_sla:.1f}%",
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
                    df_sto    = df_sto.sort_values("pct_sla", ascending=True)
                    colors_sl = [COLORS["success"] if v >= 85 else COLORS["warning"] if v >= 70 else COLORS["primary"]
                                 for v in df_sto["pct_sla"]]
                    fig_bar = go.Figure()
                    fig_bar.add_trace(go.Bar(
                        y=df_sto["sto"], x=df_sto["pct_sla"],
                        orientation="h",
                        marker=dict(color=colors_sl),
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
        st.error(f"❌ Error: {e}") if "no such table" not in str(e).lower() else \
        st.info("💡 Belum ada data. Upload file Excel via halaman Upload & ETL.")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — ANALISIS STO
# ══════════════════════════════════════════════════════════════════════════════
with tabs[2]:
    try:
        sto_data = get_wo_per_sto(filters)
        df       = pd.DataFrame(sto_data)

        if df.empty:
            st.info("💡 Belum ada data. Upload file Excel via halaman Upload & ETL.")
        else:
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("🏢 Total STO",    f"{len(df):,}")
            c2.metric("📋 Total WO",     f"{df['total_wo'].sum():,}")
            best_sto  = df.nlargest(1, "pct_sla")["sto"].values[0]  if not df.empty else "-"
            worst_sto = df.nsmallest(1, "pct_sla")["sto"].values[0] if not df.empty else "-"
            c3.metric("🏆 STO Terbaik",  best_sto)
            c4.metric("⚠️ STO Terburuk", worst_sto)

            st.markdown("---")
            st.markdown('<p class="section-header">📊 Total Work Order per STO</p>', unsafe_allow_html=True)
            df_sorted = df.sort_values("total_wo", ascending=False)
            colors_wo = [COLORS["primary"] if i < 3 else COLORS["info"] if i < 10 else COLORS["muted"]
                         for i in range(len(df_sorted))]
            fig_wo = go.Figure(go.Bar(
                x=df_sorted["sto"], y=df_sorted["total_wo"],
                marker=dict(color=colors_wo, line=dict(width=0)),
                text=df_sorted["total_wo"], textposition="outside",
                hovertemplate="<b>%{x}</b><br>Total WO: %{y:,}<extra></extra>"
            ))
            apply_plotly_defaults(fig_wo, height=380)
            fig_wo.update_layout(
                xaxis=dict(tickangle=-45),
                yaxis=dict(title="Jumlah WO"),
                showlegend=False, margin=dict(l=0, r=0, t=30, b=90)
            )
            st.plotly_chart(fig_wo, use_container_width=True)

            st.markdown("---")
            left, right = st.columns(2)

            with left:
                st.markdown('<p class="section-header">🎯 SLA Rate per STO</p>', unsafe_allow_html=True)
                df_sla     = df.sort_values("pct_sla", ascending=True)
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
                fig_sla.update_layout(xaxis=dict(range=[0, 115], title="SLA (%)"), showlegend=False)
                st.plotly_chart(fig_sla, use_container_width=True)

            with right:
                st.markdown('<p class="section-header">❌ Work Fail per STO</p>', unsafe_allow_html=True)
                df_wf     = df.sort_values("work_fail", ascending=False).head(20)
                colors_wf = [COLORS["primary"] if v > 10 else COLORS["warning"] if v > 5 else COLORS["success"]
                             for v in df_wf["work_fail"]]
                fig_wf = go.Figure(go.Bar(
                    x=df_wf["sto"], y=df_wf["work_fail"],
                    marker=dict(color=colors_wf),
                    text=df_wf["work_fail"], textposition="outside",
                ))
                apply_plotly_defaults(fig_wf, height=460)
                fig_wf.update_layout(
                    xaxis=dict(tickangle=-45),
                    yaxis=dict(title="Jumlah Work Fail"),
                    showlegend=False, margin=dict(l=0, r=0, t=10, b=90)
                )
                st.plotly_chart(fig_wf, use_container_width=True)

            # Scatter
            st.markdown("---")
            st.markdown('<p class="section-header">🔵 Pemetaan STO: Volume WO vs SLA Rate</p>', unsafe_allow_html=True)
            fig_sc = go.Figure(go.Scatter(
                x=df["total_wo"], y=df["pct_sla"],
                mode="markers+text",
                text=df["sto"], textposition="top center", textfont=dict(size=9),
                marker=dict(
                    size=df["work_fail"].clip(5, 50) + 8,
                    color=df["pct_sla"],
                    colorscale=[[0, COLORS["primary"]], [0.5, COLORS["warning"]], [1, COLORS["success"]]],
                    showscale=True, colorbar=dict(title="SLA %"),
                    line=dict(color="#fff", width=1)
                ),
                hovertemplate="<b>%{text}</b><br>WO: %{x:,}<br>SLA: %{y:.1f}%<extra></extra>"
            ))
            fig_sc.add_hline(y=85, line=dict(color=COLORS["accent"], width=1.5, dash="dot"),
                             annotation_text="Target SLA 85%",
                             annotation_font=dict(color=COLORS["accent"], size=10))
            apply_plotly_defaults(fig_sc, height=400)
            fig_sc.update_layout(xaxis=dict(title="Total WO"), yaxis=dict(title="SLA Rate (%)"))
            st.plotly_chart(fig_sc, use_container_width=True)

            # Table
            st.markdown("---")
            st.markdown('<p class="section-header">📋 Data Lengkap per STO</p>', unsafe_allow_html=True)
            df_display = df.copy()
            df_display.columns = ["STO", "Total WO", "SLA OK", "Work Fail", "Avg Durasi (Hari)", "SLA Rate (%)"]
            st.dataframe(df_display.sort_values("Total WO", ascending=False),
                         use_container_width=True, height=350)

    except Exception as e:
        st.error(f"❌ Error: {e}") if "no such table" not in str(e).lower() else \
        st.info("💡 Belum ada data. Upload file Excel via halaman Upload & ETL.")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — ANALISIS TEKNISI
# ══════════════════════════════════════════════════════════════════════════════
with tabs[3]:
    try:
        _fc1, _fc2 = st.columns([4, 1])
        top_n = _fc2.selectbox("🔢 Tampilkan Top N", [10, 20, 30], key="tek_topn_tab")

        tek_data = get_teknisi_performance(filters)
        df       = pd.DataFrame(tek_data)

        if df.empty:
            st.info("💡 Belum ada data. Upload file Excel via halaman Upload & ETL.")
        else:
            df = df.head(top_n)

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("👨‍🔧 Total Teknisi",      f"{len(df):,}")
            c2.metric("📋 Total WO Dikerjakan", f"{df['total_wo'].sum():,}")
            best_tek = df.nlargest(1, "total_wo")["nama_teknisi"].values[0] if not df.empty else "-"
            c3.metric("🏆 Teknisi Teraktif",    str(best_tek)[:22])
            c4.metric("🎯 Avg SLA Rate",        f"{df['pct_sla'].mean():.1f}%")

            st.markdown("---")
            df_sorted  = df.sort_values("total_wo", ascending=True).tail(top_n)
            col_l, col_r = st.columns(2)

            with col_l:
                st.markdown('<p class="section-header">📊 Jumlah WO per Teknisi</p>', unsafe_allow_html=True)
                colors_wo = [
                    COLORS["primary"] if i >= len(df_sorted) - 3 else
                    COLORS["info"]    if i >= len(df_sorted) - 10 else COLORS["muted"]
                    for i in range(len(df_sorted))
                ]
                fig_wo = go.Figure(go.Bar(
                    y=df_sorted["nama_teknisi"], x=df_sorted["total_wo"],
                    orientation="h",
                    marker=dict(color=colors_wo, line=dict(width=0)),
                    text=df_sorted["total_wo"], textposition="outside",
                    customdata=df_sorted[["mitra", "pct_sla"]].values,
                    hovertemplate="<b>%{y}</b><br>WO: %{x:,}<br>Mitra: %{customdata[0]}<br>SLA: %{customdata[1]:.1f}%<extra></extra>"
                ))
                apply_plotly_defaults(fig_wo, height=560)
                fig_wo.update_layout(xaxis=dict(title="Jumlah WO"), showlegend=False,
                                     margin=dict(l=0, r=60, t=10, b=0))
                st.plotly_chart(fig_wo, use_container_width=True)

            with col_r:
                st.markdown('<p class="section-header">🎯 SLA Rate per Teknisi</p>', unsafe_allow_html=True)
                df_sla     = df.sort_values("pct_sla", ascending=True).tail(top_n)
                colors_sla = [COLORS["success"] if v >= 85 else COLORS["warning"] if v >= 70 else COLORS["primary"]
                              for v in df_sla["pct_sla"]]
                fig_sla = go.Figure(go.Bar(
                    y=df_sla["nama_teknisi"], x=df_sla["pct_sla"],
                    orientation="h",
                    marker=dict(color=colors_sla),
                    text=[f"{v:.0f}%" for v in df_sla["pct_sla"]],
                    textposition="outside",
                ))
                fig_sla.add_vline(x=85, line=dict(color=COLORS["accent"], width=1.5, dash="dot"),
                                  annotation_text="Target 85%",
                                  annotation_font=dict(color=COLORS["accent"], size=9))
                apply_plotly_defaults(fig_sla, height=560)
                fig_sla.update_layout(xaxis=dict(range=[0, 115], title="SLA Rate (%)"), showlegend=False,
                                      margin=dict(l=0, r=60, t=10, b=0))
                st.plotly_chart(fig_sla, use_container_width=True)

            # Avg durasi bar
            st.markdown("---")
            st.markdown('<p class="section-header">⏱️ Rata-rata Durasi per Teknisi (Hari)</p>', unsafe_allow_html=True)
            df_dur     = df.sort_values("avg_durasi", ascending=False).head(20)
            colors_dur = [COLORS["primary"] if v > 7 else COLORS["warning"] if v > 3 else COLORS["success"]
                          for v in df_dur["avg_durasi"]]
            fig_dur = go.Figure(go.Bar(
                x=df_dur["nama_teknisi"], y=df_dur["avg_durasi"],
                marker=dict(color=colors_dur),
                text=[f"{v:.1f}" for v in df_dur["avg_durasi"]],
                textposition="outside",
            ))
            fig_dur.add_hline(y=3, line=dict(color=COLORS["success"], width=1.5, dash="dot"),
                              annotation_text="SLA 3 Hari",
                              annotation_font=dict(color=COLORS["success"], size=10))
            apply_plotly_defaults(fig_dur, height=380)
            fig_dur.update_layout(
                xaxis=dict(tickangle=-45), yaxis=dict(title="Hari"),
                showlegend=False, margin=dict(l=0, r=0, t=30, b=110)
            )
            st.plotly_chart(fig_dur, use_container_width=True)

            # Bubble chart
            st.markdown("---")
            st.markdown('<p class="section-header">🔵 Pemetaan Teknisi: WO vs SLA vs Durasi</p>', unsafe_allow_html=True)
            fig_bub = go.Figure(go.Scatter(
                x=df["total_wo"], y=df["pct_sla"],
                mode="markers+text",
                text=df["nama_teknisi"].str[:15],
                textposition="top center", textfont=dict(size=8),
                marker=dict(
                    size=df["avg_durasi"].clip(2, 20) * 3 + 10,
                    color=df["avg_durasi"],
                    colorscale=[[0, COLORS["success"]], [0.5, COLORS["warning"]], [1, COLORS["primary"]]],
                    showscale=True, colorbar=dict(title="Avg Durasi (Hari)"),
                    line=dict(color="#fff", width=1)
                ),
                hovertemplate="<b>%{text}</b><br>WO: %{x:,}<br>SLA: %{y:.1f}%<extra></extra>"
            ))
            fig_bub.add_hline(y=85, line=dict(color=COLORS["accent"], width=1.5, dash="dot"),
                              annotation_text="Target SLA 85%",
                              annotation_font=dict(color=COLORS["accent"], size=10))
            apply_plotly_defaults(fig_bub, height=450)
            fig_bub.update_layout(xaxis=dict(title="Total WO"), yaxis=dict(title="SLA Rate (%)"))
            st.plotly_chart(fig_bub, use_container_width=True)

            # Table
            st.markdown("---")
            st.markdown('<p class="section-header">📋 Data Lengkap Teknisi</p>', unsafe_allow_html=True)
            df_display = df[["nama_teknisi", "mitra", "total_wo", "pct_sla", "avg_durasi", "work_fail"]].copy()
            df_display.columns = ["Nama Teknisi", "Mitra", "Total WO", "SLA Rate (%)", "Avg Durasi (Hari)", "Work Fail"]
            st.dataframe(df_display.sort_values("Total WO", ascending=False),
                         use_container_width=True, height=350)

    except Exception as e:
        st.error(f"❌ Error: {e}") if "no such table" not in str(e).lower() else \
        st.info("💡 Belum ada data. Upload file Excel via halaman Upload & ETL.")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — ANALISIS KENDALA
# ══════════════════════════════════════════════════════════════════════════════
with tabs[4]:
    try:
        _c1, _c2 = st.columns([4, 1])
        top_n_kend = _c2.selectbox("🔢 Top Kendala", [10, 15, 20], key="kend_topn_tab")

        kendala_data = get_kendala_top(filters, top_n=top_n_kend)
        df           = pd.DataFrame(kendala_data)

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
            st.markdown(f'<p class="section-header">📊 Pareto Chart — Top {top_n_kend} Kendala</p>', unsafe_allow_html=True)

            df = df.sort_values("jumlah", ascending=False)
            df["pct"]            = df["jumlah"] / df["jumlah"].sum() * 100
            df["cumulative_pct"] = df["pct"].cumsum()
            df["label"]          = df["kendala_pt1"].astype(str).str[:40]
            bar_colors           = [PALETTE[i % len(PALETTE)] for i in range(len(df))]

            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=df["label"], y=df["jumlah"],
                name="Jumlah Kendala",
                marker=dict(color=bar_colors, line=dict(width=0)),
                text=df["jumlah"], textposition="outside",
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

            # Kategori ROC
            try:
                kat_data = get_kendala_kategori(filters)
                df_kat   = pd.DataFrame(kat_data)
                if not df_kat.empty:
                    st.markdown("---")
                    col_l, col_r = st.columns(2)

                    with col_l:
                        st.markdown('<p class="section-header">🗂️ Kendala per Kategori ROC</p>', unsafe_allow_html=True)
                        fig_kat = go.Figure(go.Bar(
                            x=df_kat["kategori_roc"], y=df_kat["jumlah"],
                            marker=dict(color=PALETTE[:len(df_kat)]),
                            text=df_kat["jumlah"], textposition="outside",
                        ))
                        apply_plotly_defaults(fig_kat, height=350)
                        fig_kat.update_layout(
                            xaxis=dict(tickangle=-30), yaxis=dict(title="Jumlah"),
                            showlegend=False, margin=dict(l=0, r=0, t=10, b=90)
                        )
                        st.plotly_chart(fig_kat, use_container_width=True)

                    with col_r:
                        st.markdown('<p class="section-header">🥧 Proporsi Kategori</p>', unsafe_allow_html=True)
                        fig_pie = go.Figure(go.Pie(
                            labels=df_kat["kategori_roc"], values=df_kat["jumlah"],
                            hole=0.4,
                            marker=dict(colors=PALETTE[:len(df_kat)], line=dict(color="#fff", width=2)),
                            textinfo="percent+label", textfont=dict(size=11),
                        ))
                        apply_plotly_defaults(fig_pie, height=350)
                        fig_pie.update_layout(showlegend=False)
                        st.plotly_chart(fig_pie, use_container_width=True)
            except Exception:
                pass

            # Table kendala
            st.markdown("---")
            st.markdown('<p class="section-header">📋 Tabel Detail Kendala</p>', unsafe_allow_html=True)
            df_table = df[["kendala_pt1", "jumlah", "pct", "cumulative_pct"]].copy()
            df_table.columns = ["Kendala", "Jumlah", "Persentase (%)", "Kumulatif (%)"]
            df_table["Persentase (%)"] = df_table["Persentase (%)"].round(2)
            df_table["Kumulatif (%)"]  = df_table["Kumulatif (%)"].round(2)
            st.dataframe(df_table, use_container_width=True, height=300)

    except Exception as e:
        st.error(f"❌ Error: {e}") if "no such table" not in str(e).lower() else \
        st.info("💡 Belum ada data. Upload file Excel via halaman Upload & ETL.")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 6 — ANALISIS INFRASTRUKTUR
# ══════════════════════════════════════════════════════════════════════════════
with tabs[5]:
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
            cols = st.columns(len(df_infra))
            for i, (_, row) in enumerate(df_infra.iterrows()):
                cols[i].metric(f"🔌 {row['infra']}", f"{int(row['jumlah']):,}")

            st.markdown("---")
            st.markdown('<p class="section-header">📊 Jumlah WO per Infrastruktur</p>', unsafe_allow_html=True)
            colors_list = [INFRA_COLORS.get(r["infra"], COLORS["muted"]) for _, r in df_infra.iterrows()]
            fig_bar = go.Figure(go.Bar(
                x=df_infra["infra"], y=df_infra["jumlah"],
                marker=dict(color=colors_list, line=dict(width=0)),
                text=df_infra["jumlah"], textposition="outside", width=0.5,
            ))
            apply_plotly_defaults(fig_bar, height=380)
            fig_bar.update_layout(yaxis=dict(title="Jumlah Record"), showlegend=False,
                                  margin=dict(l=0, r=0, t=30, b=20))
            st.plotly_chart(fig_bar, use_container_width=True)

            st.markdown("---")
            col_l, col_r = st.columns(2)

            with col_l:
                st.markdown('<p class="section-header">🥧 Proporsi Infrastruktur</p>', unsafe_allow_html=True)
                fig_pie = go.Figure(go.Pie(
                    labels=df_infra["infra"], values=df_infra["jumlah"],
                    hole=0.45,
                    marker=dict(colors=colors_list, line=dict(color="#fff", width=2)),
                    textinfo="percent+label", textfont=dict(size=12),
                ))
                apply_plotly_defaults(fig_pie, height=350)
                fig_pie.update_layout(showlegend=True)
                st.plotly_chart(fig_pie, use_container_width=True)

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
                        df_odp  = df_odp.sort_values("odp_count", ascending=True)
                        fig_odp = go.Figure()
                        fig_odp.add_trace(go.Bar(
                            y=df_odp["sto"], x=df_odp["odp_count"],
                            name="ODP", orientation="h", marker=dict(color=COLORS["primary"])
                        ))
                        fig_odp.add_trace(go.Bar(
                            y=df_odp["sto"], x=df_odp["gpon_count"],
                            name="GPON", orientation="h", marker=dict(color=COLORS["info"])
                        ))
                        fig_odp.update_layout(barmode="group")
                        apply_plotly_defaults(fig_odp, height=350)
                        fig_odp.update_layout(
                            xaxis=dict(title="Jumlah"),
                            legend=dict(orientation="h", y=-0.15)
                        )
                        st.plotly_chart(fig_odp, use_container_width=True)
                except Exception:
                    st.info("Data ODP per STO tidak tersedia.")

            # Top ODP
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
                        x=df_top_odp["odp"], y=df_top_odp["jumlah_wo"],
                        marker=dict(
                            color=df_top_odp["jumlah_wo"],
                            colorscale=[[0, COLORS["info"]], [1, COLORS["primary"]]],
                            showscale=True, colorbar=dict(title="Jumlah WO"),
                        ),
                        text=df_top_odp["jumlah_wo"], textposition="outside",
                        customdata=df_top_odp["sto"],
                        hovertemplate="<b>%{x}</b><br>WO: %{y}<br>STO: %{customdata}<extra></extra>"
                    ))
                    apply_plotly_defaults(fig_odp2, height=400)
                    fig_odp2.update_layout(
                        xaxis=dict(tickangle=-45), yaxis=dict(title="Jumlah WO"),
                        showlegend=False, margin=dict(l=0, r=60, t=30, b=130)
                    )
                    st.plotly_chart(fig_odp2, use_container_width=True)
            except Exception:
                pass

    except Exception as e:
        st.error(f"❌ Error: {e}") if "no such table" not in str(e).lower() else \
        st.info("💡 Belum ada data. Upload file Excel via halaman Upload & ETL.")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 7 — ANALISIS DURASI
# ══════════════════════════════════════════════════════════════════════════════
with tabs[6]:
    try:
        dist_data = get_durasi_distribution(filters)
        df        = pd.DataFrame(dist_data)

        if df.empty:
            st.info("💡 Belum ada data. Upload file Excel via halaman Upload & ETL.")
        else:
            df["durasi_hari"] = pd.to_numeric(df["durasi_hari"], errors="coerce")
            df = df.dropna(subset=["durasi_hari"])
            df = df[df["durasi_hari"] >= 0]

            q3            = df["durasi_hari"].quantile(0.75)
            iqr           = q3 - df["durasi_hari"].quantile(0.25)
            outlier_count = len(df[df["durasi_hari"] > q3 + 1.5 * iqr])

            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("📊 Total Record", f"{len(df):,}")
            c2.metric("📈 Avg Durasi",   f"{df['durasi_hari'].mean():.1f} Hari")
            c3.metric("📉 Min Durasi",   f"{df['durasi_hari'].min():.1f} Hari")
            c4.metric("📈 Max Durasi",   f"{df['durasi_hari'].max():.1f} Hari")
            c5.metric("⚠️ Outlier",      f"{outlier_count:,}",
                      f"{outlier_count/len(df)*100:.1f}%", delta_color="inverse")

            st.markdown("---")

            # Boxplot per STO
            st.markdown('<p class="section-header">📦 Boxplot Distribusi Durasi per STO</p>', unsafe_allow_html=True)
            df_valid   = df[df["sto"].notna() & (df["sto"] != "")]
            sto_groups = df_valid.groupby("sto")["durasi_hari"].count().sort_values(ascending=False)
            top_stos   = sto_groups.head(15).index.tolist()
            df_top     = df_valid[df_valid["sto"].isin(top_stos)]

            if not df_top.empty:
                fig_box = go.Figure()
                for i, sto in enumerate(top_stos):
                    data_sto = df_top[df_top["sto"] == sto]["durasi_hari"]
                    fig_box.add_trace(go.Box(
                        y=data_sto, name=sto,
                        marker=dict(color=PALETTE[i % len(PALETTE)]),
                        line=dict(color=PALETTE[i % len(PALETTE)]),
                        boxpoints="outliers", jitter=0.3,
                    ))
                fig_box.add_hline(y=3, line=dict(color=COLORS["success"], width=2, dash="dot"),
                                  annotation_text="SLA 3 Hari",
                                  annotation_font=dict(color=COLORS["success"], size=11))
                apply_plotly_defaults(fig_box, height=460)
                fig_box.update_layout(
                    xaxis=dict(tickangle=-30), yaxis=dict(title="Durasi (Hari)"),
                    showlegend=False, margin=dict(l=0, r=0, t=10, b=90)
                )
                st.plotly_chart(fig_box, use_container_width=True)

            st.markdown("---")
            col_l, col_r = st.columns(2)

            with col_l:
                st.markdown('<p class="section-header">📊 Histogram Distribusi Durasi</p>', unsafe_allow_html=True)
                clip_val = df["durasi_hari"].quantile(0.99)
                fig_hist = go.Figure(go.Histogram(
                    x=df["durasi_hari"].clip(0, clip_val),
                    nbinsx=40,
                    marker=dict(color=COLORS["info"], line=dict(color=COLORS["info"], width=1)),
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
                    xaxis=dict(title="Durasi (Hari)"), yaxis=dict(title="Frekuensi"), showlegend=False
                )
                st.plotly_chart(fig_hist, use_container_width=True)

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
                            "< 1 Hari":        COLORS["success"],
                            "1-3 Hari":        COLORS["info"],
                            "4-7 Hari":        COLORS["warning"],
                            "8-14 Hari":       COLORS["secondary"],
                            "> 14 Hari":       COLORS["primary"],
                            "Tidak Diketahui": COLORS["muted"],
                        }
                        bar_colors = [grup_colors.get(g, COLORS["muted"]) for g in df_grup["durasi_grup"]]
                        fig_grup = go.Figure(go.Bar(
                            x=df_grup["durasi_grup"], y=df_grup["jumlah"],
                            marker=dict(color=bar_colors),
                            text=df_grup["jumlah"], textposition="outside",
                        ))
                        apply_plotly_defaults(fig_grup, height=380)
                        fig_grup.update_layout(
                            xaxis=dict(tickangle=-20), yaxis=dict(title="Jumlah WO"),
                            showlegend=False, margin=dict(l=0, r=0, t=10, b=70)
                        )
                        st.plotly_chart(fig_grup, use_container_width=True)
                except Exception:
                    pass

            # Box SLA vs Non-SLA
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
                    legend=dict(orientation="h", y=-0.15)
                )
                st.plotly_chart(fig_sla_box, use_container_width=True)

    except Exception as e:
        st.error(f"❌ Error: {e}") if "no such table" not in str(e).lower() else \
        st.info("💡 Belum ada data. Upload file Excel via halaman Upload & ETL.")