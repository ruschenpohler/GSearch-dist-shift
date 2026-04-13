"""Pull EF English Proficiency Index (EPI) country-level scores.

Source: Wikipedia's EF English Proficiency Index page, which contains the
latest country ranking table. Score scale is 0-800.

Reference: https://en.wikipedia.org/wiki/EF_English_Proficiency_Index
"""

import logging
from io import StringIO
from pathlib import Path

import pandas as pd
import requests

logger = logging.getLogger(__name__)

RAW_DIR = Path(__file__).resolve().parents[2] / "data" / "raw"

WIKI_URL = "https://en.wikipedia.org/wiki/EF_English_Proficiency_Index"

COUNTRY_TO_ISO2 = {
    "Argentina": "AR",
    "Austria": "AT",
    "Belgium": "BE",
    "Brazil": "BR",
    "Cambodia": "KH",
    "Chile": "CL",
    "China": "CN",
    "Colombia": "CO",
    "Costa Rica": "CR",
    "Croatia": "HR",
    "Czech Republic": "CZ",
    "Czechia": "CZ",
    "Denmark": "DK",
    "Dominican Republic": "DO",
    "Ecuador": "EC",
    "Egypt": "EG",
    "El Salvador": "SV",
    "Estonia": "EE",
    "Ethiopia": "ET",
    "Finland": "FI",
    "France": "FR",
    "Germany": "DE",
    "Greece": "GR",
    "Guatemala": "GT",
    "Honduras": "HN",
    "Hong Kong": "HK",
    "Hungary": "HU",
    "Iceland": "IS",
    "India": "IN",
    "Indonesia": "ID",
    "Israel": "IL",
    "Italy": "IT",
    "Japan": "JP",
    "Jordan": "JO",
    "Kazakhstan": "KZ",
    "Kenya": "KE",
    "Latvia": "LV",
    "Lebanon": "LB",
    "Lithuania": "LT",
    "Luxembourg": "LU",
    "Malaysia": "MY",
    "Mexico": "MX",
    "Morocco": "MA",
    "Myanmar": "MM",
    "Netherlands": "NL",
    "New Zealand": "NZ",
    "Nicaragua": "NI",
    "Nigeria": "NG",
    "Norway": "NO",
    "Oman": "OM",
    "Pakistan": "PK",
    "Panama": "PA",
    "Paraguay": "PY",
    "Peru": "PE",
    "Philippines": "PH",
    "Poland": "PL",
    "Portugal": "PT",
    "Qatar": "QA",
    "Romania": "RO",
    "Russia": "RU",
    "Saudi Arabia": "SA",
    "Senegal": "SN",
    "Serbia": "RS",
    "Singapore": "SG",
    "Slovakia": "SK",
    "Slovenia": "SI",
    "South Africa": "ZA",
    "South Korea": "KR",
    "Spain": "ES",
    "Sri Lanka": "LK",
    "Sweden": "SE",
    "Switzerland": "CH",
    "Taiwan": "TW",
    "Thailand": "TH",
    "Tunisia": "TN",
    "Turkey": "TR",
    "Uganda": "UG",
    "Ukraine": "UA",
    "United Arab Emirates": "AE",
    "United Kingdom": "GB",
    "United States": "US",
    "Uruguay": "UY",
    "Venezuela": "VE",
    "Vietnam": "VN",
    "Bangladesh": "BD",
    "Bolivia": "BO",
    "Bulgaria": "BG",
    "Cyprus": "CY",
    "Dominica": "DM",
    "Georgia": "GE",
    "Ghana": "GH",
    "Ireland": "IE",
    "Jamaica": "JM",
    "Laos": "LA",
    "Malta": "MT",
    "Moldova": "MD",
    "Mongolia": "MN",
    "Mozambique": "MZ",
    "Nepal": "NP",
    "North Macedonia": "MK",
    "Palestine": "PS",
    "Puerto Rico": "PR",
    "Rwanda": "RW",
    "Sudan": "SD",
    "Tanzania": "TZ",
    "Uzbekistan": "UZ",
    "Zimbabwe": "ZW",
    "Algeria": "DZ",
    "Angola": "AO",
    "Armenia": "AM",
    "Azerbaijan": "AZ",
    "Bahrain": "BH",
    "Barbados": "BB",
    "Belarus": "BY",
    "Benin": "BJ",
    "Bosnia and Herzegovina": "BA",
    "Botswana": "BW",
    "Brunei": "BN",
    "Burkina Faso": "BF",
    "Burundi": "BI",
    "Cameroon": "CM",
    "Cape Verde": "CV",
    "Central African Republic": "CF",
    "Chad": "TD",
    "Congo": "CG",
    "Democratic Republic of the Congo": "CD",
    "Djibouti": "DJ",
    "East Timor": "TL",
    "Eritrea": "ER",
    "Eswatini": "SZ",
    "Fiji": "FJ",
    "Gabon": "GA",
    "Gambia": "GM",
    "Guinea": "GN",
    "Guyana": "GY",
    "Haiti": "HT",
    "Iraq": "IQ",
    "Ivory Coast": "CI",
    "Kuwait": "KW",
    "Kyrgyzstan": "KG",
    "Lesotho": "LS",
    "Liberia": "LR",
    "Libya": "LY",
    "Madagascar": "MG",
    "Malawi": "MW",
    "Maldives": "MV",
    "Mali": "ML",
    "Mauritania": "MR",
    "Mauritius": "MU",
    "Montenegro": "ME",
    "Namibia": "NA",
    "Niger": "NE",
    "Oman": "OM",
    "Papua New Guinea": "PG",
    "South Sudan": "SS",
    "Suriname": "SR",
    "Tajikistan": "TJ",
    "Togo": "TG",
    "Trinidad and Tobago": "TT",
    "Turkmenistan": "TM",
    "Uganda": "UG",
    "Yemen": "YE",
    "Zambia": "ZM",
    "Albania": "AL",
    "Cuba": "CU",
    "Iran": "IR",
    "Bhutan": "BT",
    "Syria": "SY",
    "Afghanistan": "AF",
    "Somalia": "SO",
}


