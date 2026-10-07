#!/usr/bin/env python3
"""
Elite Prospects NHL Stats Scraper with Selenium
================================================
Cross-platform: runs on Windows (local) and Linux (GitHub Actions)
"""

import re
import time
import glob
import platform
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pymongo import MongoClient
from dotenv import load_dotenv
import json
import os

load_dotenv()

# Configuration
# No season in the URL: Elite Prospects shows the current season automatically.
# (The old URL was pinned to /2025-2026, so it kept returning last season's stats.)
STATS_URL = "https://www.eliteprospects.com/team/75/tampa-bay-lightning?tab=stats"
MONGODB_URI = os.getenv('MONGODB_URI')
if not MONGODB_URI:
    raise ValueError("MONGODB_URI not found in environment variables")
DB_NAME = 'lightning_tracker'
COLLECTION_NAME = 'player_stats'

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
print(f"Script directory: {SCRIPT_DIR}\n")


def detect_season(html):
    """Read the season from the page heading, e.g. '2026-2027 Tampa Bay Lightning Player Stats'.
    Falls back to a date-based guess (NHL league year starts July 1) if the heading is missing."""
    text = re.sub(r'<[^>]+>', ' ', html)
    m = re.search(r'(\d{4}-\d{4})\s+Tampa Bay Lightning\s+Player\s+Stats', text)
    if m:
        return m.group(1)
    print("WARNING: season heading not found on page - guessing from today's date")
    today = datetime.now()
    start = today.year if today.month >= 7 else today.year - 1
    return f"{start}-{start + 1}"


def setup_driver():
    """Setup Chrome - works on both Windows (local) and Linux (GitHub Actions)"""
    print("Setting up Chrome driver...")

    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

    try:
        if platform.system() == 'Linux':
            # GitHub Actions: use system-installed chromium + chromedriver
            import shutil
            chromedriver_path = shutil.which('chromedriver') or '/usr/bin/chromedriver'
            chrome_path = (shutil.which('chromium-browser')
                           or shutil.which('chromium')
                           or '/usr/bin/chromium-browser')
            options.binary_location = chrome_path
            service = ChromeService(executable_path=chromedriver_path)
        else:
            # Windows: use webdriver-manager
            from webdriver_manager.chrome import ChromeDriverManager
            service = Service(ChromeDriverManager().install())

        driver = webdriver.Chrome(service=service, options=options)
        return driver
    except Exception as e:
        print(f"ERROR: Could not start Chrome: {e}")
        raise


def scrape_stats_table(url):
    """Scrape the NHL roster stats table"""
    print(f"Loading page: {url}")
    print("=" * 70)

    driver = None
    try:
        driver = setup_driver()
        print("OK: Browser started")

        driver.get(url)
        print("OK: Page loaded")

        print("Waiting for stats table to load...")
        wait = WebDriverWait(driver, 15)
        try:
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
            print("OK: Table element found")
        except:
            print("WARNING: Timeout waiting for table")

        print("Waiting for JavaScript to execute (5 seconds)...")
        time.sleep(5)
        print("OK: Wait complete")

        html_content = driver.page_source

        debug_file = os.path.join(SCRIPT_DIR, 'selenium_page_source.html')
        with open(debug_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"OK: Saved page source to: {debug_file}")

        # Record which season this page shows so combine_tbl_data.py can label the data
        season = detect_season(html_content)
        with open(os.path.join(SCRIPT_DIR, 'nhl_season.txt'), 'w') as f:
            f.write(season)
        print(f"OK: Detected season: {season}")

        print("\nExtracting tables...")
        from io import StringIO
        tables = pd.read_html(StringIO(html_content))
        print(f"OK: Found {len(tables)} tables")

        # Once the season is underway, Elite Prospects adds a 'Postseason' column
        # group next to 'Regular Season', which gives pandas a two-row header -
        # columns come back as tuples like ('Regular Season', 'GP') instead of
        # plain 'GP'. Flatten to the innermost label so the scoring below (which
        # looks for plain 'Skater'/'GP'/'G'/etc.) still matches. This duplicates
        # each stat name once for Regular Season and once for Postseason, same
        # as the preseason table's GP/GP.1 columns - handled the same way
        # downstream (via CSV round-trip auto-dedup).
        for t_idx, tbl in enumerate(tables):
            if isinstance(tbl.columns, pd.MultiIndex):
                tbl.columns = [c[-1] if isinstance(c, tuple) else c for c in tbl.columns]

        # Score each table - pick the one most likely to be the full current roster
        stats_table = None
        best_score = -999

        for i, table in enumerate(tables):
            cols = list(table.columns)
            rows = len(table)

            print(f"\nTable {i+1}: {rows} rows, columns: {cols[:10]}")

            # A player-stats table needs BOTH a name column and real per-player
            # scoring columns. 'GP' alone isn't enough: the franchise history/
            # standings table on this same page also has a 'GP' column (team
            # games played per season), and on slow-loading days that table
            # can be the only one pandas finds - without this check it gets
            # mistaken for the roster table.
            has_name_col = any(col in ['Skater', 'Player', 'Name', 'N'] for col in cols)
            scoring_cols_present = sum(col in cols for col in ['G', 'A', 'TP', 'PTS'])
            if not has_name_col or scoring_cols_present < 2 or rows < 6:
                continue

            score = 0
            if 'Skater' in cols:  score += 200  # Current roster uses 'Skater'
            if 'N' in cols:       score += 50   # Jersey number column
            if '+/-' in cols:     score += 50   # NHL-specific stat
            if rows > 20:         score += 100  # Full roster: 25-33 players
            elif rows < 15:       score -= 100  # Sidebar widgets are small

            print(f"   Score: {score}, rows: {rows}")

            if score > best_score:
                best_score = score
                stats_table = table
                table_file = os.path.join(SCRIPT_DIR, f'table_{i+1}.csv')
                table.to_csv(table_file, index=False)
                print(f"   [BEST TABLE] Saved to: {table_file}")

        if stats_table is not None:
            # Save best table with consistent filename for combine_tbl_data.py
            best_file = os.path.join(SCRIPT_DIR, 'nhl_best_table.csv')
            stats_table.to_csv(best_file, index=False)
            print(f"\nOK: Saved best table to: {best_file}")
            print("=" * 70)
            print("OK: Successfully extracted stats table!")
            print("=" * 70)
            return stats_table
        else:
            print("\nERROR: No player stats table found")
            return None

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return None

    finally:
        if driver:
            driver.quit()
            print("\nOK: Browser closed")


def main():
    """Main scraping process"""
    print("=" * 70)
    print("Elite Prospects NHL Stats Scraper")
    print("=" * 70)
    print()

    df = scrape_stats_table(STATS_URL)

    if df is None:
        print("\nERROR: Failed to scrape stats table")
        print("Check selenium_page_source.html to see what was loaded")
        raise SystemExit(1)  # fail this step, not the next one, when nothing usable was found

    if df is not None:
        csv_file = os.path.join(SCRIPT_DIR, 'selenium_nhl_stats.csv')
        df.to_csv(csv_file, index=False)
        print(f"\nOK: Saved raw table to: {csv_file}")

        print("\nPreview of scraped data:")
        print("=" * 70)
        print(df.head(10).to_string())

        print("\n" + "=" * 70)
        print("SUCCESS: NHL stats scraped!")
        print("=" * 70)


if __name__ == '__main__':
    main()