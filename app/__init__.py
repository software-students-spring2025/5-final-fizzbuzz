from flask import Flask
from flask_pymongo import PyMongo
from flask_cors import CORS
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize PyMongo without app
mongo = PyMongo()

def create_app():
    # Initialize Flask app
    app = Flask(__name__,
                static_url_path='',
                static_folder='static',
                template_folder='templates')
    
    # Enable debug mode and template auto-reload
    app.config['DEBUG'] = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    
    # Enable CORS
    CORS(app)
    
    # MongoDB Configuration
    mongodb_uri = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/fizzbuzz')
    app.config['MONGO_URI'] = mongodb_uri
    
    try:
        # Initialize mongo with app
        mongo.init_app(app)
        logger.info(f"Successfully connected to MongoDB at {mongodb_uri}")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {str(e)}")
        raise
    
    # Register blueprints
    from app.routes import main_bp
    app.register_blueprint(main_bp)
    
    return app

