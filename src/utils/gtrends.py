import time
import logging
from pathlib import Path

import numpy as np
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
    kw_list: list[str],
    geo_codes: list[str],
    timeframe: str = "2020-01-01 2026-03-31",
    cat: int = 0,
) -> pd.DataFrame:
    pts = build_pytrends()
    rows = []
    for geo in geo_codes:
        for i in range(0, len(kw_list), 5):
            batch = kw_list[i : i + 5]
            logger.info(f"MSA {geo} cat={cat}: {batch}")
            try:
                pts.build_payload(batch, geo=geo, timeframe=timeframe, cat=cat)
                df = pytrends_request(pts.interest_over_time)
            except Exception as e:
                logger.warning(f"Failed MSA {geo} cat={cat} batch {batch}: {e}")
                continue
            if df is None or df.empty:
                logger.warning(f"Empty response MSA {geo} cat={cat} batch {batch}")
                continue
            if "isPartial" in df.columns:
                df = df.drop(columns=["isPartial"])
            df = df.reset_index()
            df["geo"] = geo
            df["cat_id"] = cat
            rows.append(df)
            time.sleep(30)
    if not rows:
        return pd.DataFrame()
    result = pd.concat(rows, ignore_index=True)
    result = result.melt(
        id_vars=["date", "geo", "cat_id"], var_name="keyword", value_name="svi"
    )
    result["suppressed"] = result["svi"] < 5
    return result


def pull_monthly_country(
    kw_list: list[str],
    countries: list[str],
    timeframe: str = "2020-01-01 2026-03-31",
    cat: int = 0,
) -> pd.DataFrame:
    pts = build_pytrends()
    rows = []
    for country in countries:
        for i in range(0, len(kw_list), 5):
            batch = kw_list[i : i + 5]
            logger.info(f"Country {country} cat={cat}: {batch}")
            try:
                pts.build_payload(batch, geo=country, timeframe=timeframe, cat=cat)
                df = pytrends_request(pts.interest_over_time)
            except Exception as e:
                logger.warning(f"Failed country {country} cat={cat} batch {batch}: {e}")
                continue
            if df is None or df.empty:
                logger.warning(
                    f"Empty response country {country} cat={cat} batch {batch}"
                )
                continue
            if "isPartial" in df.columns:
                df = df.drop(columns=["isPartial"])
            df = df.reset_index()
            df["geo"] = country
            df["cat_id"] = cat
            rows.append(df)
            time.sleep(30)
    if not rows:
        return pd.DataFrame()
    result = pd.concat(rows, ignore_index=True)
    result = result.melt(
        id_vars=["date", "geo", "cat_id"], var_name="keyword", value_name="svi"
    )
    result["suppressed"] = result["svi"] < 5
    return result


def pull_weekly_country(
    kw_list: list[str],
    countries: list[str],
    start_year: int = 2018,
    end_year: int = 2026,
    cat: int = 0,
) -> pd.DataFrame:
    pts = build_pytrends()
    rows = []
    for country in countries:
        for window_start in range(start_year, end_year - 4):
            window_end = window_start + 4
            tf = f"{window_start}-01-01 {window_end}-12-31"
            for i in range(0, len(kw_list), 5):
                batch = kw_list[i : i + 5]
                logger.info(f"Country {country} weekly {tf} cat={cat}: {batch}")
                try:
                    pts.build_payload(batch, geo=country, timeframe=tf, cat=cat)
                    df = pytrends_request(pts.interest_over_time)
                except Exception as e:
                    logger.warning(
                        f"Failed {country} weekly {tf} cat={cat} batch {batch}: {e}"
                    )
                    continue
                if df is None or df.empty:
                    continue
                if "isPartial" in df.columns:
                    df = df.drop(columns=["isPartial"])
                df = df.reset_index()
                df["geo"] = country
                df["cat_id"] = cat
                df["window_start"] = window_start
                rows.append(df)
                time.sleep(30)
    if not rows:
        return pd.DataFrame()
    result = pd.concat(rows, ignore_index=True)
    result = result.melt(
        id_vars=["date", "geo", "cat_id", "window_start"],
        var_name="keyword",
        value_name="svi",
    )
    result["suppressed"] = result["svi"] < 5
    return result


def stitch_weekly(df: pd.DataFrame) -> pd.DataFrame:
    """Stitch overlapping 5-year GTrends windows using proportional rescaling.

    Google Trends normalizes each 5-year window to 0-100 independently.
    When windows overlap, the overlap period provides an anchor for rescaling.
    The most recent window is used as the reference scale; earlier windows
    are rescaled to match it using the ratio of mean SVI in the overlap period.
    """
    if df.empty:
        return df

    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])

    out_frames = []
    for (geo, kw), grp in df.groupby(["geo", "keyword"]):
        grp = grp.sort_values(["date", "window_start"])

        if grp["svi"].max() == 0:
            grp = grp.drop(columns=["window_start"])
            grp = grp.drop_duplicates(subset=["date"], keep="last")
            out_frames.append(grp)
            continue

        windows = sorted(grp["window_start"].unique())
        if len(windows) <= 1:
            grp = grp.drop(columns=["window_start"])
            grp = grp.drop_duplicates(subset=["date"], keep="last")
            out_frames.append(grp)
            continue

        latest_window = windows[-1]
        rescaled_parts = []
        rescaled_parts.append(grp[grp["window_start"] == latest_window].copy())

        for i in range(len(windows) - 2, -1, -1):
            current_ws = windows[i]
            next_ws = windows[i + 1]

            current_df = grp[grp["window_start"] == current_ws].copy()
            next_df = grp[grp["window_start"] == next_ws].copy()

            overlap_start = pd.Timestamp(f"{next_ws}-01-01")
            overlap_end = pd.Timestamp(f"{current_ws + 4}-12-31")

            overlap_current = current_df[
                (current_df["date"] >= overlap_start)
                & (current_df["date"] <= overlap_end)
            ]
            overlap_next = next_df[
                (next_df["date"] >= overlap_start) & (next_df["date"] <= overlap_end)
            ]

            if len(overlap_current) > 0 and overlap_current["svi"].mean() > 0:
                scale_factor = (
                    overlap_next["svi"].mean() / overlap_current["svi"].mean()
                )
            else:
                scale_factor = 1.0

            before_overlap = current_df[current_df["date"] < overlap_start].copy()
            if not before_overlap.empty:
                before_overlap["svi"] = np.clip(
                    before_overlap["svi"].astype(float) * scale_factor, 0, 100
                ).round(1)
                rescaled_parts.append(before_overlap)

        rescaled = pd.concat(rescaled_parts, ignore_index=False)
        rescaled = rescaled.drop(columns=["window_start"])
        rescaled = rescaled.drop_duplicates(subset=["date"], keep="last")
        out_frames.append(rescaled)

    if not out_frames:
        return pd.DataFrame()

    result = pd.concat(out_frames, ignore_index=True)
    result = result.sort_values(["geo", "keyword", "date"]).reset_index(drop=True)
    return result