def pull_ef_epi() -> pd.DataFrame:
    """Pull EF EPI scores from Wikipedia country rankings table.

    Returns DataFrame with columns: country, iso2, year, epi_score, proficiency_band.
    """
    logger.info(f"Scraping EF EPI from {WIKI_URL}")
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        resp = requests.get(WIKI_URL, headers=headers, timeout=30)
        resp.raise_for_status()
        tables = pd.read_html(StringIO(resp.text))
    except Exception as e:
        logger.error(f"Failed to scrape Wikipedia: {e}")
        logger.info("Falling back to manual CSV at data/raw/ef_epi.csv")
        csv_path = RAW_DIR / "ef_epi.csv"
        if csv_path.exists():
            return pd.read_csv(csv_path)
        raise

    country_table = None
    for table in tables:
        cols_lower = [str(c).lower() for c in table.columns]
        if "score" in cols_lower and "country" in str(table.columns[0]).lower():
            country_table = table
            break

    if country_table is None:
        logger.error("Could not find EPI country table on Wikipedia")
        csv_path = RAW_DIR / "ef_epi.csv"
        if csv_path.exists():
            return pd.read_csv(csv_path)
        return pd.DataFrame(columns=["country", "iso2", "year", "epi_score"])

    country_col = country_table.columns[0]
    score_col = [c for c in country_table.columns if "score" in str(c).lower()][0]
    band_col = [
        c
        for c in country_table.columns
        if "band" in str(c).lower() or "proficiency" in str(c).lower()
    ]
    band_col = band_col[0] if band_col else None

    year = 2025
    if any("2024" in str(c) for c in country_table.columns):
        year = 2024
    if any("2025" in str(c) for c in country_table.columns):
        year = 2025

    result = country_table[[country_col, score_col]].copy()
    result.columns = ["country", "epi_score"]
    result["epi_score"] = pd.to_numeric(
        result["epi_score"].astype(str).str.replace(",", ".").str.strip(),
        errors="coerce",
    )
    if band_col:
        result["proficiency_band"] = country_table[band_col].astype(str)
    else:
        result["proficiency_band"] = ""
    result["year"] = year
    result["iso2"] = result["country"].map(COUNTRY_TO_ISO2)

    unmapped = result[result["iso2"].isna()]["country"].unique()
    if len(unmapped) > 0:
        logger.warning(f"Unmapped countries: {list(unmapped)}")

    result = result.dropna(subset=["epi_score"]).reset_index(drop=True)
    logger.info(f"Pulled {len(result)} countries from EF EPI {year}")

    return result[["country", "iso2", "year", "epi_score", "proficiency_band"]]


if __name__ == "__main__":
    import logging

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s"
    )

    df = pull_ef_epi()
    out_path = RAW_DIR / "ef_epi.parquet"
    df.to_parquet(out_path, index=False)
    logger.info(f"Saved {len(df)} rows to {out_path}")
    logger.info(f"Year: {df['year'].iloc[0] if len(df) > 0 else 'N/A'}")
    logger.info(f"Countries with ISO2: {df.dropna(subset=['iso2']).iso2.nunique()}")
    logger.info(f"Sample:\n{df.head(10)}")
