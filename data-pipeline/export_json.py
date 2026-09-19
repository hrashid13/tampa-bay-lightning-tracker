"""Export player stats from MongoDB Atlas to a static JSON file.

The dashboard is built as a static site (GitHub Pages), so instead of querying
MongoDB on every page view it reads this file, which is regenerated whenever
the site is deployed.

Environment variables:
    MONGODB_URI         (required) Atlas connection string
    MONGODB_DB          (optional) database name; falls back to the database in
                        the URI, then to the only database if there is one
    MONGODB_COLLECTION  (optional) collection name; falls back to the only
                        collection in the database if there is exactly one
    MIN_DOCS            (optional) refuse to write if fewer documents come back
                        than this (default 20), so a bad scrape can't blank the site
"""
import json
import math
import os
import sys
from datetime import date, datetime, timezone
from pathlib import Path

from bson import ObjectId
from pymongo import MongoClient

OUTPUT = (
    Path(__file__).resolve().parent.parent / "tbl-dashboard" / "data" / "players.json"
)
SYSTEM_DBS = {"admin", "local", "config"}


def pick_database(client):
    name = os.getenv("MONGODB_DB")
    if name:
        return client[name]
    try:
        return client.get_default_database()
    except Exception:
        pass
    try:
        names = [n for n in client.list_database_names() if n not in SYSTEM_DBS]
    except Exception:
        names = []
    if len(names) == 1:
        return client[names[0]]
    sys.exit(
        "Could not tell which database to use. Set MONGODB_DB. "
        f"Databases visible: {names or 'unknown'}"
    )


def pick_collection(db):
    name = os.getenv("MONGODB_COLLECTION")
    if name:
        return db[name]
    names = [n for n in db.list_collection_names() if not n.startswith("system.")]
    if len(names) == 1:
        return db[names[0]]
    sys.exit(
        "Could not tell which collection to use. Set MONGODB_COLLECTION. "
        f"Collections in '{db.name}': {names}"
    )


def clean(value):
    """Make Mongo/BSON values JSON-safe."""
    if isinstance(value, dict):
        return {k: clean(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [clean(v) for v in value]
    if isinstance(value, ObjectId):
        return str(value)
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return None  # NaN is not valid JSON and breaks JSON.parse in the browser
    return value


def main():
    uri = os.getenv("MONGODB_URI")
    if not uri:
        sys.exit("MONGODB_URI is not set.")

    client = MongoClient(uri, serverSelectionTimeoutMS=15000)
    collection = pick_collection(pick_database(client))
    docs = [clean(d) for d in collection.find({})]

    min_docs = int(os.getenv("MIN_DOCS", "20"))
    if len(docs) < min_docs:
        sys.exit(
            f"Only {len(docs)} documents found (expected at least {min_docs}); "
            "not overwriting the existing file."
        )

    payload = {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "players": docs,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2, allow_nan=False), encoding="utf-8")
    print(
        f"Wrote {len(docs)} documents from "
        f"{collection.database.name}.{collection.name} to {OUTPUT}"
    )


if __name__ == "__main__":
    main()
