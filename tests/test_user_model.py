import pytest
from unittest.mock import patch, MagicMock
from app.models import User
from bson import ObjectId

def test_create_user():
    mock_result = MagicMock()
    mock_result.inserted_id = ObjectId("656f99ab8a5f3c2ef4c50b1a")

    with patch('app.models.mongo') as mock_mongo:
        mock_mongo.db.users.insert_one.return_value = mock_result

        user_id = User.create(
            username="testuser",
            email="test@example.com",
            password_hash="hashed_pass"
        )

        assert user_id == str(mock_result.inserted_id)

def test_find_by_username():
    mock_user = {"username": "testuser", "email": "test@example.com"}

    with patch('app.models.mongo') as mock_mongo:
        mock_mongo.db.users.find_one.return_value = mock_user

        result = User.find_by_username("testuser")

        assert result["username"] == "testuser"
        assert result["email"] == "test@example.com"

def test_find_by_id():
    user_id = ObjectId("656f99ab8a5f3c2ef4c50b1a")
    mock_user = {"_id": user_id, "username": "testuser"}

    with patch('app.models.mongo') as mock_mongo:
        mock_mongo.db.users.find_one.return_value = mock_user

        result = User.find_by_id(str(user_id))

        assert result["_id"] == user_id
        assert result["username"] == "testuser"

