#!/usr/bin/env python3
"""
Elite Prospects NHL Stats Scraper with Selenium - WINDOWS VERSION
==================================================================

This scraper:
1. Opens a headless Chrome browser
2. Loads the Elite Prospects stats page
3. Waits for JavaScript to load the data
4. Extracts the full stats table
5. Saves to CSV and JSON

Auto-installs ChromeDriver - no manual setup needed!
"""

import time
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from pymongo import MongoClient
from dotenv import load_dotenv
import json
import os

load_dotenv()

# Configuration
STATS_URL = "https://www.eliteprospects.com/team/75/tampa-bay-lightning/2025-2026?tab=stats"
MONGODB_URI = os.getenv('MONGODB_URI')
if not MONGODB_URI:
    raise ValueError("MONGODB_URI not found in environment variables")
DB_NAME = 'lightning_tracker'

# Get script directory for saving files
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

print(f"Script directory: {SCRIPT_DIR}\n")


def get_mongo_client():
    """Get MongoDB client with error handling"""
    try:
        client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=2000)
        client.admin.command('ping')
        return client
    except Exception as e:
        print(f" MongoDB not connected: {e}")
        return None


def setup_driver():
    """Setup Chrome with automatic driver management"""
    print("Setting up Chrome driver...")
    
    options = Options()
    options.add_argument('--headless')  # Run without opening browser window
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    
    try:
        # Auto-install ChromeDriver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        return driver
    except Exception as e:
        print(f" Error setting up Chrome: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure Google Chrome is installed")
        print("2. Check your internet connection (needs to download ChromeDriver)")
        print("3. Try running as administrator")
        raise


def scrape_stats_table(url):
    """
    Scrape stats using Selenium
    This gets the data AFTER JavaScript loads it!
    """
    print(f" Loading page: {url}")
    print("=" * 70)
    
    driver = None
    try:
        # Start browser
        driver = setup_driver()
        print(" Browser started")
        
        # Load page
        driver.get(url)
        print(" Page loaded")
        
        # Wait for the stats table to appear
        print(" Waiting for stats table to load...")
        wait = WebDriverWait(driver, 15)
        
        # Wait for table element
        try:
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
            print(" Table element found")
        except:
            print(" Timeout waiting for table")
        
        # Give extra time for JavaScript to populate the table
        print(" Waiting for JavaScript to execute (5 seconds)...")
        time.sleep(5)
        print(" Wait complete")
        
        # Get the page source (now with data!)
        html_content = driver.page_source
        
        # Save the HTML for debugging
        debug_file = os.path.join(SCRIPT_DIR, 'selenium_page_source.html')
        with open(debug_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f" Saved page source to: {debug_file}")
        
        # Extract tables using pandas
        print("\n Extracting tables...")
        from io import StringIO
        tables = pd.read_html(StringIO(html_content))
        
        print(f" Found {len(tables)} tables")
        
        # Find the player stats table
        stats_table = None
        for i, table in enumerate(tables):
            cols = list(table.columns)
            rows = len(table)
            
            print(f"\nTable {i+1}: {rows} rows, columns: {cols[:10]}")
            
            # Look for player stats columns
            has_player_col = any(col in ['#', 'N', 'SKATER', 'Player'] for col in cols)
            has_stat_cols = any(col in ['GP', 'G', 'A', 'TP'] for col in cols)
            has_data = rows > 5
            
            if has_player_col and has_stat_cols and has_data:
                print(f"    THIS LOOKS LIKE THE PLAYER STATS TABLE!")
                print(f"   Dimensions: {table.shape[0]} rows × {table.shape[1]} columns")
                
                stats_table = table
                
                # Save this table
                table_file = os.path.join(SCRIPT_DIR, f'table_{i+1}.csv')
                table.to_csv(table_file, index=False)
                print(f"    Saved to: {table_file}")
                
                # Don't break - check all tables
        
        if stats_table is not None:
            print("\n" + "=" * 70)
            print(" Successfully extracted stats table!")
            print("=" * 70)
            return stats_table
        else:
            print("\n" + "=" * 70)
            print(" No player stats table found with data")
            print("=" * 70)
            print("\nAll tables summary:")
            for i, table in enumerate(tables):
                print(f"  Table {i+1}: {table.shape[0]} rows × {table.shape[1]} cols")
            return None
        
    except Exception as e:
        print(f"\n Error: {e}")
        import traceback
        traceback.print_exc()
        return None
        
    finally:
        if driver:
            driver.quit()
            print("\n Browser closed")


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
        print("\n No stats to insert")
        return
    
    client = get_mongo_client()
    if not client:
        print("\n MongoDB not available - stats saved to JSON only")
        return
    
    db = client[DB_NAME]
    stats_collection = db['player_stats']
    
    print(f"\n Updating database...")
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
            print(f"   Error: {record['player_name']} - {e}")
    
    print(f"✓ Inserted: {inserted}")
    print(f"✓ Updated: {updated}")
    print(f"✓ Total in database: {stats_collection.count_documents({})}")


def main():
    """Main scraping process"""
    print("=" * 70)
    print("Elite Prospects NHL Stats Scraper (Windows + Selenium)")
    print("=" * 70)
    print()
    
    # Scrape the stats table
    df = scrape_stats_table(STATS_URL)
    
    if df is not None:
        # Save to CSV
        csv_file = os.path.join(SCRIPT_DIR, 'selenium_nhl_stats.csv')
        df.to_csv(csv_file, index=False)
        print(f"\n✓ Saved raw table to: {csv_file}")
        
        # Show preview
        print("\n Preview of scraped data:")
        print("=" * 70)
        print(df.head(10).to_string())
        
        # Format for MongoDB
        records = format_for_mongodb(df)
        
        if records:
            # Save to JSON
            json_file = os.path.join(SCRIPT_DIR, 'selenium_nhl_stats.json')
            with open(json_file, 'w') as f:
                json.dump(records, f, indent=2, default=str)
            print(f"\n✓ Saved {len(records)} player records to: {json_file}")
            
            # Show sample
            print("\n Sample player record:")
            print("=" * 70)
            print(json.dumps(records[0], indent=2, default=str))
            
            print("\n" + "=" * 70)
            print("✓✓✓ SUCCESS! NHL Stats Extracted with Selenium! ✓✓✓")
            print("=" * 70)
            print(f"\nExtracted {len(records)} NHL players with detailed stats")
            print("\nFiles created:")
            print(f"  - {csv_file}")
            print(f"  - {json_file}")
            
            print("\n" + "=" * 70)
            print("Next Steps:")
            print("=" * 70)
            print("1. Review the CSV and JSON files")
            print("2. Start MongoDB (if not running)")
            print("3. Uncomment update_database() in the script")
            print("4. Run again to insert into MongoDB")
            
            # Push to MongoDB Atlas
            update_database(records)
        else:
            print("\n Could not format data for MongoDB")
    else:
        print("\n✗ Failed to scrape stats table")
        print("\nCheck the selenium_page_source.html file to see what was loaded")


if __name__ == '__main__':
    main()
