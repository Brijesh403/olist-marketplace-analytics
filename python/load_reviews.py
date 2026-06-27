"""
load_reviews.py
---------------
Loads olist_order_reviews_dataset.csv into the MySQL `order_reviews` table.

Why not LOAD DATA INFILE?
The review_comment_message field contains embedded newlines and imperfectly
escaped quotes. MySQL's line parser fails at row 77,917. pandas handles
multi-line quoted fields natively, so we use it as the loader here.

Usage (PowerShell):
    $env:OLIST_DB_PASSWORD = "your_password"   # required
    $env:OLIST_DB_USER     = "root"            # optional, defaults to root
    python python/load_reviews.py

Usage (bash/zsh):
    export OLIST_DB_PASSWORD="your_password"
    python python/load_reviews.py

Note: env var names are consistent across all three scripts in this project
(load_reviews.py, sentiment_analysis.py, reason_analysis_v2.py).
"""

import os
import pandas as pd
from sqlalchemy import create_engine
from pathlib import Path

# --- DB connection — credentials from environment variables ---
# Naming convention: OLIST_DB_* matches sentiment_analysis.py and reason_analysis_v2.py
DB_USER = os.environ.get("OLIST_DB_USER", "root")
DB_PASS = os.environ.get("OLIST_DB_PASSWORD", "")
DB_HOST = os.environ.get("OLIST_DB_HOST", "127.0.0.1")
DB_PORT = os.environ.get("OLIST_DB_PORT", "3306")
DB_NAME = os.environ.get("OLIST_DB_NAME", "olist")

engine = create_engine(
    f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# --- locate CSV relative to this script ---
BASE_DIR = Path(__file__).resolve().parent.parent
CSV = BASE_DIR / "data" / "olist_order_reviews_dataset.csv"

# --- load ---
df = pd.read_csv(CSV)

# empty strings / NaN -> None so MySQL stores NULL
df = df.where(pd.notnull(df), None)

# append into the existing (empty) table; if_exists="append" does not recreate it
df.to_sql("order_reviews", engine, if_exists="append", index=False, chunksize=5000)

print(f"Loaded {len(df):,} review rows into `order_reviews`")