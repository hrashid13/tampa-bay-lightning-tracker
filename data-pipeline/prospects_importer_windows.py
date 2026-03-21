#!/usr/bin/env python3
"""
Elite Prospects - TBL Prospects Scraper
========================================
Scrapes the 'In The System' prospects page.
Cross-platform: runs on Windows (local) and Linux (GitHub Actions)
"""

import time
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
PROSPECTS_URL = "https://www.eliteprospects.com/team/75/tampa-bay-lightning/2025-2026?tab=prospects"
MONGODB_URI = os.getenv('MONGODB_URI')
if not MONGODB_URI:
    raise ValueError("MONGODB_URI not found in environment variables")
DB_NAME = 'lightning_tracker'

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
print(f"Script directory: {SCRIPT_DIR}\n")


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
    """Scrape the prospects stats table"""
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

        debug_file = os.path.join(SCRIPT_DIR, 'prospects_page_source.html')
        with open(debug_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"OK: Saved page source to: {debug_file}")

        print("\nExtracting tables...")
        from io import StringIO
        tables = pd.read_html(StringIO(html_content))
        print(f"OK: Found {len(tables)} tables")

        # Score each table - pick the actual stats table, not biographical info
        stats_table = None
        best_score = -999

        for i, table in enumerate(tables):
            cols = list(table.columns)
            rows = len(table)

            print(f"\nTable {i+1}: {rows} rows, columns: {cols[:10]}")

            has_stat_cols = any(col in ['GP', 'G', 'A', 'TP', 'PTS'] for col in cols)
            if not has_stat_cols or rows < 6:
                continue

            score = 0
            if 'Player' in cols:  score += 100
            if 'GP' in cols:      score += 100
            if 'G' in cols:       score += 50
            if 'A' in cols:       score += 50
            if rows > 20:         score += 100  # Full prospect list
            elif rows < 15:       score -= 100  # Sidebar widgets

            # Heavy penalty for biographical tables
            if any(col in cols for col in ['Born', 'HT', 'WT', 'Birthplace']):
                score -= 500

            print(f"   Score: {score}, rows: {rows}")

            table_file = os.path.join(SCRIPT_DIR, f'prospects_table_{i+1}.csv')
            table.to_csv(table_file, index=False)
            print(f"   Saved to: {table_file}")

            if score > best_score:
                best_score = score
                stats_table = table
                print(f"   [BEST TABLE SO FAR]")

        if stats_table is not None:
            print("\n" + "=" * 70)
            print("OK: Successfully extracted prospects table!")
            print("=" * 70)
            return stats_table
        else:
            print("\nERROR: No prospects stats table found")
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


def format_records(df):
    """Convert DataFrame to list of records"""
    if df is None or df.empty:
        return []

    records = []
    cols = list(df.columns)

    # Detect player name column
    name_col = None
    for candidate in ['Player', 'Skater', 'SKATER', 'Name', 'player', 'name']:
        if candidate in cols:
            name_col = candidate
            break

    if not name_col:
        print(f"ERROR: No player name column found. Available: {cols}")
        return []

    print(f"OK: Using '{name_col}' as player name column")

    for idx, row in df.iterrows():
        player_name = str(row[name_col]).strip()
        if not player_name or player_name == 'nan' or len(player_name) < 3:
            continue

        stats = {}
        for col in ['GP', 'G', 'A', 'TP', 'PTS', 'PIM', '+/-']:
            if col in row and not pd.isna(row[col]):
                stats[col] = str(row[col])

        if not stats:
            continue

        # Normalize PTS to TP
        if 'PTS' in stats and 'TP' not in stats:
            stats['TP'] = stats.pop('PTS')

        record = {
            'player_name': player_name,
            'season': '2025-2026',
            'team_name': 'Tampa Bay Lightning',
            'league_name': 'prospect',
            'stats': stats,
            'is_prospect': True,
            'is_playoff': False,
            'source': 'prospects_scraper',
            'updated_at': datetime.utcnow().isoformat()
        }

        records.append(record)

    return records


def main():
    """Main scraping process"""
    print("=" * 70)
    print("Elite Prospects - TBL Prospects Scraper")
    print("=" * 70)
    print()

    df = scrape_stats_table(PROSPECTS_URL)

    if df is not None:
        records = format_records(df)

        if records:
            # Save as extracted_all_stats.json (required by combine_tbl_data.py)
            json_file = os.path.join(SCRIPT_DIR, 'extracted_all_stats.json')
            with open(json_file, 'w') as f:
                json.dump(records, f, indent=2, default=str)
            print(f"\nOK: Saved {len(records)} prospect records to: {json_file}")

            print("\n" + "=" * 70)
            print("SUCCESS: Prospects scraped!")
            print("=" * 70)
        else:
            print("\nERROR: Could not format prospect data")
    else:
        print("\nERROR: Failed to scrape prospects table")
        print("Check prospects_page_source.html to see what was loaded")


if __name__ == '__main__':
    main()
