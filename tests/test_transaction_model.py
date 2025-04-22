import pytest
from unittest.mock import patch, MagicMock
from app.models import Transaction
from bson import ObjectId

def test_create_transaction():
    mock_result = MagicMock()
    mock_result.inserted_id = ObjectId("656f99ab8a5f3c2ef4c50b1a")

    with patch('app.models.mongo') as mock_mongo:
        mock_mongo.db.transactions.insert_one.return_value = mock_result

        transaction_id = Transaction.create(
            user_id="656f99ab8a5f3c2ef4c50b1a",
            amount=45.67,
            type="expense",
            category_id=None,
            description="Test transaction"
        )

        assert transaction_id == str(mock_result.inserted_id)

def test_get_by_user():
    mock_transactions = [
        {"amount": 9.99, "description": "Netflix", "type": "expense"},
        {"amount": 1200.00, "description": "Scholarship", "type": "income"}
    ]

    with patch('app.models.mongo') as mock_mongo:
        mock_mongo.db.transactions.find.return_value.sort.return_value.limit.return_value = mock_transactions

        result = Transaction.get_by_user("656f99ab8a5f3c2ef4c50b1a")
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["description"] == "Netflix"

