"""
Business logic for the Procurement Intelligence section. Kept free of
Streamlit calls so it can be unit-tested / reused headlessly.

Methodology (see also docs/SCHEMA.md and the in-app Methodology tab):
- Market benchmark = MEDIAN price of listings in listing_status == "valid"
  matching the selected specification (CPU tier, RAM, storage, GPU).
- Outlier detection = 1.5x IQR fence per specification bucket.
- Potential savings (volume calc) = benchmark_price x qty x assumed_discount_pct,
  where assumed_discount_pct comes from procurement_scenarios.csv and is
  explicitly labeled an assumption, never a regulatory fact.
"""
import numpy as np
import pandas as pd

PPN_RATE = 0.12  # UU HPP No.7/2021, general rate since 1 Jan 2025
CPU_TIER_ORDER = ["entry", "mid", "high", "premium"]
CPU_TIER_LABEL = {
    "entry": "Entry (Core i3 / Ryzen 3 / setara)",
    "mid": "Mid (Core i5 / Ryzen 5 / setara)",
    "high": "High (Core i7 / Ryzen 7 / setara)",
    "premium": "Premium (Core i9 / Ryzen 9 / Core Ultra / Ryzen AI tinggi)",
}


def valid_listings(df: pd.DataFrame) -> pd.DataFrame:
    return df[df["listing_status"] == "valid"].copy()


def data_quality_funnel(df: pd.DataFrame) -> pd.DataFrame:
    raw = len(df)
    cleaned = (~df["is_duplicate_listing"]).sum()
    valid = (df["listing_status"] == "valid").sum()
    benchmark_ready = (df["listing_status"] == "valid").sum()  # same set, kept distinct stage name for the funnel story
    return pd.DataFrame({
        "stage": ["Raw Listings", "Cleaned (dedup)", "Valid (spec lengkap, tidak suspicious)", "Benchmark Dataset"],
        "count": [raw, cleaned, valid, benchmark_ready],
    })


def normalize_tax(df: pd.DataFrame, price_col: str, include_ppn: bool) -> pd.Series:
    if include_ppn:
        return df[price_col].astype(float)
    return df[price_col].astype(float) / (1 + PPN_RATE)


def bucket_stats(g: pd.DataFrame, price_col: str = "price_rp") -> dict | None:
    p = g[price_col].astype(float)
    n = len(p)
    if n == 0:
        return None
    q1, med, q3 = p.quantile([.25, .5, .75])
    iqr = q3 - q1
    return dict(n=n, mean=p.mean(), median=med, std=(p.std(ddof=0) if n > 1 else 0.0),
                min=p.min(), max=p.max(), q1=q1, q3=q3,
                lower_fence=q1 - 1.5 * iqr, upper_fence=q3 + 1.5 * iqr)


def find_comparable(df: pd.DataFrame, cpu_tier: str, ram_gb: int, storage_gb: int,
                     gpu: bool, price_col: str = "price_rp", min_n: int = 5):
    stages = [
        ("CPU tier + RAM + storage + GPU", lambda d: d[(d.cpu_tier == cpu_tier) & (d.ram_gb >= ram_gb) &
                                                         (d.storage_gb >= storage_gb) & (d.dedicated_gpu == gpu)]),
        ("CPU tier + RAM + storage", lambda d: d[(d.cpu_tier == cpu_tier) & (d.ram_gb >= ram_gb) &
                                                   (d.storage_gb >= storage_gb)]),
        ("CPU tier + RAM (storage diabaikan)", lambda d: d[(d.cpu_tier == cpu_tier) & (d.ram_gb >= ram_gb)]),
        ("CPU tier saja", lambda d: d[d.cpu_tier == cpu_tier]),
    ]
    best = None
    for label, fn in stages:
        sub = fn(df)
        if len(sub) >= min_n:
            return sub, label
        if best is None and len(sub) >= 1:
            best = (sub, label)
    return best if best else (df.iloc[0:0], "Tidak ada data sebanding")


def volume_scenario_table(df: pd.DataFrame, cpu_tier: str, ram_gb: int, storage_gb: int, gpu: bool,
                           scenarios: pd.DataFrame, price_col: str = "price_rp") -> pd.DataFrame:
    sub, level = find_comparable(df, cpu_tier, ram_gb, storage_gb, gpu, price_col=price_col)
    stats = bucket_stats(sub, price_col=price_col)
    rows = []
    if stats is None:
        return pd.DataFrame()
    for _, r in scenarios.iterrows():
        qty = int(r["qty_tier"])
        disc = float(r["assumed_discount_pct"]) / 100.0
        unit_price = stats["median"] * (1 - disc)
        total = unit_price * qty
        total_no_disc = stats["median"] * qty
        rows.append(dict(
            qty=qty, benchmark_unit_price=stats["median"], assumed_discount_pct=r["assumed_discount_pct"],
            unit_price_after_discount=unit_price, estimated_total=total,
            potential_saving_vs_no_discount=total_no_disc - total, rationale=r["rationale"],
        ))
    out = pd.DataFrame(rows)
    out.attrs["match_level"] = level
    out.attrs["n_sample"] = stats["n"]
    return out


def outside_benchmark_flags(history: pd.DataFrame, listings: pd.DataFrame) -> pd.DataFrame:
    """Flags BNI-side current quotes that sit outside the marketplace benchmark
    range for the same specification — a *procurement risk indicator*, not an
    accusation. See app copy for the exact responsible-terminology wording."""
    valid = valid_listings(listings)
    out_rows = []
    for spec_id, g in history.groupby("spec_id"):
        first = g.iloc[0]
        sub, _ = find_comparable(valid, first["cpu_tier"], first["ram_gb"], first["storage_gb"],
                                  bool(first["dedicated_gpu"]), min_n=3)
        stats = bucket_stats(sub)
        if stats is None:
            continue
        g = g.copy()
        g["benchmark_median"] = stats["median"]
        g["benchmark_upper_fence"] = stats["upper_fence"]
        g["outside_benchmark"] = g["current_quote_unit_price_rp"] > stats["upper_fence"]
        g["deviation_pct"] = (g["current_quote_unit_price_rp"] - stats["median"]) / stats["median"] * 100
        out_rows.append(g)
    return pd.concat(out_rows, ignore_index=True) if out_rows else history.copy()


def fmt_rp(x) -> str:
    if pd.isna(x):
        return "-"
    return f"Rp{x:,.0f}".replace(",", ".")
