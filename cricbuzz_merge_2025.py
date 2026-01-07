import requests
import pandas as pd
from bs4 import BeautifulSoup
import os

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

OUTPUT_FILE = "cricbuzz_all_2025_t20_stats.csv"


URLS = [
    ("IPL", "2025",
     "https://www.cricbuzz.com/cricket-series/9237/indian-premier-league-2025/stats"),

    ("BBL", "2025-26",
     "https://www.cricbuzz.com/cricket-series/10289/big-bash-league-2025-26/stats"),

    ("SMAT", "2025",
     "https://www.cricbuzz.com/cricket-series/10493/syed-mushtaq-ali-trophy-elite-2025/stats"),

    ("T10", "2025",
     "https://www.cricbuzz.com/cricket-series/11119/abu-dhabi-t10-league-2025/stats"),

    ("T20I", "2025",
     "https://www.cricbuzz.com/cricket-stats/icc-rankings/men/batting"),
]


def scrape(url):
    r = requests.get(url, headers=HEADERS, timeout=20)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "lxml")
    table = soup.find("table")

    if table is None:
        raise RuntimeError("❌ No table found on page")

    df = pd.read_html(str(table))[0]

    df.columns = (
        df.columns.astype(str)
        .str.lower()
        .str.replace(" ", "_")
        .str.replace(".", "", regex=False)
    )

    return df


all_data = []

for league, season, url in URLS:
    print(f"➡️ Scraping {league} {season}")
    df = scrape(url)

    print(f"   Rows scraped: {len(df)}")

    df["league"] = league
    df["season"] = season

    all_data.append(df)


merged = pd.concat(all_data, ignore_index=True)
merged.drop_duplicates(inplace=True)

print("\n✅ TOTAL ROWS:", len(merged))

# SAVE CSV (same folder as script)
merged.to_csv(OUTPUT_FILE, index=False)

print("\n🎯 CSV FILE CREATED SUCCESSFULLY")
print("📁 File location:", os.path.abspath(OUTPUT_FILE))
