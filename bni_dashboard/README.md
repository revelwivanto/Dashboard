# BNI — Legal Document Creation, Citation with RAG & Procurement Efficiency / Anti-Corruption

Internal prototype dashboard. **Not an official BNI publication** — visual
identity is BNI-inspired (navy + orange accent), not a verified brand
specification.

## Install & run
```bash
pip install -r requirements.txt
streamlit run app.py
```

Runs immediately after download. To regenerate every dataset from scratch
(optional — the CSVs are already shipped):
```bash
python data/generate_synthetic_data.py
```

## Traceability model — how to verify any number on the dashboard
Every figure you see follows the same chain:

```
Dashboard number → CSV column → function in utils/ → its inputs → row in assumptions.csv (source/rationale)
```

Concretely: pick any KPI, then
1. Find the CSV it's read from (`utils/data_loader.py` shows exactly which file each loader reads).
2. Open `data/generate_synthetic_data.py` and find the section that writes that CSV — it calls a function in `utils/roi_calc.py`, `utils/procurement_calc.py`, `utils/rag_metrics.py`, or `utils/governance.py`.
3. That function's inputs are either (a) another generated dataset, (b) a real dataset (marketplace_listings.csv observed rows), or (c) a named row in `assumptions.csv` with a `source` column.
4. `app.py` calls the **same function** live to display an expander showing the calculation — e.g. the Executive Summary page has a "Tunjukkan perhitungannya" expander that recomputes the ROI live, with every intermediate number shown, and the Legal & RAG page has one for citation validity.

Nothing is hard-coded into a CSV by hand. Where a number genuinely can't be
sourced yet (e.g. "before/after minutes" for a system that doesn't exist
yet to time-motion-study), it's labeled `illustrative` and everything
*derived* from it downstream is labeled `calculated`.

## Folder structure
```
bni_dashboard/
├── app.py                          # Streamlit entry point — 5 pages (sidebar nav)
├── requirements.txt
├── README.md
├── data/
│   ├── generate_synthetic_data.py  # reproducible generator (seed=42) — imports utils/ for every formula
│   ├── marketplace_listings.csv    # 17 REAL Tokopedia listings + 165 synthetic
│   ├── procurement_history.csv     # synthetic BNI-side PO history (24 months, seeded split-purchase clusters)
│   ├── procurement_laptops.csv     # BNI standard laptop spec catalog
│   ├── procurement_scenarios.csv   # volume-discount ASSUMPTIONS by qty tier
│   ├── assumptions.csv             # central register of every input, with sources — READ THIS FIRST
│   ├── legal_documents.csv         # synthetic document registry
│   ├── rag_answers.csv             # synthetic RAG answer log (confidence/source SAMPLED, not forced)
│   ├── citations.csv               # synthetic citation/provenance log
│   ├── citation_evaluations.csv    # per-citation validity simulation (feeds the % chart)
│   ├── citation_validity_by_category.csv  # = groupby output of citation_evaluations.csv
│   ├── process_time_comparison.csv # before/after minutes (illustrative hypothesis) + calculated % reduction
│   ├── process_annual_volume.csv   # annual occurrence assumption per process, scaled off real dataset sizes
│   ├── investment_breakdown.csv    # pilot investment components, sums to pilot_investment_rp
│   ├── roi_scenarios.csv           # fully bottom-up computed ROI per scenario
│   ├── pilot_metrics.csv           # scalar KPIs — every value = an actual computed count
│   ├── business_unit_impact.csv    # computed allocation, not typed
│   ├── doc_prep_time.csv           # Image 1, chart 1 (illustrative hypothesis)
│   └── pilot_ramp_curve.csv        # computed logistic ramp
├── utils/
│   ├── data_loader.py       # cached CSV → DataFrame loaders (only place that reads files)
│   ├── procurement_calc.py  # benchmarking, IQR outliers, volume scenarios, tax normalization
│   ├── rag_metrics.py       # citation coverage, confidence bands, provenance chain
│   ├── governance.py        # split-purchase detection, evidence coverage
│   └── roi_calc.py          # citation-validity simulation, time/procurement savings, ROI, ramp curve — single source of truth, used by BOTH the generator and the live app
├── components/
│   ├── styling.py     # BNI color tokens + global CSS
│   ├── kpi_card.py     # animated KPI card row (HTML/CSS/JS via components.html)
│   └── flow.py          # provenance-chain / tax-normalization flow diagrams
└── docs/
    └── SCHEMA.md         # full column-level schema, per dataset, with what's real/synthetic/assumption/calculated
```

