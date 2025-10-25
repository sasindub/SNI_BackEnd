"""
Token-based authentication service for cross-origin support
"""

import jwt
import datetime
import logging
from functools import wraps
from flask import request, jsonify
import bcrypt

logger = logging.getLogger(__name__)

class TokenAuthService:
    def __init__(self, db_service, secret_key):
        """Initialize token auth service"""
        self.db_service = db_service
        self.admin_users = db_service.get_collection('admin_users')
        self.secret_key = secret_key
    
    def authenticate_admin(self, username, password):
        """Authenticate admin and return JWT token"""
        try:
            # Find admin user
            admin_user = self.admin_users.find_one({'username': username})
            
            if not admin_user:
                return {
                    'success': False,
                    'error': 'Invalid username or password'
                }
            
            # Verify password
            password_match = bcrypt.checkpw(
                password.encode('utf-8'),
                admin_user['password']
            )
            
            if not password_match:
                return {
                    'success': False,
                    'error': 'Invalid username or password'
                }
            
            # Generate JWT token
            token = jwt.encode({
                'username': admin_user['username'],
                'role': admin_user.get('role', 'admin'),
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
            }, self.secret_key, algorithm='HS256')
            
            return {
                'success': True,
                'token': token,
                'user': {
                    'username': admin_user['username'],
                    'role': admin_user.get('role', 'admin')
                },
                'message': 'Login successful'
            }
        except Exception as e:
            logger.error(f"Error authenticating admin: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def verify_token(self, token):
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return {
                'success': True,
                'user': {
                    'username': payload['username'],
                    'role': payload.get('role', 'admin')
                }
            }
        except jwt.ExpiredSignatureError:
            return {
                'success': False,
                'error': 'Token has expired'
            }
        except jwt.InvalidTokenError:
            return {
                'success': False,
                'error': 'Invalid token'
            }
    
    def get_token_from_request(self):
        """Extract token from Authorization header"""
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            return auth_header.split(' ')[1]
        return None

def require_token_auth(token_service):
    """Decorator to require token authentication"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = token_service.get_token_from_request()
            
            if not token:
                return jsonify({
                    'success': False,
                    'error': 'No authentication token provided'
                }), 401
            
            result = token_service.verify_token(token)
            
            if not result['success']:
                return jsonify({
                    'success': False,
                    'error': result['error']
                }), 401
            
            # Attach user info to request
            request.current_user = result['user']
            return f(*args, **kwargs)
        return decorated_function
    return decorator

