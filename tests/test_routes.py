import pytest
from unittest.mock import patch, MagicMock
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_check(client):
    response = client.get('/api/health')
    assert response.status_code == 200
    assert response.get_json() == {"status": "healthy"}

def test_register_user_success(client):
    mock_user = None  # user doesn't exist
    mock_user_id = "mocked_user_id"

    with patch('app.routes.User.find_by_username', return_value=mock_user), \
         patch('app.routes.User.create', return_value=mock_user_id):
        
        response = client.post('/api/register', json={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "securepassword123",
            "university": "NYU",
            "monthly_income": 1000
        })

        assert response.status_code == 201
        assert response.get_json() == {
            "message": "User created successfully",
            "user_id": mock_user_id
        }

def test_register_user_existing_username(client):
    mock_user = {"username": "existinguser"}

    with patch('app.routes.User.find_by_username', return_value=mock_user):
        response = client.post('/api/register', json={
            "username": "existinguser",
            "email": "test@example.com",
            "password": "password123",
            "university": "NYU",
            "monthly_income": 1000
        })

        assert response.status_code == 400
        assert response.get_json() == {
            "error": "Username already exists"
        }

def test_get_transactions_missing_user_id(client):
    response = client.get('/api/transactions')
    assert response.status_code == 400
    assert response.get_json() == {"error": "User ID is required"}

def test_create_transaction_missing_field(client):
    response = client.post('/api/transactions', json={
        "user_id": "656f99ab8a5f3c2ef4c50b1a",
        "amount": 20.0,
        "type": "expense",
        # "category_id" is missing
        "description": "Groceries"
    })
    assert response.status_code == 400
    assert response.get_json() == {"error": "Missing required field: category_id"}

def test_get_transactions_success(client):
    mock_transactions = [
        {"amount": 9.99, "description": "Netflix", "type": "expense"},
        {"amount": 100.00, "description": "Refund", "type": "income"}
    ]

    with patch('app.routes.Transaction.get_by_user', return_value=mock_transactions):
        response = client.get('/api/transactions?user_id=656f99ab8a5f3c2ef4c50b1a')
        assert response.status_code == 200
        assert response.get_json() == {"transactions": mock_transactions}

def test_create_transaction_success(client):
    mock_transaction_id = "mocked_transaction_id"

    with patch('app.routes.Transaction.create', return_value=mock_transaction_id):
        response = client.post('/api/transactions', json={
            "user_id": "656f99ab8a5f3c2ef4c50b1a",
            "amount": 50.0,
            "type": "income",
            "category_id": "1234567890abcdef12345678",
            "description": "Salary",
            "date": "2024-04-22T00:00:00Z"
        })

        assert response.status_code == 201
        assert response.get_json() == {
            "message": "Transaction created",
            "transaction_id": mock_transaction_id
        }
