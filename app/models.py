from datetime import datetime
from bson import ObjectId
from app import mongo
from werkzeug.security import generate_password_hash, check_password_hash
import logging

logger = logging.getLogger(__name__)

class User:
    def __init__(self, username, email, password=None, password_hash=None):
        self.username = username
        self.email = email
        if password:
            self.password_hash = generate_password_hash(password)
        else:
            self.password_hash = password_hash
        self.created_at = datetime.now()

    def to_dict(self):
        return {
            "username": self.username,
            "email": self.email,
            "password_hash": self.password_hash,
            "created_at": self.created_at
        }

    @staticmethod
    def get_by_email(email):
        return mongo.db.users.find_one({"email": email})

    @staticmethod
    def get_by_id(user_id):
        if not isinstance(user_id, ObjectId):
            user_id = ObjectId(user_id)
        return mongo.db.users.find_one({"_id": user_id})

    def save(self):
        result = mongo.db.users.insert_one(self.to_dict())
        if result.inserted_id:
            return mongo.db.users.find_one({"_id": result.inserted_id})
        return None

    @staticmethod
    def create(username, email, password):
        # Check if email already exists
        if User.get_by_email(email):
            return None
        user = User(username=username, email=email, password=password)
        return user.save()

    @staticmethod
    def login(email, password):
        user = mongo.db.users.find_one({"email": email})
        if user and check_password_hash(user['password_hash'], password):
            return user
        return None

class Transaction:
    def __init__(self, amount, category, description, date=None, user_id=None, type=None):
        # Convert amount to float and make it positive for income, negative for expense
        amount = float(amount)
        self.amount = amount if type == 'income' else -abs(amount)
        self.category = category
        self.description = description
        self.date = date if date else datetime.now()
        self.user_id = user_id
        self.type = type

    def to_dict(self):
        return {
            "amount": self.amount,
            "category": self.category,
            "description": self.description,
            "date": self.date,
            "user_id": self.user_id,
            "type": self.type
        }

    def save(self):
        try:
            result = mongo.db.transactions.insert_one(self.to_dict())
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Error saving transaction: {str(e)}")
            raise

    @staticmethod
    def get_all():
        try:
            return list(mongo.db.transactions.find())
        except Exception as e:
            logger.error(f"Error getting all transactions: {str(e)}")
            raise

    @staticmethod
    def create(data):
        try:
            transaction = Transaction(
                amount=data['amount'],
                category=data['category'],
                description=data['description'],
                user_id=data['user_id'],
                type=data['type'],
                date=data.get('date', datetime.now())
            )
            transaction_id = transaction.save()
            return {"_id": transaction_id}
        except Exception as e:
            logger.error(f"Error creating transaction: {str(e)}")
            raise

    @staticmethod
    def get_by_user(user_id):
        try:
            return list(mongo.db.transactions.find({"user_id": user_id}).sort("date", -1))
        except Exception as e:
            logger.error(f"Error getting transactions for user {user_id}: {str(e)}")
            raise

    @staticmethod
    def delete(transaction_id, user_id):
        try:
            result = mongo.db.transactions.delete_one({
                "_id": transaction_id,
                "user_id": user_id
            })
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting transaction {transaction_id}: {str(e)}")
            raise

    @staticmethod
    def aggregate(pipeline):
        try:
            return mongo.db.transactions.aggregate(pipeline)
        except Exception as e:
            logger.error(f"Error running aggregation: {str(e)}")
            raise

class Category:
    def __init__(self, user_id, name, type):
        self.user_id = user_id
        self.name = name
        self.type = type

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "name": self.name,
            "type": self.type
        }

    def save(self):
        try:
            result = mongo.db.categories.insert_one(self.to_dict())
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Error saving category: {str(e)}")
            raise

    @staticmethod
    def create(data):
        try:
            category = Category(
                user_id=data['user_id'],
                name=data['name'],
                type=data['type']
            )
            category_id = category.save()
            return category_id
        except Exception as e:
            logger.error(f"Error creating category: {str(e)}")
            raise

    @staticmethod
    def get_by_user(user_id):
        try:
            return list(mongo.db.categories.find({"user_id": user_id}))
        except Exception as e:
            logger.error(f"Error getting categories for user {user_id}: {str(e)}")
            raise