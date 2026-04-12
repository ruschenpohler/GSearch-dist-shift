import logging
import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

load_dotenv()

CENSUS_API_KEY = os.getenv("CENSUS_API_KEY")

RAW_DIR = Path(__file__).resolve().parents[2] / "data" / "raw"

ACS5_BASE_URL = "https://api.census.gov/data/{year}/acs/acs5/profile"

MSA_GEOMETRY = "metropolitan statistical area/micropolitan statistical area"

VARIABLES = {
    "DP02_0068PE": "pct_bachelors_or_higher",
    "DP05_0017E": "median_age",
}


def pull_acs_msa(year: int = 2023) -> pd.DataFrame:
    if not CENSUS_API_KEY:
        raise ValueError("CENSUS_API_KEY not found. Set it in .env file.")

    import requests

    var_list = ",".join(VARIABLES.keys())
    url = ACS5_BASE_URL.format(year=year)
    params = {
        "get": f"NAME,{var_list}",
        "for": MSA_GEOMETRY,
        "key": CENSUS_API_KEY,
    }

    logger.info(f"Pulling ACS {year} MSA-level demographics")
    resp = requests.get(url, params=params, timeout=60)
    resp.raise_for_status()
    data = resp.json()

    headers = data[0]
    rows = data[1:]

    df = pd.DataFrame(rows, columns=headers)
    for var in VARIABLES:
        df[var] = pd.to_numeric(df[var], errors="coerce")
    df = df.rename(columns=VARIABLES)
    df = df.rename(columns={"NAME": "msa_name"})
    df["year"] = year
    df = df.dropna(subset=["pct_bachelors_or_higher", "median_age"])

    logger.info(f"Pulled {len(df)} MSAs for ACS {year}")
    return df


def pull_acs_multiyear(years: list[int] | None = None) -> pd.DataFrame:
    if years is None:
        years = [2021, 2022, 2023]
    frames = []
    for year in years:
        try:
            df = pull_acs_msa(year)
            frames.append(df)
        except Exception as e:
            logger.warning(f"Failed to pull ACS {year}: {e}")
    if not frames:
        raise RuntimeError("No ACS data pulled successfully")
    result = pd.concat(frames, ignore_index=True)
    return result


if __name__ == "__main__":
    df = pull_acs_multiyear()
    out_path = RAW_DIR / "acs_msa_demographics.parquet"
    df.to_parquet(out_path, index=False)
    logger.info(f"Saved {len(df)} rows to {out_path}")
