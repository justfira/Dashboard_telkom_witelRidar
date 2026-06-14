"""
Dashboard Utama — BI Support Telkom Witel Ridar
Ringkasan KPI, Trend WO, Monitoring SLA, Top Kendala, Teknisi, STO, dll.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime

from utils.queries import (
    get_kpi_summary,
    get_kpi_monthly_comparison,
    get_trend_monthly,
    get_trend_weekly,
    get_sla_summary,
    get_sla_per_sto,
    get_wo_per_sto,
    get_teknisi_performance,
    get_kendala_top,
    get_kendala_kategori,
    get_durasi_grup,
    get_filter_options,
    _build_where,
)
from utils.db import run_query
from utils.theme import get_theme_css, apply_plotly_defaults, COLORS, PALETTE

st.set_page_config(
    page_title="Dashboard Utama | BI Support Telkom Ridar",
    page_icon="📊",
    layout="wide",
)
st.markdown(get_theme_css(), unsafe_allow_html=True)

# ── Additional CSS for Dashboard Utama ─────────────────────────────────────────
st.markdown("""
<style>
/* Alert/Banner styling */
.alert-banner {
    padding: 10px 16px;
    border-radius: 10px;
    margin-bottom: 8px;
    font-size: 0.82rem;
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 10px;
}
.alert-warning {
    background: #FFF3CD;
    border-left: 4px solid #D4832A;
    color: #7B4A00;
}
.alert-danger {
    background: #FDECEA;
    border-left: 4px solid #D24F3C;
    color: #8B1A0E;
}
.alert-info {
    background: #E8F4FD;
    border-left: 4px solid #4A7EC0;
    color: #1A3D6B;
}
.alert-time {
    margin-left: auto;
    font-size: 0.75rem;
    opacity: 0.7;
    font-weight: 400;
    white-space: nowrap;
}

/* KPI Card */
.kpi-card {
    background: #FFFFFF;
    border: 1.5px solid #F5C8BC;
    border-radius: 16px;
    padding: 18px 20px;
    box-shadow: 0 2px 12px rgba(180,80,60,0.08);
    transition: all 0.3s ease;
    height: 100%;
    min-height: 100px;
}
.kpi-card:hover {
    border-color: #D24F3C;
    box-shadow: 0 6px 24px rgba(180,80,60,0.18);
    transform: translateY(-2px);
}
.kpi-label {
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    color: #9B7B75 !important;
    margin-bottom: 6px;
}
.kpi-value {
    font-size: 1.9rem;
    font-weight: 800;
    color: #2C1810 !important;
    line-height: 1.1;
}
.kpi-sub {
    font-size: 0.75rem;
    color: #9B7B75 !important;
    margin-top: 4px;
    font-weight: 500;
}
.kpi-delta-pos {
    color: #4A9B6F !important;
    font-size: 0.78rem;
    font-weight: 700;
}
.kpi-delta-neg {
    color: #D24F3C !important;
    font-size: 0.78rem;
    font-weight: 700;
}

/* Chart card */
.chart-card {
    background: #FFFFFF;
    border: 1.5px solid #F5C8BC;
    border-radius: 16px;
    padding: 16px;
    box-shadow: 0 2px 12px rgba(180,80,60,0.07);
    margin-bottom: 16px;
}

/* Section divider label */
.section-label {
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    color: #9B7B75;
    padding: 4px 12px;
    background: #FFF1EB;
    border-radius: 6px;
    display: inline-block;
    margin-bottom: 12px;
    border: 1px solid #F5C8BC;
}

/* Table Summary row */
.summary-row {
    display: flex;
    gap: 12px;
    margin-bottom: 10px;
    flex-wrap: wrap;
}
.summary-chip {
    background: #FFF1EB;
    border: 1px solid #F5C8BC;
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 0.78rem;
    font-weight: 600;
    color: #4A2C20;
}
.summary-chip span {
    color: #D24F3C !important;
    font-weight: 800;
}

/* Badge pill */
.badge-green {
    background: #E8F5EE;
    color: #2E7D4F !important;
    border: 1px solid #A8D5B8;
    padding: 2px 10px;
    border-radius: 12px;
    font-size: 0.72rem;
    font-weight: 700;
}
.badge-red {
    background: #FDECEA;
    color: #C0392B !important;
    border: 1px solid #F5ADAD;
    padding: 2px 10px;
    border-radius: 12px;
    font-size: 0.72rem;
    font-weight: 700;
}

