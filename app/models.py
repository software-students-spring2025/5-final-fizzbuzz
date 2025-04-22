from datetime import datetime
from app import mongo
from bson.objectid import ObjectId
import json

class User:
    @staticmethod
    def create(username, email, password_hash, university=None, monthly_income=0):
        user = {
            "username": username,
            "email": email,
            "password_hash": password_hash,
            "university": university,
            "monthly_income": float(monthly_income) if monthly_income else 0,
            "created_at": datetime.utcnow()
        }
        result = mongo.db.users.insert_one(user)
        return str(result.inserted_id)
    
    @staticmethod
    def find_by_username(username):
        return mongo.db.users.find_one({"username": username})
    
    @staticmethod
    def find_by_id(user_id):
        return mongo.db.users.find_one({"_id": ObjectId(user_id)})

class Transaction:
    @staticmethod
    def create(user_id, amount, type, category_id, description, date=None):
        transaction = {
            "user_id": ObjectId(user_id),
            "amount": float(amount),
            "type": type,  # "expense" or "income"
            "category_id": ObjectId(category_id) if category_id else None,
            "description": description,
            "date": date or datetime.utcnow()
        }
        result = mongo.db.transactions.insert_one(transaction)
        return str(result.inserted_id)
    
    @staticmethod
    def get_by_user(user_id, limit=50):
        cursor = mongo.db.transactions.find({"user_id": ObjectId(user_id)}).sort("date", -1).limit(limit)
        transactions = list(cursor)
        
        # Convert ObjectId to string for JSON serialization
        for transaction in transactions:
            transaction['_id'] = str(transaction['_id'])
            transaction['user_id'] = str(transaction['user_id'])
            if transaction.get('category_id'):
                transaction['category_id'] = str(transaction['category_id'])
            if isinstance(transaction.get('date'), datetime):
                transaction['date'] = transaction['date'].isoformat()
                
        return transactions