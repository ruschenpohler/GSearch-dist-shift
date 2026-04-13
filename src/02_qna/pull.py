import logging
from pathlib import Path
from io import StringIO

import pandas as pd
import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

RAW_DIR = Path(__file__).resolve().parents[2] / "data" / "raw"

QNA_BASE_URL = "https://stats.oecd.org/SDMX-JSON/data/QNA"

OECD_MEMBER_ISO3 = [
    "AUS",
    "AUT",
    "BEL",
    "CAN",
    "CHL",
    "COL",
    "CRI",
    "CZE",
    "DNK",
    "EST",
    "FIN",
    "FRA",
    "DEU",
    "GRC",
    "HUN",
    "ISL",
    "IRL",
    "ISR",
    "ITA",
    "JPN",
    "KOR",
    "LVA",
    "LTU",
    "LUX",
    "MEX",
    "NLD",
    "NZL",
    "NOR",
    "POL",
    "PRT",
    "SVK",
    "SVN",
    "ESP",
    "SWE",
    "CHE",
    "TUR",
    "GBR",
    "USA",
]

ISO3_TO_ISO2 = {
    "AUS": "AU",
    "AUT": "AT",
    "BEL": "BE",
    "CAN": "CA",
    "CHL": "CL",
    "COL": "CO",
    "CRI": "CR",
    "CZE": "CZ",
    "DNK": "DK",
    "EST": "EE",
    "FIN": "FI",
    "FRA": "FR",
    "DEU": "DE",
    "GRC": "GR",
    "HUN": "HU",
    "ISL": "IS",
    "IRL": "IE",
    "ISR": "IL",
    "ITA": "IT",
    "JPN": "JP",
    "KOR": "KR",
    "LVA": "LV",
    "LTU": "LT",
    "LUX": "LU",
    "MEX": "MX",
    "NLD": "NL",
    "NZL": "NZ",
    "NOR": "NO",
    "POL": "PL",
    "PRT": "PT",
    "SVK": "SK",
    "SVN": "SI",
    "ESP": "ES",
    "SWE": "SE",
    "CHE": "CH",
    "TUR": "TR",
    "GBR": "GB",
    "USA": "US",
}


def pull_qna() -> pd.DataFrame:
    logger.info(
        "Pulling OECD QNA quarterly GDP growth (y-o-y, sadj) from stats.oecd.org"
    )

    params = {
        "contentType": "csv",
        "startPeriod": "2018-Q1",
        "endPeriod": "2026-Q1",
    }

    logger.info(f"Requesting: {QNA_BASE_URL}/all with params {params}")
    resp = requests.get(f"{QNA_BASE_URL}/all", params=params, timeout=300)
    resp.raise_for_status()

    df = pd.read_csv(StringIO(resp.text), low_memory=False)
    logger.info(f"Downloaded {len(df)} rows from OECD QNA")

    gdp = df[
        (df["FREQ"] == "Q")
        & (df["ADJUSTMENT"] == "Y")
        & (df["REF_AREA"].isin(OECD_MEMBER_ISO3))
        & (df["SECTOR"] == "S1")
        & (df["TRANSACTION"] == "B1GQ")
        & (df["UNIT_MEASURE"] == "PC")
        & (df["PRICE_BASE"] == "L")
        & (df["TRANSFORMATION"] == "G1")
    ].copy()

    gdp = gdp.rename(
        columns={
            "REF_AREA": "country_iso3",
            "TIME_PERIOD": "quarter",
            "OBS_VALUE": "gdp_growth_yoy",
        }
    )

    gdp["country_iso2"] = gdp["country_iso3"].map(ISO3_TO_ISO2)

    gdp = gdp[["country_iso3", "country_iso2", "quarter", "gdp_growth_yoy"]]
    gdp = gdp.sort_values(["country_iso3", "quarter"]).reset_index(drop=True)

    n_countries = gdp["country_iso3"].nunique()
    date_range = f"{gdp['quarter'].min()} to {gdp['quarter'].max()}"
    logger.info(
        f"Filtered to {len(gdp)} rows for {n_countries} OECD countries ({date_range})"
    )

    return gdp


if __name__ == "__main__":
    df = pull_qna()
    out_path = RAW_DIR / "oecd_qna_gdp.parquet"
    df.to_parquet(out_path, index=False)
    logger.info(f"Saved {len(df)} rows to {out_path}")
    logger.info(f"Countries: {sorted(df['country_iso3'].unique())}")
    logger.info(f"Quarters: {df['quarter'].min()} to {df['quarter'].max()}")
    logger.info(f"Sample:\n{df.head(10)}")
