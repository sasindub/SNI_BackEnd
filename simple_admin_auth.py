"""
Simple JWT-based admin authentication
No sessions, no cookies - just tokens!
"""

import jwt
import bcrypt
import datetime
from functools import wraps
from flask import request, jsonify
from services.database_service import DatabaseService
from config import Config

# Initialize once
config = Config()
db_service = DatabaseService(config)
admin_users = db_service.get_collection('admin_users')

SECRET_KEY = config.SECRET_KEY

def create_token(username):
    """Create JWT token"""
    payload = {
        'username': username,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)  # 7 days expiry
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def verify_token(token):
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return {'valid': True, 'username': payload['username']}
    except jwt.ExpiredSignatureError:
        return {'valid': False, 'error': 'Token expired'}
    except jwt.InvalidTokenError:
        return {'valid': False, 'error': 'Invalid token'}

def admin_login(username, password):
    """Authenticate admin and return token"""
    try:
        # Find user
        user = admin_users.find_one({'username': username})
        if not user:
            return {'success': False, 'message': 'Invalid credentials'}
        
        # Check password
        if bcrypt.checkpw(password.encode('utf-8'), user['password']):
            token = create_token(username)
            return {
                'success': True,
                'token': token,
                'user': {'username': username}
            }
        else:
            return {'success': False, 'message': 'Invalid credentials'}
    except Exception as e:
        return {'success': False, 'message': str(e)}

def require_token(f):
    """Decorator to require token authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'error': 'No token provided'}), 401
        
        token = auth_header.split(' ')[1]
        result = verify_token(token)
        
        if not result['valid']:
            return jsonify({'success': False, 'error': result.get('error', 'Invalid token')}), 401
        
        return f(*args, **kwargs)
    return decorated

