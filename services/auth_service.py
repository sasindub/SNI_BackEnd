import bcrypt
import logging
from functools import wraps
from flask import session, jsonify

logger = logging.getLogger(__name__)

class AuthService:
    def __init__(self, db_service):
        """Initialize auth service with database connection"""
        self.db_service = db_service
        self.admin_users = db_service.get_collection('admin_users')
    
    def authenticate_admin(self, username, password):
        """Authenticate admin user"""
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
            
            # Return success with user info (without password)
            return {
                'success': True,
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
    
    def create_session(self, user_data):
        """Create user session"""
        try:
            session['user'] = user_data
            session['authenticated'] = True
            return True
        except Exception as e:
            logger.error(f"Error creating session: {str(e)}")
            return False
    
    def destroy_session(self):
        """Destroy user session"""
        try:
            session.clear()
            return True
        except Exception as e:
            logger.error(f"Error destroying session: {str(e)}")
            return False
    
    def is_authenticated(self):
        """Check if user is authenticated"""
        return session.get('authenticated', False)
    
    def get_current_user(self):
        """Get current user from session"""
        return session.get('user', None)

def require_auth(f):
    """Decorator to require authentication for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('authenticated', False):
            return jsonify({
                'success': False,
                'error': 'Authentication required'
            }), 401
        return f(*args, **kwargs)
    return decorated_function



