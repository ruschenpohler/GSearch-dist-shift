import logging
from pathlib import Path

import pandas as pd

from src.utils.crosswalks import load_bls_state_unemployment, RAW_DIR

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def process_bls():
    logger.info("Processing BLS LAUS state-level unemployment data")
    df = load_bls_state_unemployment()
    out_path = RAW_DIR / "bls_state_unemployment.parquet"
    df.to_parquet(out_path, index=False)
    logger.info(f"Saved {len(df)} rows to {out_path}")
    logger.info(
        f"States: {df['state_abbr'].nunique()}, Date range: {df['date'].min()} to {df['date'].max()}"
    )


if __name__ == "__main__":
    process_bls()
