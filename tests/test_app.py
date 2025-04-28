import pytest
from unittest.mock import patch, MagicMock
from app import create_app
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from flask_cors import CORS

def test_create_app_success():
    with patch('app.mongo.init_app') as mock_init, \
         patch('app.mongo.db') as mock_db, \
         patch('app.CORS') as mock_cors:
        mock_db.command.return_value = True
        app = create_app()
        assert app.config['DEBUG'] is True
        assert app.config['TEMPLATES_AUTO_RELOAD'] is True
        mock_init.assert_called_once()
        # Check that blueprints are registered
        assert 'main' in app.blueprints
        # Check that CORS is initialized
        mock_cors.assert_called_once()

def test_create_app_connection_failure():
    with patch('app.mongo.init_app') as mock_init, \
         patch('app.mongo.db') as mock_db, \
         patch('app.CORS') as mock_cors:
        mock_db.command.side_effect = ConnectionFailure("Connection failed")
        app = create_app()
        assert app.config['DEBUG'] is True
        mock_init.assert_called_once()
        mock_cors.assert_called_once()

def test_create_app_server_selection_timeout():
    with patch('app.mongo.init_app') as mock_init, \
         patch('app.mongo.db') as mock_db, \
         patch('app.CORS') as mock_cors:
        mock_db.command.side_effect = ServerSelectionTimeoutError("Timeout")
        app = create_app()
        assert app.config['DEBUG'] is True
        mock_init.assert_called_once()
        mock_cors.assert_called_once()

def test_create_app_production_mode():
    with patch('app.mongo.init_app') as mock_init, \
         patch('app.mongo.db') as mock_db, \
         patch('app.CORS') as mock_cors:
        mock_db.command.side_effect = ConnectionFailure("Connection failed")
        # Create app with DEBUG=False to simulate production mode
        with pytest.raises(ConnectionFailure):
            create_app(debug=False)
        mock_cors.assert_called_once()

def test_create_app_unexpected_error():
    with patch('app.mongo.init_app') as mock_init, \
         patch('app.mongo.db') as mock_db, \
         patch('app.CORS') as mock_cors:
        mock_db.command.side_effect = Exception("Unexpected error")
        app = create_app()
        assert app.config['DEBUG'] is True
        mock_init.assert_called_once()
        mock_cors.assert_called_once()

def test_create_app_production_unexpected_error():
    with patch('app.mongo.init_app') as mock_init, \
         patch('app.mongo.db') as mock_db, \
         patch('app.CORS') as mock_cors:
        mock_db.command.side_effect = Exception("Unexpected error")
        # Create app with DEBUG=False to simulate production mode
        with pytest.raises(Exception):
            create_app(debug=False)
        mock_cors.assert_called_once()

def test_create_app_with_custom_config():
    with patch('app.mongo.init_app') as mock_init, \
         patch('app.mongo.db') as mock_db, \
         patch('app.CORS') as mock_cors:
        mock_db.command.return_value = True
        app = create_app()
        app.config['MONGO_URI'] = 'mongodb://custom:27017/db'
        assert app.config['MONGO_URI'] == 'mongodb://custom:27017/db'
        mock_cors.assert_called_once() 