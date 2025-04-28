import pytest
from datetime import datetime
from app.models import User, Transaction, Category
from unittest.mock import patch, MagicMock
from bson import ObjectId
from werkzeug.security import generate_password_hash
import logging

@pytest.fixture
def mock_db():
    with patch('app.models.mongo') as mock_mongo:
        yield mock_mongo

def test_user_creation():
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash="hashed_password"
    )
    
    user_dict = user.to_dict()
    assert user_dict["username"] == "testuser"
    assert user_dict["email"] == "test@example.com"
    assert user_dict["password_hash"] == "hashed_password"
    assert isinstance(user_dict["created_at"], datetime)

def test_user_creation_minimal():
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash="hashed_password"
    )
    
    user_dict = user.to_dict()
    assert user_dict["username"] == "testuser"
    assert user_dict["email"] == "test@example.com"
    assert user_dict["password_hash"] == "hashed_password"

def test_user_get_by_email(mock_db):
    mock_user = {
        "_id": ObjectId("123456789012345678901234"),
        "username": "testuser",
        "email": "test@example.com"
    }
    
    mock_db.db.users.find_one.return_value = mock_user
    result = User.get_by_email("test@example.com")
    mock_db.db.users.find_one.assert_called_once_with({"email": "test@example.com"})
    assert result == mock_user

def test_user_get_by_id(mock_db):
    user_id = ObjectId("123456789012345678901234")
    mock_user = {
        "_id": user_id,
        "username": "testuser",
        "email": "test@example.com"
    }
    
    mock_db.db.users.find_one.return_value = mock_user
    result = User.get_by_id(str(user_id))
    mock_db.db.users.find_one.assert_called_once_with({"_id": user_id})
    assert result == mock_user

def test_user_save(mock_db):
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash="hashed_password"
    )
    
    mock_result = MagicMock()
    mock_result.inserted_id = ObjectId("123456789012345678901234")
    mock_db.db.users.insert_one.return_value = mock_result
    
    mock_saved_user = {
        "_id": mock_result.inserted_id,
        "username": "testuser",
        "email": "test@example.com"
    }
    mock_db.db.users.find_one.return_value = mock_saved_user
    
    result = user.save()
    mock_db.db.users.insert_one.assert_called_once_with(user.to_dict())
    assert result == mock_saved_user

def test_user_save_error(mock_db):
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash="hashed_password"
    )
    
    mock_db.db.users.insert_one.side_effect = Exception("Database error")
    
    with pytest.raises(Exception) as exc_info:
        user.save()
    assert str(exc_info.value) == "Database error"

def test_user_get_by_email_error(mock_db):
    mock_db.db.users.find_one.side_effect = Exception("Database error")
    
    with pytest.raises(Exception) as exc_info:
        User.get_by_email("test@example.com")
    assert str(exc_info.value) == "Database error"

def test_user_get_by_id_error(mock_db):
    mock_db.db.users.find_one.side_effect = Exception("Database error")
    
    with pytest.raises(Exception) as exc_info:
        User.get_by_id("123456789012345678901234")
    assert str(exc_info.value) == "Database error"

def test_transaction_creation():
    transaction = Transaction(
        amount=100.0,
        category="Food",
        description="Groceries",
        type="expense"
    )
    
    transaction_dict = transaction.to_dict()
    assert transaction_dict["amount"] == -100.0  # Negative for expense
    assert transaction_dict["category"] == "Food"
    assert transaction_dict["description"] == "Groceries"
    assert isinstance(transaction_dict["date"], datetime)

def test_transaction_creation_with_date():
    test_date = datetime(2024, 4, 22)
    transaction = Transaction(
        amount=50.0,
        category="Entertainment",
        description="Movie tickets",
        date=test_date,
        type="income"
    )
    
    transaction_dict = transaction.to_dict()
    assert transaction_dict["amount"] == 50.0  # Positive for income
    assert transaction_dict["category"] == "Entertainment"
    assert transaction_dict["description"] == "Movie tickets"
    assert transaction_dict["date"] == test_date

def test_transaction_save(mock_db):
    transaction = Transaction(
        amount=100.0,
        category="Food",
        description="Groceries",
        type="expense"
    )
    
    mock_result = MagicMock()
    mock_result.inserted_id = ObjectId("123456789012345678901234")
    mock_db.db.transactions.insert_one.return_value = mock_result
    
    result = transaction.save()
    mock_db.db.transactions.insert_one.assert_called_once_with(transaction.to_dict())
    assert result == str(mock_result.inserted_id)

def test_transaction_save_error(mock_db):
    transaction = Transaction(
        amount=100.0,
        category="Food",
        description="Groceries",
        type="expense"
    )
    
    mock_db.db.transactions.insert_one.side_effect = Exception("Database error")
    
    with pytest.raises(Exception) as exc_info:
        transaction.save()
    assert str(exc_info.value) == "Database error"

