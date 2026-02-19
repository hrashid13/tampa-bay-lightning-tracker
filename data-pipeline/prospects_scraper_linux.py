#!/usr/bin/env python3
"""
Elite Prospects - In the System Scraper - LINUX VERSION
========================================================

Scrapes the Tampa Bay Lightning prospect page and outputs
extracted_all_stats.json (the file combine_tbl_data.py expects).

Each record matches the format already used by combine_tbl_data.py.
"""

import time
import json
import os
import re
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# ── Config ────────────────────────────────────────────────────────────────────
PROSPECTS_URL = "https://www.eliteprospects.com/team/75/tampa-bay-lightning/in-the-system"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(SCRIPT_DIR, "extracted_all_stats.json")
SEASON = "2025-2026"

print("=" * 70)
print("Tampa Bay Lightning - Prospects Scraper (Linux)")
print("=" * 70)
print(f"URL : {PROSPECTS_URL}")
print(f"Output: {OUTPUT_FILE}")
print()


# ── Driver setup (identical pattern to selenium_nhl_scraper_linux.py) ─────────
def setup_driver():
    print("Setting up Chrome driver...")
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument(
        "user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
    )
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver


# ── Scrape page HTML ──────────────────────────────────────────────────────────
def fetch_page_html(url):
    driver = None
    try:
        driver = setup_driver()
        print("Browser started")
        driver.get(url)
        print("Page loaded")

        # Wait for at least one prospect row to appear
        wait = WebDriverWait(driver, 20)
        try:
            wait.until(
                EC.presence_of_element_located(
                    (By.CLASS_NAME, "InTheSystemTab_playerColumn__537Zy")
                )
            )
            print("Prospect table found")
        except Exception:
            print("Timed out waiting for prospect table — will try anyway")

        # Extra wait for all rows to render
        print("Waiting 5 seconds for full render...")
        time.sleep(5)

        html = driver.page_source

        # Save debug copy
        debug_path = os.path.join(SCRIPT_DIR, "prospects_page_source.html")
        with open(debug_path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"Saved page source to: {debug_path}")

        return html

    except Exception as e:
        print(f"Error fetching page: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        if driver:
            driver.quit()
            print("Browser closed")


# ── Parse HTML into records ───────────────────────────────────────────────────
def parse_prospects(html):
    """
    Parse the In-the-System table using BeautifulSoup.

    Column order in the rendered table (from inspecting System_Players.html):
      0  – rank (#)
      1  – flag (nation image, skip)
      2  – player name + position  ← InTheSystemTab_playerColumn
      3  – team name               ← InTheSystemTab_teamColumn
      4  – league                  ← InTheSystemTab_leagueColumn
      5  – GP
      6  – G
      7  – A
      8  – TP  (bold, sorted column)
      9  – P/GP
      10 – PIM
      11 – +/-
    """
    soup = BeautifulSoup(html, "html.parser")

    # Find every prospect row
    rows = soup.find_all("tr", class_=re.compile(r"SortTable_tr__"))
    print(f"Found {len(rows)} table rows to parse")

    records = []
    skipped = 0

    for row in rows:
        cells = row.find_all("td")
        if len(cells) < 9:
            skipped += 1
            continue

        # ── Player name & position ────────────────────────────────────────
        player_cell = row.find("td", class_=re.compile(r"InTheSystemTab_playerColumn"))
        if not player_cell:
            skipped += 1
            continue

        player_link = player_cell.find("a")
        if not player_link:
            skipped += 1
            continue

        # Full text looks like: "Conor Geekie\n(RW/C)"
        raw_text = player_link.get_text(separator=" ", strip=True)
        # Extract position in parentheses if present
        pos_match = re.search(r"\(([^)]+)\)", raw_text)
        position = pos_match.group(1) if pos_match else ""
        # Remove position from name
        player_name = re.sub(r"\s*\([^)]*\)", "", raw_text).strip()

        if not player_name or len(player_name) < 2:
            skipped += 1
            continue

        # ── Team ──────────────────────────────────────────────────────────
        team_cell = row.find("td", class_=re.compile(r"InTheSystemTab_teamColumn"))
        team_name = ""
        if team_cell:
            team_link = team_cell.find("a")
            if team_link:
                team_name = team_link.get_text(strip=True)

        # ── League ────────────────────────────────────────────────────────
        league_cell = row.find("td", class_=re.compile(r"InTheSystemTab_leagueColumn"))
        league_name = ""
        if league_cell:
            league_link = league_cell.find("a")
            if league_link:
                league_name = league_link.get_text(strip=True)

        # Skip if no team or league — likely a header/filler row
        if not team_name and not league_name:
            skipped += 1
            continue

        # ── Stats (numeric cells after league column) ─────────────────────
        # Grab all right-aligned stat cells in this row
        stat_cells = row.find_all(
            "td", class_=re.compile(r"SortTable_right__")
        )

        stat_labels = ["GP", "G", "A", "TP", "P/GP", "PIM", "+/-"]
        stats = {}

        for i, label in enumerate(stat_labels):
            if i < len(stat_cells):
                val = stat_cells[i].get_text(strip=True)
                if val and val != "":
                    stats[label] = val

        # Must have at least GP to be a real row
        if "GP" not in stats:
            skipped += 1
            continue

        record = {
            "player_name": player_name,
            "position": position,
            "season": SEASON,
            "team_name": team_name,
            "league_name": league_name,
            "stats": stats,
            "is_playoff": False,
            "is_prospect": True,
            "source": "prospects_scraper_linux",
            "updated_at": datetime.utcnow().isoformat(),
        }

        records.append(record)

    print(f"Parsed {len(records)} prospect records ({skipped} rows skipped)")
    return records


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    # 1. Fetch
    html = fetch_page_html(PROSPECTS_URL)
    if not html:
        print("Failed to fetch page. Exiting.")
        exit(1)

    # 2. Parse
    print("\nParsing prospect data...")
    records = parse_prospects(html)

    if not records:
        print("No records parsed — check prospects_page_source.html for clues.")
        exit(1)

    # 3. Show breakdown by league
    league_counts = {}
    for r in records:
        lg = r["league_name"] or "Unknown"
        league_counts[lg] = league_counts.get(lg, 0) + 1

    print("\nBreakdown by league:")
    for league, count in sorted(league_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {league}: {count}")

    # 4. Sample record
    print("\nSample record:")
    print(json.dumps(records[0], indent=2))

    # 5. Save
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)

    print(f"\nSaved {len(records)} records to: {OUTPUT_FILE}")
    print("\n" + "=" * 70)
    print("SUCCESS! Prospects data ready for combine_tbl_data.py")
    print("=" * 70)


if __name__ == "__main__":
    main()