/* Compact section header */
.sec-hdr {
    font-size: 1rem;
    font-weight: 700;
    color: #2C1810;
    border-left: 4px solid #D24F3C;
    padding-left: 10px;
    margin-bottom: 12px;
}
</style>
""", unsafe_allow_html=True)

# ── Header ─────────────────────────────────────────────────────────────────────
now = datetime.now().strftime("%d %b %Y · %H:%M")
st.markdown(f"""
<div style="display:flex; align-items:center; justify-content:space-between;
            background:linear-gradient(135deg,#FFF1EB 0%,#FDE8DF 100%);
            border:1.5px solid #F5C8BC; border-radius:16px; padding:16px 24px; margin-bottom:16px;">
    <div style="display:flex; align-items:center; gap:14px;">
        <div style="font-size:2rem;">📊</div>
        <div>
            <div style="font-size:1.3rem; font-weight:800; color:#2C1810; margin:0;">
                BI SUPPORT — Dashboard Utama
            </div>
            <div style="font-size:0.8rem; color:#9B7B75; margin-top:2px; font-weight:500;">
                Monitoring Work Order & Service Connectivity · Telkom Witel Ridar
            </div>
        </div>
    </div>
    <div style="text-align:right;">
        <div style="font-size:0.72rem; color:#9B7B75; font-weight:600; text-transform:uppercase; letter-spacing:1px;">
            Update Terakhir
        </div>
        <div style="font-size:0.9rem; font-weight:700; color:#2C1810;">{now}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Filters ────────────────────────────────────────────────────────────────────
filters = {}
try:
    opts = get_filter_options()
    with st.expander("🔽 Filter Data", expanded=False):
        fc1, fc2, fc3, fc4 = st.columns(4)
        sel_tahun   = fc1.multiselect("📅 Tahun",    opts["years"],
            default=opts["years"][:1] if opts["years"] else [], key="du_tahun")
        sel_sto     = fc2.multiselect("🏢 STO",      opts["stos"],     key="du_sto")
        sel_status  = fc3.multiselect("📌 Status WO", opts["statuses"], key="du_status")
        sel_segment = fc4.multiselect("👤 Segment",  opts["segments"], key="du_segment")
    if sel_tahun:   filters["tahun"]     = sel_tahun
    if sel_sto:     filters["sto"]       = sel_sto
    if sel_status:  filters["status_wo"] = sel_status
    if sel_segment: filters["segment"]   = sel_segment
except Exception as e:
    filters = {}
    st.warning(f"⚠️ Tidak dapat memuat filter: {e}")

# ── KPI Summary ────────────────────────────────────────────────────────────────
try:
    kpi = get_kpi_summary(filters)
    if not kpi:
        kpi = {}

    total_wo      = int(kpi.get("total_wo", 0) or 0)
    wo_selesai    = int(kpi.get("wo_selesai", 0) or 0)
    sla_ok        = int(kpi.get("sla_tercapai", 0) or 0)
    work_fail     = int(kpi.get("work_fail", 0) or 0)
    avg_durasi    = float(kpi.get("avg_durasi", 0) or 0)
    unsc          = int(kpi.get("unsc", 0) or 0)
    jml_teknisi   = int(kpi.get("jumlah_teknisi", 0) or 0)
    jml_sto       = int(kpi.get("jumlah_sto", 0) or 0)

    sla_rate      = (sla_ok / total_wo * 100) if total_wo > 0 else 0
    selesai_rate  = (wo_selesai / total_wo * 100) if total_wo > 0 else 0
    wf_rate       = (work_fail / total_wo * 100) if total_wo > 0 else 0

    # Alert banners
    if total_wo > 0:
        alerts = []
        if sla_rate < 85:
            alerts.append(("danger", f"⚠️ SLA rate saat ini {sla_rate:.1f}% — di bawah target 85%. Perlu perhatian segera.", "Kritis"))
        if work_fail > 0:
            alerts.append(("warning", f"🔴 Terdapat {work_fail:,} Work Fail ({wf_rate:.1f}%) — pantau teknisi terkait.", "Peringatan"))
        if unsc > 0:
            alerts.append(("info", f"ℹ️ {unsc:,} WO berstatus UNSC — pastikan penanganan sudah dilakukan.", "Info"))
        if avg_durasi > 3:
            alerts.append(("warning", f"⏱️ Rata-rata durasi pengerjaan {avg_durasi:.1f} hari — melampaui SLA 3 hari.", "Peringatan"))

        for atype, msg, label in alerts:
            st.markdown(f"""
            <div class="alert-banner alert-{atype}">
                {msg}
                <span class="alert-time">{label} · {now}</span>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # KPI Row
    k1, k2, k3, k4, k5 = st.columns(5)

    def kpi_card(col, label, value, sub=None, delta=None, delta_pos=True, icon=""):
        delta_html = ""
        if delta is not None:
            cls = "kpi-delta-pos" if delta_pos else "kpi-delta-neg"
            delta_html = f'<div class="{cls}">{delta}</div>'
        sub_html = f'<div class="kpi-sub">{sub}</div>' if sub else ""
        col.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">{icon} {label}</div>
            <div class="kpi-value">{value}</div>
            {sub_html}
            {delta_html}
        </div>
        """, unsafe_allow_html=True)

    kpi_card(k1, "Total Work Order",  f"{total_wo:,}",
             sub=f"{jml_sto} STO · {jml_teknisi} Teknisi", icon="📋")
    kpi_card(k2, "WO Selesai",        f"{wo_selesai:,}",
             sub=f"Progress {selesai_rate:.1f}%",
             delta=f"▲ {selesai_rate:.1f}%" if selesai_rate >= 50 else f"▼ {selesai_rate:.1f}%",
             delta_pos=selesai_rate >= 50, icon="✅")
    kpi_card(k3, "SLA Tercapai",      f"{sla_rate:.1f}%",
             sub=f"{sla_ok:,} dari {total_wo:,} WO",
             delta="▲ On Target" if sla_rate >= 85 else "▼ Below Target",
             delta_pos=sla_rate >= 85, icon="🎯")
    kpi_card(k4, "Work Fail",         f"{work_fail:,}",
             sub=f"Rate {wf_rate:.1f}%",
             delta="✓ Normal" if work_fail == 0 else f"⚠ {wf_rate:.1f}%",
             delta_pos=work_fail == 0, icon="❌")
    kpi_card(k5, "Rata-rata Durasi",  f"{avg_durasi:.1f}",
             sub="hari per WO",
             delta="✓ SLA 3 Hari" if avg_durasi <= 3 else f"▼ {avg_durasi-3:.1f} hari over",
             delta_pos=avg_durasi <= 3, icon="⏱️")

except Exception as e:
    if "no such table" in str(e).lower():
        st.info("💡 Belum ada data. Upload file Excel via halaman Upload & ETL.")
    else:
        st.error(f"❌ Error KPI: {e}")

st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION: TREND WO + MONITORING HARIAN + GAUGE SLA
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.markdown('<p class="section-header">📈 Trend & Monitoring WO</p>', unsafe_allow_html=True)

col_trend, col_weekly, col_gauge = st.columns([2, 2, 1])

# T1 — Trend Bulanan
with col_trend:
    st.markdown('<p class="sec-hdr">T1 — Trend Ganendra Bulanan</p>', unsafe_allow_html=True)
    try:
        monthly = get_trend_monthly(filters)
        df_m = pd.DataFrame(monthly)
        if not df_m.empty:
            df_m["total_wo"] = pd.to_numeric(df_m["total_wo"], errors="coerce").fillna(0).astype(int)
            df_m["sla_ok"]   = pd.to_numeric(df_m["sla_ok"],   errors="coerce").fillna(0).astype(int)
            df_m["work_fail"]= pd.to_numeric(df_m["work_fail"],errors="coerce").fillna(0).astype(int)
            df_m["label"]    = df_m.apply(lambda r: f"{str(r.get('nama_bulan',''))[:3]} {r.get('tahun','')}", axis=1)

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df_m["label"], y=df_m["total_wo"],
                name="Total WO", mode="lines+markers+text",
                text=df_m["total_wo"], textposition="top center",
                textfont=dict(color=COLORS["primary"], size=9),
                line=dict(color=COLORS["primary"], width=2.5),
                marker=dict(size=8, color=COLORS["primary"], line=dict(width=2, color="#fff")),
                fill="tozeroy", fillcolor="rgba(210,79,60,0.05)"
            ))
            fig.add_trace(go.Scatter(
                x=df_m["label"], y=df_m["sla_ok"],
                name="SLA OK", mode="lines+markers",
                line=dict(color=COLORS["success"], width=2, dash="dot"),
                marker=dict(size=6, color=COLORS["success"])
            ))
            apply_plotly_defaults(fig, height=280)
            fig.update_layout(
                xaxis=dict(tickangle=-30, tickfont=dict(size=9)),
                yaxis=dict(title=""),
                legend=dict(orientation="h", y=-0.25, font=dict(size=10)),
                hovermode="x unified",
                margin=dict(l=0, r=0, t=10, b=60)
            )
            st.plotly_chart(fig, use_container_width=True, key="trend_bulanan")
        else:
            st.info("💡 Belum ada data trend bulanan.")
    except Exception as e:
        st.info("💡 Belum ada data.") if "no such table" in str(e).lower() else st.error(f"❌ {e}")

# T2 — Monitoring Mingguan
with col_weekly:
    st.markdown('<p class="sec-hdr">T2 — Monitoring Harian</p>', unsafe_allow_html=True)
    try:
        weekly = get_trend_weekly(filters)
        df_w = pd.DataFrame(weekly)
        if not df_w.empty:
            df_w["total_wo"] = pd.to_numeric(df_w["total_wo"], errors="coerce").fillna(0).astype(int)
            df_w["sla_ok"]   = pd.to_numeric(df_w["sla_ok"],   errors="coerce").fillna(0).astype(int)
            df_w["label"]    = df_w.apply(lambda r: f"W{r.get('minggu','')}/{str(r.get('tahun',''))[-2:]}", axis=1)

            fig_w = go.Figure()
            fig_w.add_trace(go.Scatter(
                x=df_w["label"], y=df_w["total_wo"],
                name="Total WO", mode="lines+markers",
                line=dict(color=COLORS["purple"], width=2),
                marker=dict(size=6, color=COLORS["purple"]),
                fill="tozeroy", fillcolor="rgba(139,92,246,0.07)"
            ))
            fig_w.add_trace(go.Scatter(
                x=df_w["label"], y=df_w["sla_ok"],
                name="SLA OK", mode="lines",
                line=dict(color=COLORS["success"], width=2, dash="dot")
            ))
            apply_plotly_defaults(fig_w, height=280)
            fig_w.update_layout(
                xaxis=dict(tickangle=-45, nticks=15, tickfont=dict(size=8)),
                yaxis=dict(title=""),
                legend=dict(orientation="h", y=-0.25, font=dict(size=10)),
                hovermode="x unified",
                margin=dict(l=0, r=0, t=10, b=60)
            )
            st.plotly_chart(fig_w, use_container_width=True, key="trend_mingguan")
        else:
            st.info("💡 Belum ada data mingguan.")
    except Exception as e:
        st.info("💡 Belum ada data.") if "no such table" in str(e).lower() else st.error(f"❌ {e}")

