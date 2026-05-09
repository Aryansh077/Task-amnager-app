"""
Authentication routes for user registration and login.
"""

from flask import Blueprint, request, jsonify, session
import logging
from app.models.user import User

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user
    Expected JSON: {
        "username": "string",
        "email": "string",
        "password": "string"
    }
    """
    try:
        data = request.get_json()
        
        # Validation
        if not all(key in data for key in ['username', 'email', 'password']):
            return jsonify({'error': 'Missing required fields'}), 400
        
        if len(data['password']) < 6:
            return jsonify({'error': 'Password must be at least 6 characters'}), 400
        
        # Register user
        user = User.register(
            data['username'],
            data['email'],
            data['password']
        )
        
        if user:
            session['user_id'] = user['id']
            return jsonify({
                'message': 'User registered successfully',
                'user': user
            }), 201
        
        return jsonify({'error': 'Registration failed'}), 400
    
    except Exception as e:
        logger.error(f"Registration error: {e}")
        return jsonify({'error': 'Server error'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Login user
    Expected JSON: {
        "username": "string",
        "password": "string"
    }
    """
    try:
        data = request.get_json()
        
        if not all(key in data for key in ['username', 'password']):
            return jsonify({'error': 'Missing username or password'}), 400
        
        # Authenticate user
        user = User.login(data['username'], data['password'])
        
        if user:
            session['user_id'] = user['id']
            return jsonify({
                'message': 'Login successful',
                'user': user
            }), 200
        
        return jsonify({'error': 'Invalid credentials'}), 401
    
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({'error': 'Server error'}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Logout user"""
    try:
        session.clear()
        return jsonify({'message': 'Logged out successfully'}), 200
    except Exception as e:
        logger.error(f"Logout error: {e}")
        return jsonify({'error': 'Server error'}), 500

@auth_bp.route('/user', methods=['GET'])
def get_user():
    """Get current user info"""
    try:
        user_id = session.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'Not authenticated'}), 401
        
        user = User.get_by_id(user_id)
        
        if user:
            return jsonify({'user': user}), 200
        
        return jsonify({'error': 'User not found'}), 404
    
    except Exception as e:
        logger.error(f"Error fetching user: {e}")
        return jsonify({'error': 'Server error'}), 500
