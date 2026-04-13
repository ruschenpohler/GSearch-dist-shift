"""Phase 0: Proxy Validation

0a. Temporal: AI series near-zero before Nov 2022, sharp rise after.
0b. Cross-sectional: Regress MSA-level mean AI^sub on Census demographics
    (median age, pct college), separately for 2023, 2024, 2025 (stability test).
0c. Internal consistency: Aggregate MSA-level AI to national; compare to country pull.

Outputs written to data/processed/ and figures/.
"""

import logging
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.api import OLS, add_constant

from src.utils.crosswalks import load_bls_state_unemployment

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
FIGURES_DIR = Path(__file__).resolve().parents[1] / "figures"

POST_AI_DATE = "2022-11-01"


def run_phase0() -> dict:
    """Run all Phase 0 validation checks. Returns dict of results."""
    results = {}
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    results["0a"] = _temporal_validation()
    results["0b"] = _crosssectional_validation()
    results["0c"] = _internal_consistency()

    return results


def _temporal_validation() -> dict:
    """0a: Verify AI series near-zero before Nov 2022, sharp rise after."""
    logger.info("Phase 0a: Temporal validation of AI proxy")

    ai_monthly = pd.read_parquet(RAW_DIR / "gtrends_ai_country_monthly.parquet")
    ai_monthly["date"] = pd.to_datetime(ai_monthly["date"])
    ai_monthly["post_ai"] = ai_monthly["date"] >= POST_AI_DATE

    pre_ai = ai_monthly[ai_monthly["date"] < POST_AI_DATE]
    post_ai = ai_monthly[ai_monthly["date"] >= POST_AI_DATE]

    stats = {}
    for keyword in ai_monthly["keyword"].unique():
        kw_pre = pre_ai[pre_ai["keyword"] == keyword]
        kw_post = post_ai[post_ai["keyword"] == keyword]
        stats[keyword] = {
            "pre_ai_mean": round(kw_pre["svi"].mean(), 2),
            "pre_ai_max": int(kw_pre["svi"].max()),
            "post_ai_mean": round(kw_post["svi"].mean(), 2),
            "post_ai_max": int(kw_post["svi"].max()),
        }

    logger.info("AI proxy temporal validation:")
    for kw, s in stats.items():
        logger.info(
            f"  {kw}: pre={s['pre_ai_mean']} (max {s['pre_ai_max']}), "
            f"post={s['post_ai_mean']} (max {s['post_ai_max']})"
        )

    fig, axes = plt.subplots(2, 2, figsize=(14, 8))
    for ax, keyword in zip(axes.flat, ai_monthly["keyword"].unique()):
        kw_data = ai_monthly[ai_monthly["keyword"] == keyword]
        for geo in kw_data["geo"].unique():
            geo_data = kw_data[kw_data["geo"] == geo]
            ax.plot(geo_data["date"], geo_data["svi"], label=geo, alpha=0.7)
        ax.axvline(pd.Timestamp(POST_AI_DATE), color="red", linestyle="--", alpha=0.5)
        ax.set_title(keyword)
        ax.set_xlabel("")
        ax.set_ylabel("SVI")
        ax.legend(fontsize=7)
    fig.suptitle("AI Search Terms Over Time (Monthly)", fontsize=14)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "0a_ai_temporal.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    logger.info(f"Saved figure to {FIGURES_DIR / '0a_ai_temporal.png'}")

    return stats


