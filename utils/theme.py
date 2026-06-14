"""
Shared CSS Theme — Cream & Soft Red
Dipakai di semua halaman Streamlit.
"""

def get_theme_css() -> str:
    return """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

/* ── 1. Reset Font & Proteksi Ikon Bawaan Streamlit ── */
p, h1, h2, h3, h4, h5, h6, li, label, input, button, select, textarea, table,
[data-testid="stMetricValue"], [data-testid="stMetricLabel"], [data-testid="stMetricDelta"] div {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}

/* Mengunci agar simbol/ikon bawaan tetap memakai font ikon aslinya */
.material-icons,
.material-symbols-rounded,
[data-testid="stIconMaterial"],
summary span, 
[data-testid="stHeader"] span {
    font-family: "Material Symbols Rounded", "Material Icons", sans-serif !important;
}

/* ── 2. Top Header & Background Utama ── */
[data-testid="stHeader"] {
    background-color: rgba(0,0,0,0) !important;
}
.main, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
    background-color: #FDF6F0 !important;
}

/* ── 3. Sidebar (Warna Teks & Ikon Gelap Sempurna) ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #FFF1EB 0%, #FDE8DF 100%) !important;
    border-right: 1.5px solid #F5C8BC !important;
}

/* Memaksa semua teks di dalam sidebar berwarna cokelat gelap */
[data-testid="stSidebar"] p, 
[data-testid="stSidebar"] span, 
[data-testid="stSidebar"] label {
    color: #2C1810 !important;
}

/* MEMPERBAIKI WARNA IKON SIDEBAR: Mengubah ikon SVG dan material icon menjadi cokelat gelap */
[data-testid="stSidebar"] [data-testid="stIconMaterial"],
[data-testid="stSidebar"] svg,
[data-testid="stSidebar"] .material-icons,
[data-testid="stSidebar"] .material-symbols-rounded {
    color: #2C1810 !important;
    fill: #2C1810 !important;
}

/* Styling Menu Navigasi */
[data-testid="stSidebarNavItems"] a {
    border-radius: 10px !important;
    margin: 2px 8px !important;
    transition: all 0.25s ease !important;
}

/* Efek Hover Menu Sidebar (Ikon & Teks Berubah Merah Lembut) */
[data-testid="stSidebarNavItems"] a:hover {
    background: rgba(210,78,60,0.08) !important;
}
[data-testid="stSidebarNavItems"] a:hover span,
[data-testid="stSidebarNavItems"] a:hover svg,
[data-testid="stSidebarNavItems"] a:hover [data-testid="stIconMaterial"] {
    color: #C0392B !important;
    fill: #C0392B !important;
}

/* Tampilan Menu yang Sedang Aktif */
[data-testid="stSidebarNavItems"] a[aria-current="page"] {
    background: rgba(210,78,60,0.15) !important;
}
[data-testid="stSidebarNavItems"] a[aria-current="page"] span,
[data-testid="stSidebarNavItems"] a[aria-current="page"] svg,
[data-testid="stSidebarNavItems"] a[aria-current="page"] [data-testid="stIconMaterial"] {
    color: #C0392B !important;
    fill: #C0392B !important;
    font-weight: 700 !important;
}

/* ── 4. Expander Filter (Putih Bersih & Bebas Glitch Teks) ── */
[data-testid="stExpander"] {
    background-color: #FFFFFF !important;
    border: 1.5px solid #F5C8BC !important;
    border-radius: 12px !important;
}
[data-testid="stExpander"] details,
[data-testid="stExpander"] summary {
    background-color: #FFFFFF !important;
    color: #2C1810 !important;
    border-radius: 12px !important;
}
[data-testid="stExpander"] summary:hover {
    background-color: #FFF1EB !important;
}
[data-testid="stExpander"] summary p {
    font-weight: 700 !important;
    color: #2C1810 !important;
}

/* ── 5. Input & Multiselect (Warna Putih Bersih) ── */
[data-baseweb="select"] > div,
[data-testid="stMultiSelect"] > div > div {
    background-color: #FFFFFF !important;
    border: 1.5px solid #F5C8BC !important;
    border-radius: 10px !important;
    color: #2C1810 !important;
}
[data-baseweb="select"] div {
    color: #2C1810 !important;
}
[data-baseweb="tag"] {
    background-color: #FFF1EB !important;
    border: 1px solid #F5C8BC !important;
}
[data-baseweb="tag"] span {
    color: #C0392B !important;
    font-weight: 600 !important;
}
[data-baseweb="select"] [data-baseweb="icon"] svg,
[data-baseweb="tag"] span[role="presentation"] svg {
    fill: #D24F3C !important;
}
ul[role="listbox"], [data-baseweb="popover"], [data-baseweb="menu"] {
    background-color: #FFFFFF !important;
}
li[role="option"] {
    color: #2C1810 !important;
    background-color: #FFFFFF !important;
}
li[role="option"]:hover, li[role="option"][aria-selected="true"] {
    background-color: #FFF1EB !important;
    color: #D24F3C !important;
}

/* ── 6. Metric Cards & Typography Halaman Utama ── */
h1, h2, h3, h4, h5 { color: #2C1810 !important; }
p, li, div, label { color: #4A2C20 !important; }

[data-testid="metric-container"] {
    background: #FFFFFF !important;
    border: 1.5px solid #F5C8BC !important;
    border-radius: 16px !important;
    padding: 20px !important;
    box-shadow: 0 2px 12px rgba(180,80,60,0.08) !important;
    transition: all 0.3s ease !important;
}
[data-testid="metric-container"]:hover {
    border-color: #D24F3C !important;
    box-shadow: 0 6px 24px rgba(180,80,60,0.18) !important;
    transform: translateY(-3px) !important;
}
[data-testid="stMetricLabel"] {
    color: #9B7B75 !important;
    font-size: 0.75rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.8px !important;
    font-weight: 600 !important;
}
[data-testid="stMetricValue"] {
    color: #2C1810 !important;
    font-weight: 800 !important;
    font-size: 1.75rem !important;
}
[data-testid="stMetricDelta"] > div {
    font-size: 0.8rem !important;
    font-weight: 600 !important;
}

/* ── 7. Komponen Kustom Tambahan (Card, Alert, Scrollbar) ── */
.section-header {
    font-size: 1.15rem;
    font-weight: 700;
    color: #2C1810;
    padding: 10px 0 8px 0;
    border-bottom: 2.5px solid #F5C8BC;
    margin-bottom: 16px;
}
.custom-card {
    background: #FFFFFF;
    border: 1.5px solid #F5C8BC;
    border-radius: 16px;
    padding: 24px;
    margin: 10px 0;
    box-shadow: 0 2px 12px rgba(180,80,60,0.07);
    transition: all 0.3s ease;
}
.custom-card:hover {
    box-shadow: 0 6px 24px rgba(180,80,60,0.14);
    transform: translateY(-2px);
    border-color: #D24F3C;
}
.page-header {
    background: linear-gradient(135deg, #FFF1EB 0%, #FDE8DF 100%);
    border: 1.5px solid #F5C8BC;
    border-radius: 20px;
    padding: 28px 36px;
    margin-bottom: 28px;
    box-shadow: 0 2px 16px rgba(180,80,60,0.08);
}
hr { border-color: #F5C8BC !important; }
::-webkit-scrollbar { width: 7px; height: 7px; }
::-webkit-scrollbar-track { background: #FDF6F0; }
::-webkit-scrollbar-thumb { background: #E8A090; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #D24F3C; }

[data-testid="stAlert"] {
    border-radius: 12px !important;
    font-weight: 500 !important;
}
[data-testid="stAlert"][data-baseweb="notification"] {
    background: #FFF1EB !important;
    border-left: 4px solid #D24F3C !important;
    color: #3D1E18 !important;
}
div[data-testid="stNotificationContentInfo"] {
    background: #E8F5E8 !important;
    border-color: #4A9B6F !important;
}
</style>
"""

