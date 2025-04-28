import pytest
from bson import ObjectId
from unittest.mock import MagicMock, patch
from app.models import User

def test_create_user():
    mock_result = MagicMock()
    mock_result.inserted_id = ObjectId("656f99ab8a5f3c2ef4c50b1a")
    mock_user = {
        "_id": ObjectId("656f99ab8a5f3c2ef4c50b1a"),
        "username": "testuser",
        "email": "test@example.com",
        "password_hash": "hashed_pass"
    }

    with patch('app.models.mongo') as mock_mongo:
        mock_mongo.db.users.find_one.side_effect = [None, mock_user]  # First None for get_by_email, then mock_user for find_one after insert
        mock_mongo.db.users.insert_one.return_value = mock_result

        result = User.create(
            username="testuser",
            email="test@example.com",
            password="testpass"
        )

        assert isinstance(result, dict)
        assert result == mock_user
        mock_mongo.db.users.insert_one.assert_called_once()

def test_save_user():
    user = User(
        username="testuser",
        email="test@example.com",
        password="testpass"
    )

    mock_result = MagicMock()
    mock_result.inserted_id = ObjectId("656f99ab8a5f3c2ef4c50b1a")
    mock_user = {
        "_id": ObjectId("656f99ab8a5f3c2ef4c50b1a"),
        "username": "testuser",
        "email": "test@example.com"
    }

    with patch('app.models.mongo') as mock_mongo:
        mock_mongo.db.users.insert_one.return_value = mock_result
        mock_mongo.db.users.find_one.return_value = mock_user

        result = user.save()

        assert result == mock_user
        mock_mongo.db.users.insert_one.assert_called_once()
        inserted_data = mock_mongo.db.users.insert_one.call_args[0][0]
        assert inserted_data["username"] == "testuser"
        assert inserted_data["email"] == "test@example.com"

def test_get_by_email():
    mock_user = {
        "_id": ObjectId("656f99ab8a5f3c2ef4c50b1a"),
        "username": "testuser",
        "email": "test@example.com"
    }

    with patch('app.models.mongo') as mock_mongo:
        mock_mongo.db.users.find_one.return_value = mock_user

        user = User.get_by_email("test@example.com")

        assert user == mock_user
        mock_mongo.db.users.find_one.assert_called_once_with({"email": "test@example.com"})

def test_get_by_id():
    user_id = ObjectId("656f99ab8a5f3c2ef4c50b1a")
    mock_user = {"_id": user_id, "username": "testuser"}

    with patch('app.models.mongo') as mock_mongo:
        mock_mongo.db.users.find_one.return_value = mock_user

        result = User.get_by_id(str(user_id))

        assert result == mock_user
        mock_mongo.db.users.find_one.assert_called_once_with({"_id": user_id})

