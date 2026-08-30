"""
Wondr by BNI visual identity — vivid orange primary with purple, teal, lime
and cream accents, sampled from the Wondr brand artwork. Approximate /
inspired by the public brand, not a verified brand-guideline spec; this
dashboard is an internal prototype, not an official BNI publication.

The legacy token names (NAVY, ORANGE, ...) are kept so every existing import
keeps working — only their VALUES moved to the Wondr palette. NAVY is now
the palette's dark anchor (deep purple), not BNI navy.
"""
import streamlit as st

# --- Wondr palette ---------------------------------------------------------
WONDR_ORANGE = "#FF6A00"
WONDR_ORANGE_DEEP = "#E25200"
WONDR_PURPLE = "#7C4DFF"
WONDR_PURPLE_DEEP = "#3D1E8A"
WONDR_TEAL = "#00C4CC"
WONDR_LIME = "#C6E84E"
WONDR_CREAM = "#FBF3B9"
WONDR_INK = "#1E1633"

# --- legacy aliases (same names, Wondr values) ------------------------------
NAVY = WONDR_PURPLE_DEEP      # dark anchor: sidebar, headings, KPI values
NAVY_LIGHT = WONDR_PURPLE
ORANGE = WONDR_ORANGE
ORANGE_DARK = WONDR_ORANGE_DEEP
BG = "#FFF8F2"                # warm off-white so the orange reads as brand
CARD = "#FFFFFF"
TEXT = WONDR_INK
TEXT_MUTED = "#6B6480"
BORDER = "#EADFF2"
GREEN = "#00A88B"
AMBER = "#C9A227"
RED = "#D93025"

DATA_TYPE_COLORS = {
    "observed": GREEN,
    "synthetic": TEXT_MUTED,
    "illustrative": ORANGE_DARK,
    "assumption": AMBER,
    "assumption-based": AMBER,
    "internal_assumption": AMBER,
    "regulatory_fact": NAVY,
    "no_regulatory_basis": RED,
    "calculated": NAVY_LIGHT,
}

CATEGORICAL_SEQUENCE = [WONDR_ORANGE, WONDR_PURPLE, WONDR_TEAL, WONDR_LIME,
                        WONDR_PURPLE_DEEP, WONDR_ORANGE_DEEP]


