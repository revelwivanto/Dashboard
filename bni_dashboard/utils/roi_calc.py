"""
Every function here is pure (DataFrame/scalar in, DataFrame/scalar out) and
is imported BOTH by data/generate_synthetic_data.py (to produce the shipped
CSVs) and by app.py (to re-display the exact same calculation live, with
its inputs, on the dashboard). There is exactly one implementation of each
formula — the CSV is the output of running this code, never a manually
typed number.

Traceability chain for every figure in this module:
  dashboard number -> this function -> its input CSV/DataFrame -> the
  assumption/source row in assumptions.csv that justifies each input.
"""
import re

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# 1. Citation validity (Graphs 2/8/10/11's underlying evidence)
# ---------------------------------------------------------------------------
DOC_TYPE_TO_CATEGORY = {
    "SOP": "SOP & Sirkular Internal",
    "Kebijakan Internal": "SOP & Sirkular Internal",
    "Nota Dinas": "SOP & Sirkular Internal",
    "Kontrak Vendor": "Kontrak & Perjanjian Vendor",
    "RKS/RAB": "Kontrak & Perjanjian Vendor",
    "Peraturan Perundangan (referensi)": "Referensi Regulasi Eksternal",
}

# Base validity prior per category — an ASSUMPTION (see assumptions.csv
# CITATION-PRIOR-*), reasoned as: internal SOPs/circulars are short, use a
# consistent template and are well-indexed -> easiest for a retriever to
# pinpoint the exact clause. Vendor contracts are longer and more varied.
# External regulatory references are the longest and least uniformly
# formatted -> hardest to cite precisely. This ordering is a documented
# modeling assumption, not a measured fact — a real pilot would replace it
# with actual human-reviewed citation audits.
CATEGORY_BASE_PRIOR = {
    "SOP & Sirkular Internal": 0.80,
    "Kontrak & Perjanjian Vendor": 0.72,
    "Referensi Regulasi Eksternal": 0.62,
}
# A citation attached to a higher-confidence answer is modeled as more
# likely to be a genuinely correct citation (confidence and citation
# correctness are assumed to be positively correlated) — linear adjustment,
# documented in assumptions.csv (CITATION-CONF-SLOPE).
CONFIDENCE_SLOPE = 0.35  # applied to (confidence_score - 0.7)


