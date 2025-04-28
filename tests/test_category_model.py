import pytest
from bson import ObjectId
from unittest.mock import MagicMock, patch
from app.models import Category

def test_create_category():
    mock_result = MagicMock()
    mock_result.inserted_id = ObjectId("656f99ab8a5f3c2ef4c50b1a")

    with patch('app.models.mongo') as mock_mongo:
        mock_mongo.db.categories.insert_one.return_value = mock_result

        category_id = Category.create(
            data={
                "user_id": "656f99ab8a5f3c2ef4c50b1a",
                "name": "Food",
                "type": "expense"
            }
        )

        assert category_id == str(mock_result.inserted_id)
        mock_mongo.db.categories.insert_one.assert_called_once()

def test_save_category():
    category = Category(
        user_id="656f99ab8a5f3c2ef4c50b1a",
        name="Food",
        type="expense"
    )

    with patch('app.models.mongo') as mock_mongo:
        category.save()

        mock_mongo.db.categories.insert_one.assert_called_once()
        inserted_data = mock_mongo.db.categories.insert_one.call_args[0][0]
        assert inserted_data["user_id"] == "656f99ab8a5f3c2ef4c50b1a"
        assert inserted_data["name"] == "Food"
        assert inserted_data["type"] == "expense"

def test_get_by_user():
    mock_categories = [
        {"_id": ObjectId("656f99ab8a5f3c2ef4c50b1a"), "name": "Food", "type": "expense"},
        {"_id": ObjectId("656f99ab8a5f3c2ef4c50b1b"), "name": "Salary", "type": "income"}
    ]

    with patch('app.models.mongo') as mock_mongo:
        mock_mongo.db.categories.find.return_value = mock_categories

        categories = Category.get_by_user("656f99ab8a5f3c2ef4c50b1a")

        assert len(categories) == 2
        assert categories[0]["name"] == "Food"
        assert categories[1]["name"] == "Salary"
        mock_mongo.db.categories.find.assert_called_once_with({"user_id": "656f99ab8a5f3c2ef4c50b1a"}) 