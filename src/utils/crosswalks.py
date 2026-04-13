import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
RAW_DIR = DATA_DIR / "raw"


MSA_TO_STATE: dict[str, str] = {
    "Abilene, TX": "TX",
    "Akron, OH": "OH",
    "Albany, GA": "GA",
    "Albany-Schenectady-Troy, NY": "NY",
    "Albuquerque, NM": "NM",
    "Alexandria, LA": "LA",
    "Allentown-Bethlehem-Easton, PA-NJ": "PA",
    "Altoona, PA": "PA",
    "Amarillo, TX": "TX",
    "Appleton, WI": "WI",
    "Asheville, NC": "NC",
    "Athens-Clarke County, GA": "GA",
    "Atlanta-Sandy Springs-Roswell, GA": "GA",
    "Atlantic City-Hammonton, NJ": "NJ",
    "Auburn-Opelika, AL": "AL",
    "Augusta-Richmond County, GA-SC": "GA",
    "Austin-Round Rock-Georgetown, TX": "TX",
    "Bakersfield, CA": "CA",
    "Baltimore-Columbia-Towson, MD": "MD",
    "Bangor, ME": "ME",
    "Barnstable Town, MA": "MA",
    "Baton Rouge, LA": "LA",
    "Beaumont-Port Arthur, TX": "TX",
    "Belleville, IL": "IL",
    "Bellevue-Kirkland, WA": "WA",
    "Bellingham, WA": "WA",
    "Bend-Redmond, OR": "OR",
    "Billings, MT": "MT",
    "Binghamton, NY": "NY",
    "Birmingham-Hoover, AL": "AL",
    "Blacksburg-Christiansburg, VA": "VA",
    "Bloomington, IL": "IL",
    "Bloomington, IN": "IN",
    "Boise City, ID": "ID",
    "Boston-Cambridge-Newton, MA-NH": "MA",
    "Boulder, CO": "CO",
    "Bremerton-Silverdale-Port Orchard, WA": "WA",
    "Bridgeport-Stamford-Norwalk, CT": "CT",
    "Brownsville-Harlingen, TX": "TX",
    "Buffalo-Cheektowaga, NY": "NY",
    "Burlington-South Burlington, VT": "VT",
    "Canton-Massillon, OH": "OH",
    "Cape Coral-Fort Myers, FL": "FL",
    "Carson City, NV": "NV",
    "Cedar Rapids, IA": "IA",
    "Champaign-Urbana, IL": "IL",
    "Charleston, WV": "WV",
    "Charleston-North Charleston, SC": "SC",
    "Charlotte-Concord-Gastonia, NC-SC": "NC",
    "Chattanooga, TN-GA": "TN",
    "Cheyenne, WY": "WY",
    "Chicago-Naperville-Elgin, IL-IN-WI": "IL",
    "Chico, CA": "CA",
    "Cincinnati, OH-KY-IN": "OH",
    "Clarksville, TN-KY": "TN",
    "Cleveland, OH": "OH",
    "Cleveland-Elyria, OH": "OH",
    "Columbia, SC": "SC",
    "Columbia, MO": "MO",
    "Colorado Springs, CO": "CO",
    "Columbus, OH": "OH",
    "Corpus Christi, TX": "TX",
    "Dallas-Fort Worth-Arlington, TX": "TX",
    "Daphne-Fairhope-Foley, AL": "AL",
    "Davenport-Moline-Rock Island, IA-IL": "IA",
    "Dayton, OH": "OH",
    "Deltona-Daytona Beach-Ormond Beach, FL": "FL",
    "Denver-Aurora-Lakewood, CO": "CO",
    "Des Moines-West Des Moines, IA": "IA",
    "Detroit-Warren-Dearborn, MI": "MI",
    "Dover, DE": "DE",
    "Durham-Chapel Hill, NC": "NC",
    "El Centro, CA": "CA",
    "El Paso, TX": "TX",
    "Erie, PA": "PA",
    "Eugene, OR": "OR",
    "Fayetteville, NC": "NC",
    "Fayetteville-Springdale-Rogers, AR-MO": "AR",
    "Fresno, CA": "CA",
    "Gainesville, FL": "FL",
    "Grand Rapids-Wyoming, MI": "MI",
    "Greeley, CO": "CO",
    "Green Bay, WI": "WI",
    "Greensboro-High Point, NC": "NC",
    "Greenville, SC": "SC",
    "Greenville, NC": "NC",
    "Harrisburg-Carlisle, PA": "PA",
    "Hartford-West Hartford-East Hartford, CT": "CT",
    "Hickory-Lenoir-Morganton, NC": "NC",
    "Honolulu, HI": "HI",
    "Houston-The Woodlands-Sugar Land, TX": "TX",
    "Huntington-Ashland, WV-KY-OH": "WV",
    "Huntsville, AL": "AL",
    "Idaho Falls, ID": "ID",
    "Indianapolis-Carmel-Anderson, IN": "IN",
    "Iowa City, IA": "IA",
    "Jackson, MS": "MS",
    "Jacksonville, FL": "FL",
    "Johnstown, PA": "PA",
    "Kalamazoo-Portage, MI": "MI",
    "Kansas City, MO-KS": "MO",
    "Kennewick-Richland, WA": "WA",
    "Kingsport-Bristol-Bristol, TN-VA": "TN",
    "Knoxville, TN": "TN",
    "Lafayette, LA": "LA",
    "Lafayette-West Lafayette, IN": "IN",
    "Lake Charles, LA": "LA",
    "Lakeland-Winter Haven, FL": "FL",
    "Lancaster, PA": "PA",
    "Lansing-East Lansing, MI": "MI",
    "Laredo, TX": "TX",
    "Las Vegas-Henderson-Paradise, NV": "NV",
    "Lewiston, ID": "ID",
    "Lexington-Fayette, KY": "KY",
    "Lincoln, NE": "NE",
    "Little Rock-North Little Rock-Conway, AR": "AR",
    "Los Angeles-Long Beach-Anaheim, CA": "CA",
    "Louisville-Jefferson County, KY-IN": "KY",
    "Lubbock, TX": "TX",
    "Lynchburg, VA": "VA",
    "Madison, WI": "WI",
    "Manchester-Nashua, NH": "NH",
    "McAllen-Edinburg-Mission, TX": "TX",
    "Medford, OR": "OR",
    "Melbourne-Titusville, FL": "FL",
    "Memphis, TN-MS-AR": "TN",
    "Merced, CA": "CA",
    "Miami-Fort Lauderdale-West Palm Beach, FL": "FL",
    "Milwaukee-Waukesha-West Allis, WI": "WI",
    "Minneapolis-St. Paul-Bloomington, MN-WI": "MN",
    "Modesto, CA": "CA",
    "Monroe, LA": "LA",
    "Monroe, MI": "MI",
    "Montgomery, AL": "AL",
    "Morgantown, WV": "WV",
    "Mount Vernon-Anacortes, WA": "WA",
    "Muskegon, MI": "MI",
    "Myrtle Beach-Conway-North Myrtle Beach, SC-NC": "SC",
    "Naples-Immokalee-Marco Island, FL": "FL",
    "Nashville-Davidson-Murfreesboro-Franklin, TN": "TN",
    "New Haven-Milford, CT": "CT",
    "New Orleans-Metairie, LA": "LA",
    "New York-Newark-Jersey City, NY-NJ-PA": "NY",
    "Niles, MI": "MI",
    "Norfolk, NE": "NE",
    "North Port-Sarasota-Bradenton, FL": "FL",
    "Ogden-Clearfield, UT": "UT",
    "Oklahoma City, OK": "OK",
    "Olympia-Lacey-Tumwater, WA": "WA",
    "Omaha-Council Bluffs, NE-IA": "NE",
    "Orlando-Kissimmee-Sanford, FL": "FL",
    "Oxnard-Thousand Oaks-Ventura, CA": "CA",
    "Palm Bay-Melbourne-Titusville, FL": "FL",
    "Philadelphia-Camden-Wilmington, PA-NJ-DE-MD": "PA",
    "Phoenix-Mesa-Chandler, AZ": "AZ",
    "Pittsburgh, PA": "PA",
    "Pocatello, ID": "ID",
    "Portland-South Portland, ME": "ME",
    "Portland-Vancouver-Hillsboro, OR-WA": "OR",
    "Port St. Lucie, FL": "FL",
    "Providence-Warwick, RI-MA": "RI",
    "Provo-Orem, UT": "UT",
    "Raleigh, NC": "NC",
    "Rapid City, SD": "SD",
    "Reading, PA": "PA",
    "Redding, CA": "CA",
    "Reno, NV": "NV",
    "Richmond, VA": "VA",
    "Riverside-San Bernardino-Ontario, CA": "CA",
    "Rochester, MN": "MN",
    "Rochester, NY": "NY",
    "Rockford, IL": "IL",
    "Sacramento-Roseville-Folsom, CA": "CA",
    "Salem, OR": "OR",
    "Salinas, CA": "CA",
    "Salt Lake City, UT": "UT",
    "San Antonio-New Braunfels, TX": "TX",
    "San Diego-Chula Vista-Carlsbad, CA": "CA",
    "San Francisco-Oakland-Berkeley, CA": "CA",
    "San Jose-Sunnyvale-Santa Clara, CA": "CA",
    "San Luis Obispo-Paso Robles, CA": "CA",
    "Santa Cruz-Watsonville, CA": "CA",
    "Santa Fe, NM": "NM",
    "Savannah, GA": "GA",
    "Scranton-Wilkes-Barre, PA": "PA",
    "Seattle-Tacoma-Bellevue, WA": "WA",
    "Sebastian-Vero Beach, FL": "FL",
    "Shreveport-Bossier City, LA": "LA",
    "Sioux Falls, SD": "SD",
    "South Bend-Mishawaka, IN-MI": "IN",
    "Spokane-Spokane Valley, WA": "WA",
    "Springfield, IL": "IL",
    "Springfield, MA": "MA",
    "Springfield, MO": "MO",
    "St. Louis, MO-IL": "MO",
    "Stockton, CA": "CA",
    "Syracuse, NY": "NY",
    "Tallahassee, FL": "FL",
    "Tampa-St. Petersburg-Clearwater, FL": "FL",
    "Toledo, OH": "OH",
    "Trenton, NJ": "NJ",
    "Tucson, AZ": "AZ",
    "Tulsa, OK": "OK",
    "Tuscaloosa, AL": "AL",
    "Urban Honolulu, HI": "HI",
    "Vallejo, CA": "CA",
    "Virginia Beach-Norfolk-Newport News, VA-NC": "VA",
    "Visalia, CA": "CA",
    "Waco, TX": "TX",
    "Washington-Arlington-Alexandria, DC-VA-MD-WV": "DC",
    "Waterbury, CT": "CT",
    "Watertown-Fort Drum, NY": "NY",
    "Wausau, WI": "WI",
    "West Palm Beach-Boca Raton-Delray Beach, FL": "FL",
    "Wichita, KS": "KS",
    "Wilmington, NC": "NC",
    "Worcester, MA-CT": "MA",
    "York-Hanover, PA": "PA",
    "Youngstown-Warren-Boardman, OH-PA": "OH",
    "Yuba City, CA": "CA",
}

