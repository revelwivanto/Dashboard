"""
Generates every CSV in data/ from scratch, deterministically (seed=42).

Run this only if you want to regenerate the synthetic portions of the
dataset (e.g. after changing the parameters below). The repo already
ships with the generated CSVs, so running this is optional.

    python data/generate_synthetic_data.py

WHAT IS REAL VS SYNTHETIC
--------------------------------------------------------------------
marketplace_listings.csv : rows with data_type="observed" were fetched
    live from Tokopedia search result pages on 2026-08-27 (see
    source_url + checked_date columns). All other rows are
    data_type="synthetic" — generated here to resemble the observed
    price/spec patterns closely enough to run realistic statistics
    without pretending to be real transactions.
Everything else in this file (procurement_history, legal_documents,
rag_answers, citations, pilot_metrics, business_unit_impact,
process_time_comparison, roi_scenarios, pilot_ramp_curve) is entirely
synthetic/illustrative, built to demonstrate the dashboard's logic.
None of it is actual BNI data. See docs/SCHEMA.md for column-level
detail and REPLACING_WITH_REAL_DATA in README.md for how to swap in
real data later without touching app.py / utils / components.
"""
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta

rng = np.random.default_rng(42)
OUT = Path(__file__).parent

# ============================================================
# 1. marketplace_listings.csv
# ============================================================
OBSERVED = [
    # (title, brand, cpu_brand, cpu_tier, cpu_model, ram, storage, gpu, gpu_model, screen, form_factor,
    #  price, orig_price, rating, sold_min, seller, city, url)
    ("Lenovo IdeaPad Slim 3 14 Ryzen 5 7535HS 16GB/512GB", "Lenovo", "AMD", "mid", "Ryzen 5 7535HS", 16, 512, False, "", 14.0, "clamshell", 11049000, 16999000, 5.0, 9, "royalltech", "Jakarta Utara", "https://www.tokopedia.com/find/laptop-ram-16gb-ssd-512gb"),
    ("ASUS TUF A15 FA506NCG Ryzen 7 7445HS RTX3050 16GB/512GB", "Asus", "AMD", "high", "Ryzen 7 7445HS", 16, 512, True, "RTX 3050 4GB", 15.6, "clamshell", 14269000, np.nan, 5.0, 4, "PUSAT GAMING LAPTOP", "Bekasi", "https://www.tokopedia.com/find/laptop-ram-16gb-ssd-512gb"),
    ("AXIOO PONGO 735 Core i7-13620H RTX3050 16GB/512GB", "Axioo", "Intel", "high", "Core i7-13620H", 16, 512, True, "RTX 3050 6GB", 15.6, "clamshell", 14699000, 17000000, 5.0, 5, "Gamer ID Surabaya", "Surabaya", "https://www.tokopedia.com/find/laptop-ram-16gb-ssd-512gb"),
    ("HP OmniBook 7 Aero 13 Ryzen AI 7-350 16GB/512GB", "HP", "AMD", "high", "Ryzen AI 7-350", 16, 512, False, "", 13.3, "clamshell", 19998500, 19999000, 5.0, 30, "Onestop Gaming", "Jakarta Pusat", "https://www.tokopedia.com/find/laptop-ram-16gb-ssd-512gb"),
    ("Tecno MegaBook T1 14 Core i9-13900HK 16GB/512GB", "Tecno", "Intel", "premium", "Core i9-13900HK", 16, 512, False, "", 14.0, "clamshell", 12479000, 12579000, 5.0, 3, "Herlinacom", "Depok", "https://www.tokopedia.com/find/laptop-ram-16gb-ssd-512gb"),
    ("HP Pavilion Aero OmniBook 7 13 Ryzen AI 7 Radeon 860M 16GB/512GB", "HP", "AMD", "high", "Ryzen AI 7 350", 16, 512, False, "", 13.0, "clamshell", 19529000, np.nan, 5.0, 3, "MyHartono", "Bandung", "https://www.tokopedia.com/find/laptop-ram-16gb-ssd-512gb"),
    ("Colorful Rimbook S1 Core i5-12450H 16GB/512GB UHD", "Colorful", "Intel", "mid", "Core i5-12450H", 16, 512, False, "", 14.0, "clamshell", 9254000, 9259000, 5.0, 1, "GASOL KALIURANG", "Malang", "https://www.tokopedia.com/find/laptop-ram-16gb-ssd-512gb"),
    ("ASUS Vivobook 14 Flip OLED TP3407SA Core Ultra 7 256V 16GB/512GB", "Asus", "Intel", "premium", "Core Ultra 7 256V", 16, 512, False, "", 14.0, "2-in-1 convertible", 23139000, 32000000, 5.0, 3, "Gamer ID Surabaya", "Surabaya", "https://www.tokopedia.com/find/laptop-ram-16gb-ssd-512gb"),
    ("Acer Nitro V15 ANV15-42 Ryzen 7 7445HS RTX4050 16GB/512GB", "Acer", "AMD", "high", "Ryzen 7 7445HS", 16, 512, True, "RTX 4050 6GB", 15.6, "clamshell", 18866000, np.nan, 5.0, 1, "Enter Komputer Official", "Jakarta Pusat", "https://www.tokopedia.com/find/laptop-ram-16gb-ssd-512gb"),
    ("Infinix Xbook B14 Ryzen 5 7535HS 16GB/512GB", "Infinix", "AMD", "mid", "Ryzen 5 7535HS", 16, 512, False, "", 14.0, "clamshell", 8769000, np.nan, 5.0, 2, "AGRES ID PURWAKARTA", "Kab. Purwakarta", "https://www.tokopedia.com/find/laptop-ram-16gb-ssd-512gb"),
    ("SPC Life 5 X Style 5 Core i5-12450H/Ryzen 5 3500 16GB/512GB", "SPC", "Mixed", "mid", "Core i5-12450H / Ryzen 5 3500", 16, 512, False, "", 14.0, "clamshell", 6859000, 9999000, 5.0, 100, "ProStoreComputer", "Jakarta Utara", "https://www.tokopedia.com/find/laptop-i5-ryzen-5"),
    ("Tecno MegaBook T1 14X K16S Core i5-13420H/Ryzen 5 7430 16GB/512GB", "Tecno", "Mixed", "mid", "Core i5-13420H / Ryzen 5 7430", 16, 512, False, "", 14.0, "clamshell", 7819000, 12499000, 5.0, 500, "AI Official Store", "Jakarta Utara", "https://www.tokopedia.com/find/laptop-i5-ryzen-5"),
    ("SPC Life 5 X Style 5 Core i5-12450H/Ryzen 5 3500 16GB/512GB (v2)", "SPC", "Mixed", "mid", "Core i5-12450H / Ryzen 5 3500", 16, 512, False, "", 14.0, "clamshell", 6859000, 10999000, 5.0, 15, "AI Official Store", "Jakarta Utara", "https://www.tokopedia.com/find/laptop-i5-ryzen-5"),
    ("Tecno MegaBook T1 14 K15S Ryzen 5 7430/Core i5-13420H 16GB/512GB", "Tecno", "Mixed", "mid", "Ryzen 5 7430 / Core i5-13420H", 16, 512, False, "", 14.0, "clamshell", 7819000, 12499000, 5.0, 40, "AI Official Store", "Jakarta Utara", "https://www.tokopedia.com/find/laptop-i5-ryzen-5"),
    ("Avita Pura A+ Core i5-1235U/i3-1215U/Ryzen 5 5500U 8GB/256GB", "Avita", "Mixed", "entry", "Core i5-1235U / i3-1215U / Ryzen 5 5500U", 8, 256, False, "", 14.0, "clamshell", 5459000, 12999000, 5.0, 9, "Deca Computer", "Jakarta Utara", "https://www.tokopedia.com/find/laptop-i5-ryzen-5"),
    ("Infinix Xbook/InBook X2 2025 Ryzen 7/Ryzen 5/Core i5-1334 16GB/512GB", "Infinix", "Mixed", "mid", "Ryzen 7 / Ryzen 5 / Core i5-1334", 16, 512, False, "", 14.0, "clamshell", 7709000, 14298900, 4.8, 500, "Gateway Indonesia Comp", "Jakarta Utara", "https://www.tokopedia.com/find/laptop-i5-ryzen-5"),
    ("Avita Pura A+ Core i5-1235U/i3-1215U/Ryzen 5 5500U 8GB/256GB (v2)", "Avita", "Mixed", "entry", "Core i5-1235U / i3-1215U / Ryzen 5 5500U", 8, 256, False, "", 14.0, "clamshell", 5459000, 10999000, np.nan, 1, "AI Official Store", "Jakarta Utara", "https://www.tokopedia.com/find/laptop-i5-ryzen-5"),
]
OBS_COLS = ["title", "brand", "cpu_brand", "cpu_tier", "cpu_model", "ram_gb", "storage_gb", "dedicated_gpu",
            "gpu_model", "screen_in", "form_factor", "price_rp", "orig_price_rp", "rating", "sold_min",
            "seller", "seller_location", "source_url"]
