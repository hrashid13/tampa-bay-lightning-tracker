from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv('MONGODB_URI')
if not MONGODB_URI:
    raise ValueError("MONGODB_URI not found in environment variables")

def explore():
    client = MongoClient(MONGO_URI)
    db = client.lightning_tracker
    
    print(" Exploring your database...\n")
    
    # List collections
    print("Collections:")
    for collection in db.list_collection_names():
        count = db[collection].count_documents({})
        print(f"  - {collection}: {count} documents")
    
    print("\n" + "="*50)
    
    # Show all players
    print("\n All Players:")
    players = db.player_profiles.find({})
    for player in players:
        print(f"  - {player['name']} ({player['position']}) - {player['current_status']['team']}")
    
    print("\n" + "="*50)
    
    # Show all stats
    print("\n Recent Stats:")
    stats = db.player_daily_stats.find({}).sort("date", -1).limit(5)
    for stat in stats:
        print(f"  - {stat['player_name']}: {stat['points']}pts in {stat['games_played']}gp on {stat['date'].strftime('%Y-%m-%d')}")
    
    print("\n" + "="*50)
    
    # Try a query
    print("\n Query Example - NHL players only:")
    nhl_players = db.player_profiles.find({"current_status.league": "NHL"})
    for player in nhl_players:
        print(f"  - {player['name']}")

if __name__ == "__main__":
    explore()