STATE_FIPS = {
    "AL": "01",
    "AK": "02",
    "AZ": "04",
    "AR": "05",
    "CA": "06",
    "CO": "08",
    "CT": "09",
    "DE": "10",
    "DC": "11",
    "FL": "12",
    "GA": "13",
    "HI": "15",
    "ID": "16",
    "IL": "17",
    "IN": "18",
    "IA": "19",
    "KS": "20",
    "KY": "21",
    "LA": "22",
    "ME": "23",
    "MD": "24",
    "MA": "25",
    "MI": "26",
    "MN": "27",
    "MS": "28",
    "MO": "29",
    "MT": "30",
    "NE": "31",
    "NV": "32",
    "NH": "33",
    "NJ": "34",
    "NM": "35",
    "NY": "36",
    "NC": "37",
    "ND": "38",
    "OH": "39",
    "OK": "40",
    "OR": "41",
    "PA": "42",
    "RI": "44",
    "SC": "45",
    "SD": "46",
    "TN": "47",
    "TX": "48",
    "UT": "49",
    "VT": "50",
    "VA": "51",
    "WA": "53",
    "WV": "54",
    "WI": "55",
    "WY": "56",
}

COUNTRY_CODES = {
    "US": "United States",
    "GB": "United Kingdom",
    "DE": "Germany",
    "FR": "France",
    "JP": "Japan",
    "IT": "Italy",
    "CA": "Canada",
    "AU": "Australia",
    "ES": "Spain",
    "NL": "Netherlands",
    "KR": "South Korea",
    "SE": "Sweden",
    "BR": "Brazil",
    "IN": "India",
    "MX": "Mexico",
    "CH": "Switzerland",
    "NO": "Norway",
    "DK": "Denmark",
    "FI": "Finland",
    "AT": "Austria",
    "BE": "Belgium",
    "IE": "Ireland",
    "PT": "Portugal",
    "PL": "Poland",
    "NZ": "New Zealand",
    "IL": "Israel",
    "SG": "Singapore",
    "CZ": "Czech Republic",
    "HU": "Hungary",
    "GR": "Greece",
}