def inject_global_css():
    st.markdown(f"""
    <style>
    .stApp {{ background: {BG}; font-size: 1.1rem; }}
    html, body, [class*="css"] {{ font-family: 'Inter', 'Segoe UI', system-ui, sans-serif; }}
    h1, h2, h3 {{ color: {NAVY}; font-weight: 700; }}
    h4, h5 {{ color: {NAVY}; font-weight: 700; }}
    h4 {{ font-size: 1.35rem; }}
    h5 {{ font-size: 1.15rem; }}
    /* Baseline bump: captions and table text were the two things that got
       unreadable first, so they are raised more than the body copy. */
    [data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p {{ font-size: 0.97rem; }}
    [data-testid="stMarkdownContainer"] p, [data-testid="stMarkdownContainer"] li {{ font-size: 1.08rem; }}
    [data-testid="stDataFrame"] {{ font-size: 1.02rem; }}
    [data-testid="stMetricValue"] {{ font-size: 1.9rem; }}
    [data-testid="stMetricLabel"], [data-testid="stMetricLabel"] p {{ font-size: 0.98rem; }}
    [data-testid="stWidgetLabel"], [data-testid="stWidgetLabel"] p,
    label[data-testid="stWidgetLabel"] > div {{ font-size: 1.02rem; font-weight: 600; }}
    .stTabs [data-baseweb="tab"] {{ font-size: 1.05rem; font-weight: 600; }}
    .stTabs [aria-selected="true"] {{ color: {WONDR_ORANGE} !important; }}
    .stTabs [data-baseweb="tab-highlight"] {{ background: {WONDR_ORANGE} !important; }}
    [data-baseweb="tag"] {{ background: {WONDR_PURPLE} !important; }}
    [data-testid="stSlider"] [role="slider"] {{ background: {WONDR_ORANGE} !important; }}
    .stButton button[kind="primary"] {{ background: {WONDR_ORANGE}; border-color: {WONDR_ORANGE}; }}
    [data-testid="stMetricValue"] {{ color: {WONDR_PURPLE_DEEP}; }}
    /* Pipeline / lifecycle stage labels (Raw Listings, Cleaned, Valid, ...)
       read as headings, so they are set bold wherever Plotly renders them. */
    .js-plotly-plot .yaxislayer-above text, .js-plotly-plot .xaxislayer-above text {{ font-weight: 600 !important; }}
    /* Charts sat in tall default blocks with a gap above and below each one.
       Tightening the vertical rhythm puts adjacent graphs on one screen. */
    [data-testid="stPlotlyChart"] {{ margin-top: -6px; margin-bottom: -10px; }}
    [data-testid="stVerticalBlock"] {{ gap: 0.6rem; }}
    [data-testid="stHorizontalBlock"] {{ gap: 0.8rem; }}
    [data-testid="stElementContainer"]:has(> [data-testid="stPlotlyChart"]) {{ margin-bottom: 0; }}
    [data-testid="stSidebar"] {{ background: linear-gradient(180deg, {WONDR_PURPLE_DEEP} 0%, {WONDR_INK} 100%); }}
    [data-testid="stSidebar"] * {{ color: #F6EEFF !important; }}
    [data-testid="stSidebar"] .stRadio label {{ font-size: 1.02rem; }}
    [data-testid="stSidebar"] .stRadio [role="radiogroup"] > label {{
        border-radius: 10px; padding: 6px 10px; margin-bottom: 2px; transition: background .15s; }}
    [data-testid="stSidebar"] .stRadio [role="radiogroup"] > label:hover {{ background: rgba(255,106,0,0.18); }}
    [data-testid="stSidebar"] [role="radiogroup"] input:checked + div {{ color: {WONDR_LIME} !important; }}
    [data-testid="stMetricValue"] {{ color: {NAVY}; font-weight: 700; }}
    [data-testid="stMetricLabel"] {{ color: {TEXT_MUTED}; }}
    /* Container chrome is deliberately neutral: no accent borders, tinted
       fills or drop shadows on bounding boxes. Colour is reserved for data. */
    div[data-testid="stExpander"] {{ background: {CARD}; border: 1px solid {BORDER};
                                     border-radius: 10px; box-shadow: none; }}
    div[data-testid="stExpander"] summary:hover {{ color: {TEXT} !important; }}
    div[data-testid="stExpander"] details {{ border-color: {BORDER} !important; }}
    [data-testid="stAlert"] {{ background: {CARD} !important; border: 1px solid {BORDER} !important;
                               border-radius: 10px; box-shadow: none; color: {TEXT} !important; }}
    [data-testid="stAlert"] * {{ color: {TEXT} !important; }}
    [data-testid="stAlertContentInfo"], [data-testid="stAlertContentWarning"],
    [data-testid="stAlertContentSuccess"], [data-testid="stAlertContentError"] {{ background: transparent !important; }}
    div[data-testid="stVerticalBlockBorderWrapper"] {{ box-shadow: none; }}
    [data-testid="stNotification"] {{ box-shadow: none; }}
    .block-container {{ padding-top: 1.6rem; }}
    hr {{ border-color: {BORDER}; }}
    .bni-header {{
        background:
            radial-gradient(circle at 88% 18%, {WONDR_LIME}cc 0 12%, transparent 12.5%),
            radial-gradient(circle at 97% 76%, {WONDR_TEAL}cc 0 9%, transparent 9.5%),
            radial-gradient(circle at 74% 96%, {WONDR_PURPLE}dd 0 10%, transparent 10.5%),
            radial-gradient(circle at 60% 8%, {WONDR_CREAM}bb 0 7%, transparent 7.5%),
            linear-gradient(120deg, {WONDR_ORANGE} 0%, {WONDR_ORANGE_DEEP} 100%);
        padding: 28px 32px; border-radius: 14px; color: #333333; margin-bottom: 18px;
        box-shadow: none;
    }}
    .bni-header .accent {{ color: {WONDR_LIME}; }}
    .bni-header .subtitle {{ color: #333333; font-size: 1.0rem; margin-top: 6px; }}
    .bni-badge {{ display:inline-block; padding:2px 10px; border-radius:999px; font-size:0.72rem;
                  font-weight:700; letter-spacing:0.02em; text-transform:uppercase; }}
    .section-tag {{ color:{ORANGE}; font-weight:700; letter-spacing:0.08em; font-size:0.78rem;
                     text-transform:uppercase; margin-bottom:2px; }}
    </style>
    """, unsafe_allow_html=True)


def data_badge(data_type: str) -> str:
    labels = {
        "observed": "Observed / Real", "synthetic": "Synthetic", "illustrative": "Illustrative",
        "assumption": "Assumption", "assumption-based": "Assumption-based",
        "internal_assumption": "Internal Assumption", "regulatory_fact": "Regulatory Fact",
        "no_regulatory_basis": "No Regulatory Basis Found", "calculated": "Calculated",
    }
    color = DATA_TYPE_COLORS.get(data_type, TEXT_MUTED)
    label = labels.get(data_type, data_type)
    return f'<span class="bni-badge" style="background:{color}20;color:{color};border:1px solid {color}55;">{label}</span>'
