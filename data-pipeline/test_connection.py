from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv


# Connection string from Atlas
load_dotenv()

MONGODB_URI = os.getenv('MONGODB_URI')
if not MONGODB_URI:
    raise ValueError("MONGODB_URI not found in environment variables")

# Connect
client = MongoClient(MONGO_URI)

# Create/access database
db = client.lightning_tracker

# Test: Insert a sample player
test_player = {
    "_id": "test_001",
    "name": "Test Player",
    "position": "C",
    "current_status": {
        "team": "Tampa Bay Lightning",
        "league": "NHL"
    },
    "created_at": datetime.now()
}

# Insert
result = db.player_profiles.insert_one(test_player)
print(f" Inserted player with ID: {result.inserted_id}")

# Read it back
found = db.player_profiles.find_one({"_id": "test_001"})
print(f" Found player: {found['name']}")

# Clean up test
db.player_profiles.delete_one({"_id": "test_001"})
print(" Cleaned up test data")

print("\n MongoDB connection successful!")