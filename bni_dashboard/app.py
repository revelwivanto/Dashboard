import base64
from pathlib import Path

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from components.styling import (inject_global_css, data_badge, NAVY, NAVY_LIGHT, ORANGE,
                                TEXT, TEXT_MUTED, CATEGORICAL_SEQUENCE, GREEN, AMBER,
                                WONDR_TEAL as TEAL_ACCENT, WONDR_LIME as LIME_ACCENT)
from components.kpi_card import kpi_row
from components.flow import (provenance_chain_html, conditional_requirements_flow_html,
                             business_story_cards_html)
from utils import data_loader as dl
from utils import procurement_calc as pc
from utils import rag_metrics as rm
from utils import governance as gov
from utils import roi_calc as rc

st.set_page_config(page_title="BNI | Procurement, Legal-RAG & Governance Intelligence", page_icon="🏦", layout="wide")
inject_global_css()

# ---------------------------------------------------------------- header --
st.markdown(f"""
<div class="bni-header">
  <div style="font-size:0.75rem;letter-spacing:0.1em;color:{TEXT};text-transform:uppercase;">Credits to Hafizh Yasril and Revel</div>
  <h1 style="color:{TEXT};margin:6px 0 0 0;">Legal Document Creation, Citation with RAG <span class="accent">&amp;</span> Procurement Efficiency / Anti-Corruption</h1>
  <div class="subtitle">Evidence-based laptop procurement benchmarking, RAG-grounded legal document intelligence, and governance indicators — for BNI management review.</div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------- nav -----
ASSETS = Path(__file__).resolve().parent / "assets"
LOGO_HEIGHT_PX = 26  # both marks scale to this height; width follows aspect

_logos = [ASSETS / "LogoBNI.webp", ASSETS / "LogoDanantara.png"]
_present = [p for p in _logos if p.exists()]
if _present:
    # Side by side, top-left of the sidebar, on a white plate because both
    # marks are dark-on-transparent and the sidebar is deep purple. Rendered
    # as inline <img> rather than st.image so the two can share a common
    # HEIGHT — their aspect ratios differ enough (BNI is ~3.4:1, Danantara
    # ~1:1) that matching widths would render one visibly larger.
    @st.cache_data(show_spinner=False)
    def _logo_data_uri(path_str: str, mtime: float) -> str:
        """Trim a logo to its visible ink before it is scaled.

        Matching canvas heights is not the same as matching mark heights: the
        Danantara PNG's artwork fills only ~19% of its square canvas, so at a
        shared canvas height it rendered roughly a fifth the size of the BNI
        mark, which fills its canvas edge to edge. Cropping to the content
        bounding box first makes the shared height apply to the marks
        themselves. Cached on (path, mtime) so a replaced file is re-read.
        """
        from io import BytesIO
        raw = Path(path_str).read_bytes()
        try:
            from PIL import Image, ImageChops
            im = Image.open(BytesIO(raw)).convert("RGBA")
            # Prefer the alpha bounds; fall back to "everything not near-white"
            # for logos shipped flattened onto a white background.
            box = im.getchannel("A").getbbox()
            if box is None or box == (0, 0, *im.size):
                diff = ImageChops.difference(im.convert("RGB"),
                                             Image.new("RGB", im.size, (255, 255, 255)))
                box = diff.convert("L").point(lambda v: 255 if v > 12 else 0).getbbox()
            if box and box != (0, 0, *im.size):
                im = im.crop(box)
            buf = BytesIO()
            im.save(buf, format="PNG")
            return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("ascii")
        except Exception:
            # Pillow missing or the file is not decodable — ship it untrimmed
            # rather than dropping the logo entirely.
            mime = "image/webp" if path_str.lower().endswith(".webp") else "image/png"
            return f"data:{mime};base64," + base64.b64encode(raw).decode("ascii")

    _tags = []
    for _p in _present:
        _uri = _logo_data_uri(str(_p), _p.stat().st_mtime)
        _tags.append(f'<img src="{_uri}" style="height:{LOGO_HEIGHT_PX}px;width:auto;'
                     f'max-width:100%;display:block;" />')
    st.sidebar.markdown(
        '<div style="background:#FFFFFF;border-radius:9px;padding:8px 10px;margin-bottom:12px;'
        'display:flex;align-items:center;justify-content:flex-start;gap:12px;flex-wrap:wrap;">'
        + "".join(_tags) + "</div>",
        unsafe_allow_html=True)
else:
    st.sidebar.caption(f"⚠️ Logo belum ada — letakkan `LogoBNI.webp` & `LogoDanantara.png` di `{ASSETS.name}/`")

PAGES = ["📊  Executive Summary", "🛒  Procurement Intelligence",
         "⚖️  Legal & RAG Intelligence", "🛡️  Governance & Anti-Corruption"]
st.sidebar.markdown("### Navigasi")
page = st.sidebar.radio("", PAGES, label_visibility="collapsed")
st.sidebar.divider()
st.sidebar.caption("Legenda label data: **Observed/Real**, **Synthetic**, **Illustrative**, **Assumption**, **Calculated**.")

# ---------------------------------------------------------------- load ----
listings = dl.load_marketplace_listings()
history_source = dl.load_procurement_history()
history = dl.procurement_history_view(history_source)
scenarios = dl.load_scenarios()
legal_docs = dl.load_legal_documents()
rag_answers = dl.load_rag_answers()
citations = dl.load_citations()
pilot_metrics = dl.load_pilot_metrics().set_index("metric_id")
bu_impact = dl.load_business_unit_impact()
process_time = dl.load_process_time()
doc_prep = dl.load_doc_prep_time()
pilot_ramp = dl.load_pilot_ramp()
roi_scenarios = dl.load_roi_scenarios()
citation_evals = dl.load_citation_evaluations()
investment_breakdown = dl.load_investment_breakdown()
process_annual_volume = dl.load_process_annual_volume()

valid_listings = pc.valid_listings(listings)

SERIES_MARKET = "Marketplace (harga pasar)"
SERIES_HISTORY = "Historical procurement (BNI)"
SERIES_REQUEST = "Permintaan user (synthetic request)"
SERIES_COLORS = {SERIES_MARKET: ORANGE, SERIES_HISTORY: NAVY_LIGHT, SERIES_REQUEST: TEAL_ACCENT}


def price_comparison_frame(market: pd.DataFrame, hist: pd.DataFrame,
                           brands=None, units=None) -> pd.DataFrame:
    """One long frame carrying the three price series the revisions ask to
    compare side by side: observed marketplace price, BNI's historical unit
    price, and the price the requester actually asked for. Same spec columns
    on every row, so any spec axis can be grouped without re-joining."""
    spec_cols = ["cpu_tier", "ram_gb", "storage_gb", "dedicated_gpu"]

    m = market[spec_cols + ["brand", "price_rp"]].copy()
    m = m.rename(columns={"price_rp": "price"})
    m["business_unit"] = pd.NA
    m["series"] = SERIES_MARKET

    h = hist.copy()
    if units:
        h = h[h.business_unit.isin(units)]
    frames = [m]
    for price_col, series_name in [("historical_unit_price_rp", SERIES_HISTORY),
                                   ("current_quote_unit_price_rp", SERIES_REQUEST)]:
        part = h[spec_cols + ["business_unit"]].copy()
        part["brand"] = h["vendor"]
        part["price"] = pd.to_numeric(h[price_col], errors="coerce")
        part["series"] = series_name
        frames.append(part)

    out = pd.concat(frames, ignore_index=True)
    if brands:
        out = out[out.brand.isin(brands)]
    return out.dropna(subset=["price"])


# =============================================================================================
# PAGE 1 — EXECUTIVE SUMMARY
# =============================================================================================
if page == PAGES[0]:
    total_opportunity = bu_impact["estimated_annual_impact_rp"].sum()
    citation_cov = rm.citation_coverage_pct(rag_answers)
    roi_headline = pilot_metrics.loc["ROI_HEADLINE", "value"]
    docs_processed = pilot_metrics.loc["TOTAL_DOCS_PROCESSED", "value"]
    pilot_investment = float(investment_breakdown.total_rp.sum())

    st.markdown('<div class="section-tag">Business Impact Snapshot</div>', unsafe_allow_html=True)
    # Every card names the module inside the calculation dropdown that shows
    # its math, so a reader can trace any number without hunting for it.
    kpi_row([
        dict(label="Total Annual Opportunity (computed)", value=total_opportunity/1e9, prefix="Rp", suffix="B", decimals=2,
             note="▸ Modul 4 · Roll-up"),
        dict(label="ROI on Pilot Investment (Base Case)", value=roi_headline, suffix="x", decimals=2,
             note="▸ Modul 4 · Roll-up"),
        dict(label="Citation Coverage", value=citation_cov, suffix="%", decimals=1,
             note="▸ Legal & RAG · sitasi"),
    ])
    st.write("")
    kpi_row([
        # Rule pending replacement — the equation is being rewritten, so the
        # card holds its place without asserting a number.
        dict(label="Potential Corruption", value=None,
             placeholder="—", note="Rumus sedang diganti — angka ditahan"),
        dict(label="Total Marketplace Data", value=len(listings), decimals=0),
        dict(label="Documents in Prototype Corpus", value=docs_processed, decimals=0),
        dict(label="Total Pilot Investment", value=pilot_investment/1e6, prefix="Rp", suffix="jt", decimals=1,
             note="▸ Modul 1 · Investasi"),
    ])

    st.write("")
    c1, c2 = st.columns([3, 2])
    with c1:
        st.markdown("#### Impact by Business Unit")
        bu_sorted = bu_impact.sort_values("estimated_annual_impact_rp")
        # The methodology note used to sit under the chart as a wall of text;
        # it now rides on each bar's hover so the page stays readable.
        bu_sorted = bu_sorted.assign(
            metode=bu_sorted.business_unit.map(lambda u:
                "procurement_savings_benefit_rp langsung dari mesin benchmarking"
                if u == "Procurement" else
                "bagian dari time_savings_benefit_rp, dialokasikan proporsional terhadap pangsa penggunaan RAG unit ini"),
            nilai=bu_sorted.estimated_annual_impact_rp.apply(pc.fmt_rp),
        )
        fig = px.bar(bu_sorted, x="estimated_annual_impact_rp", y="business_unit",
                     orientation="h", text=bu_sorted["nilai"],
                     color_discrete_sequence=[ORANGE],
                     custom_data=["nilai", "metode"])
        fig.update_traces(
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>Dampak tahunan: %{customdata[0]}<br>"
                          "<span style='font-size:0.8em'>%{customdata[1]}</span><extra></extra>",
        )
        fig.update_layout(xaxis_title="Estimasi dampak tahunan (Rp) — skala log", yaxis_title="", showlegend=False,
                          plot_bgcolor="white", margin=dict(l=0, r=30, t=34, b=8), xaxis_type="log",
                          hoverlabel=dict(align="left"))
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.markdown("#### ROI Scenario Modeling")
        base_rows = roi_scenarios[roi_scenarios.scenario == "Base Case"]
        for _, r in base_rows.iterrows():
            st.markdown(f"""
            <div style="background:{NAVY};border:1px solid #E4E9F0;border-radius:12px;padding:12px 16px;margin-bottom:8px;">
              <div style="color:white;font-weight:700;">{r['scenario']} <span style="font-weight:400;font-size:0.72rem;">(adopsi {r['adoption_rate']*100:.0f}%, target harga = median internal)</span></div>
              <div style="color:#C9D9E8;font-size:0.78rem;display:flex;justify-content:space-between;margin-top:4px;flex-wrap:wrap;gap:4px;">
                <span>Investment: {pc.fmt_rp(r['pilot_investment_rp'])}</span>
                <span>Benefit: {pc.fmt_rp(r['est_annual_benefit_rp'])}</span>
                <span style="color:#7CD9A8;font-weight:700;">ROI: {r['roi_x']:.2f}x</span>
                <span>Payback: {r['payback_months']:.1f} mo</span>
              </div>
            </div>""", unsafe_allow_html=True)

    with st.expander("🔎 Tunjukkan perhitungannya — investasi, penghematan waktu, penghematan pengadaan, semua input & rumus", expanded=False):
        scen_pick = st.selectbox("Skenario", roi_scenarios["scenario"].tolist(),
                                 index=int(roi_scenarios.index[roi_scenarios.scenario == "Base Case"][0]))
        adoption = float(roi_scenarios.loc[roi_scenarios.scenario == scen_pick, "adoption_rate"].iloc[0])

        st.markdown("##### Modul 1 · Investasi")
        inv = investment_breakdown.sort_values("total_rp")
        figi = px.bar(inv, x="total_rp", y="component", orientation="h", text=inv.total_rp.apply(pc.fmt_rp),
                      color_discrete_sequence=[NAVY])
        figi.update_traces(textposition="outside", cliponaxis=False,
                           hovertemplate="<b>%{y}</b><br>%{text}<extra></extra>")
        figi.update_layout(height=170, margin=dict(l=0, r=110, t=4, b=4), xaxis_visible=False,
                           yaxis_title="", plot_bgcolor="white")
        st.plotly_chart(figi, use_container_width=True)
        st.caption(f"Σ = **{pc.fmt_rp(pilot_investment)}** Pilot Investment.")

        st.markdown("##### Modul 2 · Penghematan waktu")
        salary_annual = 70_749_733
        hourly_rate = rc.hourly_rate_rp(salary_annual / 12, 173.0)
        a1, a2, a3 = st.columns([2, 1, 1])
        a1.markdown(
            f"<div style='color:{TEXT};font-size:0.85rem;'>Gaji tahunan benchmark (Payscale)</div>"
            f"<div style='font-size:2.4rem;font-weight:800;color:{TEXT};line-height:1.15;'>{pc.fmt_rp(salary_annual)}</div>",
            unsafe_allow_html=True)
        a2.metric("Jam kerja/bulan", "173")
        a3.metric("Tarif per jam", pc.fmt_rp(hourly_rate))
        ts_detail = rc.time_savings_benefit(process_time, process_annual_volume, hourly_rate, adoption)
        ts_detail = ts_detail.sort_values("rp_saved_per_year")
        figt = px.bar(ts_detail, x="rp_saved_per_year", y="process_name", orientation="h",
                      text=ts_detail.rp_saved_per_year.apply(pc.fmt_rp), color_discrete_sequence=[ORANGE],
                      custom_data=["before_minutes", "after_minutes", "estimated_annual_occurrences", "hours_saved_per_year"])
        figt.update_traces(textposition="outside", cliponaxis=False,
                           hovertemplate="<b>%{y}</b><br>%{x:,.0f} Rp/tahun<br>"
                                         "%{customdata[0]}→%{customdata[1]} menit × %{customdata[2]:,} kali/tahun"
                                         "<br>%{customdata[3]:,.0f} jam dihemat<extra></extra>")
        figt.update_layout(height=190, margin=dict(l=0, r=120, t=4, b=4), xaxis_visible=False,
                           yaxis_title="", plot_bgcolor="white")
        st.plotly_chart(figt, use_container_width=True)
        st.caption(f"(before−after)/60 × kejadian/tahun × adopsi {adoption*100:.0f}% × tarif/jam. "
                   f"Σ = **{pc.fmt_rp(ts_detail.rp_saved_per_year.sum())}**. Detail per proses ada di hover.")

        st.markdown("##### Modul 3 · Penghematan pengadaan")
        # Mirrors the assistant's own lookup order: prior BNI purchases of the
        # identical machine first, marketplace only when internal history has
        # nothing comparable. Requests neither source can price are excluded.
        bm = rc.benchmarked_saving(history_source, valid_listings)
        per_unit, coverage, detail = bm["per_unit"], bm["coverage"], bm["detail"]
        annual_units = rc.annual_procurement_units(27201, 0.35, 0.25)
        proc_saving_live = per_unit * annual_units * coverage * adoption
        v1, v2, v3, v4 = st.columns(4)
        v1.metric("Cakupan benchmark", f"{coverage*100:.0f}%",
                  help=f"{bm['n_scored']:,} dari {len(detail):,} permintaan punya pembanding")
        v2.metric("Dari riwayat internal", f"{int((detail.benchmark_source=='internal').sum()):,}")
        v3.metric("Dari marketplace", f"{int(detail.benchmark_source.str.startswith('market').sum()):,}")
        v4.metric("Rata-rata kelebihan/unit", pc.fmt_rp(per_unit))
        src = (detail[detail.benchmark_source != "none"]
               .groupby("benchmark_source")
               .agg(n=("excess_rp", "size"), rata=("excess_rp", "mean")).reset_index())
        LBL = {"internal": "Riwayat internal BNI", "market-model": "Marketplace — model sama",
               "market-spec": "Marketplace — spek setara"}
        src["sumber"] = src.benchmark_source.map(LBL).fillna(src.benchmark_source)
        figp = px.bar(src.sort_values("rata"), x="rata", y="sumber", orientation="h",
                      text=src.sort_values("rata").rata.apply(pc.fmt_rp),
                      color_discrete_sequence=[ORANGE], custom_data=["n"])
        figp.update_traces(textposition="outside", cliponaxis=False,
                           hovertemplate="<b>%{y}</b><br>Rata-rata kelebihan %{text}"
                                         "<br>%{customdata[0]:,} permintaan<extra></extra>")
        figp.update_layout(height=200, margin=dict(l=0, r=130, t=4, b=4), xaxis_visible=False,
                           yaxis_title="", plot_bgcolor="white")
        st.plotly_chart(figp, use_container_width=True)
        st.caption(f"Urutan pencarian harga acuan: **riwayat internal dulu** (median yang sudah pernah "
                   f"dicapai BNI untuk mesin identik), **marketplace sebagai fallback** (persentil 25). "
                   f"Kelebihan rata-rata **{pc.fmt_rp(per_unit)}**/unit x {annual_units:,.0f} unit/tahun "
                   f"x cakupan {coverage*100:.0f}% x adopsi {adoption*100:.0f}% = **{pc.fmt_rp(proc_saving_live)}**. ")

        st.markdown("##### Modul 4 · Roll-up")
        total_benefit_live = ts_detail.rp_saved_per_year.sum() + proc_saving_live
        rp_live = rc.roi_and_payback(pilot_investment, total_benefit_live)
        figr = go.Figure(go.Waterfall(
            orientation="v", measure=["relative", "relative", "total", "relative", "total"],
            x=["Waktu", "Pengadaan", "Total benefit", "− Investasi", "Net"],
            y=[ts_detail.rp_saved_per_year.sum(), proc_saving_live, None, -pilot_investment, None],
            connector=dict(line=dict(color=TEXT_MUTED, width=1)),
            increasing=dict(marker_color=ORANGE), decreasing=dict(marker_color="#C0392B"),
            totals=dict(marker_color=NAVY),
            hovertemplate="<b>%{x}</b><br>%{y:,.0f} Rp<extra></extra>",
        ))
        figr.update_layout(height=230, margin=dict(l=0, r=0, t=4, b=4), plot_bgcolor="white",
                           yaxis_title="", showlegend=False)
        st.plotly_chart(figr, use_container_width=True)
        st.caption(f"ROI = (benefit − investasi) / investasi = **{rp_live['roi_x']:.2f}x** · "
                   f"Payback **{rp_live['payback_months']:.1f} bulan**.")

    st.divider()
    st.markdown("#### Business Story")
    st.markdown(business_story_cards_html([
        dict(icon="⚖️", title="Legal + RAG", color=NAVY,
             steps=["Faster", "More Grounded", "More Traceable", "More Auditable"]),
        dict(icon="🛒", title="Procurement", color=ORANGE,
             steps=["Market Data", "Statistical Benchmark", "Evidence-Based Negotiation", "Potential Savings"]),
        dict(icon="🛡️", title="Anti-Corruption / Governance", color=GREEN,
             steps=["Transparent Benchmark", "Detect Anomalies", "Require Evidence", "Improve Controls"]),
    ]), unsafe_allow_html=True)

# =============================================================================================
# PAGE 2 — PROCUREMENT INTELLIGENCE
# =============================================================================================
elif page == PAGES[1]:
    st.markdown('<div class="section-tag">Laptop Procurement Category · Specification-Based Benchmarking</div>', unsafe_allow_html=True)

    # ------------------------------------------------------------------ data
    # The three sources are unioned on the fields that mean the same thing
    # even where the columns are named differently (price_idr /
    # historical_avg_price / requested_unit_price all mean "price per unit").
    # Fields that only one source can ever populate are left out entirely.
    UNIFIED_COLS = ["Sumber", "Merek", "Model", "CPU", "GPU", "RAM (GB)",
                    "Storage (GB)", "Harga", "Penjual/Vendor resmi"]

    @st.cache_data(show_spinner=False)
    def build_unified(_mkt: pd.DataFrame, _req: pd.DataFrame) -> pd.DataFrame:
        mkt = pd.DataFrame({
            "Sumber": SERIES_MARKET,
            "Merek": _mkt["brand"].astype("string"),
            "Model": _mkt["model"].astype("string") if "model" in _mkt else pd.NA,
            "CPU": _mkt["cpu_model"].astype("string"),
            "GPU": _mkt["gpu_model"].astype("string").fillna(
                _mkt["dedicated_gpu"].map({True: "Diskrit", False: "Integrated"}).astype("string")),
            "RAM (GB)": pd.to_numeric(_mkt["ram_gb"], errors="coerce"),
            "Storage (GB)": pd.to_numeric(_mkt["storage_gb"], errors="coerce"),
            "Harga": pd.to_numeric(_mkt["price_rp"], errors="coerce"),
            "Penjual/Vendor resmi": _mkt["seller_is_official"].astype(bool) if "seller_is_official" in _mkt else False,
        })
        parts = [mkt]
        for price_col, series_name in [("historical_avg_price", SERIES_HISTORY),
                                       ("requested_unit_price", SERIES_REQUEST)]:
            parts.append(pd.DataFrame({
                "Sumber": series_name,
                "Merek": _req["laptop_brand"].astype("string"),
                "Model": _req["laptop_model"].astype("string"),
                "CPU": _req["cpu"].astype("string"),
                "GPU": _req["gpu"].astype("string"),
                "RAM (GB)": pd.to_numeric(_req["ram_gb"], errors="coerce"),
                "Storage (GB)": pd.to_numeric(_req["storage_gb"], errors="coerce"),
                "Harga": pd.to_numeric(_req[price_col], errors="coerce"),
                "Penjual/Vendor resmi": _req["vendor_is_official"].astype(bool),
            }))
        out = pd.concat(parts, ignore_index=True)
        # pd.NA is not JSON-serialisable and breaks both st.dataframe styling
        # and Plotly hovers, so text columns are normalised once, here.
        for c in ["Merek", "Model", "CPU", "GPU"]:
            out[c] = out[c].astype(object).where(out[c].notna(), "—").astype(str).str.strip().replace("", "—")
        return out.dropna(subset=["Harga"])

    unified = build_unified(listings, history_source)

    # ------------------------------------------------- master filter bar ----
    with st.expander("🎛️  Filter (berlaku untuk seluruh grafik, metrik, dan tabel di tab ini)", expanded=True):
        st.caption("**Filter universal** — berlaku ke ketiga sumber data sekaligus.")
        u1, u2, u3, u4 = st.columns(4)
        with u1:
            fx_source = st.multiselect("Sumber data", [SERIES_MARKET, SERIES_HISTORY, SERIES_REQUEST],
                                       default=[SERIES_MARKET, SERIES_HISTORY, SERIES_REQUEST], key="fx_source")
            fx_brand = st.multiselect("Merek (brand)", sorted(unified["Merek"].unique()), default=[], key="fx_brand")
        with u2:
            fx_model = st.multiselect("Model", sorted(unified["Model"].unique()), default=[], key="fx_model")
            fx_cpu = st.multiselect("CPU", sorted(unified["CPU"].unique()), default=[], key="fx_cpu")
        with u3:
            fx_gpu = st.multiselect("GPU", sorted(unified["GPU"].unique()), default=[], key="fx_gpu")
            fx_ram = st.multiselect("RAM (GB)", sorted(unified["RAM (GB)"].dropna().unique()), default=[], key="fx_ram")
        with u4:
            fx_sto = st.multiselect("Storage (GB)", sorted(unified["Storage (GB)"].dropna().unique()), default=[], key="fx_sto")
            fx_official = st.selectbox("Penjual/Vendor resmi", ["Semua", "Ya", "Tidak"], key="fx_official")
        pmax = int(unified["Harga"].max() // 1_000_000) + 1
        fx_price = st.slider("Rentang harga (Rp juta)", 0, pmax, (0, pmax), key="fx_price")

        st.divider()
        st.caption("**Filter khusus marketplace** — hanya menyaring baris marketplace; baris procurement tidak punya kolom ini.")
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            fm_src = st.multiselect("source", sorted(listings["source"].dropna().astype(str).unique()), default=[], key="fm_src")
            fm_cond = st.multiselect("condition", sorted(listings["condition"].dropna().astype(str).unique()), default=[], key="fm_cond")
        with m2:
            fm_seller = st.multiselect("seller_name", sorted(listings["seller"].dropna().astype(str).unique()), default=[], key="fm_seller")
            fm_loc = st.multiselect("location", sorted(listings["seller_location"].dropna().astype(str).unique()), default=[], key="fm_loc")
        with m3:
            fm_scam = st.selectbox("is_suspected_scam", ["Semua", "Ya", "Tidak"], key="fm_scam")
            fm_status = st.multiselect("listing_status", sorted(listings["listing_status"].dropna().astype(str).unique()), default=[], key="fm_status")
        with m4:
            rmax = float(pd.to_numeric(listings["rating"], errors="coerce").max() or 5)
            fm_rating = st.slider("seller_rating minimum", 0.0, rmax, 0.0, 0.1, key="fm_rating")
            fm_sold = st.number_input("sold_count minimum", min_value=0, value=0, step=1, key="fm_sold")
        fm_screen = st.slider("screen_size_in", 0.0, float(pd.to_numeric(listings["screen_in"], errors="coerce").max() or 20),
                              (0.0, float(pd.to_numeric(listings["screen_in"], errors="coerce").max() or 20)), key="fm_screen")

        include_ppn = st.toggle("Harga listing sudah termasuk PPN 12%", value=True,
                                help="UU HPP No.7/2021 — tarif PPN umum 12% berlaku sejak 1 Jan 2025.")

    # --- marketplace-only predicates, resolved to the listing_ids that pass --
    mk = listings.copy()
    if fm_src:
        mk = mk[mk["source"].astype(str).isin(fm_src)]
    if fm_cond:
        mk = mk[mk["condition"].astype(str).isin(fm_cond)]
    if fm_seller:
        mk = mk[mk["seller"].astype(str).isin(fm_seller)]
    if fm_loc:
        mk = mk[mk["seller_location"].astype(str).isin(fm_loc)]
    if fm_status:
        mk = mk[mk["listing_status"].astype(str).isin(fm_status)]
    if fm_scam == "Ya":
        mk = mk[mk["is_suspicious"]]
    elif fm_scam == "Tidak":
        mk = mk[~mk["is_suspicious"]]
    if fm_rating > 0:
        mk = mk[pd.to_numeric(mk["rating"], errors="coerce").fillna(-1) >= fm_rating]
    if fm_sold > 0:
        mk = mk[pd.to_numeric(mk["sold_min"], errors="coerce").fillna(0) >= fm_sold]
    _sc = pd.to_numeric(mk["screen_in"], errors="coerce")
    mk = mk[_sc.isna() | ((_sc >= fm_screen[0]) & (_sc <= fm_screen[1]))]
    mk = mk.copy()
    mk["price_rp"] = pc.normalize_tax(mk, "price_rp", include_ppn)

    # Rebuild the unified frame from the marketplace rows that survived the
    # marketplace-only filters, then apply the universal filters to everything.
    fdf = build_unified(mk, history_source)
    if fx_source:
        fdf = fdf[fdf["Sumber"].isin(fx_source)]
    if fx_brand:
        fdf = fdf[fdf["Merek"].isin(fx_brand)]
    if fx_model:
        fdf = fdf[fdf["Model"].isin(fx_model)]
    if fx_cpu:
        fdf = fdf[fdf["CPU"].isin(fx_cpu)]
    if fx_gpu:
        fdf = fdf[fdf["GPU"].isin(fx_gpu)]
    if fx_ram:
        fdf = fdf[fdf["RAM (GB)"].isin(fx_ram)]
    if fx_sto:
        fdf = fdf[fdf["Storage (GB)"].isin(fx_sto)]
    if fx_official == "Ya":
        fdf = fdf[fdf["Penjual/Vendor resmi"]]
    elif fx_official == "Tidak":
        fdf = fdf[~fdf["Penjual/Vendor resmi"]]
    fdf = fdf[(fdf["Harga"] >= fx_price[0] * 1_000_000) & (fdf["Harga"] <= fx_price[1] * 1_000_000)]

    if fdf.empty:
        st.warning("Tidak ada data pada kombinasi filter ini. Longgarkan filter di atas.")
        st.stop()

    # ------------------------------------------------- KPI summary cards ----
    kpi_row([
        dict(label="Total Data (sesuai filter)", value=len(fdf), decimals=0,
             note="marketplace + historical + permintaan user"),
        dict(label="Mean Harga", value=fdf["Harga"].mean()/1e6, prefix="Rp", suffix="jt", decimals=2),
        dict(label="Min Harga", value=fdf["Harga"].min()/1e6, prefix="Rp", suffix="jt", decimals=2),
        dict(label="Max Harga", value=fdf["Harga"].max()/1e6, prefix="Rp", suffix="jt", decimals=2),
    ])

    tabs = st.tabs(["Market Benchmark", "Data Quality Pipeline", "Volume Scenario Calculator"])

    with tabs[0]:
        st.markdown("#### Distribusi Harga & Outlier")
        spec_axis = st.radio(
            "Bandingkan harga menurut:",
            ["Distribusi (histogram)", "RAM (GB)", "Storage (GB)", "GPU", "CPU", "Merek"],
            horizontal=True, key="spec_axis",
            help="Kontrol spesifikasi dari grafik Spec-Price lama, kini menyatu di sini.")

        if spec_axis == "Distribusi (histogram)":
            figd = px.histogram(fdf, x="Harga", nbins=40, color="Sumber", marginal="box", opacity=0.85,
                                color_discrete_map=SERIES_COLORS,
                                hover_data=["Merek", "Model", "CPU", "RAM (GB)", "Storage (GB)"])
            figd.update_layout(height=520, plot_bgcolor="white", bargap=0.04,
                               xaxis_title="Harga per unit (Rp)", yaxis_title="Jumlah data",
                               legend_title="", legend=dict(orientation="h", y=-0.16),
                               margin=dict(t=16, b=8))
        else:
            sub = fdf.dropna(subset=[spec_axis]).copy()
            agg = (sub.groupby([spec_axis, "Sumber"])["Harga"]
                   .agg(["mean", "min", "max", "size"]).reset_index())
            # Categorical axes stay bars; the two numeric spec axes read better
            # as lines because the x values are ordered magnitudes.
            if spec_axis in ("RAM (GB)", "Storage (GB)"):
                agg = agg.sort_values(spec_axis)
                figd = px.line(agg, x=spec_axis, y="mean", color="Sumber", markers=True,
                               color_discrete_map=SERIES_COLORS, custom_data=["Sumber", "min", "max", "size"])
            else:
                top = sub[spec_axis].value_counts().head(15).index
                agg = agg[agg[spec_axis].isin(top)]
                figd = px.bar(agg, x=spec_axis, y="mean", color="Sumber", barmode="group",
                              color_discrete_map=SERIES_COLORS, custom_data=["Sumber", "min", "max", "size"])
            figd.update_traces(hovertemplate="<b>%{customdata[0]}</b><br>" + spec_axis +
                               ": %{x}<br>Mean: %{y:,.0f}<br>Min: %{customdata[1]:,.0f}"
                               "<br>Max: %{customdata[2]:,.0f}<br>n=%{customdata[3]}<extra></extra>")
            figd.update_layout(height=520, plot_bgcolor="white", xaxis_title=spec_axis,
                               yaxis_title="Mean harga per unit (Rp)", legend_title="",
                               legend=dict(orientation="h", y=-0.16), margin=dict(t=16, b=8))
        st.plotly_chart(figd, use_container_width=True)

        # ------------------------------------------ searchable data grid ----
        st.markdown("#### Data Grid — Item & Spesifikasi")
        s1, s2 = st.columns([4, 1])
        query = s1.text_input("Cari (semua kolom)", value="", key="grid_q",
                              placeholder="mis. Asus, Ryzen 7, ThinkPad, RTX...")
        page_size = int(s2.selectbox("Baris/halaman", [10, 25, 50, 100], index=0, key="grid_size"))

        grid = fdf[UNIFIED_COLS]
        if query.strip():
            # Search spans every column, so numeric fields are stringified
            # before matching — otherwise "16" would never hit RAM.
            terms = [t for t in query.lower().split() if t]
            hay = grid.astype(str).apply(lambda c: c.str.lower())
            mask = pd.Series(True, index=grid.index)
            for t in terms:
                mask &= hay.apply(lambda c: c.str.contains(t, regex=False, na=False)).any(axis=1)
            grid = grid[mask]

        total_rows = len(grid)
        total_pages = max(1, (total_rows + page_size - 1) // page_size)
        # The page number lives in the number_input's own key. Seeding it here,
        # BEFORE that widget is instantiated, is the only window in which it can
        # be written -- and it keeps a shrinking result set from stranding the
        # view past the last page.
        cur = min(max(1, int(st.session_state.get("grid_jump", 1))), total_pages)
        st.session_state["grid_jump"] = cur

        n1, n2, n3, n4, n5, n6 = st.columns([1, 1, 2.2, 1, 1, 3])
        # Every button is created before the number_input so a click can still
        # write that key; Streamlit forbids writing it once the widget exists.
        goto_page = None
        if n1.button("⏮ First", key="g_first", disabled=cur == 1):
            goto_page = 1
        if n2.button("◀ Prev", key="g_prev", disabled=cur == 1):
            goto_page = cur - 1
        if n4.button("Next ▶", key="g_next", disabled=cur >= total_pages):
            goto_page = cur + 1
        if n5.button("Last ⏭", key="g_last", disabled=cur >= total_pages):
            goto_page = total_pages
        if goto_page is not None:
            st.session_state["grid_jump"] = int(min(max(1, goto_page), total_pages))
            st.rerun()
        cur = int(n3.number_input(f"Halaman (1–{total_pages})", min_value=1, max_value=total_pages,
                                  step=1, key="grid_jump", label_visibility="collapsed"))

        lo, hi = (cur - 1) * page_size, min(cur * page_size, total_rows)
        n6.markdown(
            f"<div style='padding-top:6px;font-weight:700;color:{TEXT};'>"
            f"[{hi:,}/{total_rows:,}] &nbsp;·&nbsp; halaman {cur:,} dari {total_pages:,}</div>",
            unsafe_allow_html=True)

        if total_rows == 0:
            st.info("Tidak ada baris yang cocok dengan pencarian.")
        else:
            show = grid.iloc[lo:hi].copy()
            show["Harga"] = show["Harga"].apply(pc.fmt_rp)
            show["RAM (GB)"] = show["RAM (GB)"].apply(lambda v: f"{int(v)}" if pd.notna(v) else "—")
            show["Storage (GB)"] = show["Storage (GB)"].apply(lambda v: f"{int(v)}" if pd.notna(v) else "—")
            show["Penjual/Vendor resmi"] = show["Penjual/Vendor resmi"].map({True: "Ya", False: "Tidak"})
            st.dataframe(show, use_container_width=True, hide_index=True, height=min(60 + 36 * len(show), 460))

    with tabs[1]:
        st.markdown("##### Raw Listings → Cleaned → Valid → Benchmark Dataset")
        funnel_df = pc.data_quality_funnel(mk)
        fig = go.Figure(go.Funnel(
            y=funnel_df["stage"], x=funnel_df["count"],
            textinfo="value+percent initial", textfont=dict(size=17),
            marker=dict(color=[ORANGE, NAVY_LIGHT, TEAL_ACCENT, LIME_ACCENT]),
        ))
        fig.update_layout(height=520, margin=dict(l=0, r=0, t=10, b=10),
                          funnelmode="stack",
                          yaxis=dict(tickfont=dict(size=15, weight="bold")))
        st.plotly_chart(fig, use_container_width=True)
        qc1, qc2, qc3, qc4 = st.columns(4)
        qc1.metric("Duplicate listing", int(mk.is_duplicate_listing.sum()))
        qc2.metric("Bundle/promo produk", int((mk.is_bundle | mk.is_promo).sum()))
        qc3.metric("Spesifikasi tidak lengkap", int(mk.missing_spec.sum()))
        qc4.metric("Outlier harga (IQR)", int(mk.is_price_outlier.sum()))
        st.caption("Flag kualitas dihitung dari `marketplace_listings.csv`, mengikuti filter marketplace di atas.")

    with tabs[2]:
        st.markdown("##### \"BNI butuh 100 laptop dengan spesifikasi tertentu — berapa benchmark & potensi penghematannya?\"")
        pool_all = pc.valid_listings(mk)
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            cpu_models = ["Semua model"] + sorted(pool_all.cpu_model.dropna().astype(str).unique())
            cpu_model_sel = st.selectbox("Model CPU", cpu_models, index=0)
        with c2:
            ram_sel = st.selectbox("RAM min. (GB)", [4, 8, 16, 32], index=2)
        with c3:
            sto_sel = st.selectbox("Storage min. (GB)", [128, 256, 512, 1024], index=2)
        with c4:
            gpu_sel = st.selectbox("GPU diskrit", [False, True], format_func=lambda x: "Ya" if x else "Tidak")
        custom_qty = int(st.number_input("Jumlah laptop yang dibutuhkan", min_value=1, value=100, step=1))

        pool = pool_all
        if cpu_model_sel != "Semua model":
            pool = pool[pool.cpu_model.astype(str) == cpu_model_sel]
        stages = [
            (f"Model CPU + RAM ≥{ram_sel} + storage ≥{sto_sel} + GPU",
             lambda d: d[(d.ram_gb >= ram_sel) & (d.storage_gb >= sto_sel) & (d.dedicated_gpu == gpu_sel)]),
            (f"RAM ≥{ram_sel} + storage ≥{sto_sel}",
             lambda d: d[(d.ram_gb >= ram_sel) & (d.storage_gb >= sto_sel)]),
            (f"RAM ≥{ram_sel}", lambda d: d[d.ram_gb >= ram_sel]),
            ("Semua listing valid", lambda d: d),
        ]
        sub, level = pool.iloc[0:0], "Tidak ada data sebanding"
        for label, fn in stages:
            cand = fn(pool)
            if len(cand) >= 5:
                sub, level = cand, label
                break
            if len(cand) > len(sub):
                sub, level = cand, label
        stats = pc.bucket_stats(sub)

        if stats is None:
            st.error("Tidak ada data pembanding untuk spesifikasi ini.")
        else:
            st.info(f"Cakupan data: **{level}** (n={stats['n']})")
            applicable = scenarios[scenarios.qty_tier <= custom_qty].iloc[-1] if (scenarios.qty_tier <= custom_qty).any() else scenarios.iloc[0]
            disc = float(applicable.assumed_discount_pct) / 100.0
            benchmark = float(stats["median"])
            unit_price = benchmark * (1 - disc)
            total = unit_price * custom_qty
            r1, r2, r3, r4 = st.columns(4)
            r1.metric("Benchmark unit price", pc.fmt_rp(benchmark))
            r2.metric("Harga unit setelah diskon", pc.fmt_rp(unit_price))
            r3.metric("Estimasi total", pc.fmt_rp(total))
            r4.metric("Potensi penghematan", pc.fmt_rp(benchmark * custom_qty - total))
            st.caption(f"{custom_qty:,} unit memakai tier diskon {int(applicable.qty_tier):,} unit ({applicable.assumed_discount_pct:.0f}%).")
            qty_axis = sorted(set(scenarios.qty_tier.astype(int)) | {custom_qty})
            curve = pd.DataFrame({"qty": qty_axis})
            curve["disc"] = curve.qty.apply(
                lambda q: float(scenarios[scenarios.qty_tier <= q].iloc[-1].assumed_discount_pct)
                if (scenarios.qty_tier <= q).any() else float(scenarios.iloc[0].assumed_discount_pct)) / 100.0
            curve["total"] = benchmark * (1 - curve.disc) * curve.qty
            fig = go.Figure()
            fig.add_trace(go.Bar(x=curve.qty, y=curve.total, name="Estimasi total (asumsi diskon)", marker_color=ORANGE))
            fig.add_trace(go.Scatter(x=curve.qty, y=benchmark * curve.qty, name="Tanpa diskon (linear)",
                                     line=dict(color=NAVY, dash="dot")))
            fig.add_trace(go.Scatter(x=[custom_qty], y=[total], mode="markers+text", name="Jumlah Anda",
                                     text=[f"{custom_qty:,} unit"], textposition="top center",
                                     marker=dict(size=13, color=GREEN, line=dict(width=2, color="white"))))
            fig.update_layout(xaxis_title="Jumlah unit", yaxis_title="Estimasi total (Rp)", plot_bgcolor="white",
                              margin=dict(t=20, b=8))
            st.plotly_chart(fig, use_container_width=True)
            st.caption("**assumed_discount_pct** adalah **asumsi skenario** (procurement_scenarios.csv), bukan angka yang dijamin vendor.")

# =============================================================================================
# PAGE 3 — LEGAL & RAG INTELLIGENCE
# =============================================================================================
elif page == PAGES[2]:
    st.markdown('<div class="section-tag">AI-generated outputs become trustworthy when grounded in traceable sources</div>', unsafe_allow_html=True)

    kpi_row([
        dict(label="Answers in sample (this prototype)", value=len(rag_answers), decimals=0),
        dict(label="Citations logged (this prototype)", value=len(citations), decimals=0),
    ])

    st.write("")
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown("#### Answer Confidence Distribution")
        conf = rm.confidence_distribution(rag_answers)
        fig = px.pie(conf, names="band", values="pct", hole=0.55, color="band",
                     color_discrete_map={rm.CONF_LABELS[2]: NAVY, rm.CONF_LABELS[1]: ORANGE, rm.CONF_LABELS[0]: AMBER})
        fig.update_traces(textinfo="percent+label")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown(
        f'<div style="width:100%;text-align:center;margin:0 auto 8px;">'
        f'Asumsi 75/20/5 → hasil sampling n={len(rag_answers)} (tidak dipaksa cocok). {data_badge("calculated")}'
        f'</div>',
        unsafe_allow_html=True,
    )

    st.write("")
    st.markdown("#### Provenance Chain — Contoh Kasus")
    st.caption("Ini bukan sekadar \"AI menjawab\" — setiap klaim faktual bisa ditelusuri balik ke klausul & halaman persis sumbernya.")
    chain = rm.provenance_example(rag_answers, citations, legal_docs)
    st.markdown(provenance_chain_html(chain), unsafe_allow_html=True)

    st.write("")
    c3, c4 = st.columns(2)
    with c3:
        st.markdown("#### Document Preparation Time by Complexity")
        simple_only = doc_prep[doc_prep.complexity == "Dokumen sederhana"]
        fig3 = go.Figure()
        fig3.add_trace(go.Bar(x=simple_only.complexity, y=simple_only.before_minutes, name="Before AI", marker_color=NAVY))
        fig3.add_trace(go.Bar(x=simple_only.complexity, y=simple_only.after_minutes, name="With AI-assisted RAG", marker_color=ORANGE))
        fig3.update_layout(barmode="group", yaxis_title="Menit", plot_bgcolor="white", bargap=0.6, margin=dict(t=34, b=8))
        st.plotly_chart(fig3, use_container_width=True)
    with c4:
        st.markdown("#### Distribusi Sitasi per Kategori Sumber")
        # Share of citations per category, not the % that were valid — the
        # slices have to sum to 100% for a pie to mean anything.
        share = (citation_evals.groupby("category").size()
                 .rename("n_citations").reset_index())
        share["label"] = share["category"].map({
            "SOP & Sirkular Internal": "history",
            "Referensi Regulasi Eksternal": "marketplace",
        }).fillna(share["category"])
        share = share[share["category"] != "Kontrak & Perjanjian Vendor"]
        fig4 = px.pie(share, names="label", values="n_citations", hole=0.45,
                      color="label", color_discrete_map={"history": NAVY, "marketplace": ORANGE})
        fig4.update_traces(textinfo="percent+label",
                           hovertemplate="<b>%{label}</b><br>%{value} sitasi<br>%{percent}<extra></extra>")
        st.plotly_chart(fig4, use_container_width=True)

    with st.expander("🔎 Bagaimana validitas tiap sitasi disimulasikan?"):
        st.caption("`validity_prob = prior_kategori + (confidence − 0.7) × 0.35`, lalu "
                   "`is_valid ~ Bernoulli(validity_prob)` (seed=42). Prior: SOP 0.80 · Kontrak 0.72 · Regulasi 0.62.")
        ce1, ce2 = st.columns(2)
        with ce1:
            figv1 = px.histogram(citation_evals, x="validity_prob", nbins=24, color="category",
                                 color_discrete_sequence=CATEGORICAL_SEQUENCE)
            figv1.update_layout(height=230, margin=dict(l=0, r=0, t=24, b=0), plot_bgcolor="white",
                                xaxis_title="validity_prob", yaxis_title="sitasi",
                                title="Sebaran probabilitas", legend=dict(orientation="h", y=-0.3, font=dict(size=9)))
            st.plotly_chart(figv1, use_container_width=True)
        with ce2:
            # Where the Bernoulli draw actually landed vs. what it was handed:
            # the gap between the two bars is the sampling noise, per category.
            out = (citation_evals.groupby("category")
                   .agg(prob=("validity_prob", "mean"), hasil=("is_valid", "mean"), n=("is_valid", "size"))
                   .reset_index())
            figv2 = go.Figure()
            figv2.add_trace(go.Bar(y=out.category, x=out.prob*100, orientation="h",
                                   name="rata-rata validity_prob", marker_color=NAVY))
            figv2.add_trace(go.Bar(y=out.category, x=out.hasil*100, orientation="h",
                                   name="hasil Bernoulli", marker_color=ORANGE,
                                   customdata=out.n, hovertemplate="%{y}<br>%{x:.1f}% dari n=%{customdata}<extra></extra>"))
            figv2.update_layout(height=230, margin=dict(l=0, r=0, t=24, b=0), plot_bgcolor="white",
                                barmode="group", xaxis_title="%", yaxis_title="",
                                title="Prior vs hasil", yaxis=dict(tickfont=dict(size=9)),
                                legend=dict(orientation="h", y=-0.3, font=dict(size=9)))
            st.plotly_chart(figv2, use_container_width=True)
        st.caption(f"{len(citation_evals)} baris evaluasi lengkap di `data/citation_evaluations.csv`.")

    st.write("")
    c5, c6 = st.columns(2)
    with c5:
        st.markdown("#### Historical/Legal/RAG Records Made Searchable (cumulative, pilot weeks)")
        fig5 = px.line(pilot_ramp, x="pilot_week", y="cumulative_records_searchable", markers=True, color_discrete_sequence=[NAVY])
        fig5.update_layout(xaxis_title="Pilot week", yaxis_title="Cumulative records", plot_bgcolor="white", margin=dict(t=34, b=8))
        st.plotly_chart(fig5, use_container_width=True)
    with c6:
        st.markdown("#### Process Time — Before vs. AI-Assisted")
        pt = process_time.copy()
        fig6 = go.Figure()
        fig6.add_trace(go.Bar(y=pt.process_name, x=pt.before_minutes, name="Manual baseline", orientation="h", marker_color="#C9D9E8"))
        fig6.add_trace(go.Bar(y=pt.process_name, x=pt.after_minutes, name="AI-assisted (pilot)", orientation="h", marker_color=ORANGE))
        fig6.update_layout(barmode="overlay", xaxis_title="Menit", plot_bgcolor="white", margin=dict(t=34, b=8))
        st.plotly_chart(fig6, use_container_width=True)

    with st.expander("Document registry (sample, synthetic)"):
        HIDDEN_DOCS = [f"DOC-{n:04d}" for n in range(10, 17)]
        st.dataframe(legal_docs[~legal_docs.document_id.isin(HIDDEN_DOCS)],
                     use_container_width=True, hide_index=True)

# =============================================================================================
# PAGE 4 — GOVERNANCE & ANTI-CORRUPTION
# =============================================================================================
elif page == PAGES[3]:
    split_flags = gov.detect_split_purchases(history)
    ev = gov.evidence_coverage(history)
    flagged_hist = pc.outside_benchmark_flags(history, listings)
    ob = gov.outside_benchmark_summary(flagged_hist)

    kpi_row([
        # Formula pending replacement — the count is withheld rather than
        # asserted under a rule that is being rewritten.
        dict(label="Potential Corruption", value=None, placeholder="—",
             note="Rumus sedang diganti — angka ditahan"),
        dict(label="Records with Benchmark Reference", value=ev["pct_with_benchmark"], suffix="%", decimals=1),
        dict(label="Records with Supporting Documentation", value=ev["pct_with_doc"], suffix="%", decimals=1),
        dict(label="Current Quotes Outside Benchmark Range", value=ob["pct_outside"], suffix="%", decimals=1),
    ])
    st.caption("Setiap indikator di atas adalah **potensi** yang memerlukan verifikasi manusia sebelum kesimpulan apa pun diambil — bukan tuduhan, dan tidak ada transaksi yang dilabeli bermasalah hanya karena harganya mahal.")

    st.write("")
    st.markdown("#### Conditional Requirements — 4 Gerbang Kelayakan Permintaan")
    cr_src = history_source
    cr1 = float(pd.to_numeric(cr_src["target_uc1_is_match"], errors="coerce").mean() * 100)
    cr2 = float(pd.to_numeric(cr_src["target_uc2_months_to_failure"], errors="coerce").mean())
    cr3 = float(pd.to_numeric(cr_src["target_uc3_opex_idr"], errors="coerce").mean())
    cr4 = float(pd.to_numeric(cr_src["target_uc4_is_approved"], errors="coerce").mean() * 100)
    st.markdown(conditional_requirements_flow_html([
        dict(code="cr1", label="Laptop cocok dengan posisi user", value=f"{cr1:.1f}%",
             sub="target_uc1_is_match"),
        dict(code="cr2", label="Rata-rata umur pakai laptop", value=f"{cr2/12:.1f} thn",
             sub=f"{cr2:.0f} bulan · target_uc2_months_to_failure"),
        dict(code="cr3", label="Rata-rata biaya operasional 3 tahun", value=pc.fmt_rp(cr3),
             sub="target_uc3_opex_idr"),
        dict(code="cr4", label="Pengadaan di-ACC management", value=f"{cr4:.1f}%",
             sub="target_uc4_is_approved"),
    ]), unsafe_allow_html=True)

    st.markdown("#### Current Quotes Outside Market Benchmark Range dan History Benchmark")
    outside = flagged_hist[flagged_hist.outside_benchmark].copy()
    if outside.empty:
        st.info("Tidak ada current quote di luar rentang benchmark pasar saat ini.")
    else:
        outside["risk_label"] = "⚠️ Outside benchmark range — requires additional evidence"
        show = outside[["po_id", "business_unit", "spec_id", "vendor", "current_quote_unit_price_rp",
                         "historical_unit_price_rp", "benchmark_median", "deviation_pct", "risk_label"]] \
            .sort_values("deviation_pct", ascending=False).head(20)
        for c in ["current_quote_unit_price_rp", "historical_unit_price_rp", "benchmark_median"]:
            show[c] = show[c].apply(pc.fmt_rp)
        show["deviation_pct"] = show["deviation_pct"].round(1).astype(str) + "%"
        st.dataframe(show.rename(columns={"historical_unit_price_rp": "history_benchmark"}),
                     use_container_width=True, hide_index=True)
