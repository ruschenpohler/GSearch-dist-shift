"""
Run all GTrends data pulls sequentially with rate limiting.

This script handles the full pipeline: AI terms + economic categories,
for both country-level (monthly + weekly) and MSA-level (monthly pilot).

Each pull has 30s delays between queries built in.
Total estimated runtime: 4-8 hours depending on rate limiting.

Usage:
    uv run python run_all_pulls.py [--skip-msa] [--skip-weekly]

Data will be saved to data/raw/ as parquet files.
    Log written to pull_log.txt.
"""

import argparse
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(module)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("pull_log.txt", mode="a"),
    ],
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Run all GTrends data pulls")
    parser.add_argument("--skip-msa", action="store_true", help="Skip MSA-level pulls")
    parser.add_argument("--skip-weekly", action="store_true", help="Skip weekly pulls")
    parser.add_argument(
        "--skip-ai", action="store_true", help="Skip AI search term pulls"
    )
    parser.add_argument(
        "--skip-econ", action="store_true", help="Skip economic category pulls"
    )
    args = parser.parse_args()

    if not args.skip_ai:
        logger.info("=" * 60)
        logger.info("PHASE 1: AI search terms")
        logger.info("=" * 60)

        import importlib

        ai_pull = importlib.import_module("src.00_gtrends_ai.pull")

        logger.info("--- AI terms: country-level monthly ---")
        try:
            ai_pull.pull_ai_country_monthly()
        except Exception as e:
            logger.error(f"Monthly AI pull failed: {e}")

        if not args.skip_weekly:
            logger.info("--- AI terms: country-level weekly (stitched) ---")
            try:
                ai_pull.pull_ai_country_weekly()
            except Exception as e:
                logger.error(f"Weekly AI pull failed: {e}")

        if not args.skip_msa:
            logger.info("--- AI terms: MSA-level monthly (pilot: 10 MSAs) ---")
            try:
                ai_pull.pull_ai_msa_monthly_pilot()
            except Exception as e:
                logger.error(f"MSA AI pull failed: {e}")

    if not args.skip_econ:
        logger.info("=" * 60)
        logger.info("PHASE 2: Economic categories")
        logger.info("=" * 60)

        import importlib

        econ_pull = importlib.import_module("src.01_gtrends_econ.pull")

        logger.info("--- Economic categories: country-level monthly (pilot) ---")
        try:
            econ_pull.pull_econ_pilot_country_monthly()
        except Exception as e:
            logger.error(f"Country monthly econ pull failed: {e}")

        if not args.skip_weekly:
            logger.info("--- Economic categories: country-level weekly (pilot) ---")
            try:
                econ_pull.pull_econ_pilot_country_weekly()
            except Exception as e:
                logger.error(f"Country weekly econ pull failed: {e}")

        if not args.skip_msa:
            logger.info(
                "--- Economic categories: MSA-level monthly (pilot: 10 MSAs) ---"
            )
            try:
                econ_pull.pull_econ_pilot_msa_monthly()
            except Exception as e:
                logger.error(f"MSA econ pull failed: {e}")

    logger.info("=" * 60)
    logger.info("DONE. Check data/raw/ for parquet files.")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