def build_citation_evaluations(citations: pd.DataFrame, legal_documents: pd.DataFrame,
                                rag_answers: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    df = citations.merge(legal_documents[["document_id", "doc_type"]], on="document_id", how="left")
    df = df.merge(rag_answers[["answer_id", "confidence_score"]], on="answer_id", how="left")
    df["category"] = df["doc_type"].map(DOC_TYPE_TO_CATEGORY).fillna("Referensi Regulasi Eksternal")
    df["confidence_score"] = df["confidence_score"].fillna(df["confidence_score"].median())
    base = df["category"].map(CATEGORY_BASE_PRIOR)
    adj = (df["confidence_score"] - 0.7) * CONFIDENCE_SLOPE
    df["validity_prob"] = (base + adj).clip(0.05, 0.99)
    df["is_valid"] = rng.random(len(df)) < df["validity_prob"]
    df["data_type"] = "calculated"
    return df[["citation_id", "answer_id", "document_id", "category", "confidence_score",
               "validity_prob", "is_valid", "data_type"]]


def citation_validity_by_category(evals: pd.DataFrame) -> pd.DataFrame:
    out = evals.groupby("category")["is_valid"].agg(["mean", "count"]).reset_index()
    out.columns = ["category", "pct_valid_citation", "n_citations"]
    out["pct_valid_citation"] = (out["pct_valid_citation"] * 100).round(1)
    out["data_type"] = "calculated"
    return out


# ---------------------------------------------------------------------------
# 2. Time-savings benefit (Graph 6 monetized)
# ---------------------------------------------------------------------------
def hourly_rate_rp(monthly_salary_rp: float, work_hours_per_month: float) -> float:
    return monthly_salary_rp / work_hours_per_month


def time_savings_benefit(process_time: pd.DataFrame, annual_volume: pd.DataFrame,
                          hourly_rate: float, adoption_rate: float) -> pd.DataFrame:
    df = process_time.merge(annual_volume, on="process_name", how="left")
    df["minutes_saved_per_occurrence"] = df["before_minutes"] - df["after_minutes"]
    df["hours_saved_per_year"] = (df["minutes_saved_per_occurrence"] / 60.0
                                   * df["estimated_annual_occurrences"] * adoption_rate)
    df["rp_saved_per_year"] = df["hours_saved_per_year"] * hourly_rate
    return df


# ---------------------------------------------------------------------------
# 3. Procurement savings benefit (ties directly into the benchmarking engine)
# ---------------------------------------------------------------------------
def annual_procurement_units(total_employees: int, device_eligible_pct: float, annual_refresh_rate: float) -> float:
    return total_employees * device_eligible_pct * annual_refresh_rate


def procurement_savings_benefit(current_quote_avg_rp: float, benchmark_median_rp: float,
                                 annual_units: float, adoption_rate: float) -> float:
    per_unit_saving = max(current_quote_avg_rp - benchmark_median_rp, 0.0)
    return per_unit_saving * annual_units * adoption_rate


def effective_benchmark_with_discount(current_quote_avg_rp: float, benchmark_median_rp: float, discount_pct: float) -> float:
    """A negotiated volume discount off the current quote can only ever improve
    the effective benchmark down to (never below) the raw market median —
    it cannot make the benchmark cheaper than the market itself. Used
    identically by the data generator and the live app so the two never
    diverge."""
    discounted_quote = current_quote_avg_rp * (1 - discount_pct)
    return discounted_quote if discounted_quote > benchmark_median_rp else benchmark_median_rp


# ---------------------------------------------------------------------------
# 4. ROI / payback (identical formula used everywhere)
# ---------------------------------------------------------------------------
def roi_and_payback(investment_rp: float, annual_benefit_rp: float) -> dict:
    if investment_rp <= 0:
        return dict(roi_x=np.nan, payback_months=np.nan)
    roi_x = (annual_benefit_rp - investment_rp) / investment_rp
    payback_months = (investment_rp / annual_benefit_rp) * 12 if annual_benefit_rp > 0 else np.nan
    return dict(roi_x=roi_x, payback_months=payback_months)


# ---------------------------------------------------------------------------
# 5. Ingestion ramp curve (logistic ramp — Image 1, chart 3)
# ---------------------------------------------------------------------------
def logistic_ramp(total: float, n_weeks: int, midpoint_week: float, steepness: float) -> np.ndarray:
    weeks = np.arange(1, n_weeks + 1)
    raw = total / (1 + np.exp(-steepness * (weeks - midpoint_week)))
    return np.round(raw, 0)


# ---------------------------------------------------------------------------
# 6. Internal price-variance saving (replaces the market-gap model)
# ---------------------------------------------------------------------------
# Why this rather than "BNI quote vs marketplace median": the marketplace
# scrape is consumer retail stock (Axioo, Acer Aspire Lite) while BNI requests
# business-class fleet SKUs (Latitude, ThinkPad, ExpertBook). Comparing the two
# prices a segment difference, not an overpayment, and the resulting number
# swung from +19.9x to -0.7x purely on the unmeasurable "enterprise premium"
# allowed for warranty/vPro/TPM. The marketplace data is retained for its real
# jobs -- the Perpres 16/2018 HPS market survey, spec-delta pricing and outlier
# detection -- but it no longer sets the ROI.
#
# This model compares BNI only against itself: for the IDENTICAL machine
# (model + RAM + storage), no request should sit above the median price the
# organisation already achieved for it. Requires no market data, no premium,
# and no tier mapping.
MIN_PEER_GROUP = 20  # below this, a "median achieved price" is not meaningful


def internal_price_variance(requests: pd.DataFrame, price_col: str = "requested_unit_price",
                            key: tuple = ("laptop_model", "ram_gb", "storage_gb"),
                            quantile: float = 0.50,
                            min_peers: int = MIN_PEER_GROUP) -> pd.DataFrame:
    """Per-request excess over the target price for its identical-machine peer
    group. Groups thinner than `min_peers` are excluded rather than scored off
    a handful of observations."""
    df = requests.copy()
    df["req_price"] = pd.to_numeric(df[price_col], errors="coerce")
    g = df.groupby(list(key))["req_price"]
    df["peer_n"] = g.transform("size")
    df["peer_target"] = g.transform(lambda s: s.quantile(quantile))
    df = df[(df.peer_n >= min_peers) & df["req_price"].notna()].copy()
    df["excess_rp"] = (df["req_price"] - df["peer_target"]).clip(lower=0)
    return df


def internal_variance_saving_per_unit(requests: pd.DataFrame, **kwargs) -> float:
    d = internal_price_variance(requests, **kwargs)
    return float(d.excess_rp.sum() / len(d)) if len(d) else 0.0


# ---------------------------------------------------------------------------
# 7. Benchmark targets: internal history first, marketplace as fallback
# ---------------------------------------------------------------------------
# Mirrors what the assistant actually does at request time: look for prior
# purchases of the same machine inside BNI first, and only go out to the
# marketplace when internal history has nothing comparable to offer. A request
# that neither source can price is left OUT of the savings entirely rather
# than benchmarked against something incomparable.
MARKET_MODEL_MIN_N = 3      # listings needed to price a named model
MARKET_SPEC_MIN_N = 5       # listings needed to price a cpu-family+RAM+storage bucket
BENCHMARK_QUANTILE = 0.25   # "readily achievable" market price, not the single cheapest

_CPU_FAMILY_PATTERNS = [
    (r"\bI9\b|CORE ?I9", "i9"), (r"\bI7\b|CORE ?I7", "i7"),
    (r"\bI5\b|CORE ?I5", "i5"), (r"\bI3\b|CORE ?I3", "i3"),
    (r"RYZEN ?9", "ryzen9"), (r"RYZEN ?7", "ryzen7"),
    (r"RYZEN ?5", "ryzen5"), (r"RYZEN ?3", "ryzen3"),
    (r"\bM[1-4]\b", "apple-m"),
]


def cpu_family(text) -> str | None:
    """Coarse CPU family shared by both datasets. Used instead of the old
    compute_tier -> cpu_tier mapping, which put Core i7 machines into a
    Core i5 bucket."""
    s = str(text).upper()
    for pattern, name in _CPU_FAMILY_PATTERNS:
        if re.search(pattern, s):
            return name
    return None


def benchmark_targets(requests: pd.DataFrame, listings: pd.DataFrame,
                      min_peers: int = MIN_PEER_GROUP,
                      quantile: float = BENCHMARK_QUANTILE) -> pd.DataFrame:
    """Attach a price target and its provenance to every request.

    Priority, highest confidence first:
      1. `internal`     - median already achieved by BNI for the identical
                          model + RAM + storage (needs >= min_peers peers)
      2. `market-model` - 25th percentile of marketplace listings naming the
                          same model
      3. `market-spec`  - 25th percentile for the same CPU family + RAM + storage
      4. `none`         - no defensible benchmark; excluded from savings
    """
    df = requests.copy()
    df["req_price"] = pd.to_numeric(df["requested_unit_price"], errors="coerce")
    df["cpu_fam"] = df["cpu"].map(cpu_family)

    grp = df.groupby(["laptop_model", "ram_gb", "storage_gb"])["req_price"]
    df["peer_n"] = grp.transform("size")
    df["internal_target"] = grp.transform("median")

    mkt = listings.copy()
    mkt["_price"] = pd.to_numeric(mkt["price_rp"], errors="coerce")
    mkt["_fam"] = (mkt["cpu_model"].fillna("").astype(str) + " "
                   + mkt["title"].fillna("").astype(str)).map(cpu_family)
    titles = mkt["title"].fillna("").astype(str).str.upper()

    by_model = {}
    for model in df["laptop_model"].dropna().unique():
        hits = mkt[titles.str.contains(re.escape(str(model).upper()), na=False)]
        if len(hits) >= MARKET_MODEL_MIN_N:
            by_model[model] = float(hits["_price"].quantile(quantile))

    spec = mkt.dropna(subset=["_fam", "ram_gb", "storage_gb"]).groupby(["_fam", "ram_gb", "storage_gb"])["_price"]
    by_spec = {k: float(v) for k, v in spec.quantile(quantile).items() if spec.size()[k] >= MARKET_SPEC_MIN_N}

    targets, sources = [], []
    for row in df.itertuples():
        if row.peer_n >= min_peers and pd.notna(row.internal_target):
            targets.append(row.internal_target); sources.append("internal")
        elif row.laptop_model in by_model:
            targets.append(by_model[row.laptop_model]); sources.append("market-model")
        elif (row.cpu_fam, row.ram_gb, row.storage_gb) in by_spec:
            targets.append(by_spec[(row.cpu_fam, row.ram_gb, row.storage_gb)]); sources.append("market-spec")
        else:
            targets.append(np.nan); sources.append("none")
    df["price_target"] = targets
    df["benchmark_source"] = sources
    df["excess_rp"] = (df["req_price"] - df["price_target"]).clip(lower=0)
    return df


def benchmarked_saving(requests: pd.DataFrame, listings: pd.DataFrame, **kwargs) -> dict:
    """Per-unit saving plus the coverage it was measured over. Savings scale by
    coverage, so unbenchmarkable requests contribute nothing rather than being
    silently assumed to behave like the rest."""
    df = benchmark_targets(requests, listings, **kwargs)
    ok = df[df.benchmark_source != "none"]
    if ok.empty:
        return dict(per_unit=0.0, coverage=0.0, n_scored=0, detail=df)
    return dict(per_unit=float(ok.excess_rp.sum() / len(ok)),
                coverage=len(ok) / len(df), n_scored=len(ok), detail=df)
