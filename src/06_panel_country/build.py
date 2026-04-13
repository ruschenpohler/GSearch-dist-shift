"""Build country-level panel for Phase 4 (nowcasting).

Merges GTrends (country × week → quarterly mean) + QNA GDP (country × quarter)
+ EF EPI (country, annual).

Join on ISO-3 × year-quarter.
"""

import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"

ISO2_TO_ISO3 = {
    "AU": "AUS",
    "AT": "AUT",
    "BE": "BEL",
    "CA": "CAN",
    "CL": "CHL",
    "CO": "COL",
    "CR": "CRI",
    "CZ": "CZE",
    "DK": "DNK",
    "EE": "EST",
    "FI": "FIN",
    "FR": "FRA",
    "DE": "DEU",
    "GR": "GRC",
    "HU": "HUN",
    "IS": "ISL",
    "IE": "IRL",
    "IL": "ISR",
    "IT": "ITA",
    "JP": "JPN",
    "KR": "KOR",
    "LV": "LVA",
    "LT": "LTU",
    "LU": "LUX",
    "MX": "MEX",
    "NL": "NLD",
    "NZ": "NZL",
    "NO": "NOR",
    "PL": "POL",
    "PT": "PRT",
    "SK": "SVK",
    "SI": "SVN",
    "ES": "ESP",
    "SE": "SWE",
    "CH": "CHE",
    "TR": "TUR",
    "GB": "GBR",
    "US": "USA",
    "AR": "ARG",
    "BR": "BRA",
    "CN": "CHN",
    "ID": "IDN",
    "IN": "IND",
    "RU": "RUS",
    "ZA": "ZAF",
    "SA": "SAU",
    "EG": "EGY",
    "TH": "THA",
    "VN": "VNM",
    "PH": "PHL",
    "MY": "MYS",
    "PE": "PER",
    "CO": "COL",
    "BG": "BGR",
    "HR": "HRV",
    "RO": "ROU",
    "RS": "SRB",
    "UA": "UKR",
    "AE": "ARE",
    "HK": "HKG",
    "SG": "SGP",
    "TW": "TWN",
    "BD": "BGD",
    "PK": "PAK",
    "LK": "LKA",
    "KE": "KEN",
    "NG": "NGA",
    "GH": "GHA",
    "GT": "GTM",
    "HN": "HND",
    "SV": "SLV",
    "NI": "NIC",
    "BO": "BOL",
    "PY": "PRY",
    "EC": "ECU",
    "PA": "PAN",
    "CU": "CUB",
    "DO": "DOM",
    "JM": "JAM",
    "TT": "TTO",
    "UY": "URY",
    "VE": "VEN",
    "KH": "KHM",
    "MM": "MMR",
    "LA": "LAO",
    "NP": "NPL",
    "LK": "LKA",
    "JO": "JOR",
    "LB": "LBN",
    "IQ": "IRQ",
    "KZ": "KAZ",
    "UZ": "UZB",
    "KG": "KGZ",
    "TJ": "TJK",
    "TM": "TKM",
    "MN": "MNG",
    "GE": "GEO",
    "AM": "ARM",
    "AZ": "AZJ",
    "BY": "BLR",
    "MD": "MDA",
    "AL": "ALB",
    "MK": "MKD",
    "ME": "MNE",
    "BA": "BIH",
    "PS": "PSE",
    "DZ": "DZA",
    "MA": "MAR",
    "TN": "TUN",
    "EG": "EGY",
    "SN": "SEN",
    "CM": "CMR",
    "CI": "CIV",
    "GH": "GHA",
    "ET": "ETH",
    "KE": "KEN",
    "TZ": "TZA",
    "UG": "UGA",
    "MZ": "MOZ",
    "MG": "MDG",
    "MW": "MWI",
    "ZM": "ZMB",
    "ZW": "ZWE",
    "SD": "SDN",
    "BJ": "BEN",
    "GA": "GAB",
    "GM": "GMB",
    "GN": "GIN",
    "ML": "MLI",
    "MR": "MRT",
    "NE": "NER",
    "TD": "TCD",
    "TG": "TGO",
    "BF": "BFA",
    "BI": "BDI",
    "RW": "RWA",
    "SO": "SOM",
    "SS": "SSD",
    "AF": "AFG",
    "BT": "BTN",
    "BN": "BRN",
    "FJ": "FJI",
    "PG": "PNG",
    "WS": "WSM",
    "TO": "TON",
    "KH": "KHM",
    "MV": "MDV",
    "QA": "QAT",
    "KW": "KWT",
    "BH": "BHR",
    "OM": "OMN",
    "YE": "YEM",
    "SY": "SYR",
    "LY": "LBY",
    "GL": "GRL",
    "IS": "ISL",
    "MT": "MLT",
    "CY": "CYP",
    "BB": "BRB",
    "DM": "DMA",
    "GD": "GRD",
    "LC": "LCA",
    "VC": "VCT",
    "SR": "SUR",
    "GY": "GUY",
    "PF": "PYF",
    "NC": "NCL",
    "RE": "REU",
}