obs_df = pd.DataFrame(OBSERVED, columns=OBS_COLS)
obs_df["marketplace"] = "Tokopedia"
obs_df["checked_date"] = "2026-08-27"
obs_df["data_type"] = "observed"
obs_df["condition"] = "new"
obs_df["listing_status"] = "raw"

# Synthetic listings: sample around the observed price/spec relationship so the
# combined dataset has enough n per bucket for defensible statistics.
BRANDS = ["Lenovo", "Asus", "HP", "Acer", "Dell", "MSI", "Axioo", "Advan", "Zyrex", "SPC", "Infinix"]
CPU_TIER_BASE_PRICE = {"entry": 5.0e6, "mid": 7.5e6, "high": 13.5e6, "premium": 19.0e6}
CPU_MODELS = {
    "entry": ["Core i3-1215U", "Ryzen 3 7320U", "Core i3-N305", "Ryzen 3 5300U"],
    "mid": ["Core i5-1235U", "Ryzen 5 7530U", "Core i5-12450H", "Ryzen 5 7535HS"],
    "high": ["Core i7-1355U", "Ryzen 7 7735HS", "Core i7-13620H", "Ryzen 7 7445HS"],
    "premium": ["Core i9-13900H", "Ryzen 9 7940HS", "Core Ultra 7 155H", "Ryzen AI 9 365"],
}
RAM_OPTS = [4, 8, 16, 32]
STORAGE_OPTS = [128, 256, 512, 1024]
FORM_FACTORS = ["clamshell", "clamshell", "clamshell", "2-in-1 convertible"]
CITIES = ["Jakarta Utara", "Jakarta Pusat", "Jakarta Selatan", "Bandung", "Surabaya", "Semarang", "Bekasi", "Depok", "Malang", "Medan"]

RAM_BY_TIER = {
    "entry": ([4, 8], [0.35, 0.65]),
    "mid": ([8, 16], [0.30, 0.70]),
    "high": ([16, 32], [0.75, 0.25]),
    "premium": ([16, 32], [0.45, 0.55]),
}
STORAGE_BY_TIER = {
    "entry": ([128, 256, 512], [0.30, 0.55, 0.15]),
    "mid": ([256, 512, 1024], [0.25, 0.65, 0.10]),
    "high": ([512, 1024], [0.70, 0.30]),
    "premium": ([512, 1024], [0.55, 0.45]),
}