FIPS_TO_STATE = {
    "01": "AL",
    "02": "AK",
    "04": "AZ",
    "05": "AR",
    "06": "CA",
    "08": "CO",
    "09": "CT",
    "10": "DE",
    "11": "DC",
    "12": "FL",
    "13": "GA",
    "15": "HI",
    "16": "ID",
    "17": "IL",
    "18": "IN",
    "19": "IA",
    "20": "KS",
    "21": "KY",
    "22": "LA",
    "23": "ME",
    "24": "MD",
    "25": "MA",
    "26": "MI",
    "27": "MN",
    "28": "MS",
    "29": "MO",
    "30": "MT",
    "31": "NE",
    "32": "NV",
    "33": "NH",
    "34": "NJ",
    "35": "NM",
    "36": "NY",
    "37": "NC",
    "38": "ND",
    "39": "OH",
    "40": "OK",
    "41": "OR",
    "42": "PA",
    "44": "RI",
    "45": "SC",
    "46": "SD",
    "47": "TN",
    "48": "TX",
    "49": "UT",
    "50": "VT",
    "51": "VA",
    "53": "WA",
    "54": "WV",
    "55": "WI",
    "56": "WY",
}


PILOT_MSA_GEOS = [
    "US-NY-New York-Newark-Jersey City",
    "US-CA-Los Angeles-Long Beach-Anaheim",
    "US-IL-Chicago-Naperville-Elgin",
    "US-TX-Dallas-Fort Worth-Arlington",
    "US-PA-Philadelphia-Camden-Wilmington",
    "US-DC-Washington-Arlington-Alexandria",
    "US-FL-Miami-Fort Lauderdale-West Palm Beach",
    "US-GA-Atlanta-Sandy Springs-Roswell",
    "US-MA-Boston-Cambridge-Nashua",
    "US-WA-Seattle-Tacoma-Bellevue",
]

