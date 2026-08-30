"""
Governance / anti-corruption indicators computed from procurement_history.csv.

IMPORTANT — responsible terminology: nothing here labels a transaction as
"corruption." Every flag is a *potential indicator that a human reviewer
should look at*, phrased as such throughout the UI ("potential anomaly",
"requires review", "outside benchmark range"). See app.py copy.

Split-purchase heuristic (APPROVAL_THRESHOLD_RP):
  Flags pairs of purchase orders for the same business unit + same
  specification + same vendor, placed within a short window of each
  other, where EACH individual order is below the stated Director
  approval threshold (Rp200,000,000 — see assumptions.csv / the sample
  RAG question about approval thresholds). Two small orders that could
  have been one larger order, placed close together, is a classic
  textbook indicator worth a second look — it is not proof of anything
  improper on its own.
"""
import pandas as pd

APPROVAL_THRESHOLD_RP = 200_000_000
SPLIT_WINDOW_DAYS = 14


def detect_split_purchases(history: pd.DataFrame, threshold: float = APPROVAL_THRESHOLD_RP,
                            window_days: int = SPLIT_WINDOW_DAYS) -> pd.DataFrame:
    flagged_pairs = []
    for (unit, spec, vendor), g in history.groupby(["business_unit", "spec_id", "vendor"]):
        g = g.sort_values("po_date")
        recs = g[["po_id", "po_date", "current_quote_total_rp"]].to_dict("records")
        for i in range(len(recs)):
            for j in range(i + 1, len(recs)):
                gap = (recs[j]["po_date"] - recs[i]["po_date"]).days
                if gap > window_days:
                    break
                if recs[i]["current_quote_total_rp"] < threshold and recs[j]["current_quote_total_rp"] < threshold:
                    flagged_pairs.append(dict(
                        business_unit=unit, spec_id=spec, vendor=vendor,
                        po_id_1=recs[i]["po_id"], po_id_2=recs[j]["po_id"],
                        date_1=recs[i]["po_date"].date(), date_2=recs[j]["po_date"].date(),
                        gap_days=gap, value_1=recs[i]["current_quote_total_rp"], value_2=recs[j]["current_quote_total_rp"],
                        combined_value=recs[i]["current_quote_total_rp"] + recs[j]["current_quote_total_rp"],
                    ))
    return pd.DataFrame(flagged_pairs)


def evidence_coverage(history: pd.DataFrame) -> dict:
    n = len(history)
    if n == 0:
        return dict(pct_with_benchmark=0.0, pct_with_doc=0.0, n=0)
    return dict(
        pct_with_benchmark=round(history["has_benchmark_reference"].mean() * 100, 1),
        pct_with_doc=round(history["has_supporting_doc"].mean() * 100, 1),
        n=n,
    )


def outside_benchmark_summary(flagged: pd.DataFrame) -> dict:
    n = len(flagged)
    n_outside = int(flagged["outside_benchmark"].sum()) if "outside_benchmark" in flagged.columns else 0
    return dict(n_total=n, n_outside=n_outside, pct_outside=round(n_outside / n * 100, 1) if n else 0.0)
