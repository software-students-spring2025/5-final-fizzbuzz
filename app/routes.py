from flask import Blueprint, request, jsonify, current_app, render_template, send_from_directory, redirect, url_for, session
from app.models import User, Transaction
from app import mongo
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from bson import ObjectId
import logging
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from functools import wraps

logger = logging.getLogger(__name__)

main_bp = Blueprint('main', __name__)

def handle_db_error(e):
    """Handle database connection errors"""
    if isinstance(e, (ConnectionFailure, ServerSelectionTimeoutError)):
        logger.error(f"Database connection error: {str(e)}")
        return jsonify({
            "error": "Database connection error",
            "message": "Unable to connect to database"
        }), 503
    logger.error(f"Database error: {str(e)}")
    return jsonify({
        "error": "Database error",
        "message": str(e)
    }), 500

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return decorated_function

@main_bp.route('/')
@login_required
def index():
    return redirect(url_for('main.dashboard'))

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        try:
            user = User.login(email, password)
            if user:
                session['user_id'] = str(user['_id'])
                session['username'] = user.get('name', email.split('@')[0])
                return redirect(url_for('main.dashboard'))
            return render_template('login.html', error="Invalid email or password")
        except Exception as e:
            return render_template('login.html', error="An error occurred. Please try again.")
    
    return render_template('login.html')

@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate input
        if not all([username, email, password, confirm_password]):
            return render_template('register.html', error="All fields are required")
        
        if password != confirm_password:
            return render_template('register.html', error="Passwords do not match")
        
        try:
            if User.get_by_email(email):
                return render_template('register.html', error="Email already registered")
            
            user = User.create(username, email, password)
            if user:
                session['user_id'] = str(user['_id'])
                session['username'] = username
                return redirect(url_for('main.dashboard'))
            return render_template('register.html', error="Failed to create account")
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            return render_template('register.html', error="An error occurred. Please try again.")
    
    return render_template('register.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@main_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.login'))

@main_bp.route('/api/health')
def health_check():
    try:
        mongo.db.command('ping')
        return jsonify({
            "status": "healthy",
            "database": "connected"
        })
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            "status": "healthy",
            "database": "disconnected"
        })

@main_bp.route('/api/transactions', methods=['GET', 'POST'])
@login_required
def handle_transactions():
    if request.method == 'GET':
        try:
            logger.info(f"Fetching transactions for user {session['user_id']}")
            transactions = Transaction.get_by_user(ObjectId(session['user_id']))
            logger.info(f"Found {len(transactions)} transactions")
            
            formatted_transactions = []
            for transaction in transactions:
                formatted_transaction = {
                    '_id': str(transaction['_id']),
                    'description': transaction['description'],
                    'amount': transaction['amount'],
                    'category': transaction['category'],
                    'type': transaction['type'],
                    'date': transaction['date'].isoformat() if isinstance(transaction['date'], datetime) else transaction['date']
                }
                formatted_transactions.append(formatted_transaction)
            
            return jsonify(formatted_transactions)
        except Exception as e:
            logger.error(f"Error fetching transactions: {str(e)}")
            return jsonify({'error': str(e)}), 500

    if request.method == 'POST':
        try:
            data = request.json
            logger.info(f"Creating transaction: {data}")
            
            # Validate required fields
            required_fields = ['description', 'amount', 'category', 'type', 'date']
            if not all(field in data for field in required_fields):
                return jsonify({'error': 'Missing required fields'}), 400
            
            # Prepare transaction data
            transaction_data = {
                'description': data['description'],
                'amount': float(data['amount']),
                'category': data['category'],
                'type': data['type'],
                'date': datetime.strptime(data['date'], '%Y-%m-%d'),
                'user_id': ObjectId(session['user_id'])
            }
            
            # Create transaction
            result = Transaction.create(transaction_data)
            logger.info(f"Transaction created: {result}")
            
            return jsonify(result), 201
        except ValueError as e:
            logger.error(f"Validation error: {str(e)}")
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            logger.error(f"Error creating transaction: {str(e)}")
            return jsonify({'error': str(e)}), 500

@main_bp.route('/api/transactions/<transaction_id>', methods=['DELETE'])
@login_required
def delete_transaction(transaction_id):
    try:
        result = Transaction.delete(ObjectId(transaction_id), ObjectId(session['user_id']))
        if result:
            return '', 204
        return jsonify({'error': 'Transaction not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main_bp.route('/api/analytics/monthly')
@login_required
def get_monthly_analytics():
    try:
        pipeline = [
            {'$match': {'user_id': ObjectId(session['user_id'])}},
            {'$group': {
                '_id': {
                    'year': {'$year': '$date'},
                    'month': {'$month': '$date'}
                },
                'total': {'$sum': '$amount'}
            }},
            {'$sort': {'_id.year': 1, '_id.month': 1}}
        ]
        
        result = Transaction.aggregate(pipeline)
        return jsonify(list(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main_bp.route('/api/analytics/categories')
@login_required
def get_category_analytics():
    try:
        pipeline = [
            {'$match': {'user_id': ObjectId(session['user_id'])}},
            {'$group': {
                '_id': '$category',
                'total': {'$sum': '$amount'}
            }},
            {'$sort': {'total': -1}}
        ]
        
        result = Transaction.aggregate(pipeline)
        return jsonify(list(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main_bp.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)