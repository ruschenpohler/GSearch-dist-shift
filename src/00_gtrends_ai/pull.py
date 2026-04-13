"""Pull GTrends AI terms: pilot run for 5 countries, monthly + weekly.

This script runs with heavy rate-limiting (30s between queries).
Expected runtime: ~30-60 minutes per pull function.
Run as: uv run python src/00_gtrends_ai/pull.py
"""

import logging
import time
from pathlib import Path

import pandas as pd
from pytrends.request import TrendReq

from src.utils.crosswalks import COUNTRY_CODES

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

RAW_DIR = Path(__file__).resolve().parents[2] / "data" / "raw"

AI_TERMS = ["ChatGPT", "Perplexity AI", "Claude AI", "Gemini AI"]
MAJOR_COUNTRIES = ["US", "GB", "DE", "FR", "JP"]

DELAY = 30


def pull_ai_country_monthly():
    logger.info("Pulling AI terms: country-level monthly (5 countries, 4 terms)")
    pts = TrendReq(hl="en-US", tz=360, retries=3, backoff_factor=60)
    all_frames = []
    for country in MAJOR_COUNTRIES:
        for i in range(0, len(AI_TERMS), 4):
            batch = AI_TERMS[i : i + 4]
            logger.info(f"  Country {country}: {batch}")
            try:
                pts.build_payload(batch, geo=country, timeframe="2020-01-01 2026-03-31")
                df = pts.interest_over_time()
                if df is not None and not df.empty:
                    if "isPartial" in df.columns:
                        df = df.drop(columns=["isPartial"])
                    df = df.reset_index()
                    df["geo"] = country
                    all_frames.append(df)
                    logger.info(f"    Got {len(df)} rows")
                else:
                    logger.warning(f"    Empty response for {country}")
            except Exception as e:
                logger.warning(f"    Failed: {e}")
            time.sleep(DELAY)
    if not all_frames:
        logger.error("No data pulled!")
        return pd.DataFrame()
    result = pd.concat(all_frames, ignore_index=True)
    result = result.melt(id_vars=["date", "geo"], var_name="keyword", value_name="svi")
    out_path = RAW_DIR / "gtrends_ai_country_monthly.parquet"
    result.to_parquet(out_path, index=False)
    logger.info(f"Saved {len(result)} rows to {out_path}")
    return result


def pull_ai_country_weekly():
    logger.info(
        "Pulling AI terms: country-level weekly (5 countries, 4 terms, stitched)"
    )
    pts = TrendReq(hl="en-US", tz=360, retries=3, backoff_factor=60)
    all_frames = []
    for country in MAJOR_COUNTRIES:
        for window_start in range(2018, 2023):
            window_end = window_start + 4
            tf = f"{window_start}-01-01 {window_end}-12-31"
            for i in range(0, len(AI_TERMS), 4):
                batch = AI_TERMS[i : i + 4]
                logger.info(f"  Country {country} weekly {tf}: {batch}")
                try:
                    pts.build_payload(batch, geo=country, timeframe=tf)
                    df = pts.interest_over_time()
                    if df is not None and not df.empty:
                        if "isPartial" in df.columns:
                            df = df.drop(columns=["isPartial"])
                        df = df.reset_index()
                        df["geo"] = country
                        all_frames.append(df)
                        logger.info(f"    Got {len(df)} rows")
                except Exception as e:
                    logger.warning(f"    Failed: {e}")
                time.sleep(DELAY)
    if not all_frames:
        logger.error("No data pulled!")
        return pd.DataFrame()
    result = pd.concat(all_frames, ignore_index=True)
    result = result.melt(id_vars=["date", "geo"], var_name="keyword", value_name="svi")
    result = result.sort_values(["geo", "keyword", "date"]).drop_duplicates(
        subset=["date", "geo", "keyword"], keep="last"
    )
    out_path = RAW_DIR / "gtrends_ai_country_weekly.parquet"
    result.to_parquet(out_path, index=False)
    logger.info(f"Saved {len(result)} rows to {out_path}")
    return result


if __name__ == "__main__":
    pull_ai_country_monthly()
    pull_ai_country_weekly()
