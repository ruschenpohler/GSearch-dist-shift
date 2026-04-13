"""Pull GTrends AI terms: country-level monthly/weekly and MSA-level monthly.

Uses shared utilities from src.utils.gtrends for consistency with econ pulls.
Rate-limited with 30s delays between queries; tenacity retry on failure.
Run as: uv run python -m src.00_gtrends_ai.pull
  (or: uv run python src/00_gtrends_ai/pull.py)
"""

import logging
import sys

import pandas as pd

from src.utils.gtrends import (
    RAW_DIR,
    pull_monthly_msa,
    pull_monthly_country,
    pull_weekly_country,
    stitch_weekly,
)
from src.utils.crosswalks import PILOT_MSA_GEOS, MSA_TO_STATE

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

AI_TERMS = ["ChatGPT", "Perplexity AI", "Claude AI", "Gemini AI"]
MAJOR_COUNTRIES = ["US", "GB", "DE", "FR", "JP"]


def pull_ai_country_monthly():
    logger.info("Pulling AI terms: country-level monthly (5 countries, 4 terms)")
    result = pull_monthly_country(AI_TERMS, MAJOR_COUNTRIES)
    if result.empty:
        logger.error("No data pulled for AI country monthly!")
        return result
    out_path = RAW_DIR / "gtrends_ai_country_monthly.parquet"
    result.to_parquet(out_path, index=False)
    logger.info(f"Saved {len(result)} rows to {out_path}")
    return result


def pull_ai_country_weekly():
    logger.info(
        "Pulling AI terms: country-level weekly (5 countries, 4 terms, stitched)"
    )
    raw = pull_weekly_country(AI_TERMS, MAJOR_COUNTRIES, start_year=2018, end_year=2026)
    if raw.empty:
        logger.error("No data pulled for AI country weekly!")
        return raw
    result = stitch_weekly(raw)
    out_path = RAW_DIR / "gtrends_ai_country_weekly.parquet"
    result.to_parquet(out_path, index=False)
    logger.info(f"Saved {len(result)} rows to {out_path}")
    return result


def pull_ai_msa_monthly_pilot():
    msa_codes = PILOT_MSA_GEOS
    logger.info(
        f"Pulling AI terms: MSA-level monthly ({len(msa_codes)} pilot MSAs, 4 terms)"
    )
    result = pull_monthly_msa(AI_TERMS, msa_codes)
    if result.empty:
        logger.error("No data pulled for AI MSA monthly!")
        return result
    out_path = RAW_DIR / "gtrends_ai_msa_monthly_pilot.parquet"
    result.to_parquet(out_path, index=False)
    logger.info(f"Saved {len(result)} rows to {out_path}")
    return result


if __name__ == "__main__":
    pull_ai_country_monthly()
    pull_ai_country_weekly()
    pull_ai_msa_monthly_pilot()
