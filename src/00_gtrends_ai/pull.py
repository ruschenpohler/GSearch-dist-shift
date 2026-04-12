import logging
import time
from pathlib import Path

import pandas as pd

from src.utils.gtrends import (
    RAW_DIR,
    pull_monthly_msa,
    pull_monthly_country,
    pull_weekly_country,
    stitch_weekly,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

AI_TERMS = ["ChatGPT", "Perplexity AI", "Claude AI", "Gemini AI"]

MAJOR_COUNTRIES = ["US", "GB", "DE", "FR", "JP"]

MSA_GEO_CODES_US = [
    "US-AL-Anniston",
    "US-AL-Birmingham-Hoover",
    "US-AL-Daphne-Fairhope-Foley",
    "US-AL-Huntsville",
    "US-AL-Mobile",
    "US-AL-Montgomery",
    "US-AL-Tuscaloosa",
    "US-AZ-Phoenix-Mesa-Chandler",
    "US-AZ-Tucson",
    "US-AR-Fayetteville-Springdale-Rogers",
    "US-AR-Fort Smith",
    "US-AR-Little Rock-North Little Rock-Conway",
    "US-CA-Bakersfield",
    "US-CA-Chico",
    "US-CA-Fresno",
    "US-CA-Los Angeles-Long Beach-Anaheim",
    "US-CA-Modesto",
    "US-CA-Oxnard-Thousand Oaks-Ventura",
    "US-CA-Redding",
    "US-CA-Sacramento-Roseville-Folsom",
    "US-CA-Salinas",
    "US-CA-San Diego-Chula Vista-Carlsbad",
    "US-CA-San Francisco-Oakland-Berkeley",
    "US-CA-San Jose-Sunnyvale-Santa Clara",
    "US-CA-San Luis Obispo-Paso Robles",
    "US-CA-Santa Cruz-Watsonville",
    "US-CA-Stockton",
    "US-CA-Vallejo",
    "US-CA-Visalia",
    "US-CO-Boulder",
    "US-CO-Colorado Springs",
    "US-CO-Denver-Aurora-Lakewood",
    "US-CO-Fort Collins",
    "US-CO-Greeley",
    "US-CO-Pueblo",
    "US-CT-Bridgeport-Stamford-Norwalk",
    "US-CT-Hartford-West Hartford-East Hartford",
    "US-CT-New Haven-Milford",
    "US-CT-Waterbury",
    "US-DC-Washington-Arlington-Alexandria",
    "US-FL-Cape Coral-Fort Myers",
    "US-FL-Deltona-Daytona Beach-Ormond Beach",
    "US-FL-Gainesville",
    "US-FL-Jacksonville",
    "US-FL-Lakeland-Winter Haven",
    "US-FL-Miami-Fort Lauderdale-West Palm Beach",
    "US-FL-Naples-Immokalee-Marco Island",
    "US-FL-North Port-Sarasota-Bradenton",
    "US-FL-Orlando-Kissimmee-Sanford",
    "US-FL-Palm Bay-Melbourne-Titusville",
    "US-FL-Pensacola-Ferry Pass-Brent",
    "US-FL-Port St. Lucie",
    "US-FL-Tallahassee",
    "US-FL-Tampa-St. Petersburg-Clearwater",
    "US-GA-Albany",
    "US-GA-Athens-Clarke County",
    "US-GA-Atlanta-Sandy Springs-Roswell",
    "US-GA-Augusta-Richmond County",
    "US-GA-Columbus",
    "US-GA-Macon-Bibb County",
    "US-GA-Savannah",
    "US-IL-Chicago-Naperville-Elgin",
    "US-IL-Bloomington-Normal",
    "US-IL-Champaign-Urbana",
    "US-IL-Peoria",
    "US-IL-Rockford",
    "US-IL-Springfield",
    "US-IN-Indianapolis-Carmel-Anderson",
    "US-IN-Fort Wayne",
    "US-IN-Lafayette-West Lafayette",
    "US-IN-South Bend-Mishawaka",
    "US-IA-Cedar Rapids",
    "US-IA-Des Moines-West Des Moines",
    "US-KS-Wichita",
    "US-KY-Lexington-Fayette",
    "US-KY-Louisville-Jefferson County",
    "US-LA-Baton Rouge",
    "US-LA-Lafayette",
    "US-LA-New Orleans-Metairie",
    "US-MA-Boston-Cambridge-Nashua",
    "US-MA-Springfield",
    "US-MA-Worcester",
    "US-MD-Baltimore-Columbia-Towson",
    "US-MI-Detroit-Warren-Dearborn",
    "US-MI-Grand Rapids-Kentwood",
    "US-MI-Lansing-East Lansing",
    "US-MN-Minneapolis-St. Paul-Bloomington",
    "US-MN-Rochester",
    "US-MO-Kansas City",
    "US-MO-Springfield",
    "US-MO-St. Louis",
    "US-MS-Jackson",
    "US-MT-Billings",
    "US-NC-Charlotte-Concord-Gastonia",
    "US-NC-Durham-Chapel Hill",
    "US-NC-Greensboro-High Point",
    "US-NC-Raleigh",
    "US-NC-Winston-Salem",
    "US-ND-Fargo",
    "US-NE-Lincoln",
    "US-NE-Omaha-Council Bluffs",
    "US-NH-Manchester-Nashua",
    "US-NJ-Atlantic City-Hammonton",
    "US-NJ-Trenton",
    "US-NM-Albuquerque",
    "US-NM-Santa Fe",
    "US-NY-Buffalo-Cheektowaga",
    "US-NY-New York-Newark-Jersey City",
    "US-NY-Rochester",
    "US-NY-Syracuse",
    "US-NY-Albany-Schenectady-Troy",
    "US-OH-Cincinnati",
    "US-OH-Cleveland-Elyria",
    "US-OH-Columbus",
    "US-OH-Dayton",
    "US-OH-Toledo",
    "US-OK-Oklahoma City",
    "US-OK-Tulsa",
    "US-OR-Portland-Vancouver-Hillsboro",
    "US-OR-Salem",
    "US-OR-Eugene",
    "US-PA-Philadelphia-Camden-Wilmington",
    "US-PA-Pittsburgh",
    "US-PA-Allentown-Bethlehem-Easton",
    "US-PA-Reading",
    "US-PA-Scranton-Wilkes-Barre",
    "US-RI-Providence-Warwick",
    "US-SC-Charleston-North Charleston",
    "US-SC-Columbia",
    "US-SD-Sioux Falls",
    "US-TN-Chattanooga",
    "US-TN-Knoxville",
    "US-TN-Memphis",
    "US-TN-Nashville-Davidson-Murfreesboro-Franklin",
    "US-TX-Austin-Round Rock-Georgetown",
    "US-TX-Dallas-Fort Worth-Arlington",
    "US-TX-Houston-The Woodlands-Sugar Land",
    "US-TX-San Antonio-New Braunfels",
    "US-TX-El Paso",
    "US-TX-Fort Worth-Arlington",
    "US-UT-Salt Lake City",
    "US-UT-Provo-Orem",
    "US-VA-Richmond",
    "US-VA-Virginia Beach-Norfolk-Newport News",
    "US-VA-Washington-Arlington-Alexandria",
    "US-WA-Seattle-Tacoma-Bellevue",
    "US-WA-Spokane-Spokane Valley",
    "US-WI-Madison",
    "US-WI-Milwaukee-Waukesha-West Allis",
]


def pull_ai_monthly_msa():
    logger.info("Pulling AI search terms: MSA-level monthly")
    df = pull_monthly_msa(
        AI_TERMS, MSA_GEO_CODES_US[:50], timeframe="2020-01-01 2026-03-31"
    )
    out_path = RAW_DIR / "gtrends_ai_msa_monthly.parquet"
    df.to_parquet(out_path, index=False)
    logger.info(f"Saved {len(df)} rows to {out_path}")


def pull_ai_monthly_country():
    logger.info("Pulling AI search terms: country-level monthly")
    countries = list(MAJOR_COUNTRIES)
    df = pull_monthly_country(AI_TERMS, countries, timeframe="2020-01-01 2026-03-31")
    out_path = RAW_DIR / "gtrends_ai_country_monthly.parquet"
    df.to_parquet(out_path, index=False)
    logger.info(f"Saved {len(df)} rows to {out_path}")


def pull_ai_weekly_country():
    logger.info("Pulling AI search terms: country-level weekly (stitched)")
    df = pull_weekly_country(AI_TERMS, MAJOR_COUNTRIES)
    df = stitch_weekly(df)
    out_path = RAW_DIR / "gtrends_ai_country_weekly.parquet"
    df.to_parquet(out_path, index=False)
    logger.info(f"Saved {len(df)} rows to {out_path}")


if __name__ == "__main__":
    pull_ai_monthly_msa()
    pull_ai_monthly_country()
    pull_ai_weekly_country()
