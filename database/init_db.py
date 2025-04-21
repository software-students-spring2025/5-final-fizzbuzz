import os
import json
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get MongoDB connection string
mongo_uri = os.environ.get("MONGO_URI")
if not mongo_uri:
    raise ValueError("MONGO_URI environment variable is not set")

# Connect to MongoDB
client = MongoClient(mongo_uri)
db = client.get_database()

def setup_indexes():
    # Create indexes for better query performance
    db.users.create_index("username", unique=True)
    db.users.create_index("email", unique=True)
    db.transactions.create_index([("user_id", 1), ("date", -1)])
    db.categories.create_index([("user_id", 1), ("name", 1)])
    db.budgets.create_index([("user_id", 1), ("category_id", 1)])

def load_default_categories():
    # Default expense categories
    expense_categories = [
        {"name": "Food & Dining", "type": "expense", "icon": "restaurant", "color": "#FF5722"},
        {"name": "Transportation", "type": "expense", "icon": "directions_bus", "color": "#3F51B5"},
        {"name": "Books & Supplies", "type": "expense", "icon": "book", "color": "#009688"},
        {"name": "Entertainment", "type": "expense", "icon": "movie", "color": "#E91E63"},
        {"name": "Housing", "type": "expense", "icon": "home", "color": "#795548"},
        {"name": "Utilities", "type": "expense", "icon": "power", "color": "#FFC107"},
        {"name": "Clothing", "type": "expense", "icon": "shopping_bag", "color": "#9C27B0"},
        {"name": "Health", "type": "expense", "icon": "local_hospital", "color": "#F44336"},
        {"name": "Personal", "type": "expense", "icon": "person", "color": "#607D8B"},
        {"name": "Other", "type": "expense", "icon": "more_horiz", "color": "#9E9E9E"}
    ]
    
    # Default income categories
    income_categories = [
        {"name": "Scholarships", "type": "income", "icon": "school", "color": "#4CAF50"},
        {"name": "Part-time Job", "type": "income", "icon": "work", "color": "#2196F3"},
        {"name": "Allowance", "type": "income", "icon": "attach_money", "color": "#FFEB3B"},
        {"name": "Grants", "type": "income", "icon": "card_giftcard", "color": "#00BCD4"},
        {"name": "Other Income", "type": "income", "icon": "add", "color": "#8BC34A"}
    ]
    
    # Add user_id=None to indicate these are system defaults
    for category in expense_categories + income_categories:
        category["user_id"] = None
        db.categories.update_one(
            {"name": category["name"], "type": category["type"], "user_id": None},
            {"$set": category},
            upsert=True
        )

def main():
    print("Setting up database...")
    setup_indexes()
    print("Loading default categories...")
    load_default_categories()
    print("Database initialization complete!")

if __name__ == "__main__":
    main()