n_synth = 165
rows = []
for i in range(n_synth):
    tier = rng.choice(list(CPU_TIER_BASE_PRICE.keys()), p=[0.30, 0.38, 0.24, 0.08])
    ram_choices, ram_p = RAM_BY_TIER[tier]
    ram = int(rng.choice(ram_choices, p=ram_p))
    sto_choices, sto_p = STORAGE_BY_TIER[tier]
    storage = int(rng.choice(sto_choices, p=sto_p))
    gpu = bool(rng.random() < (0.35 if tier in ("high", "premium") else 0.04))
    base = CPU_TIER_BASE_PRICE[tier]
    ram_adj = {4: -1.4e6, 8: -0.6e6, 16: 0.0, 32: 2.6e6}[ram]
    sto_adj = {128: -0.8e6, 256: -0.3e6, 512: 0.0, 1024: 1.6e6}[storage]
    gpu_adj = 5.5e6 if gpu else 0.0
    noise = rng.normal(0, base * 0.10)
    price = max(3.0e6, base + ram_adj + sto_adj + gpu_adj + noise)
    # inject a small number of deliberately-implausible listings so the outlier/
    # data-quality logic has something real to catch
    is_bait = rng.random() < 0.035
    if is_bait:
        price = price * rng.uniform(0.15, 0.35)
    orig_bump = price * rng.uniform(0.0, 0.35) if rng.random() < 0.55 else 0.0
    rating = np.nan if (is_bait and rng.random() < 0.7) else round(float(rng.choice([5.0, 5.0, 4.9, 4.8, 4.7, 4.5])), 1)
    sold = int(rng.integers(0, 3)) if is_bait else int(rng.integers(1, 600))
    brand = rng.choice(BRANDS)
    cpu_brand = "AMD" if "Ryzen" in (m := rng.choice(CPU_MODELS[tier])) else "Intel"
    rows.append(dict(
        title=f"{brand} Notebook {m} {ram}GB/{storage}GB" + (" + GPU diskrit" if gpu else ""),
        brand=brand, cpu_brand=cpu_brand, cpu_tier=tier, cpu_model=m, ram_gb=ram, storage_gb=storage,
        dedicated_gpu=gpu, gpu_model=("RTX 3050 4GB" if gpu and tier == "high" else ("RTX 4060 8GB" if gpu else "")),
        screen_in=float(rng.choice([13.3, 14.0, 15.6, 16.0])), form_factor=rng.choice(FORM_FACTORS),
        price_rp=round(price, -3), orig_price_rp=(round(price + orig_bump, -3) if orig_bump else np.nan),
        rating=rating, sold_min=sold, seller=f"Toko {brand} Resmi {i%23}", seller_location=rng.choice(CITIES),
        source_url="", marketplace=rng.choice(["Tokopedia", "Shopee"]),
        checked_date="2026-08-27", data_type="synthetic",
        condition=rng.choice(["new", "new", "new", "refurbished"]),
        listing_status="raw",
    ))
synth_df = pd.DataFrame(rows)

listings = pd.concat([obs_df, synth_df], ignore_index=True)
listings.insert(0, "listing_id", [f"LST{i+1:04d}" for i in range(len(listings))])

# --- data-quality pipeline: raw -> cleaned -> valid ---
listings["is_duplicate_listing"] = listings.duplicated(subset=["title", "price_rp", "seller"], keep="first")
listings["is_bundle"] = listings["title"].str.contains(r"\+ Office|\+ M365|bundle", case=False, regex=True, na=False)
listings["is_promo"] = listings["orig_price_rp"].notna() & (listings["orig_price_rp"] > listings["price_rp"])
listings["missing_spec"] = listings["ram_gb"].isna() | listings["storage_gb"].isna() | listings["cpu_tier"].isna()

def flag_outliers(df):
    df = df.copy()
    df["is_price_outlier"] = False
    for tier, idx in df.groupby(["cpu_tier", "ram_gb", "storage_gb"]).groups.items():
        p = df.loc[idx, "price_rp"].astype(float)
        if len(p) < 4:
            continue
        q1, q3 = p.quantile([.25, .75])
        iqr = q3 - q1
        lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        df.loc[idx, "is_price_outlier"] = (p < lo) | (p > hi)
    return df

listings = flag_outliers(listings)
low_signal = listings["rating"].isna() | (listings["sold_min"] <= 2)
listings["is_suspicious"] = listings["is_price_outlier"] & low_signal
listings["listing_status"] = np.select(
    [listings["is_duplicate_listing"], listings["is_suspicious"]],
    ["removed_duplicate", "flagged_suspicious"],
    default="cleaned",
)
listings.loc[(listings["listing_status"] == "cleaned") & ~listings["missing_spec"], "listing_status"] = "valid"

col_order = ["listing_id", "title", "brand", "cpu_brand", "cpu_tier", "cpu_model", "ram_gb", "storage_gb",
             "dedicated_gpu", "gpu_model", "screen_in", "form_factor", "condition", "price_rp", "orig_price_rp",
             "rating", "sold_min", "marketplace", "seller", "seller_location", "source_url", "checked_date",
             "is_duplicate_listing", "is_bundle", "is_promo", "missing_spec", "is_price_outlier", "is_suspicious",
             "listing_status", "data_type"]
listings[col_order].to_csv(OUT / "marketplace_listings.csv", index=False)

# ============================================================
# 2. procurement_laptops.csv  (BNI standard specification catalog)
# ============================================================
catalog = pd.DataFrame([
    dict(spec_id="SPEC-ENTRY", spec_name="Staf Administrasi / Front Office", cpu_tier="entry", ram_gb=8, storage_gb=256, dedicated_gpu=False, screen_in=14.0, form_factor="clamshell", typical_business_unit="Operations"),
    dict(spec_id="SPEC-MID", spec_name="Staf Analis / Back Office", cpu_tier="mid", ram_gb=16, storage_gb=512, dedicated_gpu=False, screen_in=14.0, form_factor="clamshell", typical_business_unit="Finance & Risk"),
    dict(spec_id="SPEC-HIGH", spec_name="Developer / Data & IT", cpu_tier="high", ram_gb=16, storage_gb=512, dedicated_gpu=True, screen_in=15.6, form_factor="clamshell", typical_business_unit="IT & Digital"),
    dict(spec_id="SPEC-PREMIUM", spec_name="Eksekutif / Manajemen Senior", cpu_tier="premium", ram_gb=16, storage_gb=512, dedicated_gpu=False, screen_in=14.0, form_factor="2-in-1 convertible", typical_business_unit="Corporate Affairs"),
])
catalog["data_type"] = "internal_assumption"
catalog.to_csv(OUT / "procurement_laptops.csv", index=False)

# ============================================================
# 3. procurement_history.csv  (synthetic BNI-side PO history, 24 months)
# ============================================================
BUSINESS_UNITS = ["Operations", "Finance & Risk", "IT & Digital", "Corporate Affairs", "Retail Banking", "Compliance"]
SPEC_IDS = catalog["spec_id"].tolist()
SPEC_MAP = catalog.set_index("spec_id").to_dict("index")
VENDORS = ["Vendor A", "Vendor B", "Vendor C", "Vendor D", "Vendor E"]

start = datetime(2024, 9, 1)
n_po = 620
po_rows = []
# seed a controlled number of near-duplicate clusters (same unit+spec within 45 days)
cluster_dates = []
for _ in range(30):
    d0 = start + timedelta(days=int(rng.integers(0, 700)))
    cluster_dates.append(d0)

