"""
Shared CSS Theme — Cream & Soft Red
Dipakai di semua halaman Streamlit.
"""


def get_theme_css() -> str:
    return """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

/* ── Reset & Base ─────────────────────────────────────────── */
* { font-family: 'Plus Jakarta Sans', sans-serif !important; }
*:focus { outline: none !important; box-shadow: none !important; }

/* ── Background ───────────────────────────────────────────── */
.main,
[data-testid="stAppViewContainer"] {
    background: #FDF6F0 !important;
}
[data-testid="stMain"] {
    background: #FDF6F0 !important;
}

/* ── Sidebar ──────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #FFF1EB 0%, #FDE8DF 100%) !important;
    border-right: 1.5px solid #F5C8BC !important;
}
[data-testid="stSidebar"] * {
    color: #3D1E18 !important;
}
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stMarkdown {
    color: #5A3028 !important;
}
[data-testid="stSidebarNavItems"] a {
    color: #5A3028 !important;
    border-radius: 10px !important;
    margin: 2px 8px !important;
    font-weight: 500 !important;
    transition: all 0.25s ease !important;
}
[data-testid="stSidebarNavItems"] a:hover {
    background: rgba(210,78,60,0.12) !important;
    color: #C0392B !important;
    transform: translateX(4px) !important;
}
[data-testid="stSidebarNavItems"] a[aria-current="page"] {
    background: rgba(210,78,60,0.18) !important;
    color: #C0392B !important;
    font-weight: 700 !important;
}

/* ── Typography ───────────────────────────────────────────── */
h1, h2, h3, h4, h5 { color: #2C1810 !important; }
p, li, span, div, label { color: #4A2C20 !important; }

/* ── Metric Cards ─────────────────────────────────────────── */
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

/* ── Buttons ──────────────────────────────────────────────── */
[data-testid="baseButton-primary"],
button[kind="primary"] {
    background: linear-gradient(135deg, #D24F3C, #E8735A) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
    padding: 10px 24px !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 14px rgba(210,79,60,0.3) !important;
}
[data-testid="baseButton-primary"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 22px rgba(210,79,60,0.45) !important;
}
[data-testid="baseButton-secondary"] {
    background: #FFF1EB !important;
    color: #D24F3C !important;
    border: 1.5px solid #F5C8BC !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
}

/* ── Selects & Inputs ─────────────────────────────────────── */
[data-testid="stSelectbox"] > div > div,
[data-testid="stMultiSelect"] > div > div {
    background: #FFFFFF !important;
    border: 1.5px solid #F5C8BC !important;
    border-radius: 10px !important;
    color: #2C1810 !important;
}
[data-testid="stTextInput"] > div > div > input {
    background: #FFFFFF !important;
    border: 1.5px solid #F5C8BC !important;
    border-radius: 10px !important;
    color: #2C1810 !important;
}
/* Dropdown options */
li[role="option"] { color: #2C1810 !important; }

/* ── Expander ─────────────────────────────────────────────── */
[data-testid="stExpander"] {
    background: #FFFFFF !important;
    border: 1.5px solid #F5C8BC !important;
    border-radius: 12px !important;
}
[data-testid="stExpander"] summary {
    color: #4A2C20 !important;
    font-weight: 600 !important;
}

/* ── File Uploader ────────────────────────────────────────── */
[data-testid="stFileUploader"] {
    background: #FFF8F5 !important;
    border: 2px dashed #E8A090 !important;
    border-radius: 16px !important;
}
[data-testid="stFileUploader"] * {
    color: #5A3028 !important;
}

/* ── DataFrame / Tables ───────────────────────────────────── */
[data-testid="stDataFrame"] {
    background: #FFFFFF !important;
    border: 1px solid #F5C8BC !important;
    border-radius: 12px !important;
}
.dvn-scroller {
    background: #FFFFFF !important;
}

/* ── Alerts ───────────────────────────────────────────────── */
[data-testid="stAlert"] {
    border-radius: 12px !important;
    font-weight: 500 !important;
}
[data-testid="stAlert"][data-baseweb="notification"] {
    background: #FFF1EB !important;
    border-left: 4px solid #D24F3C !important;
    color: #3D1E18 !important;
}

/* ── Status / Info ────────────────────────────────────────── */
div[data-testid="stNotificationContentInfo"] {
    background: #E8F5E8 !important;
    border-color: #4A9B6F !important;
}

/* ── HR / Dividers ────────────────────────────────────────── */
hr { border-color: #F5C8BC !important; }

/* ── Scrollbar ────────────────────────────────────────────── */
::-webkit-scrollbar { width: 7px; height: 7px; }
::-webkit-scrollbar-track { background: #FDF6F0; }
::-webkit-scrollbar-thumb { background: #E8A090; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #D24F3C; }

/* ── Section Header ───────────────────────────────────────── */
.section-header {
    font-size: 1.15rem;
    font-weight: 700;
    color: #2C1810;
    padding: 10px 0 8px 0;
    border-bottom: 2.5px solid #F5C8BC;
    margin-bottom: 16px;
}

/* ── Card Component ───────────────────────────────────────── */
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

/* ── Badge ────────────────────────────────────────────────── */
.kpi-badge {
    display: inline-block;
    background: rgba(210,79,60,0.1);
    border: 1px solid rgba(210,79,60,0.3);
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 0.75rem;
    color: #C0392B;
    font-weight: 600;
}
.kpi-badge-green {
    display: inline-block;
    background: rgba(74,155,111,0.1);
    border: 1px solid rgba(74,155,111,0.3);
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 0.75rem;
    color: #2E7D4F;
    font-weight: 600;
}

/* ── Page Header Card ─────────────────────────────────────── */
.page-header {
    background: linear-gradient(135deg, #FFF1EB 0%, #FDE8DF 100%);
    border: 1.5px solid #F5C8BC;
    border-radius: 20px;
    padding: 28px 36px;
    margin-bottom: 28px;
    box-shadow: 0 2px 16px rgba(180,80,60,0.08);
}

/* ── Streamlit status container ───────────────────────────── */
[data-testid="stStatusWidget"] {
    background: #FFF1EB !important;
    border: 1px solid #F5C8BC !important;
    border-radius: 12px !important;
    color: #3D1E18 !important;
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