def _crosssectional_validation() -> dict:
    """0b: Regress MSA-level mean AI^sub on Census demographics by year."""
    logger.info("Phase 0b: Cross-sectional validation (requires MSA-level data)")

    msa_ai_path = RAW_DIR / "gtrends_ai_msa_monthly_pilot.parquet"
    if not msa_ai_path.exists():
        logger.warning(
            "MSA-level AI data not found; skipping cross-sectional validation"
        )
        return {"status": "skipped"}

    ai_msa = pd.read_parquet(msa_ai_path)
    acs = pd.read_parquet(RAW_DIR / "acs_msa_demographics.parquet")

    ai_msa["date"] = pd.to_datetime(ai_msa["date"])
    ai_msa["year"] = ai_msa["date"].dt.year
    ai_msa["post_ai"] = ai_msa["date"] >= POST_AI_DATE

    ai_agg = ai_msa.groupby(["geo", "year"])["svi"].mean().reset_index()
    ai_agg.rename(columns={"svi": "mean_ai_svi"}, inplace=True)

    from src.utils.crosswalks import CENSUS_NAME_TO_PYTRENDS

    pytrends_to_census = {v: k for k, v in CENSUS_NAME_TO_PYTRENDS.items()}
    ai_agg["msa_name"] = ai_agg["geo"].map(pytrends_to_census)

    acs["msa_name"] = acs["msa_name"].str.strip()
    acs_metro = acs[~acs["msa_name"].str.contains("Micro Area", na=False)]

    merged = ai_agg.merge(acs_metro, on=["msa_name", "year"], how="inner")

    results = {}
    for year in sorted(merged["year"].unique()):
        yr_data = merged[merged["year"] == year]
        if len(yr_data) < 5:
            continue
        X = add_constant(yr_data[["median_age", "pct_bachelors_or_higher"]])
        y = yr_data["mean_ai_svi"]
        model = OLS(y, X).fit()
        results[int(year)] = {
            "n": int(len(yr_data)),
            "median_age_coef": round(model.params.get("median_age", 0), 4),
            "median_age_p": round(model.pvalues.get("median_age", 1), 4),
            "pct_college_coef": round(
                model.params.get("pct_bachelors_or_higher", 0), 4
            ),
            "pct_college_p": round(model.pvalues.get("pct_bachelors_or_higher", 1), 4),
            "r_squared": round(model.rsquared, 4),
        }
        logger.info(
            f"  Year {year}: n={len(yr_data)}, R²={model.rsquared:.4f}, "
            f"college_coef={model.params.get('pct_bachelors_or_higher', 0):.4f} "
            f"(p={model.pvalues.get('pct_bachelors_or_higher', 1):.4f})"
        )

    return results


def _internal_consistency() -> dict:
    """0c: Aggregate MSA-level AI to national; compare to country-level pull."""
    logger.info("Phase 0c: Internal consistency (requires MSA-level data)")

    msa_ai_path = RAW_DIR / "gtrends_ai_msa_monthly_pilot.parquet"
    country_ai_path = RAW_DIR / "gtrends_ai_country_monthly.parquet"

    if not msa_ai_path.exists() or not country_ai_path.exists():
        logger.warning(
            "Missing MSA or country AI data; skipping internal consistency check"
        )
        return {"status": "skipped"}

    ai_msa = pd.read_parquet(msa_ai_path)
    ai_country = pd.read_parquet(country_ai_path)

    ai_msa["date"] = pd.to_datetime(ai_msa["date"])
    ai_country["date"] = pd.to_datetime(ai_country["date"])

    msa_agg = ai_msa.groupby(["date", "keyword"])["svi"].mean().reset_index()
    msa_agg["source"] = "msa_aggregated"

    country_us = ai_country[ai_country["geo"] == "US"].copy()
    country_us["source"] = "country_pull"

    compare = pd.concat(
        [msa_agg, country_us[["date", "keyword", "svi", "source"]]], ignore_index=True
    )

    pivot = compare.pivot_table(
        index="date", columns="source", values="svi", aggfunc="mean"
    )
    if "msa_aggregated" in pivot.columns and "country_pull" in pivot.columns:
        corr = pivot["msa_aggregated"].corr(pivot["country_pull"])
        logger.info(
            f"  Correlation between MSA-aggregated and country-level AI SVI: {corr:.4f}"
        )
    else:
        corr = None

    return {"correlation": round(corr, 4) if corr else None}


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s"
    )
    results = run_phase0()
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    import json

    out_path = PROCESSED_DIR / "phase0_results.json"
    serializable = {}
    for phase, data in results.items():
        if isinstance(data, dict):
            serializable[phase] = {str(k): v for k, v in data.items()}
        else:
            serializable[phase] = str(data)
    with open(out_path, "w") as f:
        json.dump(serializable, f, indent=2, default=str)
    logger.info(f"Saved Phase 0 results to {out_path}")
