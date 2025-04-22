from flask import Blueprint, request, jsonify
from app.models import User, Transaction
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

main_bp = Blueprint('main', __name__)

@main_bp.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"})

@main_bp.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    
    required_fields = ['username', 'email', 'password']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    # Check if user already exists
    if User.find_by_username(data.get('username')):
        return jsonify({"error": "Username already exists"}), 400
    
    # Create password hash
    password_hash = generate_password_hash(data.get('password'))
    
    # Create new user
    user_id = User.create(
        username=data.get('username'),
        email=data.get('email'),
        password_hash=password_hash,
        university=data.get('university'),
        monthly_income=data.get('monthly_income', 0)
    )
    
    return jsonify({"message": "User created successfully", "user_id": user_id}), 201

@main_bp.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data.get('username') or not data.get('password'):
        return jsonify({"error": "Username and password are required"}), 400
        
    user = User.find_by_username(data.get('username'))
    if not user:
        return jsonify({"error": "Invalid username or password"}), 401
        
    if not check_password_hash(user['password_hash'], data.get('password')):
        return jsonify({"error": "Invalid username or password"}), 401
    
    return jsonify({
        "message": "Login successful",
        "user_id": str(user['_id']),
        "username": user['username']
    })

@main_bp.route('/api/transactions', methods=['GET'])
def get_transactions():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"error": "User ID is required"}), 400
    
    transactions = Transaction.get_by_user(user_id)
    return jsonify({"transactions": transactions})

@main_bp.route('/api/transactions', methods=['POST'])
def create_transaction():
    data = request.get_json()
    
    required_fields = ['user_id', 'amount', 'type', 'category_id', 'description']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    transaction_id = Transaction.create(
        user_id=data.get('user_id'),
        amount=data.get('amount'),
        type=data.get('type'),
        category_id=data.get('category_id'),
        description=data.get('description'),
        date=data.get('date')
    )
    
    return jsonify({"message": "Transaction created", "transaction_id": transaction_id}), 201