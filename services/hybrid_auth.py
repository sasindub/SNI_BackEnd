"""
Hybrid authentication that supports both session and token auth
"""

from functools import wraps
from flask import session, request, jsonify
import logging

logger = logging.getLogger(__name__)

def require_hybrid_auth(f):
    """Decorator that accepts both session and token authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Import here to avoid circular imports
        from app import token_auth_service
        
        # Try token auth first
        if token_auth_service:
            token = token_auth_service.get_token_from_request()
            if token:
                result = token_auth_service.verify_token(token)
                if result['success']:
                    request.current_user = result['user']
                    return f(*args, **kwargs)
                elif token:  # Token provided but invalid
                    return jsonify({
                        'success': False,
                        'error': 'Invalid or expired token'
                    }), 401
        
        # Fall back to session auth
        if session.get('authenticated', False):
            request.current_user = session.get('user')
            return f(*args, **kwargs)
        
        # Neither auth method succeeded
        return jsonify({
            'success': False,
            'error': 'Authentication required'
        }), 401
        
    return decorated_function