CENSUS_NAME_TO_PYTRENDS = {
    msa_name: code
    for msa_name, code in [
        ("New York-Newark-Jersey City, NY-NJ-PA", "US-NY-New York-Newark-Jersey City"),
        ("Los Angeles-Long Beach-Anaheim, CA", "US-CA-Los Angeles-Long Beach-Anaheim"),
        ("Chicago-Naperville-Elgin, IL-IN-WI", "US-IL-Chicago-Naperville-Elgin"),
        ("Dallas-Fort Worth-Arlington, TX", "US-TX-Dallas-Fort Worth-Arlington"),
        (
            "Philadelphia-Camden-Wilmington, PA-NJ-DE-MD",
            "US-PA-Philadelphia-Camden-Wilmington",
        ),
        (
            "Washington-Arlington-Alexandria, DC-VA-MD-WV",
            "US-DC-Washington-Arlington-Alexandria",
        ),
        (
            "Miami-Fort Lauderdale-West Palm Beach, FL",
            "US-FL-Miami-Fort Lauderdale-West Palm Beach",
        ),
        ("Atlanta-Sandy Springs-Roswell, GA", "US-GA-Atlanta-Sandy Springs-Roswell"),
        ("Boston-Cambridge-Nashua, MA-NH", "US-MA-Boston-Cambridge-Nashua"),
        ("Seattle-Tacoma-Bellevue, WA", "US-WA-Seattle-Tacoma-Bellevue"),
        (
            "Houston-The Woodlands-Sugar Land, TX",
            "US-TX-Houston-The Woodlands-Sugar Land",
        ),
        ("Phoenix-Mesa-Chandler, AZ", "US-AZ-Phoenix-Mesa-Chandler"),
        ("San Francisco-Oakland-Berkeley, CA", "US-CA-San Francisco-Oakland-Berkeley"),
        (
            "Riverside-San Bernardino-Ontario, CA",
            "US-CA-Riverside-San Bernardino-Ontario",
        ),
        (
            "Minneapolis-St. Paul-Bloomington, MN-WI",
            "US-MN-Minneapolis-St. Paul-Bloomington",
        ),
        ("San Diego-Chula Vista-Carlsbad, CA", "US-CA-San Diego-Chula Vista-Carlsbad"),
        (
            "Tampa-St. Petersburg-Clearwater, FL",
            "US-FL-Tampa-St. Petersburg-Clearwater",
        ),
        ("Denver-Aurora-Lakewood, CO", "US-CO-Denver-Aurora-Lakewood"),
        ("Baltimore-Columbia-Towson, MD", "US-MD-Baltimore-Columbia-Towson"),
        ("St. Louis, MO-IL", "US-MO-St. Louis"),
        ("Orlando-Kissimmee-Sanford, FL", "US-FL-Orlando-Kissimmee-Sanford"),
        ("San Antonio-New Braunfels, TX", "US-TX-San Antonio-New Braunfels"),
        ("Portland-Vancouver-Hillsboro, OR-WA", "US-OR-Portland-Vancouver-Hillsboro"),
        ("Pittsburgh, PA", "US-PA-Pittsburgh"),
        ("Sacramento-Roseville-Folsom, CA", "US-CA-Sacramento-Roseville-Folsom"),
        ("Las Vegas-Henderson-Paradise, NV", "US-NV-Las Vegas-Henderson-Paradise"),
        (
            "Nashville-Davidson-Murfreesboro-Franklin, TN",
            "US-TN-Nashville-Davidson-Murfreesboro-Franklin",
        ),
        ("Austin-Round Rock-Georgetown, TX", "US-TX-Austin-Round Rock-Georgetown"),
        ("Cleveland-Elyria, OH", "US-OH-Cleveland-Elyria"),
        ("Kansas City, MO-KS", "US-MO-Kansas City"),
        ("Columbus, OH", "US-OH-Columbus"),
        ("Indianapolis-Carmel-Anderson, IN", "US-IN-Indianapolis-Carmel-Anderson"),
        ("Charlotte-Concord-Gastonia, NC-SC", "US-NC-Charlotte-Concord-Gastonia"),
        ("Cincinnati, OH-KY-IN", "US-OH-Cincinnati"),
        (
            "Virginia Beach-Norfolk-Newport News, VA-NC",
            "US-VA-Virginia Beach-Norfolk-Newport News",
        ),
        ("Detroit-Warren-Dearborn, MI", "US-MI-Detroit-Warren-Dearborn"),
        ("San Jose-Sunnyvale-Santa Clara, CA", "US-CA-San Jose-Sunnyvale-Santa Clara"),
        ("Jacksonville, FL", "US-FL-Jacksonville"),
        (
            "Nashville-Davidson-Murfreesboro-Franklin, TN",
            "US-TN-Nashville-Davidson-Murfreesboro-Franklin",
        ),
        ("Milwaukee-Waukesha-West Allis, WI", "US-WI-Milwaukee-Waukesha-West Allis"),
        ("Providence-Warwick, RI-MA", "US-RI-Providence-Warwick"),
        ("Memphis, TN-MS-AR", "US-TN-Memphis"),
        ("Louisville-Jefferson County, KY-IN", "US-KY-Louisville-Jefferson County"),
        (
            "Hartford-West Hartford-East Hartford, CT",
            "US-CT-Hartford-West Hartford-East Hartford",
        ),
        ("Oklahoma City, OK", "US-OK-Oklahoma City"),
        ("New Orleans-Metairie, LA", "US-LA-New Orleans-Metairie"),
        ("Buffalo-Cheektowaga, NY", "US-NY-Buffalo-Cheektowaga"),
        ("Raleigh, NC", "US-NC-Raleigh"),
        ("Birmingham-Hoover, AL", "US-AL-Birmingham-Hoover"),
        ("Salt Lake City, UT", "US-UT-Salt Lake City"),
        ("Grand Rapids-Wyoming, MI", "US-MI-Grand Rapids-Wyoming"),
    ]
}


