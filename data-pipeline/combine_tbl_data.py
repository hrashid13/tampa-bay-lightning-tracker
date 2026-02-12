#!/usr/bin/env python3

import pandas as pd
import json
import os
import os
from dotenv import load_dotenv
from datetime import datetime
from pymongo import MongoClient


load_dotenv()

MONGODB_URI = os.getenv('MONGODB_URI')
if not MONGODB_URI:
    raise ValueError("MONGODB_URI not found in environment variables")


# Configuration
DB_NAME = 'lightning_tracker'
COLLECTION_NAME = 'player_stats'
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

print("=" * 70)
print("Tampa Bay Lightning - Data Combination (TRULY FIXED)")
print("=" * 70)
print()


print("Step 1: Loading prospects data...")

prospects_file = os.path.join(SCRIPT_DIR, 'extracted_all_stats.json')

if not os.path.exists(prospects_file):
    print(f"✗ File not found: {prospects_file}")
    exit(1)

with open(prospects_file, 'r') as f:
    prospects_data = json.load(f)

print(f"✓ Loaded {len(prospects_data)} records from prospects file")


print("\nStep 2: Loading NHL stats from Selenium CSV...")

nhl_file = os.path.join(SCRIPT_DIR, 'table_1.csv')

if not os.path.exists(nhl_file):
    print(f"✗ File not found: {nhl_file}")
    exit(1)

# Read CSV
nhl_df = pd.read_csv(nhl_file)

# Remove the "NHL, NHL, NHL..." header row
nhl_df = nhl_df[nhl_df['Skater'] != 'NHL']

# Only use the FIRST set of stat columns (ignore .1 duplicates)
columns_to_keep = ['#', 'N', 'Skater', 'GP', 'G', 'A', 'TP', 'PIM', '+/-']
nhl_df = nhl_df[columns_to_keep]

print(f"✓ Loaded {len(nhl_df)} NHL players from CSV")


print("\nStep 3: Converting NHL data...")

nhl_records = []

for idx, row in nhl_df.iterrows():
    player_name = str(row['Skater']).strip()
    
    if not player_name or player_name == 'nan' or len(player_name) < 3:
        continue
    
    # Build stats dict from ALL stat columns
    stats = {}
    stat_columns = ['GP', 'G', 'A', 'TP', 'PIM', '+/-']
    
    for col in stat_columns:
        if col in row and not pd.isna(row[col]):
            value = str(row[col]).strip()
            if value and value != 'nan':
                stats[col] = value
    
    # Skip if no stats were found
    if not stats:
        print(f"   Skipping {player_name} - no stats found")
        continue
    
    record = {
        'player_name': player_name,
        'season': '2025-2026',
        'team_name': 'Tampa Bay Lightning',
        'league_name': 'NHL',
        'stats': stats,
        'is_playoff': False,
        'is_prospect': False,
        'source': 'selenium_table_1_fixed',
        'updated_at': datetime.utcnow().isoformat()
    }
    
    nhl_records.append(record)

print(f"✓ Converted {len(nhl_records)} NHL records")

# Show a sample NHL record
if nhl_records:
    print("\n Sample NHL record:")
    print(json.dumps(nhl_records[0], indent=2))


print("\n" + "=" * 70)
print("Step 4: Combining datasets...")
print("=" * 70)

# CRITICAL FIX: Filter out NHL players from prospects data
# The prospects file contains old NHL data with incomplete stats
# We only want true prospects (non-NHL leagues)
prospects_only = [p for p in prospects_data if p.get('league_name') != 'NHL']

print(f"Prospects file had: {len(prospects_data)} records")
print(f"Filtered out: {len(prospects_data) - len(prospects_only)} old NHL players")
print(f"True prospects: {len(prospects_only)}")

# Combine: True prospects + Fresh NHL data
all_players = prospects_only + nhl_records

print(f"\n✓ Total players after combining: {len(all_players)}")

# Show breakdown
print("\nBreakdown:")
print(f"  Prospects (non-NHL): {len(prospects_only)}")
print(f"  NHL (from Selenium): {len(nhl_records)}")

league_counts = {}
for player in all_players:
    league = player['league_name']
    league_counts[league] = league_counts.get(league, 0) + 1

print("\nBy league:")
for league, count in sorted(league_counts.items(), key=lambda x: x[1], reverse=True):
    print(f"  {league}: {count} players")


print("\n" + "=" * 70)
print("Step 5: Saving files...")
print("=" * 70)

# Save to JSON
master_json = os.path.join(SCRIPT_DIR, 'tbl_complete_stats_fixed.json')
with open(master_json, 'w') as f:
    json.dump(all_players, f, indent=2, default=str)
print(f"✓ Saved JSON: {master_json}")

# Save to CSV
csv_data = []
for player in all_players:
    row = {
        'player_name': player['player_name'],
        'team': player['team_name'],
        'league': player['league_name'],
        'season': player['season'],
        'is_prospect': player.get('is_prospect', False)
    }
    
    for stat_name, stat_value in player.get('stats', {}).items():
        row[stat_name] = stat_value
    
    csv_data.append(row)

master_csv = os.path.join(SCRIPT_DIR, 'tbl_complete_stats_fixed.csv')
pd.DataFrame(csv_data).to_csv(master_csv, index=False)
print(f"✓ Saved CSV: {master_csv}")


print("\n" + "=" * 70)
print("Step 6: MongoDB Upload")
print("=" * 70)

def upload_to_mongodb(data):
    """Upload all data to MongoDB"""
    try:
        client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        
        db = client[DB_NAME]
        stats_collection = db[COLLECTION_NAME]
        
        print(f"✓ Connected to MongoDB")
        print(f"✓ Database: {DB_NAME}")
        print(f"✓ Collection: {COLLECTION_NAME}")
        
        # Clear existing data
        print("\nClearing old data from player_stats...")
        delete_result = stats_collection.delete_many({})
        print(f"✓ Deleted {delete_result.deleted_count} old records")
        
        inserted = 0
        updated = 0
        
        for record in data:
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
        
        print(f"\n✓ Inserted: {inserted}")
        print(f"✓ Updated: {updated}")
        print(f"✓ Total in collection: {stats_collection.count_documents({})}")
        
        return True
        
    except Exception as e:
        print(f"\n MongoDB error: {e}")
        print("  Data is saved to JSON/CSV files")
        return False

# Upload to MongoDB
upload_to_mongodb(all_players)


print("\n" + "=" * 70)
print("✓✓✓ SUCCESS! ✓✓✓")
print("=" * 70)
print()
print(f" Total Players: {len(all_players)}")
print(f"   - NHL (Selenium): {len(nhl_records)}")
print(f"   - Prospects (non-NHL): {len(prospects_only)}")
print()
print(" Files:")
print(f"   - {master_json}")
print(f"   - {master_csv}")
print()
print("=" * 70)