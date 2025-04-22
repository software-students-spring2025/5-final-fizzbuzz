from flask import Flask
from flask_pymongo import PyMongo
from flask_cors import CORS
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize MongoDB connection
mongo = PyMongo()

def create_app():
    # Initialize Flask app
    app = Flask(__name__)
    
    # Enable CORS
    CORS(app)
    
    # Configure MongoDB
    app.config["MONGO_URI"] = os.environ.get("MONGO_URI", "mongodb://localhost:27017/finance_tracker")
    
    # Initialize extensions
    mongo.init_app(app)
    
    # Import and register blueprints
    from app.routes import main_bp
    app.register_blueprint(main_bp)
    
    return app