def test_transaction_get_all(mock_db):
    mock_transactions = [
        {
            "_id": ObjectId("123456789012345678901234"),
            "amount": -100.0,
            "category": "Food",
            "description": "Groceries",
            "date": datetime.now(),
            "type": "expense"
        },
        {
            "_id": ObjectId("123456789012345678901235"),
            "amount": 50.0,
            "category": "Entertainment",
            "description": "Movie tickets",
            "date": datetime.now(),
            "type": "income"
        }
    ]
    
    mock_db.db.transactions.find.return_value = mock_transactions
    result = Transaction.get_all()
    mock_db.db.transactions.find.assert_called_once()
    assert result == mock_transactions

def test_transaction_get_all_error(mock_db):
    mock_db.db.transactions.find.side_effect = Exception("Database error")
    
    with pytest.raises(Exception) as exc_info:
        Transaction.get_all()
    assert str(exc_info.value) == "Database error"

def test_category_creation():
    category = Category(
        user_id="123456789012345678901234",
        name="Food",
        type="expense"
    )
    
    category_dict = category.to_dict()
    assert category_dict["name"] == "Food"
    assert category_dict["type"] == "expense"
    assert category_dict["user_id"] == "123456789012345678901234"

def test_category_save(mock_db):
    category = Category(
        user_id="123456789012345678901234",
        name="Food",
        type="expense"
    )
    
    mock_result = MagicMock()
    mock_result.inserted_id = ObjectId("123456789012345678901234")
    mock_db.db.categories.insert_one.return_value = mock_result
    
    result = category.save()
    mock_db.db.categories.insert_one.assert_called_once_with(category.to_dict())
    assert result == str(mock_result.inserted_id)

def test_category_save_error(mock_db):
    category = Category(
        user_id="123456789012345678901234",
        name="Food",
        type="expense"
    )
    
    mock_db.db.categories.insert_one.side_effect = Exception("Database error")
    
    with pytest.raises(Exception) as exc_info:
        category.save()
    assert str(exc_info.value) == "Database error"

def test_category_get_by_user(mock_db):
    mock_categories = [
        {
            "_id": ObjectId("123456789012345678901234"),
            "name": "Food",
            "type": "expense",
            "user_id": "123456789012345678901234"
        },
        {
            "_id": ObjectId("123456789012345678901235"),
            "name": "Entertainment",
            "type": "expense",
            "user_id": "123456789012345678901234"
        }
    ]
    
    mock_db.db.categories.find.return_value = mock_categories
    result = Category.get_by_user("123456789012345678901234")
    mock_db.db.categories.find.assert_called_once_with({"user_id": "123456789012345678901234"})
    assert result == mock_categories

def test_category_get_by_user_error(mock_db):
    mock_db.db.categories.find.side_effect = Exception("Database error")
    
    with pytest.raises(Exception) as exc_info:
        Category.get_by_user("123456789012345678901234")
    assert str(exc_info.value) == "Database error"

def test_category_create(mock_db):
    mock_result = MagicMock()
    mock_result.inserted_id = ObjectId("123456789012345678901234")
    mock_db.db.categories.insert_one.return_value = mock_result
    
    data = {
        "user_id": "123456789012345678901234",
        "name": "Food",
        "type": "expense"
    }
    
    result = Category.create(data)
    mock_db.db.categories.insert_one.assert_called_once()
    assert result == str(mock_result.inserted_id)

def test_category_create_error(mock_db):
    mock_db.db.categories.insert_one.side_effect = Exception("Database error")
    
    data = {
        "user_id": "123456789012345678901234",
        "name": "Food",
        "type": "expense"
    }
    
    with pytest.raises(Exception) as exc_info:
        Category.create(data)
    assert str(exc_info.value) == "Database error"

def test_user_create_with_existing_email(mock_db):
    # Mock find_one to return an existing user
    mock_db.db.users.find_one.return_value = {
        "_id": ObjectId("123456789012345678901234"),
        "email": "test@example.com",
        "username": "existinguser"
    }
    
    result = User.create("testuser", "test@example.com", "password123")
    assert result is None
    mock_db.db.users.find_one.assert_called_once_with({"email": "test@example.com"})

def test_user_login_valid(mock_db):
    mock_user = {
        "_id": ObjectId("123456789012345678901234"),
        "email": "test@example.com",
        "password_hash": generate_password_hash("password123")
    }
    mock_db.db.users.find_one.return_value = mock_user
    
    result = User.login("test@example.com", "password123")
    assert result == mock_user
    mock_db.db.users.find_one.assert_called_once_with({"email": "test@example.com"})

