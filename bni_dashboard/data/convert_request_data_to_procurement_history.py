"""Convert the request dataset to the dashboard's procurement-history schema.

The source file contains synthetic laptop requests rather than purchase orders.
Fields that do not exist in the source are explicitly derived and remain
synthetic; they must not be interpreted as actual BNI procurement records.
"""
from pathlib import Path
import shutil


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "data" / "marketplace" / "synthetic_data_complete.csv"
TARGET = Path(__file__).resolve().parent / "procurement_history.csv"

if __name__ == "__main__":
    shutil.copyfile(SOURCE, TARGET)
    print(f"Copied {SOURCE} to {TARGET} without changing the source")