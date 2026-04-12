import logging
from pathlib import Path

import pandas as pd
import pickle

from src.utils.gtrends import (
    RAW_DIR,
    pull_monthly_msa,
    pull_monthly_country,
    pull_weekly_country,
    stitch_weekly,
)
from src.utils.category_mapping import SHAPLEY_QUERIES, NON_ECONOMIC_DIAGNOSTICS

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

MAJOR_COUNTRIES = ["US", "GB", "DE", "FR", "JP"]

PILOT_MSAS = [
    "US-NY-New York-Newark-Jersey City",
    "US-CA-Los Angeles-Long Beach-Anaheim",
    "US-IL-Chicago-Naperville-Elgin",
    "US-TX-Dallas-Fort Worth-Arlington",
    "US-PA-Philadelphia-Camden-Wilmington",
    "US-DC-Washington-Arlington-Alexandria",
    "US-FL-Miami-Fort Lauderdale-West Palm Beach",
    "US-GA-Atlanta-Sandy Springs-Roswell",
    "US-MA-Boston-Cambridge-Nashua",
    "US-WA-Seattle-Tacoma-Bellevue",
]


def pull_econ_pilot_country_monthly():
    logger.info(
        "PILOT: Pulling economic categories, country-level monthly (5 countries)"
    )
    all_frames = []
    for cat_name, query_type, cat_id, search_term in SHAPLEY_QUERIES:
        if query_type == "category":
            kw = [search_term]
            df = pull_monthly_country(kw, MAJOR_COUNTRIES, cat=cat_id)
        else:
            kw = [search_term]
            df = pull_monthly_country(kw, MAJOR_COUNTRIES)
        if not df.empty:
            df["category"] = cat_name
            all_frames.append(df)
            logger.info(f"  {cat_name}: {len(df)} rows")
    for diag_name, search_term in NON_ECONOMIC_DIAGNOSTICS:
        df = pull_monthly_country([search_term], MAJOR_COUNTRIES)
        if not df.empty:
            df["category"] = diag_name
            all_frames.append(df)
            logger.info(f"  {diag_name}: {len(df)} rows")
    if not all_frames:
        logger.error("No data pulled in pilot!")
        return pd.DataFrame()
    result = pd.concat(all_frames, ignore_index=True)
    out_path = RAW_DIR / "gtrends_econ_country_monthly_pilot.parquet"
    result.to_parquet(out_path, index=False)
    logger.info(f"Pilot: Saved {len(result)} rows to {out_path}")
    return result


def pull_econ_pilot_country_weekly():
    logger.info(
        "PILOT: Pulling economic categories, country-level weekly (5 countries)"
    )
    all_frames = []
    for cat_name, query_type, cat_id, search_term in SHAPLEY_QUERIES:
        if query_type == "category":
            kw = [search_term]
            df = pull_weekly_country(kw, MAJOR_COUNTRIES, cat=cat_id)
        else:
            kw = [search_term]
            df = pull_weekly_country(kw, MAJOR_COUNTRIES)
        if not df.empty:
            df["category"] = cat_name
            df = stitch_weekly(df)
            all_frames.append(df)
            logger.info(f"  {cat_name}: {len(df)} rows")
    for diag_name, search_term in NON_ECONOMIC_DIAGNOSTICS:
        df = pull_weekly_country([search_term], MAJOR_COUNTRIES)
        if not df.empty:
            df["category"] = diag_name
            df = stitch_weekly(df)
            all_frames.append(df)
            logger.info(f"  {diag_name}: {len(df)} rows")
    if not all_frames:
        logger.error("No data pulled in pilot!")
        return pd.DataFrame()
    result = pd.concat(all_frames, ignore_index=True)
    out_path = RAW_DIR / "gtrends_econ_country_weekly_pilot.parquet"
    result.to_parquet(out_path, index=False)
    logger.info(f"Pilot: Saved {len(result)} rows to {out_path}")
    return result


def pull_econ_pilot_msa_monthly():
    logger.info("PILOT: Pulling economic categories, MSA-level monthly (10 pilot MSAs)")
    all_frames = []
    for cat_name, query_type, cat_id, search_term in SHAPLEY_QUERIES:
        if query_type == "category":
            kw = [search_term]
            df = pull_monthly_msa(kw, PILOT_MSAS, cat=cat_id)
        else:
            kw = [search_term]
            df = pull_monthly_msa(kw, PILOT_MSAS)
        if not df.empty:
            df["category"] = cat_name
            all_frames.append(df)
            logger.info(f"  {cat_name}: {len(df)} rows")
    for diag_name, search_term in NON_ECONOMIC_DIAGNOSTICS:
        df = pull_monthly_msa([search_term], PILOT_MSAS)
        if not df.empty:
            df["category"] = diag_name
            all_frames.append(df)
            logger.info(f"  {diag_name}: {len(df)} rows")
    if not all_frames:
        logger.error("No data pulled in pilot!")
        return pd.DataFrame()
    result = pd.concat(all_frames, ignore_index=True)
    out_path = RAW_DIR / "gtrends_econ_msa_monthly_pilot.parquet"
    result.to_parquet(out_path, index=False)
    logger.info(f"Pilot: Saved {len(result)} rows to {out_path}")
    return result


if __name__ == "__main__":
    pull_econ_pilot_country_monthly()
    pull_econ_pilot_country_weekly()
    pull_econ_pilot_msa_monthly()
