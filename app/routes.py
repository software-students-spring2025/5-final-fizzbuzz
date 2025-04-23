from flask import Blueprint, request, jsonify, current_app, render_template, send_from_directory
from app.models import User, Transaction
from app import mongo
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    try:
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Error rendering template: {str(e)}")
        return str(e), 500

@main_bp.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

@main_bp.route('/api/health', methods=['GET'])
def health_check():
    try:
        mongo.db.command('ping')
        return jsonify({
            "status": "healthy",
            "database": "connected"
        })
    except Exception as e:
        return jsonify({
            "status": "healthy",
            "database": "disconnected",
            "message": str(e)
        })

@main_bp.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        # Check if user already exists
        if mongo.db.users.find_one({"username": data.get('username')}):
            return jsonify({"error": "Username already exists"}), 400
        
        # Create new user
        user = User(
            username=data.get('username'),
            email=data.get('email'),
            password_hash=generate_password_hash(data.get('password')),
            university=data.get('university'),
            monthly_income=data.get('monthly_income', 0)
        )
        
        result = mongo.db.users.insert_one(user.to_dict())
        return jsonify({"message": "User created successfully", "user_id": str(result.inserted_id)}), 201
    except Exception as e:
        logger.error(f"Error registering user: {str(e)}")
        return jsonify({
            "error": "Database error",
            "message": str(e)
        }), 503

@main_bp.route('/api/transactions', methods=['GET'])
def get_transactions():
    try:
        transactions = list(mongo.db.transactions.find())
        for transaction in transactions:
            transaction['_id'] = str(transaction['_id'])
        return jsonify(transactions)
    except Exception as e:
        logger.error(f"Error fetching transactions: {str(e)}")
        return jsonify({
            "error": "Database error",
            "message": str(e)
        }), 503

@main_bp.route('/api/transactions', methods=['POST'])
def add_transaction():
    try:
        data = request.json
        transaction = Transaction(
            amount=data.get('amount'),
            category=data.get('category'),
            description=data.get('description')
        )
        result = mongo.db.transactions.insert_one(transaction.to_dict())
        return jsonify({'id': str(result.inserted_id)}), 201
    except Exception as e:
        logger.error(f"Error adding transaction: {str(e)}")
        return jsonify({
            "error": "Database error",
            "message": str(e)
        }), 503

@main_bp.route('/api/transactions/<id>', methods=['DELETE'])
def delete_transaction(id):
    try:
        result = mongo.db.transactions.delete_one({'_id': ObjectId(id)})
        if result.deleted_count:
            return '', 204
        return jsonify({"error": "Transaction not found"}), 404
    except Exception as e:
        logger.error(f"Error deleting transaction: {str(e)}")
        return jsonify({
            "error": "Database error",
            "message": str(e)
        }), 503

@main_bp.route('/api/analytics/monthly', methods=['GET'])
def get_monthly_analytics():
    try:
        pipeline = [
            {
                '$group': {
                    '_id': {
                        'year': {'$year': '$date'},
                        'month': {'$month': '$date'}
                    },
                    'total': {'$sum': '$amount'},
                    'count': {'$sum': 1}
                }
            },
            {'$sort': {'_id.year': -1, '_id.month': -1}}
        ]
        analytics = list(mongo.db.transactions.aggregate(pipeline))
        return jsonify(analytics)
    except Exception as e:
        logger.error(f"Error fetching monthly analytics: {str(e)}")
        return jsonify({
            "error": "Database error",
            "message": str(e)
        }), 503

@main_bp.route('/api/analytics/categories', methods=['GET'])
def get_category_analytics():
    try:
        pipeline = [
            {
                '$group': {
                    '_id': '$category',
                    'total': {'$sum': '$amount'},
                    'count': {'$sum': 1}
                }
            },
            {'$sort': {'total': -1}}
        ]
        analytics = list(mongo.db.transactions.aggregate(pipeline))
        return jsonify(analytics)
    except Exception as e:
        logger.error(f"Error fetching category analytics: {str(e)}")
        return jsonify({
            "error": "Database error",
            "message": str(e)
        }), 503