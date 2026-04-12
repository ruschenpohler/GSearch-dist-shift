import time
import logging
from pathlib import Path

import pandas as pd
from pytrends.request import TrendReq
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
RAW_DIR = DATA_DIR / "raw"
INTERIM_DIR = DATA_DIR / "interim"
PROCESSED_DIR = DATA_DIR / "processed"


@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=60, min=60, max=600),
    retry=retry_if_exception_type((Exception,)),
    reraise=True,
)
def pytrends_request(fn, *args, **kwargs):
    return fn(*args, **kwargs)


def build_pytrends() -> TrendReq:
    return TrendReq(hl="en-US", tz=360, retries=2, backoff_factor=60)


def pull_monthly_msa(
    kw_list: list[str], geo_codes: list[str], timeframe: str = "2020-01-01 2026-03-31"
) -> pd.DataFrame:
    pts = build_pytrends()
    rows = []
    for geo in geo_codes:
        for i in range(0, len(kw_list), 5):
            batch = kw_list[i : i + 5]
            logger.info(f"MSA {geo}: {batch}")
            try:
                pts.build_payload(batch, geo=geo, timeframe=timeframe)
                df = pytrends_request(pts.interest_over_time)
            except Exception as e:
                logger.warning(f"Failed MSA {geo} batch {batch}: {e}")
                continue
            if df is None or df.empty:
                logger.warning(f"Empty response MSA {geo} batch {batch}")
                continue
            if "isPartial" in df.columns:
                df = df.drop(columns=["isPartial"])
            df = df.reset_index()
            df["geo"] = geo
            rows.append(df)
            time.sleep(30)
    if not rows:
        return pd.DataFrame()
    result = pd.concat(rows, ignore_index=True)
    result = result.melt(id_vars=["date", "geo"], var_name="keyword", value_name="svi")
    return result


def pull_monthly_country(
    kw_list: list[str], countries: list[str], timeframe: str = "2020-01-01 2026-03-31"
) -> pd.DataFrame:
    pts = build_pytrends()
    rows = []
    for country in countries:
        for i in range(0, len(kw_list), 5):
            batch = kw_list[i : i + 5]
            logger.info(f"Country {country}: {batch}")
            try:
                pts.build_payload(batch, geo=country, timeframe=timeframe)
                df = pytrends_request(pts.interest_over_time)
            except Exception as e:
                logger.warning(f"Failed country {country} batch {batch}: {e}")
                continue
            if df is None or df.empty:
                logger.warning(f"Empty response country {country} batch {batch}")
                continue
            if "isPartial" in df.columns:
                df = df.drop(columns=["isPartial"])
            df = df.reset_index()
            df["geo"] = country
            rows.append(df)
            time.sleep(30)
    if not rows:
        return pd.DataFrame()
    result = pd.concat(rows, ignore_index=True)
    result = result.melt(id_vars=["date", "geo"], var_name="keyword", value_name="svi")
    return result


def pull_weekly_country(
    kw_list: list[str],
    countries: list[str],
    start_year: int = 2018,
    end_year: int = 2026,
) -> pd.DataFrame:
    pts = build_pytrends()
    rows = []
    for country in countries:
        for window_start in range(start_year, end_year - 4):
            window_end = window_start + 4
            tf = f"{window_start}-01-01 {window_end}-12-31"
            for i in range(0, len(kw_list), 5):
                batch = kw_list[i : i + 5]
                logger.info(f"Country {country} weekly {tf}: {batch}")
                try:
                    pts.build_payload(batch, geo=country, timeframe=tf)
                    df = pytrends_request(pts.interest_over_time)
                except Exception as e:
                    logger.warning(f"Failed {country} weekly {tf} batch {batch}: {e}")
                    continue
                if df is None or df.empty:
                    continue
                if "isPartial" in df.columns:
                    df = df.drop(columns=["isPartial"])
                df = df.reset_index()
                df["geo"] = country
                rows.append(df)
                time.sleep(30)
    if not rows:
        return pd.DataFrame()
    result = pd.concat(rows, ignore_index=True)
    result = result.melt(id_vars=["date", "geo"], var_name="keyword", value_name="svi")
    return result


def stitch_weekly(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values(["geo", "keyword", "date"]).copy()
    df["year"] = pd.to_datetime(df["date"]).dt.year
    overlap_years = df.groupby(["geo", "keyword"])["year"].apply(
        lambda x: sorted(x.unique())
    )
    out_frames = []
    for (geo, kw), grp in df.groupby(["geo", "keyword"]):
        grp = grp.sort_values("date")
        if grp["svi"].max() == 0:
            out_frames.append(grp)
            continue
        grp = grp.drop_duplicates(subset=["date"], keep="last")
        out_frames.append(grp)
    if not out_frames:
        return pd.DataFrame()
    return pd.concat(out_frames, ignore_index=True)