# ── Plotly layout defaults ──────────────────────────────────────────────────────
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="#FEFAF8",
    font=dict(color="#2C1810", family="Plus Jakarta Sans"),
    margin=dict(l=0, r=0, t=20, b=0),
)

GRID_COLOR = "rgba(180,80,60,0.08)"
AXIS_COLOR = "#D4B5AE"

# Color palette
COLORS = {
    "primary":   "#D24F3C",
    "secondary": "#E8735A",
    "accent":    "#C0392B",
    "cream":     "#FDF6F0",
    "cream_mid": "#FFF1EB",
    "success":   "#4A9B6F",
    "warning":   "#D4832A",
    "info":      "#4A7EC0",
    "purple":    "#8B5CF6",
    "muted":     "#9B7B75",
    "border":    "#F5C8BC",
}

PALETTE = [
    "#D24F3C", "#E8735A", "#D4832A", "#4A9B6F",
    "#4A7EC0", "#8B5CF6", "#C0392B", "#2E7D4F",
    "#1A5D8E", "#6D3B8B", "#B7950B", "#117A65",
]

def apply_plotly_defaults(fig, height: int = 380):
    """Apply consistent Plotly layout to a figure."""
    fig.update_layout(
        **PLOTLY_LAYOUT,
        height=height,
        xaxis=dict(
            gridcolor=GRID_COLOR,
            linecolor=AXIS_COLOR,
            tickfont=dict(color="#5A3028"),
            title_font=dict(color="#3D1E18"),
        ),
        yaxis=dict(
            gridcolor=GRID_COLOR,
            linecolor=AXIS_COLOR,
            tickfont=dict(color="#5A3028"),
            title_font=dict(color="#3D1E18"),
        ),
        legend=dict(
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="#F5C8BC",
            borderwidth=1,
            font=dict(color="#2C1810"),
        ),
    )
    return fig