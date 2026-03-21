#!/usr/bin/env python3
"""
Elite Prospects - TBL Prospects Scraper
========================================
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
            import shutil
            chromedriver_path = shutil.which('chromedriver') or '/usr/bin/chromedriver'
            chrome_path = (shutil.which('chromium-browser')
                           or shutil.which('chromium')
                           or '/usr/bin/chromium-browser')
            options.binary_location = chrome_path
            service = ChromeService(executable_path=chromedriver_path)
        else:
            from webdriver_manager.chrome import ChromeDriverManager
            service = Service(ChromeDriverManager().install())

        driver = webdriver.Chrome(service=service, options=options)
        return driver
    except Exception as e:
        print(f"ERROR: Could not start Chrome: {e}")
        raise


def scrape_stats_table(url):
    """
    Scrape stats using Selenium
    This gets the data AFTER JavaScript loads it!
    """
    print(f"🌐 Loading page: {url}")
    print("=" * 70)
    
    driver = None
    try:
        # Start browser
        driver = setup_driver()
        print("✓ Browser started")
        
        # Load page
        driver.get(url)
        print("✓ Page loaded")
        
        # Wait for the stats table to appear
        print("⏳ Waiting for stats table to load...")
        wait = WebDriverWait(driver, 15)
        
        # Wait for table element
        try:
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
            print("✓ Table element found")
        except:
            print("⚠ Timeout waiting for table")
        
        # Give extra time for JavaScript to populate the table
        print("⏳ Waiting for JavaScript to execute (5 seconds)...")
        time.sleep(5)
        print("✓ Wait complete")
        
        # Get the page source (now with data!)
        html_content = driver.page_source
        
        # Save the HTML for debugging
        debug_file = os.path.join(SCRIPT_DIR, 'selenium_page_source.html')
        with open(debug_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"✓ Saved page source to: {debug_file}")
        
        # Extract tables using pandas
        print("\n📊 Extracting tables...")
        from io import StringIO
        tables = pd.read_html(StringIO(html_content))
        
        print(f"✓ Found {len(tables)} tables")
        
        # Find the player stats table (prioritize current roster)
        stats_table = None
        best_table_score = -999
        
        for i, table in enumerate(tables):
            cols = list(table.columns)
            rows = len(table)
            
            print(f"\nTable {i+1}: {rows} rows, columns: {cols[:10]}")
            
            # Must have stat columns - biographical tables don't count
            has_stat_cols = any(col in ['GP', 'G', 'A', 'TP', 'PTS'] for col in cols)
            if not has_stat_cols or rows < 6:
                continue

            # Score the table
            score = 0
            if 'Player' in cols:   score += 100
            if 'GP' in cols:       score += 100
            if 'G' in cols:        score += 50
            if 'A' in cols:        score += 50
            if rows > 20:          score += 100
            elif rows < 15:        score -= 100

            # Penalize biographical tables
            if any(col in cols for col in ['Born', 'HT', 'WT', 'Birthplace']):
                score -= 500

            # Penalize team standings / season history tables
            if any(col in cols for col in ['W', 'L', 'season', 'league']):
                score -= 500

            # Must have a player name column to be useful
            has_name_col = any(col in cols for col in ['Player', 'Skater', 'player', 'Name', 'name'])
            if not has_name_col:
                score -= 500

            print(f"   Player stats table (score: {score})")
            print(f"   Dimensions: {table.shape[0]} rows x {table.shape[1]} columns")

            # Save this table
            table_file = os.path.join(SCRIPT_DIR, f'table_{i+1}.csv')
            table.to_csv(table_file, index=False)
            print(f"   OK: Saved to: {table_file}")

            if score > best_table_score:
                stats_table = table
                best_table_score = score
                print(f"   [BEST TABLE SO FAR]")
        
        if stats_table is not None:
            print("\n" + "=" * 70)
            print("✓ Successfully extracted stats table!")
            print("=" * 70)
            return stats_table
        else:
            print("\n" + "=" * 70)
            print("⚠ No player stats table found with data")
            print("=" * 70)
            print("\nAll tables summary:")
            for i, table in enumerate(tables):
                print(f"  Table {i+1}: {table.shape[0]} rows × {table.shape[1]} cols")
            return None
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return None
        
    finally:
        if driver:
            driver.quit()
            print("\n✓ Browser closed")


def format_for_mongodb(df):
    """Convert DataFrame to MongoDB format"""
    if df is None or df.empty:
        return []
    
    records = []
    
    for idx, row in df.iterrows():
        # Extract player name (in different possible columns)
        player_name = None
        for col in ['SKATER', 'Player', 'N', 'Name']:
            if col in row and not pd.isna(row[col]):
                player_name = str(row[col]).strip()
                if player_name and len(player_name) > 2:
                    break
        
        if not player_name:
            continue
        
        # Build stats dict
        stats = {}
        stat_cols = ['GP', 'G', 'A', 'TP', 'PIM', '+/-', 'PPG', 'SHG', 'GWG', 'SOG', 'SH%']
        
        for col in stat_cols:
            if col in row and not pd.isna(row[col]):
                stats[col] = str(row[col])
        
        if not stats:
            continue
        
        record = {
            'player_name': player_name,
            'season': '2025-2026',
            'team_name': 'Tampa Bay Lightning',
            'league_name': 'NHL',
            'stats': stats,
            'is_playoff': False,
            'source': 'selenium_scraper',
            'updated_at': datetime.utcnow()
        }
        
        records.append(record)
    
    return records


def update_database(stats):
    """Insert/update stats in MongoDB"""
    if not stats:
        print("\n✗ No stats to insert")
        return
    
    client = get_mongo_client()
    if not client:
        print("\n⚠ MongoDB not available - stats saved to JSON only")
        return
    
    db = client[DB_NAME]
    stats_collection = db['player_stats']
    
    print(f"\n💾 Updating database...")
    print("=" * 70)
    
    updated = 0
    inserted = 0
    
    for record in stats:
        try:
            result = stats_collection.replace_one(
                {
                    'player_name': record['player_name'],
                    'team_name': record['team_name'],
                    'season': record['season']
                },
                record,
                upsert=True
            )
            
            if result.modified_count > 0:
                updated += 1
            elif result.upserted_id:
                inserted += 1
        except Exception as e:
            print(f"  ⚠ Error: {record['player_name']} - {e}")
    
    print(f"✓ Inserted: {inserted}")
    print(f"✓ Updated: {updated}")
    print(f"✓ Total in database: {stats_collection.count_documents({})}")


def main():
    """Main scraping process"""
    print("=" * 70)
    print("Elite Prospects - TBL Prospects Scraper")
    print("=" * 70)
    print()

    df = scrape_stats_table(PROSPECTS_URL)

    if df is not None:
        records = format_for_mongodb(df)

        if records:
            # Mark all as prospects
            for r in records:
                r['is_prospect'] = True
                r['league_name'] = r.get('league_name', 'prospect')

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