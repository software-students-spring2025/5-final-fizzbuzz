import pytest
from unittest.mock import patch, MagicMock
from app import create_app
from datetime import datetime
from bson import ObjectId
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from flask import session

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['MONGO_URI'] = 'mongodb://localhost:27017/test_db'
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess['user_id'] = "656f99ab8a5f3c2ef4c50b1a"
            sess['username'] = "testuser"
        yield client

@pytest.fixture
def unauth_client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['MONGO_URI'] = 'mongodb://localhost:27017/test_db'
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.test_client() as client:
        yield client

def test_health_check(client):
    with patch('app.routes.mongo') as mock_mongo:
        mock_mongo.db.command.return_value = True
        response = client.get('/api/health')
        assert response.status_code == 200
        assert response.get_json() == {
            "status": "healthy",
            "database": "connected"
        }

def test_health_check_db_error(client):
    with patch('app.routes.mongo') as mock_mongo:
        mock_mongo.db.command.side_effect = Exception("DB Error")
        response = client.get('/api/health')
        assert response.status_code == 200
        assert response.get_json()["database"] == "disconnected"

def test_register_success(unauth_client):
    mock_user = {
        "_id": ObjectId("656f99ab8a5f3c2ef4c50b1a"),
        "username": "newuser",
        "email": "newuser@example.com"
    }

    with patch('app.models.User.get_by_email', return_value=None), \
         patch('app.models.User.create', return_value=mock_user):
        response = unauth_client.post('/register', data={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "securepassword123",
            "confirm_password": "securepassword123"
        })

        assert response.status_code == 302  # Redirects to dashboard
        assert response.headers['Location'] == '/dashboard'

def test_register_existing_email(unauth_client):
    mock_user = {"username": "existinguser"}

    with patch('app.routes.render_template', return_value='') as mock_render:
        with patch('app.models.User.get_by_email', return_value=mock_user):
            response = unauth_client.post('/register', data={
                "username": "existinguser",
                "email": "test@example.com",
                "password": "password123",
                "confirm_password": "password123"
            })

            assert response.status_code == 200
            mock_render.assert_called_with('register.html', error="Email already registered")

def test_register_missing_fields(unauth_client):
    with patch('app.routes.render_template', return_value='') as mock_render:
        response = unauth_client.post('/register', data={
            "username": "newuser"
            # missing email and password
        })
        assert response.status_code == 200
        mock_render.assert_called_with('register.html', error="All fields are required")

def test_register_user_db_error(unauth_client):
    with patch('app.routes.render_template', return_value='') as mock_render:
        with patch('app.models.User.get_by_email', return_value=None), \
             patch('app.models.User.create', return_value=None):
            response = unauth_client.post('/register', data={
                "username": "newuser",
                "email": "test@example.com",
                "password": "password123",
                "confirm_password": "password123"
            })
            assert response.status_code == 200
            mock_render.assert_called_with('register.html', error="Failed to create account")

def test_get_transactions_success(client):
    mock_transactions = [
        {
            "_id": ObjectId("123456789012345678901234"),
            "amount": -100.0,
            "category": "Food",
            "description": "Groceries",
            "date": datetime.now(),
            "user_id": "656f99ab8a5f3c2ef4c50b1a",
            "type": "expense"
        }
    ]
    
    with patch('app.models.Transaction.get_by_user', return_value=mock_transactions):
        response = client.get('/api/transactions')
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["category"] == "Food"
        assert "_id" in data[0]

def test_get_transactions_db_error(client):
    with patch('app.models.Transaction.get_by_user', side_effect=ConnectionFailure("DB Error")):
        response = client.get('/api/transactions')
        assert response.status_code == 500
        assert "error" in response.get_json()

def test_create_transaction_missing_field(client):
    response = client.post('/api/transactions', json={
        "amount": 20.0,
        "type": "expense",
        "description": "Groceries"
        # "category" is missing
    })
    assert response.status_code == 400

def test_create_transaction_success(client):
    mock_transaction_id = "123456789012345678901234"

    with patch('app.models.Transaction.create', return_value={"_id": mock_transaction_id}):
        response = client.post('/api/transactions', json={
            "description": "Monthly salary",
            "amount": 50.0,
            "type": "income",
            "category": "Salary",
            "date": datetime.now().strftime('%Y-%m-%d')
        })

        assert response.status_code == 201

def test_create_transaction_db_error(client):
    with patch('app.models.Transaction.create', side_effect=ConnectionFailure("DB Error")):
        response = client.post('/api/transactions', json={
            "description": "Monthly salary",
            "amount": 50.0,
            "type": "income",
            "category": "Salary",
            "date": datetime.now().strftime('%Y-%m-%d')
        })
        assert response.status_code == 500
        assert "error" in response.get_json()

def test_delete_transaction_success(client):
    with patch('app.models.Transaction.delete', return_value=True):
        response = client.delete('/api/transactions/123456789012345678901234')
        assert response.status_code == 204

