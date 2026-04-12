import logging
from pathlib import Path

import pandas as pd
import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

RAW_DIR = Path(__file__).resolve().parents[2] / "data" / "raw"

QNA_DATAFLOW = "QNA"
QNA_BASE_URL = "https://sdmx.oecd.org/public/rest/data"

OECD_COUNTRIES = [
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


def pull_qna() -> pd.DataFrame:
    logger.info("Pulling OECD QNA quarterly GDP growth (y-o-y, sadj)")
    key = f"{QNA_DATAFLOW}/.S1.Q.V1OBSA.VOBARSA.Q/all"
    url = f"{QNA_BASE_URL}/{key}"
    params = {
        "format": "csv",
        "startPeriod": "2018-Q1",
        "endPeriod": "2026-Q1",
    }
    logger.info(f"Requesting: {url}")
    try:
        resp = requests.get(url, params=params, timeout=120)
        resp.raise_for_status()
        from io import StringIO

        df = pd.read_csv(StringIO(resp.text))
    except Exception as e:
        logger.warning(f"CSV pull failed ({e}), trying JSON...")
        params["format"] = "json"
        resp = requests.get(url, params=params, timeout=120)
        resp.raise_for_status()
        data = resp.json()
        df = pd.DataFrame(data["dataSets"][0]["observations"]).T
        df.columns = ["value"]
        struct = data["structure"]["dimensions"]["observation"]
        df["country"] = struct[0]["values"]
        df["period"] = struct[1]["values"]

    logger.info(f"Pulled {len(df)} rows from OECD QNA")
    return df


if __name__ == "__main__":
    df = pull_qna()
    out_path = RAW_DIR / "oecd_qna_gdp.parquet"
    df.to_parquet(out_path, index=False)
    logger.info(f"Saved {len(df)} rows to {out_path}")
