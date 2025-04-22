from datetime import datetime
from bson import ObjectId

class User:
    def __init__(self, username, email, password_hash, university=None, monthly_income=0):
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.university = university
        self.monthly_income = monthly_income
        self.created_at = datetime.now()

    def to_dict(self):
        return {
            "username": self.username,
            "email": self.email,
            "password_hash": self.password_hash,
            "university": self.university,
            "monthly_income": self.monthly_income,
            "created_at": self.created_at
        }

class Transaction:
    def __init__(self, amount, category, description, date=None):
        self.amount = amount
        self.category = category
        self.description = description
        self.date = date or datetime.now()

    def to_dict(self):
        return {
            "amount": self.amount,
            "category": self.category,
            "description": self.description,
            "date": self.date
        }