def build_panel_country(
    gtrends_path: str | None = None,
    qna_path: str | None = None,
    epi_path: str | None = None,
) -> pd.DataFrame:
    """Build country-level panel dataset.

    Monthly GTrends → quarterly averages, then merge with QNA and EF EPI.
    """
    if gtrends_path is None:
        gtrends_path = str(RAW_DIR / "gtrends_econ_country_monthly.parquet")
    if qna_path is None:
        qna_path = str(RAW_DIR / "oecd_qna_gdp.parquet")
    if epi_path is None:
        epi_path = str(RAW_DIR / "ef_epi.parquet")

    logger.info("Loading data sources...")
    gtrends = pd.read_parquet(gtrends_path)
    qna = pd.read_parquet(qna_path)
    epi = pd.read_parquet(epi_path)

    logger.info(f"GTrends: {len(gtrends)} rows, {gtrends['geo'].nunique()} countries")
    logger.info(f"QNA: {len(qna)} rows, {qna['country_iso3'].nunique()} countries")
    logger.info(f"EPI: {len(epi)} rows, {epi['iso2'].nunique()} countries")

    gtrends = _prepare_gtrends(gtrends)
    qna = _prepare_qna(qna)
    epi = _prepare_epi(epi)

    panel = gtrends.merge(qna, on=["country_iso3", "quarter"], how="left")
    panel = panel.merge(epi, on="country_iso3", how="left")
    panel["epi_year"] = panel["epi_year"].ffill()

    panel = panel.sort_values(["country_iso3", "category", "quarter"]).reset_index(
        drop=True
    )

    logger.info(
        f"Final panel: {len(panel)} rows, {panel['country_iso3'].nunique()} countries"
    )
    logger.info(f"Columns: {panel.columns.tolist()}")
    logger.info(f"Quarter range: {panel['quarter'].min()} to {panel['quarter'].max()}")
    logger.info(f"Missing gdp_growth_yoy: {panel['gdp_growth_yoy'].isna().mean():.2%}")
    logger.info(f"Missing epi_score: {panel['epi_score'].isna().mean():.2%}")

    return panel


def _prepare_gtrends(gtrends: pd.DataFrame) -> pd.DataFrame:
    """Convert monthly GTrends to quarterly averages with ISO-3 codes."""
    gtrends = gtrends.copy()
    gtrends["date"] = pd.to_datetime(gtrends["date"])

    gtrends["country_iso2"] = gtrends["geo"]
    gtrends["country_iso3"] = gtrends["country_iso2"].map(ISO2_TO_ISO3)

    unmapped = gtrends[gtrends["country_iso3"].isna()]["geo"].unique()
    if len(unmapped) > 0:
        logger.warning(f"Unmapped country codes: {unmapped}")

    gtrends["quarter"] = gtrends["date"].dt.to_period("Q").astype(str)

    if "category" not in gtrends.columns:
        gtrends["category"] = gtrends["keyword"]

    quarterly = (
        gtrends.groupby(["country_iso3", "category", "quarter"])
        .agg(svi_q=("svi", "mean"), n_months=("svi", "count"))
        .reset_index()
    )
    quarterly = quarterly.rename(columns={"svi_q": "svi"})

    logger.info(
        f"GTrends quarterly: {len(quarterly)} rows, {quarterly['country_iso3'].nunique()} countries"
    )

    return quarterly


def _prepare_qna(qna: pd.DataFrame) -> pd.DataFrame:
    """Prepare QNA GDP data for merge. Harmonize quarter format to YYYYQn."""
    qna = qna.copy()
    qna = qna[qna["quarter"] >= "2018-Q1"]
    qna["quarter"] = qna["quarter"].str.replace("-Q", "Q")
    return qna[["country_iso3", "quarter", "gdp_growth_yoy"]]


def _prepare_epi(epi: pd.DataFrame) -> pd.DataFrame:
    """Prepare EF EPI data for merge. Map ISO2→ISO3 and use as annual moderator."""
    epi = epi.copy()
    epi["country_iso3"] = epi["iso2"].map(ISO2_TO_ISO3)

    unmapped = epi[epi["country_iso3"].isna()]["country"].unique()
    if len(unmapped) > 0:
        logger.warning(f"Unmapped EPI countries: {unmapped}")

    epi_by_country = (
        epi.groupby("country_iso3")
        .agg(
            epi_score=("epi_score", "last"),
            epi_year=("year", "last"),
            proficiency_band=("proficiency_band", "last"),
        )
        .reset_index()
    )

    return epi_by_country


if __name__ == "__main__":
    import logging

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s"
    )

    panel = build_panel_country()
    out_path = PROCESSED_DIR / "panel_country.parquet"
    panel.to_parquet(out_path, index=False)
    logger.info(f"Saved country panel ({len(panel)} rows) to {out_path}")