def test_delete_transaction_not_found(client):
    with patch('app.models.Transaction.delete', return_value=False):
        response = client.delete('/api/transactions/123456789012345678901234')
        assert response.status_code == 404
        assert response.get_json() == {"error": "Transaction not found"}

def test_delete_transaction_db_error(client):
    with patch('app.models.Transaction.delete', side_effect=ConnectionFailure("DB Error")):
        response = client.delete('/api/transactions/123456789012345678901234')
        assert response.status_code == 500
        assert "error" in response.get_json()

def test_monthly_analytics(client):
    mock_data = [
        {
            "_id": {"year": 2024, "month": 4},
            "total": 1000.0,
            "count": 5
        }
    ]

    with patch('app.models.Transaction.aggregate') as mock_aggregate:
        mock_aggregate.return_value = mock_data
        response = client.get('/api/analytics/monthly')
        assert response.status_code == 200

def test_monthly_analytics_db_error(client):
    with patch('app.models.Transaction.aggregate') as mock_aggregate:
        mock_aggregate.side_effect = ConnectionFailure("DB Error")
        response = client.get('/api/analytics/monthly')
        assert response.status_code == 500
        assert "error" in response.get_json()

def test_category_analytics(client):
    mock_data = [
        {
            "_id": "Food",
            "total": 500.0,
            "count": 3
        }
    ]
    
    with patch('app.models.Transaction.aggregate') as mock_aggregate:
        mock_aggregate.return_value = mock_data
        response = client.get('/api/analytics/categories')
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["total"] == 500.0

def test_category_analytics_db_error(client):
    with patch('app.models.Transaction.aggregate', side_effect=ConnectionFailure("DB Error")):
        response = client.get('/api/analytics/categories')
        assert response.status_code == 500
        assert "error" in response.get_json()

def test_index_success(client):
    response = client.get('/')
    assert response.status_code == 302  # Redirects to dashboard

def test_serve_static(client):
    response = client.get('/static/js/app.js')
    assert response.status_code == 404  # File not found

def test_login_success(unauth_client):
    mock_user = {
        "_id": ObjectId("656f99ab8a5f3c2ef4c50b1a"),
        "username": "testuser",
        "email": "test@example.com",
        "password_hash": "hashed_password"
    }

    with patch('app.models.User.login', return_value=mock_user):
        response = unauth_client.post('/login', data={
            "email": "test@example.com",
            "password": "password123"
        })
        assert response.status_code == 302
        assert response.headers['Location'] == '/dashboard'

def test_login_invalid_credentials(unauth_client):
    with patch('app.models.User.login', return_value=None):
        with patch('app.routes.render_template', return_value='') as mock_render:
            response = unauth_client.post('/login', data={
                "email": "test@example.com",
                "password": "wrongpassword"
            })
            assert response.status_code == 200
            mock_render.assert_called_with('login.html', error="Invalid email or password")

def test_login_db_error(unauth_client):
    with patch('app.models.User.login', side_effect=ConnectionFailure("DB Error")):
        with patch('app.routes.render_template', return_value='') as mock_render:
            response = unauth_client.post('/login', data={
                "email": "test@example.com",
                "password": "password123"
            })
            assert response.status_code == 200
            mock_render.assert_called_with('login.html', error="An error occurred. Please try again.")

def test_register_passwords_dont_match(unauth_client):
    with patch('app.routes.render_template', return_value='') as mock_render:
        response = unauth_client.post('/register', data={
            "username": "newuser",
            "email": "test@example.com",
            "password": "password123",
            "confirm_password": "password456"
        })
        assert response.status_code == 200
        mock_render.assert_called_with('register.html', error="Passwords do not match")

def test_register_get_page(unauth_client):
    with patch('app.routes.render_template', return_value='') as mock_render:
        response = unauth_client.get('/register')
        assert response.status_code == 200
        mock_render.assert_called_with('register.html')

def test_login_get_page(unauth_client):
    with patch('app.routes.render_template', return_value='') as mock_render:
        response = unauth_client.get('/login')
        assert response.status_code == 200
        mock_render.assert_called_with('login.html')

def test_login_already_authenticated(client):
    response = client.get('/login')
    assert response.status_code == 302
    assert response.headers['Location'] == '/dashboard'

def test_register_already_authenticated(client):
    response = client.get('/register')
    assert response.status_code == 302
    assert response.headers['Location'] == '/dashboard'

def test_dashboard_page(client):
    with patch('app.routes.render_template', return_value='') as mock_render:
        response = client.get('/dashboard')
        assert response.status_code == 200
        mock_render.assert_called_with('dashboard.html')

def test_dashboard_unauthorized(unauth_client):
    response = unauth_client.get('/dashboard')
    assert response.status_code == 302
    assert response.headers['Location'] == '/login'

def test_logout(client):
    response = client.get('/logout')
    assert response.status_code == 302
    assert response.headers['Location'] == '/login'
    with client.session_transaction() as sess:
        assert 'user_id' not in sess
        assert 'username' not in sess