for i in range(n_po):
    unit = rng.choice(BUSINESS_UNITS)
    spec_id = rng.choice(SPEC_IDS, p=[0.35, 0.35, 0.20, 0.10])
    spec = SPEC_MAP[spec_id]
    if i < len(cluster_dates) * 2:
        # deliberately create a near-duplicate: two POs, same unit/spec, close dates
        base_date = cluster_dates[i // 2]
        po_date = base_date + timedelta(days=int(rng.integers(0, 40)) if i % 2 else 0)
        unit = BUSINESS_UNITS[i % len(BUSINESS_UNITS)]
    else:
        po_date = start + timedelta(days=int(rng.integers(0, 720)))
    base_mkt = CPU_TIER_BASE_PRICE[spec["cpu_tier"]] + (5.5e6 if spec["dedicated_gpu"] else 0.0)
    historical_price = base_mkt * rng.uniform(1.02, 1.20)
    current_quote = base_mkt * rng.uniform(0.98, 1.30)
    qty = int(rng.choice([5, 10, 15, 20, 25, 30, 40, 50], p=[0.20, 0.22, 0.15, 0.15, 0.1, 0.08, 0.06, 0.04]))
    po_rows.append(dict(
        po_id=f"PO-{2400+i:05d}", po_date=po_date.strftime("%Y-%m-%d"), business_unit=unit,
        spec_id=spec_id, cpu_tier=spec["cpu_tier"], ram_gb=spec["ram_gb"], storage_gb=spec["storage_gb"],
        dedicated_gpu=spec["dedicated_gpu"], qty=qty,
        historical_unit_price_rp=round(historical_price, -3),
        current_quote_unit_price_rp=round(current_quote, -3),
        vendor=rng.choice(VENDORS),
        has_benchmark_reference=bool(rng.random() < 0.55),
        has_supporting_doc=bool(rng.random() < 0.80),
        data_type="synthetic",
    ))
hist = pd.DataFrame(po_rows)
hist["historical_total_rp"] = hist["historical_unit_price_rp"] * hist["qty"]
hist["current_quote_total_rp"] = hist["current_quote_unit_price_rp"] * hist["qty"]
hist.to_csv(OUT / "procurement_history.csv", index=False)

# ============================================================
# 4. procurement_scenarios.csv  (volume-discount assumption by qty tier)
# ============================================================
scenarios = pd.DataFrame([
    dict(qty_tier=10, assumed_discount_pct=0, rationale="Baseline eceran, tanpa negosiasi volume", source="assumption"),
    dict(qty_tier=25, assumed_discount_pct=3, rationale="Diskon kecil lazim untuk pembelian batch di atas ~20 unit (observasi pasar umum)", source="assumption"),
    dict(qty_tier=50, assumed_discount_pct=6, rationale="Estimasi skenario negosiasi menengah", source="assumption"),
    dict(qty_tier=100, assumed_discount_pct=9, rationale="Estimasi skenario negosiasi volume besar", source="assumption"),
    dict(qty_tier=250, assumed_discount_pct=12, rationale="Estimasi skenario kontrak tahunan / rate card vendor", source="assumption"),
])
scenarios["data_type"] = "assumption"
scenarios.to_csv(OUT / "procurement_scenarios.csv", index=False)

# ============================================================
# 5. assumptions.csv  (pricing / tax / margin / ROI-input assumptions register)
# Every row here is an INPUT some downstream calculation reads — nothing
# below is a final dashboard number, only levers that feed utils/roi_calc.py.
# ============================================================
assumptions = pd.DataFrame([
    dict(assumption_id="TAX-PPN", category="tax", description="Tarif PPN umum Indonesia", value="12%",
         status="regulatory_fact", source="UU No.7/2021 (UU HPP), berlaku sejak 1 Jan 2025", notes="Berlaku untuk barang umum termasuk laptop; harga marketplace konsumen sudah termasuk PPN."),
    dict(assumption_id="PROC-HPS-BASIS", category="procurement_regulation", description="Dasar hukum penyusunan HPS pengadaan barang", value="Survei harga pasar",
         status="regulatory_fact", source="Perpres 16/2018 jo. Perpres 12/2021 jo. Perpres 46/2025", notes="HPS barang disusun dari survei pasar, bukan pendekatan cost-plus-margin seperti pekerjaan konstruksi."),
    dict(assumption_id="PROC-MARGIN-PCT", category="procurement_regulation", description="Persentase margin/keuntungan vendor yang dibakukan regulasi", value="Tidak ditemukan",
         status="no_regulatory_basis", source="Penelusuran Perpres 16/2018 jo. 12/2021 jo. 46/2025 dan turunannya (Peraturan LKPP)", notes="Tidak ada angka margin baku secara persentase untuk pengadaan barang. Setiap angka diskon/margin di dashboard ini adalah ASUMSI skenario, dapat diubah pengguna."),
    dict(assumption_id="VOL-DISCOUNT", category="volume_scenario", description="Asumsi diskon volume per tingkat kuantitas", value="lihat procurement_scenarios.csv",
         status="assumption", source="Estimasi internal, bukan data vendor aktual", notes="Ganti dengan data historis negosiasi vendor riil bila tersedia."),
    dict(assumption_id="ROI-FORMULA", category="roi", description="Formula ROI skenario pilot", value="ROI = (Est. Annual Benefit − Pilot Investment) / Pilot Investment",
         status="methodology", source="Internal", notes="Payback (bulan) = (Pilot Investment / Est. Annual Benefit) x 12. Diimplementasikan di utils/roi_calc.py:roi_and_payback()."),
    dict(assumption_id="BNI-EMPLOYEES", category="procurement_volume", description="Jumlah karyawan BNI", value="27201",
         status="observed_external", source="Wikipedia infobox 'Bank Negara Indonesia' mengutip profil perusahaan/laporan BNI (FY2025); BNI menyatakan >27.000 karyawan per akhir 2024", notes="Real, bukan pengadaan langsung — dipakai sebagai input basis estimasi volume pengadaan laptop tahunan."),
    dict(assumption_id="DEVICE-ELIGIBLE-PCT", category="procurement_volume", description="Persentase karyawan yang diasumsikan menggunakan laptop kerja (bukan staf cabang/teller front-line)", value="35%",
         status="assumption", source="Estimasi internal, bukan data BNI resmi", notes="BNI punya 1.834 kantor domestik dengan banyak staf front-office/teller yang lazimnya memakai PC desktop/terminal kasir, bukan laptop — 35% adalah asumsi kasar porsi staf kantor/analis/manajemen yang eligible laptop."),
    dict(assumption_id="DEVICE-REFRESH-RATE", category="procurement_volume", description="Persentase perangkat yang di-refresh/diadakan ulang per tahun", value="25%",
         status="assumption", source="Asumsi siklus refresh 4 tahun (umum di manajemen aset TI korporat)", notes="1/4 tahun = 25% populasi laptop diprocure ulang tiap tahun."),
    dict(assumption_id="SALARY-COMPLIANCE-ANNUAL", category="labor_cost", description="Rata-rata gaji pokok tahunan Compliance Officer di Indonesia", value="Rp70.749.733/tahun",
         status="observed_external", source="Payscale.com, 'Average Compliance Officer Salary in Indonesia' (data crowdsourced, diakses 27 Agu 2026)", notes="Bukan data spesifik BNI — benchmark pasar umum, self-reported/crowdsourced, indikatif saja. Dipakai sebagai proksi biaya tenaga kerja legal/compliance/procurement untuk monetisasi penghematan waktu."),
    dict(assumption_id="WORK-HOURS-PER-MONTH", category="labor_cost", description="Jam kerja standar per bulan", value="173",
         status="methodology", source="Konvensi umum turunan UU Ketenagakerjaan No.13/2003 (40 jam/minggu x 52 minggu / 12 bulan ≈ 173,3 jam/bulan)", notes="Dipakai untuk mengonversi gaji bulanan menjadi tarif per jam."),
    dict(assumption_id="ADOPTION-RATE", category="roi_scenario", description="Persentase potensi penghematan waktu & prosedur yang benar-benar terealisasi (adopsi staf)", value="Conservative 50% / Base 80% / Upside 100%",
         status="assumption", source="Estimasi internal skenario", notes="Diterapkan sebagai pengali pada time_savings_benefit dan procurement_savings_benefit — lihat roi_scenarios.csv."),
    dict(assumption_id="DISCOUNT-TIER-BY-SCENARIO", category="roi_scenario", description="Tingkat kuantitas prosedur diskon volume yang dipakai tiap skenario ROI", value="Conservative: qty 25 / Base: qty 100 / Upside: qty 250",
         status="assumption", source="Merujuk procurement_scenarios.csv", notes="Menentukan potongan harga volume mana yang dipakai saat menghitung procurement_savings_benefit per skenario."),
    dict(assumption_id="CITATION-PRIOR-SOP", category="rag_quality", description="Prior probabilitas sitasi valid — kategori SOP & Sirkular Internal", value="0.80",
         status="assumption", source="Asumsi pemodelan: dokumen SOP internal pendek, format konsisten, terindeks baik", notes="Diimplementasikan di utils/roi_calc.py:CATEGORY_BASE_PRIOR."),
    dict(assumption_id="CITATION-PRIOR-KONTRAK", category="rag_quality", description="Prior probabilitas sitasi valid — kategori Kontrak & Perjanjian Vendor", value="0.72",
         status="assumption", source="Asumsi pemodelan: kontrak lebih panjang & bervariasi formatnya", notes="Diimplementasikan di utils/roi_calc.py:CATEGORY_BASE_PRIOR."),
    dict(assumption_id="CITATION-PRIOR-REGULASI", category="rag_quality", description="Prior probabilitas sitasi valid — kategori Referensi Regulasi Eksternal", value="0.62",
         status="assumption", source="Asumsi pemodelan: teks regulasi eksternal paling panjang & paling tidak seragam formatnya", notes="Diimplementasikan di utils/roi_calc.py:CATEGORY_BASE_PRIOR."),
    dict(assumption_id="CITATION-CONF-SLOPE", category="rag_quality", description="Kemiringan penyesuaian probabilitas sitasi valid terhadap confidence_score jawaban induk", value="0.35",
         status="assumption", source="Asumsi pemodelan: confidence & ketepatan sitasi diasumsikan berkorelasi positif", notes="validity_prob = prior_kategori + (confidence_score − 0.7) × 0.35, di-clip ke [0.05, 0.99]."),
    dict(assumption_id="SOURCE-TYPE-PROB", category="rag_quality", description="Probabilitas sumber grounding jawaban RAG (internal KB / dokumen pengguna / web eksternal)", value="70% / 20% / 10%",
         status="assumption", source="Asumsi desain sistem: retrieval internal-first, web hanya fallback", notes="Persentase aktual pada rag_answers.csv adalah HASIL sampling dari probabilitas ini (rng.choice), bukan dipaksa sama persis."),
    dict(assumption_id="CONFIDENCE-BAND-PROB", category="rag_quality", description="Probabilitas pita confidence jawaban RAG (High >0.85 / Medium 0.60–0.85 / Low <0.60)", value="75% / 20% / 5%",
         status="assumption", source="Asumsi desain sistem pilot", notes="confidence_score disampel dari distribusi Beta per pita ini, lalu confidence_distribution() menghitung ulang persentase aktualnya dari confidence_score — angka akhir bisa sedikit berbeda dari 75/20/5 karena hasil sampling acak (seed=42)."),
    dict(assumption_id="INVEST-DEV", category="investment", description="Biaya pengembangan & integrasi (tim kecil, ~4 bulan)", value="lihat investment_breakdown.csv",
         status="assumption", source="Estimasi tarif blended tim AI engineering pilot skala kecil di Indonesia — TIDAK dikutip dari sumber pihak ketiga tunggal, perlu divalidasi dengan RAB riil", notes="Komponen terbesar dari pilot_investment_rp."),
    dict(assumption_id="INVEST-LLM", category="investment", description="Biaya API LLM & infrastruktur cloud per dokumen diproses", value="Rp500/dokumen (estimasi)",
         status="assumption", source="Estimasi order-of-magnitude biaya panggilan embedding+LLM per dokumen — bukan tarif vendor tertentu", notes="× jumlah dokumen di legal_documents.csv."),
    dict(assumption_id="INVEST-CHANGEMGMT", category="investment", description="Biaya change management & pelatihan pengguna", value="lihat investment_breakdown.csv",
         status="assumption", source="Estimasi internal", notes="Komponen tetap, tidak berskala dengan volume dokumen."),
    dict(assumption_id="RAMP-CURVE-FORMULA", category="methodology", description="Formula kurva ramp-up ingestion pilot 6 minggu", value="logistic: total / (1 + e^(-steepness × (week − midpoint)))",
         status="methodology", source="Internal — utils/roi_calc.py:logistic_ramp()", notes="midpoint_week=3.5, steepness=0.9, total = RECORDS_SEARCHABLE_TOTAL (pilot_metrics.csv)."),
])
assumptions.to_csv(OUT / "assumptions.csv", index=False)

# ============================================================
# 6. legal_documents.csv
# ============================================================
DOC_TYPES = ["SOP", "Kebijakan Internal", "Kontrak Vendor", "Peraturan Perundangan (referensi)", "Nota Dinas", "RKS/RAB"]
doc_titles = [
    "SOP Pengadaan Barang/Jasa v3", "Kebijakan Procurement Threshold 2025", "Kontrak Vendor Laptop 2024-2026",
    "Perpres 16/2018 jo. 12/2021 jo. 46/2025 (referensi)", "Nota Dinas Izin Prinsip Pengadaan", "RKS Pengadaan Laptop Batch 2025",
    "SOP Approval Matrix Procurement", "Kebijakan Anti-Fraud & Gratifikasi", "Kontrak Vendor Laptop Alternatif",
    "Pedoman HPS Barang/Jasa", "Nota Dinas Perpanjangan Kontrak", "RAB Pengadaan Perangkat IT 2025",
]
n_docs = 40
doc_rows = []
for i in range(n_docs):
    dt = rng.choice(DOC_TYPES)
    doc_rows.append(dict(
        document_id=f"DOC-{i+1:04d}", title=f"{rng.choice(doc_titles)} #{i+1}", doc_type=dt,
        business_unit=rng.choice(BUSINESS_UNITS), upload_date=(start + timedelta(days=int(rng.integers(0, 720)))).strftime("%Y-%m-%d"),
        page_count=int(rng.integers(2, 45)), status="processed", data_type="synthetic",
    ))
# guarantee the flagship provenance example document exists
doc_rows[0] = dict(document_id="DOC-0001", title="Procurement_SOP_v3", doc_type="SOP",
                    business_unit="IT & Digital", upload_date="2025-02-10", page_count=48,
                    status="processed", data_type="synthetic")
legal_docs = pd.DataFrame(doc_rows)
legal_docs.to_csv(OUT / "legal_documents.csv", index=False)

# ============================================================
# 7. rag_answers.csv + 8. citations.csv
# Confidence & source-type are SAMPLED from documented probabilities
# (assumptions.csv: SOURCE-TYPE-PROB, CONFIDENCE-BAND-PROB), not
# constructed to force a specific output percentage — the aggregate
# split you see on the dashboard is whatever this seeded simulation
# actually produces.
# ============================================================
QUESTIONS = [
    "Apa syarat approval untuk pengadaan di atas Rp200 juta?",
    "Berapa ambang batas nilai yang memerlukan tanda tangan Direktur?",
    "Apa dasar hukum penyusunan HPS untuk pengadaan laptop?",
    "Apakah kontrak vendor laptop saat ini sudah termasuk PPN?",
    "Berapa lama masa berlaku kontrak vendor laptop 2024?",
    "Dokumen apa yang wajib dilampirkan pada RKS pengadaan?",
    "Apa perbedaan RAB Direktorat Bidang dan RAB reguler?",
    "Siapa yang berwenang menyetujui perubahan spesifikasi pengadaan?",
    "Apakah ada ketentuan margin vendor yang dibakukan?",
    "Bagaimana prosedur jika ditemukan indikasi harga di luar benchmark pasar?",
]
SOURCE_TYPE_P = dict(internal_kb=0.70, user_provided=0.20, external_web=0.10)
CONF_BAND_P = dict(high=0.75, medium=0.20, low=0.05)
CONF_BAND_RANGE = dict(high=(0.86, 0.99), medium=(0.60, 0.85), low=(0.20, 0.59))

n_answers = 300
ans_rows = []
for i in range(n_answers):
    band = rng.choice(list(CONF_BAND_P.keys()), p=list(CONF_BAND_P.values()))
    lo, hi = CONF_BAND_RANGE[band]
    conf = float(rng.uniform(lo, hi))
    src = rng.choice(list(SOURCE_TYPE_P.keys()), p=list(SOURCE_TYPE_P.values()))
    grounded = src != "external_web" or conf >= 0.60
    ans_rows.append(dict(
        answer_id=f"ANS-{i+1:04d}", question=rng.choice(QUESTIONS), business_unit=rng.choice(BUSINESS_UNITS),
        answer_date=(start + timedelta(days=int(rng.integers(0, 720)))).strftime("%Y-%m-%d"),
        confidence_score=round(conf, 3), source_type=src, grounded=bool(grounded),
        has_citation=bool(rng.random() < (0.97 if grounded else 0.40)),
        data_type="synthetic",
    ))
ans_rows[0].update(dict(answer_id="ANS-0001", question="Apa syarat approval untuk pengadaan di atas Rp200 juta?",
                         confidence_score=0.94, source_type="internal_kb", grounded=True, has_citation=True))
rag_answers = pd.DataFrame(ans_rows)
rag_answers.to_csv(OUT / "rag_answers.csv", index=False)

cit_rows = []
cid = 1
for _, a in rag_answers.iterrows():
    if not a["has_citation"]:
        continue
    n_cite = int(rng.integers(1, 3))
    for _ in range(n_cite):
        doc = legal_docs.sample(1, random_state=int(rng.integers(0, 1_000_000))).iloc[0]
        cit_rows.append(dict(
            citation_id=f"CIT-{cid:05d}", answer_id=a["answer_id"], document_id=doc["document_id"],
            chunk_id=f"Chunk_{rng.integers(1, 9999):04d}", page=int(rng.integers(1, max(2, doc["page_count"]))),
            section=f"Sec. {rng.integers(1,9)}.{rng.integers(1,9)}", bbox=f"x:{rng.integers(50,400)}-{rng.integers(400,700)},y:{rng.integers(100,500)}-{rng.integers(500,700)}",
            data_type="synthetic",
        ))
        cid += 1
# flagship, exact provenance example referenced in the pilot one-pager
cit_rows[0] = dict(citation_id="CIT-00001", answer_id="ANS-0001", document_id="DOC-0001",
                    chunk_id="Chunk_0042", page=14, section="Sec. 3.2 Approval", bbox="x:105-310,y:420-435",
                    data_type="synthetic")
citations = pd.DataFrame(cit_rows)
citations.to_csv(OUT / "citations.csv", index=False)

# ============================================================
# 9. citation_evaluations.csv + citation_validity_by_category.csv
# COMPUTED via utils/roi_calc.py — pct_valid_citation is the OUTPUT of
# simulating a per-citation validity check, not a typed percentage.
# ============================================================
import sys
sys.path.insert(0, str(OUT.parent))
from utils import roi_calc as rc

citation_evals = rc.build_citation_evaluations(citations, legal_docs, rag_answers, rng)
citation_evals.to_csv(OUT / "citation_evaluations.csv", index=False)
cite_validity = rc.citation_validity_by_category(citation_evals)
cite_validity.to_csv(OUT / "citation_validity_by_category.csv", index=False)

# ============================================================
# 10. process_time_comparison.csv (Graph 6) + process_annual_volume.csv
# before/after minutes remain a hypothesis (no time-motion study exists
# for a system that hasn't been built yet) — explicitly labeled
# "illustrative" for those two input columns only. Everything derived
# from them (hours/rupiah saved) is calculated, not typed.
# ============================================================
proc_time = pd.DataFrame([
    dict(process_name="Legal document preparation", before_minutes=90, after_minutes=27, data_type="illustrative"),
    dict(process_name="Source / citation verification", before_minutes=60, after_minutes=7, data_type="illustrative"),
    dict(process_name="Procurement price comparison", before_minutes=75, after_minutes=8, data_type="illustrative"),
    dict(process_name="Document review", before_minutes=50, after_minutes=14, data_type="illustrative"),
])
proc_time["pct_reduction"] = ((proc_time["before_minutes"] - proc_time["after_minutes"]) / proc_time["before_minutes"] * 100).round(0)
proc_time.to_csv(OUT / "process_time_comparison.csv", index=False)

# Annual occurrence assumption per process — grounded where possible in
# actual generated dataset volumes (rag_answers/citations counts), rather
# than an arbitrary typed number.
annual_volume = pd.DataFrame([
    dict(process_name="Legal document preparation", estimated_annual_occurrences=len(legal_docs) * 6,
         basis="Asumsi: setiap dokumen di legal_documents.csv rata-rata direvisi/dipersiapkan ulang ~6x/tahun (amandemen, adendum, dsb)"),
    dict(process_name="Source / citation verification", estimated_annual_occurrences=len(rag_answers) * 12,
         basis=f"Diskalakan dari volume rag_answers.csv ({len(rag_answers)} jawaban sampel) x 12 asumsi run-rate bulanan produksi"),
    dict(process_name="Procurement price comparison", estimated_annual_occurrences=len(hist),
         basis="= jumlah PO di procurement_history.csv (620) — setiap PO idealnya melalui 1x price comparison"),
    dict(process_name="Document review", estimated_annual_occurrences=len(legal_docs) * 8,
         basis="Asumsi: setiap dokumen direview ~8x/tahun oleh berbagai pemangku kepentingan"),
])
annual_volume["data_type"] = "assumption"
annual_volume.to_csv(OUT / "process_annual_volume.csv", index=False)

# ============================================================
# 11. investment_breakdown.csv — components sum to pilot_investment_rp
# ============================================================
n_docs_processed = len(legal_docs)
investment_rows = [
    dict(component="Pengembangan & integrasi (tim 3 orang x 4 bulan)", basis="Estimasi tarif blended tim AI engineering pilot skala kecil di Indonesia (ASUMSI, bukan RAB riil)",
         unit_cost_rp=45_000_000, quantity=12, unit="orang-bulan"),
    dict(component="Biaya API LLM & infrastruktur cloud", basis="Rp500/dokumen (estimasi order-of-magnitude) x jumlah dokumen diproses",
         unit_cost_rp=500, quantity=n_docs_processed, unit="dokumen"),
    dict(component="Change management & pelatihan pengguna", basis="Estimasi biaya tetap sesi pelatihan lintas unit bisnis",
         unit_cost_rp=150_000_000, quantity=1, unit="paket"),
]
investment = pd.DataFrame(investment_rows)
investment["total_rp"] = investment["unit_cost_rp"] * investment["quantity"]
investment["data_type"] = "assumption"
investment.to_csv(OUT / "investment_breakdown.csv", index=False)
PILOT_INVESTMENT_RP = float(investment["total_rp"].sum())

# ============================================================
# 12. roi_scenarios.csv — fully bottom-up, computed via utils/roi_calc.py
# ============================================================
SALARY_MONTHLY_RP = 70_749_733 / 12
HOURLY_RATE_RP = rc.hourly_rate_rp(SALARY_MONTHLY_RP, work_hours_per_month=173.0)
BNI_EMPLOYEES = 27_201
DEVICE_ELIGIBLE_PCT = 0.35
DEVICE_REFRESH_RATE = 0.25
ANNUAL_PROCUREMENT_UNITS = rc.annual_procurement_units(BNI_EMPLOYEES, DEVICE_ELIGIBLE_PCT, DEVICE_REFRESH_RATE)

# Market benchmark vs BNI current-quote average, per the SAME data already
# used everywhere else in the dashboard (procurement_calc.find_comparable).
from utils import procurement_calc as pcalc
valid_mkt = pcalc.valid_listings(listings)
_sub, _level = pcalc.find_comparable(valid_mkt, "mid", 16, 512, False, min_n=5)
_stats = pcalc.bucket_stats(_sub)
BENCHMARK_MEDIAN_RP = _stats["median"]
CURRENT_QUOTE_AVG_RP = float(hist.loc[hist.spec_id == "SPEC-MID", "current_quote_unit_price_rp"].mean())

SCENARIO_PARAMS = [
    dict(scenario="Conservative", adoption_rate=0.50, discount_qty_tier=25),
    dict(scenario="Base Case", adoption_rate=0.80, discount_qty_tier=100),
    dict(scenario="Upside", adoption_rate=1.00, discount_qty_tier=250),
]
roi_rows = []
for sp in SCENARIO_PARAMS:
    ts = rc.time_savings_benefit(proc_time, annual_volume, HOURLY_RATE_RP, sp["adoption_rate"])
    time_savings_total = float(ts["rp_saved_per_year"].sum())
    disc_pct = float(scenarios.loc[scenarios.qty_tier == sp["discount_qty_tier"], "assumed_discount_pct"].iloc[0]) / 100.0
    effective_benchmark = rc.effective_benchmark_with_discount(CURRENT_QUOTE_AVG_RP, BENCHMARK_MEDIAN_RP, disc_pct)
    proc_savings = rc.procurement_savings_benefit(CURRENT_QUOTE_AVG_RP, effective_benchmark, ANNUAL_PROCUREMENT_UNITS, sp["adoption_rate"])
    annual_benefit = time_savings_total + proc_savings
    rp = rc.roi_and_payback(PILOT_INVESTMENT_RP, annual_benefit)
    roi_rows.append(dict(
        scenario=sp["scenario"], adoption_rate=sp["adoption_rate"], discount_qty_tier=sp["discount_qty_tier"],
        time_savings_benefit_rp=round(time_savings_total, -3), procurement_savings_benefit_rp=round(proc_savings, -3),
        pilot_investment_rp=PILOT_INVESTMENT_RP, est_annual_benefit_rp=round(annual_benefit, -3),
        roi_x=round(rp["roi_x"], 3), payback_months=round(rp["payback_months"], 2), data_type="calculated",
    ))
roi_scenarios = pd.DataFrame(roi_rows)
roi_scenarios.to_csv(OUT / "roi_scenarios.csv", index=False)

# ============================================================
# 13. pilot_metrics.csv — every value = an actual count/computation, not typed
# ============================================================
records_searchable_total = len(hist) + len(listings) + len(legal_docs) + len(rag_answers) + len(citations)
base_case_roi = float(roi_scenarios.loc[roi_scenarios.scenario == "Base Case", "roi_x"].iloc[0])
pilot_metrics = pd.DataFrame([
    dict(metric_id="TOTAL_DOCS_PROCESSED", label="Total Documents Processed", value=len(legal_docs), unit="documents",
         category="RAG", data_type="calculated", source="= len(legal_documents.csv)"),
    dict(metric_id="RECORDS_SEARCHABLE_TOTAL", label="Historical/Legal/RAG Records Made Searchable (this prototype dataset)",
         value=records_searchable_total, unit="records", category="RAG", data_type="calculated",
         source="= len(procurement_history)+len(marketplace_listings)+len(legal_documents)+len(rag_answers)+len(citations)"),
    dict(metric_id="ROI_HEADLINE", label="ROI on Pilot Investment (Base Case)", value=base_case_roi, unit="x",
         category="ROI", data_type="calculated", source="= roi_scenarios.csv, Base Case row (see full breakdown in-app)"),
])
pilot_metrics.to_csv(OUT / "pilot_metrics.csv", index=False)

# ============================================================
# 14. pilot_ramp_curve.csv — computed logistic ramp, not hand-picked points
# ============================================================
ramp_values = rc.logistic_ramp(total=records_searchable_total, n_weeks=6, midpoint_week=3.5, steepness=0.9)
ramp = pd.DataFrame(dict(pilot_week=range(1, 7), cumulative_records_searchable=ramp_values.astype(int)))
ramp["data_type"] = "calculated"
ramp.to_csv(OUT / "pilot_ramp_curve.csv", index=False)

# ============================================================
# 15. doc_prep_time.csv — kept as an explicit, labeled hypothesis (Image 1, chart 1)
# ============================================================
doc_prep = pd.DataFrame([
    dict(complexity="Dokumen sederhana", before_minutes=45, after_minutes=12, data_type="illustrative"),
    dict(complexity="Dokumen standar", before_minutes=70, after_minutes=20, data_type="illustrative"),
    dict(complexity="Dokumen kompleks", before_minutes=90, after_minutes=25, data_type="illustrative"),
])
doc_prep.to_csv(OUT / "doc_prep_time.csv", index=False)

# ============================================================
# 16. business_unit_impact.csv — COMPUTED allocation, not typed
# Procurement = its own directly-computed benefit (Base Case). Time-savings
# benefit (Base Case) is allocated across the other three units in
# proportion to each unit's share of rag_answers.csv usage — an explicit,
# reproducible rule instead of a hand-picked split.
# ============================================================
base_row = roi_scenarios[roi_scenarios.scenario == "Base Case"].iloc[0]
usage_share = rag_answers["business_unit"].value_counts(normalize=True)
LEGAL_ADJACENT_UNITS = {"IT & Digital": "Legal", "Finance & Risk": "Compliance",
                         "Compliance": "Compliance", "Retail Banking": "Corp. Affairs",
                         "Operations": "Corp. Affairs", "Corporate Affairs": "Corp. Affairs"}
alloc = {"Legal": 0.0, "Compliance": 0.0, "Corp. Affairs": 0.0}
for unit, share in usage_share.items():
    bucket = LEGAL_ADJACENT_UNITS.get(unit, "Corp. Affairs")
    alloc[bucket] += share
total_share = sum(alloc.values()) or 1.0
bu_rows = [dict(business_unit=k, estimated_annual_impact_rp=round(base_row["time_savings_benefit_rp"] * (v / total_share), -3),
                data_type="calculated") for k, v in alloc.items()]
bu_rows.append(dict(business_unit="Procurement", estimated_annual_impact_rp=round(base_row["procurement_savings_benefit_rp"], -3), data_type="calculated"))
bu_impact = pd.DataFrame(bu_rows)
bu_impact.to_csv(OUT / "business_unit_impact.csv", index=False)

print("All datasets generated in", OUT)
for f in sorted(OUT.glob("*.csv")):
    print(" -", f.name, len(pd.read_csv(f)), "rows")
print()
print(f"Hourly rate (compliance benchmark): Rp{HOURLY_RATE_RP:,.0f}/hour")
print(f"Annual procurement volume (units): {ANNUAL_PROCUREMENT_UNITS:,.0f}")
print(f"Pilot investment total: Rp{PILOT_INVESTMENT_RP:,.0f}")
print(roi_scenarios[["scenario", "time_savings_benefit_rp", "procurement_savings_benefit_rp", "est_annual_benefit_rp", "roi_x", "payback_months"]])

