from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv('MONGODB_URI')
if not MONGODB_URI:
    raise ValueError("MONGODB_URI not found in environment variables")

def setup_database():
    """Initialize the database with proper collections and indexes"""
    
    client = MongoClient(MONGO_URI)
    db = client.lightning_tracker
    
    print("Setting up Lightning Tracker database...")
    
    # 1. Create time-series collection for stats
    try:
        db.create_collection(
            "player_daily_stats",
            timeseries={
                "timeField": "date",
                "metaField": "player_id",
                "granularity": "hours"
            }
        )
        print(" Created time-series collection: player_daily_stats")
    except Exception as e:
        print(f"  Collection may already exist: {e}")
    
    # 2. Create indexes for player_profiles
    db.player_profiles.create_index([("name", 1)])
    db.player_profiles.create_index([("current_status.team", 1)])
    db.player_profiles.create_index([("current_status.league", 1)])
    db.player_profiles.create_index([("current_status.rights_holder", 1)])
    print(" Created indexes on player_profiles")
    
    # 3. Create indexes for player_daily_stats
    db.player_daily_stats.create_index([("player_id", 1), ("date", -1)])
    db.player_daily_stats.create_index([("league", 1), ("date", -1)])
    print(" Created indexes on player_daily_stats")
    
    # 4. Insert a sample player to verify structure
    sample_player = {
        "_id": "sample_player_001",
        "name": "Sample Player",
        "position": "LW",
        "current_status": {
            "team": "Tampa Bay Lightning",
            "league": "NHL",
            "roster_status": "active",
            "rights_holder": "Tampa Bay Lightning"
        },
        "draft_info": {
            "year": 2020,
            "round": 2,
            "pick": 45,
            "team": "Tampa Bay Lightning"
        },
        "birthdate": "2002-03-15",
        "birthplace": "Tampa, FL",
        "height": 72,
        "weight": 185,
        "organizational_history": [{
            "team": "Tampa Bay Lightning",
            "league": "NHL",
            "start_date": datetime(2024, 10, 1),
            "end_date": None,
            "reason": "initial_load"
        }],
        "injury_history": [],
        "created_at": datetime.now(),
        "last_updated": datetime.now()
    }
    
    # Insert or update
    db.player_profiles.update_one(
        {"_id": sample_player["_id"]},
        {"$set": sample_player},
        upsert=True
    )
    print(" Inserted sample player profile")
    
    # 5. Insert sample stats
    sample_stats = {
        "date": datetime.now(),
        "player_id": "sample_player_001",
        "player_name": "Sample Player",
        "team": "Tampa Bay Lightning",
        "league": "NHL",
        "season": "2024-25",
        "games_played": 30,
        "goals": 12,
        "assists": 15,
        "points": 27,
        "plus_minus": 5,
        "pim": 8,
        "powerplay_goals": 4,
        "powerplay_assists": 6,
        "shots": 85,
        "shooting_pct": 14.1,
        "toi_per_game": 18.5
    }
    
    db.player_daily_stats.insert_one(sample_stats)
    print(" Inserted sample stats")
    
    print("\n Database setup complete!")
    print(f"Database: {db.name}")
    print(f"Collections: {db.list_collection_names()}")
    
    # Show what we created
    print("\n Sample data verification:")
    player = db.player_profiles.find_one({"_id": "sample_player_001"})
    print(f"Player: {player['name']} - {player['current_status']['team']}")
    
    stats = db.player_daily_stats.find_one({"player_id": "sample_player_001"})
    print(f"Stats: {stats['goals']}G, {stats['assists']}A, {stats['points']}P")

if __name__ == "__main__":
    setup_database()