def get_pytrends_msa_codes(census_names: list[str] | None = None) -> list[str]:
    """Convert Census MSA names to pytrends geo codes.

    Args:
        census_names: List of Census-style MSA names. If None, returns all known codes.

    Returns:
        List of pytrends-format geo codes (e.g., 'US-NY-New York-Newark-Jersey City').
    """
    if census_names is None:
        return list(CENSUS_NAME_TO_PYTRENDS.values())
    codes = []
    for name in census_names:
        if name in CENSUS_NAME_TO_PYTRENDS:
            codes.append(CENSUS_NAME_TO_PYTRENDS[name])
        else:
            state = MSA_TO_STATE.get(name, "??")
            city_part = name.split(",")[0].split("-")[0].strip()
            codes.append(f"US-{state}-{city_part}")
    return codes


def load_bls_state_unemployment() -> pd.DataFrame:
    data_path = RAW_DIR / "la.data.3.AllStatesS"
    series_path = RAW_DIR / "la.series"
    area_path = RAW_DIR / "la.area"

    data = pd.read_csv(data_path, sep="\t")
    data.columns = data.columns.str.strip()
    data["value"] = pd.to_numeric(data["value"].str.strip(), errors="coerce")
    data["series_id"] = data["series_id"].str.strip()

    series = pd.read_csv(series_path, sep="\t")
    series.columns = series.columns.str.strip()
    series["series_id"] = series["series_id"].str.strip()

    area = pd.read_csv(area_path, sep="\t")
    area.columns = area.columns.str.strip()
    area["area_code"] = area["area_code"].str.strip()

    state_series = series[
        (series["area_type_code"] == "A") & (series["measure_code"] == 3)
    ].copy()

    state_series = state_series.merge(
        area[["area_code", "area_text"]], on="area_code", how="left"
    )
    state_series["fips"] = state_series["area_code"].str[2:4]
    state_series["state_abbr"] = state_series["fips"].map(FIPS_TO_STATE)
    state_series = state_series.dropna(subset=["state_abbr"])

    merged = data.merge(
        state_series[["series_id", "state_abbr"]],
        on="series_id",
        how="inner",
    )

    merged["period_num"] = merged["period"].str.extract(r"M(\d{2})").astype(int)
    merged["date"] = pd.to_datetime(
        merged["year"].astype(str)
        + "-"
        + merged["period_num"].astype(str).str.zfill(2)
        + "-01"
    )

    result = merged[["date", "state_abbr", "value"]].rename(
        columns={"value": "unemployment_rate"}
    )
    result = result.dropna(subset=["unemployment_rate", "state_abbr"])
    return result