## Data replacement guide
| When you have real... | Replace | Notes |
|---|---|---|
| Marketplace scraping pipeline | `data/marketplace_listings.csv` | Same columns; mark real rows `data_type="observed"`. Quality pipeline recomputes automatically. |
| BNI procurement/PO records | `data/procurement_history.csv` | Anonymize vendor names if needed (keep a consistent label per vendor so split-purchase detection still works). |
| RAG production logs | `data/rag_answers.csv` + `data/citations.csv` | Re-run `utils/roi_calc.py:build_citation_evaluations()` with real human-reviewed `is_valid` labels instead of the simulated priors, once available. |
| Document management export | `data/legal_documents.csv` | `TOTAL_DOCS_PROCESSED` updates automatically (it's `len()` of this file). |
| Real vendor negotiation history | `data/procurement_scenarios.csv` | Replace assumed `%` per quantity tier with observed discounts — `roi_scenarios.csv` recomputes on next generator run. |
| A real pilot budget/RAB | `data/investment_breakdown.csv` | Replace the estimated components with actual line items. |
| An actual time-motion study | `data/process_time_comparison.csv` | Replace before/after minutes; update `data_type` to `observed`. |
| Confirmed BNI headcount/salary data | `assumptions.csv` rows BNI-EMPLOYEES / SALARY-COMPLIANCE-ANNUAL | Update `status` to reflect the new source. |

## Calculation methodology (see also `docs/SCHEMA.md` and the in-app expanders)
- **Market benchmark** = median price of listings with `listing_status == "valid"` matching the selected specification.
- **Outlier detection** = 1.5×IQR fence, per specification bucket.
- **Citation validity** = simulated per-citation Bernoulli draw: `validity_prob = category_prior + (confidence_score − 0.7) × 0.35`; aggregate % = `groupby(category).mean()`. See `utils/roi_calc.py:build_citation_evaluations`.
- **Time-savings benefit** = Σ over processes of `((before_min − after_min)/60) × estimated_annual_occurrences × adoption_rate × hourly_rate`. Hourly rate = annual salary benchmark ÷ 12 ÷ 173 work-hours/month.
- **Procurement-savings benefit** = `max(current_quote_avg − benchmark_median, 0) × annual_procurement_units × adoption_rate`, where `annual_procurement_units = BNI_employees × device_eligible_% × annual_refresh_rate`.
- **ROI** = (Time-savings benefit + Procurement-savings benefit − Pilot Investment) / Pilot Investment. **Payback (months)** = Pilot Investment / Annual Benefit × 12.
- **Potential duplicate/split-purchase indicator** = two POs, same business unit + spec + vendor, dated ≤14 days apart, each individually below the Rp200,000,000 example Director-approval threshold.
- **Outside benchmark range** = current vendor quote > upper IQR fence of the matching market benchmark bucket.

## Real sources used
- **Marketplace pricing**: Tokopedia search results, `tokopedia.com/find/laptop-ram-16gb-ssd-512gb` and `.../laptop-i5-ryzen-5`, fetched live 27 Aug 2026 (17 listings).
- **Procurement regulation**: Perpres No.16/2018 jo. Perpres No.12/2021 jo. Perpres No.46/2025 — HPS for goods is built from a market price survey; **no fixed vendor-margin percentage was found** in this regulation or its LKPP derivatives.
- **Tax**: UU No.7/2021 (UU HPP) — general PPN rate is 12%, effective 1 January 2025.
- **BNI headcount**: 27,201 employees, per Wikipedia's "Bank Negara Indonesia" infobox (sourced from BNI's own FY2025 company profile / public disclosures).
- **Labor-cost benchmark**: Payscale.com "Average Compliance Officer Salary in Indonesia" — crowdsourced, indicative only, explicitly not BNI-specific or an official statistic.

## Mapping: the 16 required graphs → where they live
| # | Graph | Page | Status |
|---|---|---|---|
| 1 | Total illustrative annual opportunity | Executive Summary | **Calculated** = Σ business_unit_impact.csv |
| 2 | Citation coverage across generated answers | Executive Summary + Legal&RAG | **Calculated** live from rag_answers.csv |
| 3 | Procurement benchmarking opportunity | Executive Summary | **Calculated** = procurement_savings_benefit_rp (Base Case) |
| 4 | ROI on pilot investment | Executive Summary | **Calculated**, bottom-up (see expander) — replaces the old unreconciled headline number |
| 5 | Impact by business unit | Executive Summary | **Calculated** allocation |
| 6 | Process time — before vs AI-assisted | Legal & RAG Intelligence | Inputs illustrative; % reduction and $ savings calculated |
| 7 | Total Documents Processed | Legal & RAG Intelligence | **Calculated** = len(legal_documents.csv) |
| 8 | Citation coverage (valid source) | Legal & RAG Intelligence | Same computed metric as #2 |
| 9 | Provenance chain | Legal & RAG Intelligence | Built from a real joined example row |
| 10 | Answer confidence distribution | Legal & RAG Intelligence | **Calculated** from sampled confidence_score |
| 11 | Where answers are grounded | Legal & RAG Intelligence | **Calculated** from sampled source_type |
| 12 | Historical records searchable | Executive Summary + Legal&RAG | **Calculated** total + logistic ramp curve |
| 13 | Potential duplicate-purchase indicators | Executive Summary + Governance | **Live rule-based detection** on procurement_history.csv |
| 14 | Savings opportunity by category | Governance | **Adapted to laptop spec tier** (scope constraint) + calculated |
| Image 1 | Doc-prep time / citation validity / records-searchable ramp | Legal & RAG Intelligence | Doc-prep illustrative; citation validity & ramp calculated |
| Image 2 | ROI scenario cards | Executive Summary | **Calculated**, bottom-up, with a "show the math" expander |

Extra visuals beyond the required 16 (Procurement Intelligence page): price
distribution histogram, box plots by spec tier and by brand, data-quality
funnel, price-vs-RAM / price-vs-storage relationship charts, tax-normalization
flow, evidence-coverage and outside-benchmark governance tables.
