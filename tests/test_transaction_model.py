import pytest
from bson import ObjectId
from unittest.mock import MagicMock, patch
from app.models import Transaction
from datetime import datetime

def test_create_transaction():
    mock_result = MagicMock()
    mock_result.inserted_id = ObjectId("656f99ab8a5f3c2ef4c50b1a")

    with patch('app.models.mongo') as mock_mongo:
        mock_mongo.db.transactions.insert_one.return_value = mock_result

        result = Transaction.create(
            data={
                "user_id": "656f99ab8a5f3c2ef4c50b1a",
                "amount": 45.67,
                "type": "expense",
                "category": "Food",
                "description": "Test transaction"
            }
        )

        assert isinstance(result, dict)
        assert "_id" in result
        assert result["_id"] == str(mock_result.inserted_id)
        mock_mongo.db.transactions.insert_one.assert_called_once()

def test_save_transaction():
    transaction = Transaction(
        amount=50.0,
        category="Food",
        description="Test transaction",
        type="expense"
    )

    mock_result = MagicMock()
    mock_result.inserted_id = ObjectId("656f99ab8a5f3c2ef4c50b1a")

    with patch('app.models.mongo') as mock_mongo:
        mock_mongo.db.transactions.insert_one.return_value = mock_result
        
        transaction_id = transaction.save()
        
        assert transaction_id == str(mock_result.inserted_id)
        mock_mongo.db.transactions.insert_one.assert_called_once()
        inserted_data = mock_mongo.db.transactions.insert_one.call_args[0][0]
        assert inserted_data["amount"] == -50.0  # Should be negative for expense
        assert inserted_data["category"] == "Food"
        assert inserted_data["description"] == "Test transaction"

def test_get_by_user():
    mock_transactions = [
        {
            "_id": ObjectId("656f99ab8a5f3c2ef4c50b1a"),
            "amount": -100.0,
            "category": "Food",
            "description": "Groceries",
            "date": datetime.now(),
            "user_id": "656f99ab8a5f3c2ef4c50b1a",
            "type": "expense"
        }
    ]

    with patch('app.models.mongo') as mock_mongo:
        mock_mongo.db.transactions.find.return_value.sort.return_value = mock_transactions

        transactions = Transaction.get_by_user("656f99ab8a5f3c2ef4c50b1a")

        assert len(transactions) == 1
        assert transactions[0]["amount"] == -100.0
        assert transactions[0]["category"] == "Food"
        mock_mongo.db.transactions.find.assert_called_once_with({"user_id": "656f99ab8a5f3c2ef4c50b1a"})

def test_delete_transaction():
    transaction_id = ObjectId("656f99ab8a5f3c2ef4c50b1a")
    user_id = "656f99ab8a5f3c2ef4c50b1b"

    with patch('app.models.mongo') as mock_mongo:
        mock_mongo.db.transactions.delete_one.return_value.deleted_count = 1
        
        result = Transaction.delete(transaction_id, user_id)
        
        assert result is True
        mock_mongo.db.transactions.delete_one.assert_called_once_with({
            "_id": transaction_id,
            "user_id": user_id
        })

def test_delete_transaction_not_found():
    transaction_id = ObjectId("656f99ab8a5f3c2ef4c50b1a")
    user_id = "656f99ab8a5f3c2ef4c50b1b"

    with patch('app.models.mongo') as mock_mongo:
        mock_mongo.db.transactions.delete_one.return_value.deleted_count = 0
        
        result = Transaction.delete(transaction_id, user_id)
        
        assert result is False

def test_get_all_transactions():
    mock_transactions = [
        {
            "_id": ObjectId("656f99ab8a5f3c2ef4c50b1a"),
            "amount": -100.0,
            "category": "Food",
            "description": "Groceries",
            "date": datetime.now(),
            "user_id": "656f99ab8a5f3c2ef4c50b1a",
            "type": "expense"
        },
        {
            "_id": ObjectId("656f99ab8a5f3c2ef4c50b1b"),
            "amount": 200.0,
            "category": "Salary",
            "description": "Monthly salary",
            "date": datetime.now(),
            "user_id": "656f99ab8a5f3c2ef4c50b1a",
            "type": "income"
        }
    ]

    with patch('app.models.mongo') as mock_mongo:
        mock_mongo.db.transactions.find.return_value = mock_transactions
        
        transactions = Transaction.get_all()
        
        assert len(transactions) == 2
        assert transactions[0]["amount"] == -100.0
        assert transactions[1]["amount"] == 200.0
        mock_mongo.db.transactions.find.assert_called_once()

def test_aggregate_transactions():
    mock_pipeline = [
        {"$match": {"user_id": "656f99ab8a5f3c2ef4c50b1a"}},
        {"$group": {"_id": "$category", "total": {"$sum": "$amount"}}}
    ]
    mock_result = [
        {"_id": "Food", "total": -150.0},
        {"_id": "Salary", "total": 1000.0}
    ]

    with patch('app.models.mongo') as mock_mongo:
        mock_mongo.db.transactions.aggregate.return_value = mock_result
        
        result = Transaction.aggregate(mock_pipeline)
        
        assert list(result) == mock_result
        mock_mongo.db.transactions.aggregate.assert_called_once_with(mock_pipeline)

