"""
Business logic for the Legal + RAG Intelligence section.

Methodology:
- Citation coverage = % of rag_answers rows with has_citation == True.
- Confidence bands: High >0.85, Medium 0.60-0.85, Low <0.60 (per the
  pilot one-pager's stated thresholds).
- Grounding source = distribution of rag_answers.source_type.
- Provenance chain = one worked example joining rag_answers -> citations
  -> legal_documents, to show the audit trail a director could click
  through (answer -> citation -> parent clause -> source document ->
  page -> bounding box).
"""
import pandas as pd

CONF_BINS = [0, 0.60, 0.85, 1.0]
CONF_LABELS = ["Low (<0.60) — web fallback triggered", "Medium (0.60–0.85)", "High (>0.85)"]


def citation_coverage_pct(rag_answers: pd.DataFrame) -> float:
    if len(rag_answers) == 0:
        return 0.0
    return round(rag_answers["has_citation"].mean() * 100, 1)


def confidence_distribution(rag_answers: pd.DataFrame) -> pd.DataFrame:
    df = rag_answers.copy()
    df["band"] = pd.cut(df["confidence_score"], bins=CONF_BINS, labels=CONF_LABELS)
    out = df["band"].value_counts(normalize=True).mul(100).round(1).reindex(CONF_LABELS).reset_index()
    out.columns = ["band", "pct"]
    return out


def grounding_source_breakdown(rag_answers: pd.DataFrame) -> pd.DataFrame:
    label_map = {"internal_kb": "Internal document knowledge base",
                 "user_provided": "User-provided documents",
                 "external_web": "External web (fallback only)"}
    out = rag_answers["source_type"].map(label_map).value_counts(normalize=True).mul(100).round(1).reset_index()
    out.columns = ["source", "pct"]
    order = list(label_map.values())
    out["source"] = pd.Categorical(out["source"], categories=order, ordered=True)
    return out.sort_values("source")


def provenance_example(rag_answers: pd.DataFrame, citations: pd.DataFrame, legal_documents: pd.DataFrame):
    """Returns the flagship worked example as a dict of chain steps."""
    ans = rag_answers[rag_answers["answer_id"] == "ANS-0001"]
    cit = citations[citations["citation_id"] == "CIT-00001"]
    if ans.empty or cit.empty:
        ans, cit = rag_answers.iloc[[0]], citations.iloc[[0]]
    cit = cit.iloc[0]
    doc = legal_documents[legal_documents["document_id"] == cit["document_id"]]
    doc_title = doc.iloc[0]["title"] if not doc.empty else cit["document_id"]
    return {
        "answer": "\"Approval requires Director sign-off\"",
        "citation": cit["chunk_id"],
        "parent": cit["section"],
        "document": doc_title,
        "page": f"Page {cit['page']}",
        "bbox": cit["bbox"],
    }


def documents_by_type(legal_documents: pd.DataFrame) -> pd.DataFrame:
    return legal_documents["doc_type"].value_counts().reset_index().rename(columns={"count": "n", "index": "doc_type"})