# R2 — SLA Gauge
with col_gauge:
    st.markdown('<p class="sec-hdr">R2 — Status On/Offline</p>', unsafe_allow_html=True)
    try:
        sla_data = get_sla_summary(filters)
        if sla_data:
            s = sla_data[0]
            sla_v     = float(s.get("pct_sla", 0) or 0)
            sla_ok_v  = int(s.get("sla_ok", 0) or 0)
            sla_not_v = int(s.get("sla_not_ok", 0) or 0)

            fig_g = go.Figure(go.Indicator(
                mode="gauge+number",
                value=sla_v,
                number={"suffix": "%", "font": {"size": 28, "color": COLORS["success"] if sla_v >= 85 else COLORS["primary"]}},
                gauge={
                    "axis": {"range": [0, 100], "tickwidth": 1, "tickfont": {"size": 8}},
                    "bar": {"color": COLORS["success"] if sla_v >= 85 else COLORS["primary"], "thickness": 0.22},
                    "bgcolor": "rgba(0,0,0,0)", "borderwidth": 0,
                    "steps": [
                        {"range": [0, 60],  "color": "rgba(210,79,60,0.10)"},
                        {"range": [60, 85], "color": "rgba(212,131,42,0.10)"},
                        {"range": [85, 100],"color": "rgba(74,155,111,0.10)"},
                    ],
                    "threshold": {
                        "line": {"color": COLORS["accent"], "width": 2},
                        "thickness": 0.75, "value": 85
                    },
                },
                title={"text": "SLA Achievement", "font": {"color": COLORS["muted"], "size": 11}},
            ))
            apply_plotly_defaults(fig_g, height=200)
            fig_g.update_layout(margin=dict(l=10, r=10, t=30, b=10))
            st.plotly_chart(fig_g, use_container_width=True, key="gauge_sla")

            # Legend pills
            st.markdown(f"""
            <div style="display:flex; flex-direction:column; gap:6px; margin-top:4px;">
                <div style="display:flex; justify-content:space-between; align-items:center;
                            background:#E8F5EE; border-radius:8px; padding:6px 10px;">
                    <span style="font-size:0.72rem; font-weight:700; color:#2E7D4F;">● Tercapai</span>
                    <span style="font-size:0.85rem; font-weight:800; color:#2E7D4F;">{sla_ok_v:,}</span>
                </div>
                <div style="display:flex; justify-content:space-between; align-items:center;
                            background:#FDECEA; border-radius:8px; padding:6px 10px;">
                    <span style="font-size:0.72rem; font-weight:700; color:#C0392B;">● Tidak Tercapai</span>
                    <span style="font-size:0.85rem; font-weight:800; color:#C0392B;">{sla_not_v:,}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Belum ada data SLA.")
    except Exception as e:
        st.info("💡 Belum ada data.") if "no such table" in str(e).lower() else st.error(f"❌ {e}")

# ══════════════════════════════════════════════════════════════════════════════
# SECTION: TOP AREA KENDALA + MONITORING STATUS KENDALA
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.markdown('<p class="section-header">⚠️ Analisis Kendala & Status STO</p>', unsafe_allow_html=True)

col_kend_left, col_kend_right = st.columns(2)

with col_kend_left:
    st.markdown('<p class="sec-hdr">A4 — Top Area Kendala</p>', unsafe_allow_html=True)
    try:
        # Kendala per STO (proxy for "area kendala")
        where, params = _build_where(filters)
        area_kend = run_query(f"""
            SELECT sto, COUNT(*) AS jumlah,
                   SUM(is_workfail) AS work_fail,
                   ROUND(SUM(is_sla_tercapai)*100.0/COUNT(*),1) AS pct_sla
            FROM workorders
            WHERE sto IS NOT NULL AND sto != ''
            {(' AND ' + where[6:]) if where else ''}
            GROUP BY sto
            ORDER BY jumlah DESC
            LIMIT 12
        """, params)
        df_ak = pd.DataFrame(area_kend)
        if not df_ak.empty:
            df_ak["jumlah"]    = pd.to_numeric(df_ak["jumlah"], errors="coerce").fillna(0).astype(int)
            df_ak["work_fail"] = pd.to_numeric(df_ak["work_fail"], errors="coerce").fillna(0).astype(int)
            df_ak["pct_sla"]   = pd.to_numeric(df_ak["pct_sla"], errors="coerce").fillna(0.0)
            df_ak = df_ak.sort_values("jumlah", ascending=True)

            colors_ak = [COLORS["primary"] if i >= len(df_ak)-3 else
                         COLORS["warning"] if i >= len(df_ak)-7 else
                         COLORS["info"] for i in range(len(df_ak))]
            fig_ak = go.Figure(go.Bar(
                y=df_ak["sto"], x=df_ak["jumlah"],
                orientation="h",
                marker=dict(color=colors_ak, line=dict(width=0)),
                text=df_ak["jumlah"], textposition="outside",
                textfont=dict(size=10),
                customdata=df_ak[["work_fail", "pct_sla"]].values,
                hovertemplate="<b>%{y}</b><br>Total WO: %{x:,}<br>Work Fail: %{customdata[0]}<br>SLA: %{customdata[1]:.1f}%<extra></extra>"
            ))
            apply_plotly_defaults(fig_ak, height=380)
            fig_ak.update_layout(
                xaxis=dict(title="Jumlah WO"),
                yaxis=dict(tickfont=dict(size=9)),
                showlegend=False,
                margin=dict(l=0, r=60, t=10, b=10)
            )
            st.plotly_chart(fig_ak, use_container_width=True, key="area_kendala")

            # Summary chips
            total_area = df_ak["jumlah"].sum()
            top_area   = df_ak.iloc[-1]["sto"]
            st.markdown(f"""
            <div class="summary-row">
                <div class="summary-chip">Total WO: <span>{total_area:,}</span></div>
                <div class="summary-chip">STO Terbanyak: <span>{top_area}</span></div>
                <div class="summary-chip">Jumlah STO: <span>{len(df_ak)}</span></div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Belum ada data STO.")
    except Exception as e:
        st.info("💡 Belum ada data.") if "no such table" in str(e).lower() else st.error(f"❌ {e}")

with col_kend_right:
    st.markdown('<p class="sec-hdr">A9 — Monitoring Status Kendala</p>', unsafe_allow_html=True)
    try:
        where, params = _build_where(filters)
        status_kend = run_query(f"""
            SELECT status_wo,
                   COUNT(*) AS jumlah,
                   SUM(is_sla_tercapai) AS sla_ok,
                   SUM(is_workfail) AS work_fail
            FROM workorders
            WHERE status_wo IS NOT NULL AND status_wo != ''
            {(' AND ' + where[6:]) if where else ''}
            GROUP BY status_wo
            ORDER BY jumlah DESC
            LIMIT 15
        """, params)
        df_sk = pd.DataFrame(status_kend)
        if not df_sk.empty:
            df_sk["jumlah"]    = pd.to_numeric(df_sk["jumlah"], errors="coerce").fillna(0).astype(int)
            df_sk["sla_ok"]    = pd.to_numeric(df_sk["sla_ok"], errors="coerce").fillna(0).astype(int)
            df_sk["work_fail"] = pd.to_numeric(df_sk["work_fail"], errors="coerce").fillna(0).astype(int)
            df_sk = df_sk.sort_values("jumlah", ascending=True)

            # Stack bar: SLA OK + Work Fail + Others
            df_sk["others"] = (df_sk["jumlah"] - df_sk["sla_ok"] - df_sk["work_fail"]).clip(0)

            fig_sk = go.Figure()
            fig_sk.add_trace(go.Bar(
                y=df_sk["status_wo"], x=df_sk["sla_ok"],
                name="SLA OK", orientation="h",
                marker=dict(color=COLORS["success"]),
                text=df_sk["sla_ok"], textposition="inside",
                textfont=dict(size=9, color="white")
            ))
            fig_sk.add_trace(go.Bar(
                y=df_sk["status_wo"], x=df_sk["work_fail"],
                name="Work Fail", orientation="h",
                marker=dict(color=COLORS["primary"]),
                text=df_sk["work_fail"], textposition="inside",
                textfont=dict(size=9, color="white")
            ))
            fig_sk.add_trace(go.Bar(
                y=df_sk["status_wo"], x=df_sk["others"],
                name="Lainnya", orientation="h",
                marker=dict(color=COLORS["info"]),
            ))
            fig_sk.update_layout(barmode="stack")
            apply_plotly_defaults(fig_sk, height=380)
            fig_sk.update_layout(
                xaxis=dict(title="Jumlah WO"),
                yaxis=dict(tickfont=dict(size=9)),
                legend=dict(orientation="h", y=-0.15, font=dict(size=10)),
                margin=dict(l=0, r=0, t=10, b=40)
            )
            st.plotly_chart(fig_sk, use_container_width=True, key="status_kendala")
        else:
            st.info("Belum ada data status WO.")
    except Exception as e:
        st.info("💡 Belum ada data.") if "no such table" in str(e).lower() else st.error(f"❌ {e}")

# ══════════════════════════════════════════════════════════════════════════════
# SECTION: DISTRIBUSI KENDALA (3 kolom)
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.markdown('<p class="section-header">📊 Distribusi Kendala & Infrastruktur</p>', unsafe_allow_html=True)

col_d1, col_d2, col_d3 = st.columns(3)

with col_d1:
    st.markdown('<p class="sec-hdr">⚠️ Jumlah Kendala per Area</p>', unsafe_allow_html=True)
    try:
        kend_data = get_kendala_top(filters, top_n=8)
        df_kd = pd.DataFrame(kend_data)
        if not df_kd.empty:
            df_kd["jumlah"] = pd.to_numeric(df_kd["jumlah"], errors="coerce").fillna(0).astype(int)
            df_kd["label"]  = df_kd["kendala_pt1"].astype(str).str[:25]
            df_kd = df_kd.sort_values("jumlah", ascending=False)

            colors_kd = [PALETTE[i % len(PALETTE)] for i in range(len(df_kd))]
            fig_kd = go.Figure(go.Bar(
                x=df_kd["label"], y=df_kd["jumlah"],
                marker=dict(color=colors_kd, line=dict(width=0)),
                text=df_kd["jumlah"], textposition="outside",
                textfont=dict(size=9),
                hovertemplate="<b>%{x}</b><br>Jumlah: %{y:,}<extra></extra>"
            ))
            apply_plotly_defaults(fig_kd, height=300)
            fig_kd.update_layout(
                xaxis=dict(tickangle=-35, tickfont=dict(size=8)),
                yaxis=dict(title=""),
                showlegend=False,
                margin=dict(l=0, r=0, t=10, b=80)
            )
            st.plotly_chart(fig_kd, use_container_width=True, key="kendala_area")
        else:
            st.info("Belum ada data kendala.")
    except Exception as e:
        st.info("💡 Belum ada data.") if "no such table" in str(e).lower() else st.error(f"❌ {e}")

with col_d2:
    st.markdown('<p class="sec-hdr">🌐 Jumlah Infrastruktur per Area</p>', unsafe_allow_html=True)
    try:
        where, params = _build_where(filters)
        infra_sto = run_query(f"""
            SELECT sto,
                   COUNT(CASE WHEN odp IS NOT NULL AND odp != '' THEN 1 END) AS odp_count,
                   COUNT(CASE WHEN odc IS NOT NULL AND odc != '' THEN 1 END) AS odc_count,
                   COUNT(CASE WHEN gpon IS NOT NULL AND gpon != '' THEN 1 END) AS gpon_count
            FROM workorders
            WHERE sto IS NOT NULL AND sto != ''
            {(' AND ' + where[6:]) if where else ''}
            GROUP BY sto
            ORDER BY odp_count DESC
            LIMIT 8
        """, params)
        df_is = pd.DataFrame(infra_sto)
        if not df_is.empty:
            df_is = df_is.sort_values("odp_count", ascending=True)
            fig_is = go.Figure()
            fig_is.add_trace(go.Bar(
                y=df_is["sto"], x=df_is["odp_count"],
                name="ODP", orientation="h",
                marker=dict(color=COLORS["primary"])
            ))
            fig_is.add_trace(go.Bar(
                y=df_is["sto"], x=df_is["gpon_count"],
                name="GPON", orientation="h",
                marker=dict(color=COLORS["info"])
            ))
            fig_is.add_trace(go.Bar(
                y=df_is["sto"], x=df_is["odc_count"],
                name="ODC", orientation="h",
                marker=dict(color=COLORS["warning"])
            ))
            fig_is.update_layout(barmode="group")
            apply_plotly_defaults(fig_is, height=300)
            fig_is.update_layout(
                xaxis=dict(title=""),
                yaxis=dict(tickfont=dict(size=8)),
                legend=dict(orientation="h", y=-0.2, font=dict(size=9)),
                margin=dict(l=0, r=0, t=10, b=40)
            )
            st.plotly_chart(fig_is, use_container_width=True, key="infra_area")
        else:
            st.info("Belum ada data infrastruktur.")
    except Exception as e:
        st.info("💡 Belum ada data.") if "no such table" in str(e).lower() else st.error(f"❌ {e}")

with col_d3:
    st.markdown('<p class="sec-hdr">📅 Jumlah Kendala per Hari</p>', unsafe_allow_html=True)
    try:
        where, params = _build_where(filters)
        kend_hari = run_query(f"""
            SELECT nama_hari,
                   COUNT(*) AS jumlah,
                   SUM(is_workfail) AS work_fail
            FROM workorders
            WHERE nama_hari IS NOT NULL AND nama_hari != ''
            {(' AND ' + where[6:]) if where else ''}
            GROUP BY nama_hari
            ORDER BY jumlah DESC
        """, params)
        df_kh = pd.DataFrame(kend_hari)
        if not df_kh.empty:
            df_kh["jumlah"]    = pd.to_numeric(df_kh["jumlah"], errors="coerce").fillna(0).astype(int)
            df_kh["work_fail"] = pd.to_numeric(df_kh["work_fail"], errors="coerce").fillna(0).astype(int)

            day_order = ["Senin","Selasa","Rabu","Kamis","Jumat","Sabtu","Minggu"]
            df_kh["sort_key"] = df_kh["nama_hari"].apply(
                lambda x: day_order.index(x) if x in day_order else 99)
            df_kh = df_kh.sort_values("sort_key")

            fig_kh = go.Figure()
            fig_kh.add_trace(go.Bar(
                x=df_kh["nama_hari"], y=df_kh["jumlah"],
                name="Total WO",
                marker=dict(color=COLORS["info"]),
                text=df_kh["jumlah"], textposition="outside",
                textfont=dict(size=9)
            ))
            fig_kh.add_trace(go.Bar(
                x=df_kh["nama_hari"], y=df_kh["work_fail"],
                name="Work Fail",
                marker=dict(color=COLORS["primary"]),
            ))
            fig_kh.update_layout(barmode="group")
            apply_plotly_defaults(fig_kh, height=300)
            fig_kh.update_layout(
                xaxis=dict(tickangle=-20, tickfont=dict(size=9)),
                yaxis=dict(title=""),
                legend=dict(orientation="h", y=-0.2, font=dict(size=9)),
                margin=dict(l=0, r=0, t=10, b=50)
            )
            st.plotly_chart(fig_kh, use_container_width=True, key="kendala_hari")
        else:
            st.info("Belum ada data per hari.")
    except Exception as e:
        st.info("💡 Belum ada data.") if "no such table" in str(e).lower() else st.error(f"❌ {e}")

# ══════════════════════════════════════════════════════════════════════════════
# SECTION: DONUT CHARTS — Teknisi, SLA, Durasi
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.markdown('<p class="section-header">🍩 Proporsi & Komposisi</p>', unsafe_allow_html=True)

col_p1, col_p2, col_p3 = st.columns(3)

with col_p1:
    st.markdown('<p class="sec-hdr">🏢 Komposisi per Mitra</p>', unsafe_allow_html=True)
    try:
        where, params = _build_where(filters)
        mitra_data = run_query(f"""
            SELECT mitra,
                   COUNT(*) AS jumlah,
                   SUM(is_sla_tercapai) AS sla_ok,
                   ROUND(SUM(is_sla_tercapai)*100.0/COUNT(*),1) AS pct_sla
            FROM workorders
            WHERE mitra IS NOT NULL AND mitra != ''
            {(' AND ' + where[6:]) if where else ''}
            GROUP BY mitra
            ORDER BY jumlah DESC
            LIMIT 8
        """, params)
        df_mt = pd.DataFrame(mitra_data)
        if not df_mt.empty:
            df_mt["jumlah"]  = pd.to_numeric(df_mt["jumlah"], errors="coerce").fillna(0).astype(int)
            df_mt["pct_sla"] = pd.to_numeric(df_mt["pct_sla"], errors="coerce").fillna(0.0)

            fig_mt = go.Figure(go.Pie(
                labels=df_mt["mitra"], values=df_mt["jumlah"],
                hole=0.55,
                marker=dict(colors=PALETTE[:len(df_mt)], line=dict(color="#fff", width=2)),
                textinfo="percent", textfont=dict(size=10),
                hovertemplate="<b>%{label}</b><br>WO: %{value:,}<br>%{percent}<extra></extra>"
            ))
            total_mt = df_mt["jumlah"].sum()
            fig_mt.add_annotation(
                text=f"<b>{total_mt:,}</b>",
                x=0.5, y=0.5, font=dict(size=18, color="#2C1810"), showarrow=False
            )
            apply_plotly_defaults(fig_mt, height=260)
            fig_mt.update_layout(
                showlegend=True,
                legend=dict(orientation="v", x=0.78, y=0.5, font=dict(size=9)),
                margin=dict(l=0, r=60, t=10, b=10)
            )
            st.plotly_chart(fig_mt, use_container_width=True, key="donut_mitra")

            # Table mitra
            for _, row in df_mt.head(5).iterrows():
                badge = "badge-green" if row["pct_sla"] >= 85 else "badge-red"
                st.markdown(f"""
                <div style="display:flex; justify-content:space-between; align-items:center;
                            padding:4px 0; border-bottom:1px solid #F5C8BC; font-size:0.78rem;">
                    <span style="color:#2C1810; font-weight:600;">{str(row['mitra'])[:20]}</span>
                    <span style="color:#9B7B75;">{row['jumlah']:,} WO</span>
                    <span class="{badge}">{row['pct_sla']:.0f}%</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Belum ada data mitra.")
    except Exception as e:
        st.info("💡 Belum ada data.") if "no such table" in str(e).lower() else st.error(f"❌ {e}")

with col_p2:
    st.markdown('<p class="sec-hdr">🎯 Proporsi Status SLA</p>', unsafe_allow_html=True)
    try:
        sla_data = get_sla_summary(filters)
        if sla_data:
            s = sla_data[0]
            sla_pct  = float(s.get("pct_sla", 0) or 0)
            sla_ok_v = int(s.get("sla_ok", 0) or 0)
            sla_nok  = int(s.get("sla_not_ok", 0) or 0)

            fig_pie = go.Figure(go.Pie(
                labels=["SLA Tercapai", "Tidak Tercapai"],
                values=[sla_ok_v, sla_nok],
                hole=0.55,
                marker=dict(colors=[COLORS["success"], COLORS["primary"]],
                            line=dict(color="#fff", width=2)),
                textinfo="percent+label", textfont=dict(size=10),
                hovertemplate="<b>%{label}</b><br>%{value:,} WO<extra></extra>"
            ))
            fig_pie.add_annotation(
                text=f"<b>{sla_pct:.0f}%</b>",
                x=0.5, y=0.5, font=dict(size=22, color=COLORS["success"] if sla_pct >= 85 else COLORS["primary"]),
                showarrow=False
            )
            apply_plotly_defaults(fig_pie, height=260)
            fig_pie.update_layout(
                showlegend=False,
                margin=dict(l=0, r=0, t=10, b=10)
            )
            st.plotly_chart(fig_pie, use_container_width=True, key="donut_sla")

            # Stats
            st.markdown(f"""
            <div style="margin-top:8px;">
                <div style="display:flex; justify-content:space-between; align-items:center;
                            padding:5px 8px; background:#E8F5EE; border-radius:8px; margin-bottom:6px;">
                    <span style="font-size:0.78rem; font-weight:700; color:#2E7D4F;">● SLA Tercapai</span>
                    <span style="font-size:0.85rem; font-weight:800; color:#2E7D4F;">{sla_ok_v:,}</span>
                    <span style="font-size:0.72rem; color:#2E7D4F;">{sla_pct:.1f}%</span>
                </div>
                <div style="display:flex; justify-content:space-between; align-items:center;
                            padding:5px 8px; background:#FDECEA; border-radius:8px;">
                    <span style="font-size:0.78rem; font-weight:700; color:#C0392B;">● Tidak Tercapai</span>
                    <span style="font-size:0.85rem; font-weight:800; color:#C0392B;">{sla_nok:,}</span>
                    <span style="font-size:0.72rem; color:#C0392B;">{100-sla_pct:.1f}%</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Belum ada data SLA.")
    except Exception as e:
        st.info("💡 Belum ada data.") if "no such table" in str(e).lower() else st.error(f"❌ {e}")

with col_p3:
    st.markdown('<p class="sec-hdr">⏱️ Proporsi Durasi Nilai</p>', unsafe_allow_html=True)
    try:
        # Bar chart durasi grup
        grup_data = get_durasi_grup(filters)
        df_gr = pd.DataFrame(grup_data)
        if not df_gr.empty:
            df_gr["jumlah"] = pd.to_numeric(df_gr["jumlah"], errors="coerce").fillna(0).astype(int)
            order = ["<1 Hari", "1-3 Hari", "3-6 Hari", "6-9 Hari", "Over 9 Hari", "Tidak Diketahui"]
            df_gr["sort_key"] = df_gr["durasi_grup"].apply(lambda x: order.index(x) if x in order else 99)
            df_gr = df_gr.sort_values("sort_key")

            grup_colors_map = {
                "<1 Hari":          COLORS["success"],
                "1-3 Hari":         COLORS["info"],
                "3-6 Hari":         COLORS["warning"],
                "6-9 Hari":         COLORS.get("secondary", "#E8735A"),
                "Over 9 Hari":      COLORS["primary"],
                "Tidak Diketahui":  COLORS["muted"],
            }
            bar_colors_gr = [grup_colors_map.get(g, COLORS["muted"]) for g in df_gr["durasi_grup"]]

            # Donut version
            fig_gr = go.Figure(go.Pie(
                labels=df_gr["durasi_grup"], values=df_gr["jumlah"],
                hole=0.5,
                marker=dict(colors=bar_colors_gr, line=dict(color="#fff", width=2)),
                textinfo="percent", textfont=dict(size=10),
                hovertemplate="<b>%{label}</b><br>%{value:,} WO<br>%{percent}<extra></extra>"
            ))
            total_gr = df_gr["jumlah"].sum()
            fig_gr.add_annotation(
                text=f"<b>{total_gr:,}</b><br><span style='font-size:10px'>Total</span>",
                x=0.5, y=0.5,
                font=dict(size=16, color="#2C1810"), showarrow=False
            )
            apply_plotly_defaults(fig_gr, height=260)
            fig_gr.update_layout(
                showlegend=True,
                legend=dict(orientation="v", x=0.75, y=0.5, font=dict(size=8)),
                margin=dict(l=0, r=60, t=10, b=10)
            )
            st.plotly_chart(fig_gr, use_container_width=True, key="donut_durasi")

            # Table durasi
            for _, row in df_gr.iterrows():
                color = grup_colors_map.get(row["durasi_grup"], COLORS["muted"])
                st.markdown(f"""
                <div style="display:flex; justify-content:space-between; align-items:center;
                            padding:3px 0; border-bottom:1px solid #F5C8BC; font-size:0.78rem;">
                    <span style="color:{color}; font-weight:700;">■ {row['durasi_grup']}</span>
                    <span style="color:#2C1810; font-weight:600;">{row['jumlah']:,} WO</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Belum ada data durasi.")
    except Exception as e:
        st.info("💡 Belum ada data.") if "no such table" in str(e).lower() else st.error(f"❌ {e}")

# ══════════════════════════════════════════════════════════════════════════════
# SECTION: MONITORING TOTAL PENYESUAIAN + TARGET WO
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.markdown('<p class="section-header">📋 Monitoring Total & Target WO</p>', unsafe_allow_html=True)

col_m1, col_m2 = st.columns([1, 1])

with col_m1:
    st.markdown('<p class="sec-hdr">T1 — Analisis Total Pembukaan WO</p>', unsafe_allow_html=True)
    try:
        monthly = get_trend_monthly(filters)
        df_tm = pd.DataFrame(monthly)
        if not df_tm.empty:
            df_tm["total_wo"]  = pd.to_numeric(df_tm["total_wo"], errors="coerce").fillna(0).astype(int)
            df_tm["sla_ok"]    = pd.to_numeric(df_tm["sla_ok"],   errors="coerce").fillna(0).astype(int)
            df_tm["work_fail"] = pd.to_numeric(df_tm["work_fail"],errors="coerce").fillna(0).astype(int)
            df_tm["label"]     = df_tm.apply(lambda r: f"{str(r.get('nama_bulan',''))[:3]} {r.get('tahun','')}", axis=1)
            df_tm["others"]    = (df_tm["total_wo"] - df_tm["sla_ok"] - df_tm["work_fail"]).clip(0)

            fig_tm = go.Figure()
            fig_tm.add_trace(go.Bar(
                x=df_tm["label"], y=df_tm["sla_ok"],
                name="SLA OK", marker_color=COLORS["success"],
                text=df_tm["sla_ok"], textposition="inside",
                textfont=dict(size=9, color="white")
            ))
            fig_tm.add_trace(go.Bar(
                x=df_tm["label"], y=df_tm["work_fail"],
                name="Work Fail", marker_color=COLORS["primary"]
            ))
            fig_tm.add_trace(go.Bar(
                x=df_tm["label"], y=df_tm["others"],
                name="Proses", marker_color=COLORS["info"]
            ))
            fig_tm.update_layout(barmode="stack")
            apply_plotly_defaults(fig_tm, height=280)
            fig_tm.update_layout(
                xaxis=dict(tickangle=-30, tickfont=dict(size=9)),
                yaxis=dict(title=""),
                legend=dict(orientation="h", y=-0.25, font=dict(size=10)),
                margin=dict(l=0, r=0, t=10, b=60)
            )
            st.plotly_chart(fig_tm, use_container_width=True, key="total_wo_stacked")

            # Summary metrics row
            col_s1, col_s2, col_s3 = st.columns(3)
            col_s1.metric("Total WO", f"{df_tm['total_wo'].sum():,}")
            col_s2.metric("SLA OK",   f"{df_tm['sla_ok'].sum():,}")
            col_s3.metric("Work Fail",f"{df_tm['work_fail'].sum():,}")
        else:
            st.info("Belum ada data.")
    except Exception as e:
        st.info("💡 Belum ada data.") if "no such table" in str(e).lower() else st.error(f"❌ {e}")

with col_m2:
    st.markdown('<p class="sec-hdr">T2 — Monitoring Target Total Penyusunan</p>', unsafe_allow_html=True)
    try:
        sla_data = get_sla_summary(filters)
        if sla_data:
            s = sla_data[0]
            sla_pct = float(s.get("pct_sla", 0) or 0)
            total_v = int(s.get("total", 0) or 0)

            # Gauge + bar chart
            target = 85.0
            delta_val = sla_pct - target
            color_gauge = COLORS["success"] if sla_pct >= target else COLORS["primary"]

            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=sla_pct,
                number={"suffix": "%", "font": {"size": 30, "color": color_gauge}},
                delta={"reference": target,
                       "increasing": {"color": COLORS["success"]},
                       "decreasing": {"color": COLORS["primary"]},
                       "font": {"size": 14}},
                gauge={
                    "axis": {"range": [0, 100], "tickfont": {"size": 9}},
                    "bar": {"color": color_gauge, "thickness": 0.25},
                    "bgcolor": "rgba(0,0,0,0)", "borderwidth": 0,
                    "steps": [
                        {"range": [0, 60],  "color": "rgba(210,79,60,0.10)"},
                        {"range": [60, 85], "color": "rgba(212,131,42,0.10)"},
                        {"range": [85, 100],"color": "rgba(74,155,111,0.10)"},
                    ],
                    "threshold": {
                        "line": {"color": COLORS["accent"], "width": 2},
                        "thickness": 0.75, "value": 85
                    },
                },
                title={"text": f"SLA vs Target 85% | Total: {total_v:,} WO",
                       "font": {"color": COLORS["muted"], "size": 11}},
            ))
            apply_plotly_defaults(fig_gauge, height=280)
            fig_gauge.update_layout(margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig_gauge, use_container_width=True, key="gauge_target")

            # Status summary
            delta_txt = f"▲ +{delta_val:.1f}%" if delta_val >= 0 else f"▼ {delta_val:.1f}%"
            col_s1, col_s2 = st.columns(2)
            col_s1.metric("SLA Rate", f"{sla_pct:.1f}%",
                          delta_txt, delta_color="normal" if delta_val >= 0 else "inverse")
            col_s2.metric("vs Target 85%",
                          "✅ Tercapai" if sla_pct >= 85 else "⚠️ Belum Tercapai",
                          delta_txt, delta_color="normal" if delta_val >= 0 else "inverse")
        else:
            st.info("Belum ada data SLA.")
    except Exception as e:
        st.info("💡 Belum ada data.") if "no such table" in str(e).lower() else st.error(f"❌ {e}")

# ══════════════════════════════════════════════════════════════════════════════
# SECTION: ANALISIS INFRASTRUKTUR + SCATTER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.markdown('<p class="section-header">🌐 Analisis Infrastruktur & Pemetaan STO</p>', unsafe_allow_html=True)

col_i1, col_i2 = st.columns([1, 1])

with col_i1:
    st.markdown('<p class="sec-hdr">T1 — Analisis Jumlah Infrastruktur</p>', unsafe_allow_html=True)
    try:
        where, params = _build_where(filters)
        infra_raw = run_query(f"""
            SELECT
                COUNT(CASE WHEN odp        IS NOT NULL AND odp        != '' THEN 1 END) AS odp,
                COUNT(CASE WHEN odc        IS NOT NULL AND odc        != '' THEN 1 END) AS odc,
                COUNT(CASE WHEN gpon       IS NOT NULL AND gpon       != '' THEN 1 END) AS gpon,
                COUNT(CASE WHEN feeder     IS NOT NULL AND feeder     != '' THEN 1 END) AS feeder,
                COUNT(CASE WHEN distribusi IS NOT NULL AND distribusi != '' THEN 1 END) AS distribusi
            FROM workorders
            {where}
        """, params)

        if infra_raw and infra_raw[0]:
            row = infra_raw[0]
            labels_i = ["ODP", "ODC", "GPON", "Feeder", "Distribusi"]
            values_i = [int(row.get(k.lower(), 0) or 0) for k in labels_i]
            colors_i = [COLORS["primary"], COLORS["warning"], COLORS["info"], COLORS["purple"], COLORS["success"]]

            fig_i = go.Figure(go.Bar(
                x=labels_i, y=values_i,
                marker=dict(color=colors_i, line=dict(width=0)),
                text=values_i, textposition="outside",
                textfont=dict(size=11, color="#2C1810"),
                width=0.6
            ))
            apply_plotly_defaults(fig_i, height=260)
            fig_i.update_layout(
                yaxis=dict(title=""),
                showlegend=False,
                margin=dict(l=0, r=0, t=10, b=20)
            )
            st.plotly_chart(fig_i, use_container_width=True, key="infra_bar")

            # Infra metric chips
            cols_inf = st.columns(5)
            for ci, (lbl, val) in enumerate(zip(labels_i, values_i)):
                cols_inf[ci].metric(lbl, f"{val:,}")
        else:
            st.info("Belum ada data infrastruktur.")
    except Exception as e:
        st.info("💡 Belum ada data.") if "no such table" in str(e).lower() else st.error(f"❌ {e}")

with col_i2:
    st.markdown('<p class="sec-hdr">T2 — Pemetaan STO: Volume vs SLA</p>', unsafe_allow_html=True)
    try:
        sto_data = get_wo_per_sto(filters)
        df_sc = pd.DataFrame(sto_data)
        if not df_sc.empty:
            df_sc["total_wo"]  = pd.to_numeric(df_sc["total_wo"],  errors="coerce").fillna(0).astype(int)
            df_sc["pct_sla"]   = pd.to_numeric(df_sc["pct_sla"],   errors="coerce").fillna(0.0)
            df_sc["work_fail"] = pd.to_numeric(df_sc["work_fail"], errors="coerce").fillna(0).astype(int)

            fig_sc = go.Figure(go.Scatter(
                x=df_sc["total_wo"], y=df_sc["pct_sla"],
                mode="markers+text",
                text=df_sc["sto"], textposition="top center", textfont=dict(size=8),
                marker=dict(
                    size=df_sc["work_fail"].clip(5, 40) + 10,
                    color=df_sc["pct_sla"],
                    colorscale=[[0, COLORS["primary"]], [0.5, COLORS["warning"]], [1, COLORS["success"]]],
                    showscale=True,
                    colorbar=dict(title="SLA %", len=0.8, thickness=12, tickfont=dict(size=9)),
                    line=dict(color="#fff", width=1)
                ),
                hovertemplate="<b>%{text}</b><br>WO: %{x:,}<br>SLA: %{y:.1f}%<extra></extra>"
            ))
            fig_sc.add_hline(y=85, line=dict(color=COLORS["accent"], width=1.5, dash="dot"),
                             annotation_text="Target 85%",
                             annotation_font=dict(color=COLORS["accent"], size=10))
            apply_plotly_defaults(fig_sc, height=280)
            fig_sc.update_layout(
                xaxis=dict(title="Total WO", tickfont=dict(size=9)),
                yaxis=dict(title="SLA Rate (%)", tickfont=dict(size=9)),
                margin=dict(l=0, r=60, t=10, b=30)
            )
            st.plotly_chart(fig_sc, use_container_width=True, key="scatter_sto")
        else:
            st.info("Belum ada data STO.")
    except Exception as e:
        st.info("💡 Belum ada data.") if "no such table" in str(e).lower() else st.error(f"❌ {e}")

# ══════════════════════════════════════════════════════════════════════════════
# SECTION: MONITORING SG5 + MONITORING TASK
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.markdown('<p class="section-header">📋 Monitoring Teknisi & Task</p>', unsafe_allow_html=True)

col_t1, col_t2 = st.columns(2)

with col_t1:
    st.markdown('<p class="sec-hdr">A7 — Monitoring Progress SG5</p>', unsafe_allow_html=True)
    try:
        tek_data = get_teknisi_performance(filters)
        df_tek = pd.DataFrame(tek_data)
        if not df_tek.empty:
            df_tek["total_wo"]  = pd.to_numeric(df_tek["total_wo"],  errors="coerce").fillna(0).astype(int)
            df_tek["sla_ok"]    = pd.to_numeric(df_tek["sla_ok"],    errors="coerce").fillna(0).astype(int)
            df_tek["pct_sla"]   = pd.to_numeric(df_tek["pct_sla"],   errors="coerce").fillna(0.0)
            df_tek["avg_durasi"]= pd.to_numeric(df_tek["avg_durasi"],errors="coerce").fillna(0.0)

            # KPI row
            col_t1a, col_t1b, col_t1c = st.columns(3)
            col_t1a.metric("👨‍🔧 Total Teknisi", f"{len(df_tek):,}")
            col_t1b.metric("📋 Total WO",        f"{df_tek['total_wo'].sum():,}")
            col_t1c.metric("🎯 Avg SLA",          f"{df_tek['pct_sla'].mean():.1f}%")

            # Top teknisi table
            df_top_tek = df_tek.head(8).copy()
            df_top_tek["nama_short"] = df_top_tek["nama_teknisi"].astype(str).str[:22]

            for _, row in df_top_tek.iterrows():
                badge_cls = "badge-green" if row["pct_sla"] >= 85 else "badge-red"
                sla_txt   = f"{row['pct_sla']:.0f}%"
                st.markdown(f"""
                <div style="display:flex; justify-content:space-between; align-items:center;
                            padding:5px 6px; border-bottom:1px solid #F5C8BC; font-size:0.78rem; gap:8px;">
                    <span style="color:#2C1810; font-weight:600; flex:2;">{row['nama_short']}</span>
                    <span style="color:#9B7B75; flex:1; text-align:center;">{row['total_wo']:,} WO</span>
                    <span style="color:#9B7B75; flex:1; text-align:center;">{row['avg_durasi']:.1f}h</span>
                    <span class="{badge_cls}" style="flex:0.8; text-align:center;">{sla_txt}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Belum ada data teknisi.")
    except Exception as e:
        st.info("💡 Belum ada data.") if "no such table" in str(e).lower() else st.error(f"❌ {e}")

with col_t2:
    st.markdown('<p class="sec-hdr">A11 — Monitoring Task WO</p>', unsafe_allow_html=True)
    try:
        where, params = _build_where(filters)
        task_data = run_query(f"""
            SELECT status_wo,
                   COUNT(*) AS jumlah,
                   SUM(is_sla_tercapai) AS sla_ok,
                   SUM(is_workfail) AS work_fail,
                   ROUND(AVG(durasi_hari),1) AS avg_dur
            FROM workorders
            WHERE status_wo IS NOT NULL AND status_wo != ''
            {(' AND ' + where[6:]) if where else ''}
            GROUP BY status_wo
            ORDER BY jumlah DESC
        """, params)
        df_task = pd.DataFrame(task_data)
        if not df_task.empty:
            df_task["jumlah"]    = pd.to_numeric(df_task["jumlah"],    errors="coerce").fillna(0).astype(int)
            df_task["sla_ok"]    = pd.to_numeric(df_task["sla_ok"],    errors="coerce").fillna(0).astype(int)
            df_task["work_fail"] = pd.to_numeric(df_task["work_fail"], errors="coerce").fillna(0).astype(int)
            df_task["avg_dur"]   = pd.to_numeric(df_task["avg_dur"],   errors="coerce").fillna(0.0)

            total_task = df_task["jumlah"].sum()
            col_t2a, col_t2b = st.columns(2)
            col_t2a.metric("📊 Total WO",    f"{total_task:,}")
            col_t2b.metric("🏷️ Jenis Status", f"{len(df_task)}")

            # Render table
            for _, row in df_task.iterrows():
                pct = (row["jumlah"] / total_task * 100) if total_task > 0 else 0
                wf  = row["work_fail"]
                badge_wf = f'<span class="badge-red">{wf} WF</span>' if wf > 0 else ""
                st.markdown(f"""
                <div style="display:flex; justify-content:space-between; align-items:center;
                            padding:5px 6px; border-bottom:1px solid #F5C8BC; font-size:0.78rem; gap:6px;">
                    <span style="color:#2C1810; font-weight:600; flex:2;">{row['status_wo']}</span>
                    <span style="color:#9B7B75; flex:1; text-align:right;">{row['jumlah']:,}</span>
                    <span style="color:#9B7B75; flex:0.8; text-align:right;">{pct:.1f}%</span>
                    <span style="color:#9B7B75; flex:0.8; text-align:right;">{row['avg_dur']:.1f}h</span>
                    {badge_wf}
                </div>
                """, unsafe_allow_html=True)
            st.markdown(f"""
            <div style="margin-top:8px; font-size:0.72rem; color:#9B7B75; text-align:right;">
                ⚠️ WF = Work Fail · h = rata-rata durasi (hari)
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Belum ada data task WO.")
    except Exception as e:
        st.info("💡 Belum ada data.") if "no such table" in str(e).lower() else st.error(f"❌ {e}")

# ══════════════════════════════════════════════════════════════════════════════
# SECTION: DETAIL TABLE — WORK ORDER TERBARU
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.markdown('<p class="section-header">📑 Detail Data Work Order Terkini</p>', unsafe_allow_html=True)

try:
    where, params = _build_where(filters)
    recent_wo = run_query(f"""
        SELECT
            tanggal_order, wo_id, sto,
            TRIM(SUBSTRING_INDEX(COALESCE(nik_teknisi,''), ' - ', -1)) AS nama_teknisi,
            mitra,
            segment, layanan, status_wo,
            ROUND(durasi_hari,1) AS durasi_hari,
            is_sla_tercapai, is_workfail,
            kendala_pt1, odp
        FROM workorders
        WHERE tanggal_order IS NOT NULL
        {(' AND ' + where[6:]) if where else ''}
        ORDER BY tanggal_order DESC
        LIMIT 100
    """, params)

    df_detail = pd.DataFrame(recent_wo)
    if not df_detail.empty:
        # Clean and rename
        col_map = {
            "tanggal_order":   "Tgl Order",
            "wo_id":           "WO ID",
            "sto":             "STO",
            "nama_teknisi":    "Teknisi",
            "mitra":           "Mitra",
            "segment":         "Segment",
            "layanan":         "Layanan",
            "status_wo":       "Status WO",
            "durasi_hari":     "Durasi (hr)",
            "is_sla_tercapai": "SLA OK",
            "is_workfail":     "Work Fail",
            "kendala_pt1":     "Kendala",
            "odp":             "ODP",
        }
        df_detail = df_detail.rename(columns=col_map)
        df_detail["SLA OK"]    = df_detail["SLA OK"].apply(lambda x: "✅" if x == 1 else "❌")
        df_detail["Work Fail"] = df_detail["Work Fail"].apply(lambda x: "🔴" if x == 1 else "")

        # Filter controls
        search_col, dl_col = st.columns([4, 1])
        with search_col:
            search_txt = st.text_input("🔍 Cari WO ID / STO / Teknisi / Kendala", "", key="du_search")
        with dl_col:
            st.markdown("<br>", unsafe_allow_html=True)

        if search_txt:
            mask = df_detail.apply(
                lambda row: row.astype(str).str.contains(search_txt, case=False, na=False).any(), axis=1)
            df_detail = df_detail[mask]

        st.dataframe(df_detail, use_container_width=True, height=400,
                     column_config={
                         "SLA OK":    st.column_config.TextColumn("SLA", width="small"),
                         "Work Fail": st.column_config.TextColumn("WF",  width="small"),
                         "Durasi (hr)": st.column_config.NumberColumn("Durasi", format="%.1f"),
                     })

        st.markdown(f"""
        <div style="font-size:0.75rem; color:#9B7B75; margin-top:6px; text-align:right;">
            Menampilkan {len(df_detail):,} dari 100 WO terbaru
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("💡 Belum ada data Work Order.")
except Exception as e:
    st.info("💡 Belum ada data.") if "no such table" in str(e).lower() else st.error(f"❌ {e}")

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(f"""
<div style="text-align:center; padding:12px; font-size:0.75rem; color:#9B7B75;">
    📡 <b style="color:#D24F3C;">BI Dashboard</b> · Telkom Witel Ridar · 
    Monitoring Work Order & Service Connectivity ·
    <span style="color:#D24F3C;">Update: {now}</span>
</div>
""", unsafe_allow_html=True)
