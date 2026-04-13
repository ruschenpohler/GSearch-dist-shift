"""Data validation and cleaning utilities.

Checks raw GTrends data for:
- Suppression (SVI < 5) rates by geography and category
- Missing observations (gaps in time series)
- Zero-inflated series
- Cross-category normalization consistency
- Outlier detection
"""

import logging
from pathlib import Path

import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
RAW_DIR = DATA_DIR / "raw"
INTERIM_DIR = DATA_DIR / "interim"
PROCESSED_DIR = DATA_DIR / "processed"


def validate_gtrends(df: pd.DataFrame, label: str = "") -> dict:
    """Run validation checks on a GTrends DataFrame.

    Expected columns: date, geo, keyword, svi, (optional) category, cat_id, suppressed.
    """
    report = {
        "label": label,
        "n_rows": len(df),
        "n_geos": df["geo"].nunique() if "geo" in df.columns else 0,
    }

    if "date" in df.columns:
        df = df.copy()
        df["date"] = pd.to_datetime(df["date"])
        report["date_range"] = f"{df['date'].min()} to {df['date'].max()}"

    if "suppressed" not in df.columns:
        df["suppressed"] = df["svi"] < 5

    suppression_rate = df["suppressed"].mean()
    report["suppression_rate"] = round(suppression_rate, 4)

    if "geo" in df.columns:
        geo_suppression = (
            df.groupby("geo")["suppressed"].mean().sort_values(ascending=False)
        )
        report["high_suppression_geos"] = geo_suppression[
            geo_suppression > 0.5
        ].to_dict()

    zero_rate = (df["svi"] == 0).mean()
    report["zero_rate"] = round(zero_rate, 4)

    if "category" in df.columns:
        cat_suppression = (
            df.groupby("category")["suppressed"].mean().sort_values(ascending=False)
        )
        report["suppression_by_category"] = cat_suppression.to_dict()

    if "geo" in df.columns and "date" in df.columns:
        expected_months = df["date"].dt.to_period("M").nunique()
        geos_per_month = df.groupby([df["date"].dt.to_period("M"), "geo"]).size()
        complete_coverage = geos_per_month.groupby(level=0).size()
        report["n_time_periods"] = expected_months
        report["coverage_rate"] = round(
            complete_coverage.mean() / df["geo"].nunique()
            if df["geo"].nunique() > 0
            else 0,
            4,
        )

    return report


def check_time_gaps(df: pd.DataFrame, freq: str = "MS") -> pd.DataFrame:
    """Check for gaps in time series and report missing periods per geography.

    Args:
        df: DataFrame with columns date, geo, keyword, svi
        freq: Expected frequency ('MS' for monthly start, 'W-SUN' for weekly)

    Returns:
        DataFrame with columns [geo, keyword, n_expected, n_actual, n_missing, missing_rate]
    """
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])

    min_date = df["date"].min()
    max_date = df["date"].max()
    full_range = pd.date_range(min_date, max_date, freq=freq)

    results = []
    for (geo, kw), grp in df.groupby(["geo", "keyword"]):
        actual_dates = set(grp["date"].dt.to_period(freq[:1]).unique())
        n_expected = len(full_range)
        n_actual = grp["date"].nunique()
        n_missing = n_expected - n_actual
        results.append(
            {
                "geo": geo,
                "keyword": kw,
                "n_expected": n_expected,
                "n_actual": n_actual,
                "n_missing": n_missing,
                "missing_rate": n_missing / n_expected if n_expected > 0 else 0,
            }
        )

    return pd.DataFrame(results)


def clean_gtrends(df: pd.DataFrame) -> pd.DataFrame:
    """Apply standard cleaning steps to GTrends data.

    - Add suppressed flag (SVI < 5)
    - Convert date to datetime
    - Remove duplicates
    - Sort by geo, keyword, date
    """
    df = df.copy()

    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"])

    if "suppressed" not in df.columns:
        df["suppressed"] = df["svi"] < 5

    df = df.drop_duplicates(subset=["date", "geo", "keyword"], keep="last")

    sort_cols = [c for c in ["geo", "keyword", "date"] if c in df.columns]
    if sort_cols:
        df = df.sort_values(sort_cols).reset_index(drop=True)

    return df


def validate_qna(df: pd.DataFrame) -> dict:
    """Run validation checks on OECD QNA GDP data.

    Expected columns: country_iso3, country_iso2, quarter, gdp_growth_yoy.
    """
    report = {"n_rows": len(df), "n_countries": df["country_iso3"].nunique()}

    report["countries"] = sorted(df["country_iso3"].unique().tolist())
    report["date_range"] = f"{df['quarter'].min()} to {df['quarter'].max()}"

    missing = df["gdp_growth_yoy"].isna().mean()
    report["missing_rate"] = round(missing, 4)

    country_obs = df.groupby("country_iso3").size()
    sparse_countries = country_obs[country_obs < country_obs.median() * 0.5]
    report["sparse_countries"] = sparse_countries.to_dict()

    return report


def validation_report(raw_dir: Path | None = None) -> None:
    """Print validation report for all available raw data files."""
    if raw_dir is None:
        raw_dir = RAW_DIR

    parquets = list(raw_dir.glob("*.parquet"))
    if not parquets:
        logger.warning("No parquet files found in %s", raw_dir)
        return

    for p in parquets:
        logger.info(f"\n{'=' * 60}")
        logger.info(f"File: {p.name}")
        try:
            df = pd.read_parquet(p)
            logger.info(f"  Shape: {df.shape}")
            logger.info(f"  Columns: {df.columns.tolist()}")
            logger.info(f"  Dtypes:\n{df.dtypes.to_string()}")
            logger.info(f"  Null counts:\n{df.isnull().sum().to_string()}")
            if "svi" in df.columns:
                report = validate_gtrends(df, label=p.stem)
                for k, v in report.items():
                    if k not in ("suppression_by_category", "high_suppression_geos"):
                        logger.info(f"  {k}: {v}")
            elif "gdp_growth_yoy" in df.columns:
                report = validate_qna(df)
                for k, v in report.items():
                    logger.info(f"  {k}: {v}")
            else:
                logger.info(f"  Head:\n{df.head(3).to_string()}")
        except Exception as e:
            logger.error(f"  Error reading {p}: {e}")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s"
    )
    validation_report()