def test_user_login_invalid_password(mock_db):
    mock_user = {
        "_id": ObjectId("123456789012345678901234"),
        "email": "test@example.com",
        "password_hash": generate_password_hash("password123")
    }
    mock_db.db.users.find_one.return_value = mock_user
    
    result = User.login("test@example.com", "wrongpassword")
    assert result is None
    mock_db.db.users.find_one.assert_called_once_with({"email": "test@example.com"})

def test_user_login_nonexistent(mock_db):
    mock_db.db.users.find_one.return_value = None
    
    result = User.login("nonexistent@example.com", "password123")
    assert result is None
    mock_db.db.users.find_one.assert_called_once_with({"email": "nonexistent@example.com"})

def test_transaction_delete_success(mock_db):
    mock_result = MagicMock()
    mock_result.deleted_count = 1
    mock_db.db.transactions.delete_one.return_value = mock_result
    
    transaction_id = ObjectId("123456789012345678901234")
    user_id = "123456789012345678901234"
    
    result = Transaction.delete(transaction_id, user_id)
    assert result is True
    mock_db.db.transactions.delete_one.assert_called_once_with({
        "_id": transaction_id,
        "user_id": user_id
    })

def test_transaction_delete_not_found(mock_db):
    mock_result = MagicMock()
    mock_result.deleted_count = 0
    mock_db.db.transactions.delete_one.return_value = mock_result
    
    transaction_id = ObjectId("123456789012345678901234")
    user_id = "123456789012345678901234"
    
    result = Transaction.delete(transaction_id, user_id)
    assert result is False
    mock_db.db.transactions.delete_one.assert_called_once_with({
        "_id": transaction_id,
        "user_id": user_id
    })

def test_transaction_delete_error(mock_db):
    mock_db.db.transactions.delete_one.side_effect = Exception("Database error")
    
    transaction_id = ObjectId("123456789012345678901234")
    user_id = "123456789012345678901234"
    
    with pytest.raises(Exception) as exc_info:
        Transaction.delete(transaction_id, user_id)
    assert str(exc_info.value) == "Database error"

def test_transaction_aggregate(mock_db):
    mock_pipeline = [{"$match": {"user_id": "123456789012345678901234"}}]
    mock_result = [
        {
            "_id": "Food",
            "total": 100.0
        }
    ]
    mock_db.db.transactions.aggregate.return_value = mock_result
    
    result = Transaction.aggregate(mock_pipeline)
    assert result == mock_result
    mock_db.db.transactions.aggregate.assert_called_once_with(mock_pipeline)

def test_transaction_aggregate_error(mock_db):
    mock_pipeline = [{"$match": {"user_id": "123456789012345678901234"}}]
    mock_db.db.transactions.aggregate.side_effect = Exception("Database error")
    
    with pytest.raises(Exception) as exc_info:
        Transaction.aggregate(mock_pipeline)
    assert str(exc_info.value) == "Database error"

def test_transaction_create_error(mock_db):
    mock_db.db.transactions.insert_one.side_effect = Exception("Database error")
    
    data = {
        "amount": 100.0,
        "category": "Food",
        "description": "Groceries",
        "user_id": "123456789012345678901234",
        "type": "expense"
    }
    
    with pytest.raises(Exception) as exc_info:
        Transaction.create(data)
    assert str(exc_info.value) == "Database error"

def test_user_login_with_invalid_credentials(mock_db):
    # Test with invalid password_hash format
    mock_user = {
        "_id": ObjectId("123456789012345678901234"),
        "email": "test@example.com",
        "password_hash": "invalid_hash_format"
    }
    mock_db.db.users.find_one.return_value = mock_user
    
    result = User.login("test@example.com", "password123")
    assert result is None
    mock_db.db.users.find_one.assert_called_once_with({"email": "test@example.com"})

def test_transaction_delete_with_logging(mock_db, caplog):
    mock_db.db.transactions.delete_one.side_effect = Exception("Database error")
    
    transaction_id = ObjectId("123456789012345678901234")
    user_id = "123456789012345678901234"
    
    with pytest.raises(Exception) as exc_info, caplog.at_level(logging.ERROR):
        Transaction.delete(transaction_id, user_id)
    assert str(exc_info.value) == "Database error"
    assert f"Error deleting transaction {transaction_id}" in caplog.text

def test_transaction_aggregate_with_logging(mock_db, caplog):
    mock_pipeline = [{"$match": {"user_id": "123456789012345678901234"}}]
    mock_db.db.transactions.aggregate.side_effect = Exception("Database error")
    
    with pytest.raises(Exception) as exc_info, caplog.at_level(logging.ERROR):
        Transaction.aggregate(mock_pipeline)
    assert str(exc_info.value) == "Database error"
    assert "Error running aggregation" in caplog.text 