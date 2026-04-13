"""Build MSA-level panel for Phases 0-3.

Merges GTrends (MSA × month) + BLS unemployment (state × month via MSA→state)
+ ACS demographics (MSA, static).

Join on MSA ID × year-month.
"""

import logging
from pathlib import Path

import pandas as pd

from src.utils.crosswalks import MSA_TO_STATE, load_bls_state_unemployment

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
RAW_DIR = DATA_DIR / "raw"
INTERIM_DIR = DATA_DIR / "interim"
PROCESSED_DIR = DATA_DIR / "processed"


def build_panel_msa(
    gtrends_path: str | None = None,
    acs_path: str | None = None,
    bls_path: str | None = None,
) -> pd.DataFrame:
    """Build MSA-level panel dataset.

    Expected GTrends columns: date, geo, keyword, svi, category, cat_id, suppressed
    Expected ACS columns: msa_name, pct_bachelors_or_higher, median_age, year
    Expected BLS columns: date, state_abbr, unemployment_rate
    """
    if gtrends_path is None:
        gtrends_path = str(RAW_DIR / "gtrends_econ_msa_monthly.parquet")
    if acs_path is None:
        acs_path = str(RAW_DIR / "acs_msa_demographics.parquet")
    if bls_path is None:
        bls_path = str(RAW_DIR / "bls_state_unemployment.parquet")

    logger.info("Loading data sources...")
    gtrends = pd.read_parquet(gtrends_path)
    acs = pd.read_parquet(acs_path)
    bls = load_bls_state_unemployment()

    logger.info(f"GTrends: {len(gtrends)} rows, {gtrends['geo'].nunique()} MSAs")
    logger.info(f"ACS: {len(acs)} rows")
    logger.info(f"BLS: {len(bls)} rows, {bls['state_abbr'].nunique()} states")

    gtrends["date"] = pd.to_datetime(gtrends["date"])

    if "category" not in gtrends.columns:
        gtrends["category"] = gtrends["keyword"]

    acs = _clean_acs(acs)
    gtrends = _add_msa_name(gtrends)

    gtrends = gtrends.merge(
        acs[["msa_name", "pct_bachelors_or_higher", "median_age", "year"]],
        left_on=["msa_name", gtrends["date"].dt.year],
        right_on=["msa_name", "year"],
        how="left",
    )
    gtrends = gtrends.drop(columns=["key_1"], errors="ignore")
    gtrends = _add_state_unemployment(gtrends, bls)

    gtrends["yearmonth"] = gtrends["date"].dt.to_period("M")
    gtrends = gtrends.sort_values(["geo", "category", "date"]).reset_index(drop=True)

    logger.info(f"Final panel: {len(gtrends)} rows, {gtrends['geo'].nunique()} MSAs")
    logger.info(f"Columns: {gtrends.columns.tolist()}")
    logger.info(f"Date range: {gtrends['date'].min()} to {gtrends['date'].max()}")
    logger.info(
        f"Missing unemployment_rate: {gtrends['unemployment_rate'].isna().mean():.2%}"
    )
    logger.info(
        f"Missing pct_bachelors_or_higher: {gtrends['pct_bachelors_or_higher'].isna().mean():.2%}"
    )
    logger.info(f"Missing median_age: {gtrends['median_age'].isna().mean():.2%}")

    return gtrends


def _clean_acs(acs: pd.DataFrame) -> pd.DataFrame:
    """Clean ACS demographics and parse MSA names."""
    acs = acs.copy()
    acs["msa_name"] = acs["msa_name"].str.strip()
    acs = acs.dropna(subset=["pct_bachelors_or_higher", "median_age"])
    acs = acs[~acs["msa_name"].str.contains("Micro Area", na=False)]
    logger.info(
        f"ACS after filtering to Metro Areas: {len(acs)} rows, {acs['msa_name'].nunique()} MSAs"
    )
    return acs


def _add_msa_name(gtrends: pd.DataFrame) -> pd.DataFrame:
    """Map pytrends geo codes to Census MSA names for ACS merge."""
    gtrends = gtrends.copy()

    # Extract MSA name from pytrends geo code
    # e.g., "US-NY-New York-Newark-Jersey City" -> "New York-Newark-Jersey City, NY-NJ-PA"
    gtrends["msa_name_raw"] = gtrends["geo"].str.extract(r"US-\w+-(.+)")

    # Try to match against Census MSA names using crosswalk
    from src.utils.crosswalks import CENSUS_NAME_TO_PYTRENDS

    pytrends_to_census = {v: k for k, v in CENSUS_NAME_TO_PYTRENDS.items()}
    gtrends["msa_name"] = gtrends["geo"].map(pytrends_to_census)

    # For unmatched MSAs, try fuzzy matching on city name
    unmatched = gtrends[gtrends["msa_name"].isna()]["geo"].unique()
    if len(unmatched) > 0:
        logger.warning(
            f"{len(unmatched)} geo codes not in crosswalk: {unmatched[:5]}..."
        )

    return gtrends


def _add_state_unemployment(gtrends: pd.DataFrame, bls: pd.DataFrame) -> pd.DataFrame:
    """Merge BLS state unemployment using MSA→state mapping."""
    gtrends = gtrends.copy()

    gtrends["state"] = gtrends["msa_name"].map(MSA_TO_STATE)

    # Also try to get state from pytrends geo code
    # e.g., "US-NY-New York-Newark-Jersey City" -> "NY"
    gtrends["state_from_geo"] = gtrends["geo"].str.extract(r"US-(\w+)-")[0]

    # Prefer crosswalk, fall back to geo code
    gtrends["state"] = gtrends["state"].fillna(gtrends["state_from_geo"])

    bls["yearmonth"] = bls["date"].dt.to_period("M")
    gtrends["yearmonth"] = gtrends["date"].dt.to_period("M")

    gtrends = gtrends.merge(
        bls[["state_abbr", "unemployment_rate", "yearmonth"]],
        left_on=["state", "yearmonth"],
        right_on=["state_abbr", "yearmonth"],
        how="left",
    )

    gtrends = gtrends.drop(columns=["state_abbr_y", "state_from_geo"], errors="ignore")
    if "state_abbr_x" in gtrends.columns and "state" in gtrends.columns:
        gtrends = gtrends.drop(columns=["state_abbr_x"])

    return gtrends


if __name__ == "__main__":
    import logging

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s"
    )

    panel = build_panel_msa()
    out_path = PROCESSED_DIR / "panel_msa.parquet"
    panel.to_parquet(out_path, index=False)
    logger.info(f"Saved MSA panel ({len(panel)} rows) to {out_path}")
