from flask import Flask
from flask_pymongo import PyMongo
from flask_cors import CORS
import os
import logging
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize PyMongo without app
mongo = PyMongo()

def create_app(debug=True):
    # Initialize Flask app
    app = Flask(__name__,
                static_url_path='',
                static_folder='static',
                template_folder='templates')
    
    # Enable debug mode and template auto-reload
    app.config['DEBUG'] = debug
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    
    # Enable CORS
    CORS(app)
    
    # Configure MongoDB
    app.config["MONGO_URI"] = os.environ.get("MONGODB_URI", "mongodb://localhost:27017/student_finance")
    
    # Set secret key for session
    app.secret_key = os.environ.get("SECRET_KEY", "your-secret-key-here")
    
    try:
        # Initialize mongo with app
        mongo.init_app(app)
        # Test the connection
        mongo.db.command('ping')
        logger.info(f"Successfully connected to MongoDB at {app.config['MONGO_URI']}")
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        logger.error(f"Failed to connect to MongoDB: {str(e)}")
        # Don't raise the error in development mode
        if not app.config['DEBUG']:
            raise
    except Exception as e:
        logger.error(f"Unexpected error connecting to MongoDB: {str(e)}")
        if not app.config['DEBUG']:
            raise
    
    # Register blueprints
    from app.routes import main_bp
    app.register_blueprint(main_bp)
    
    return app

