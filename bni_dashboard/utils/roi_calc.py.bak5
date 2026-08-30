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
