"""
Simple admin routes with JWT authentication
"""

from flask import Blueprint, request, jsonify
from simple_admin_auth import admin_login, require_token
from services.warranty_service import WarrantyService
from services.database_service import DatabaseService
from config import Config

# Create blueprint
admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

# Initialize services
config = Config()
db_service = DatabaseService(config)
warranty_service = WarrantyService(db_service)

@admin_bp.route('/login', methods=['POST', 'OPTIONS'])
def login():
    """Admin login - returns JWT token"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        if not data or 'username' not in data or 'password' not in data:
            return jsonify({'success': False, 'message': 'Username and password required'}), 400
        
        result = admin_login(data['username'], data['password'])
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 401
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@admin_bp.route('/verify', methods=['GET', 'OPTIONS'])
def verify():
    """Verify if token is valid"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': True, 'authenticated': False}), 200
        
        token = auth_header.split(' ')[1]
        from simple_admin_auth import verify_token
        result = verify_token(token)
        
        return jsonify({
            'success': True,
            'authenticated': result['valid'],
            'user': {'username': result.get('username')} if result['valid'] else None
        }), 200
    except Exception as e:
        return jsonify({'success': True, 'authenticated': False}), 200

@admin_bp.route('/warranties', methods=['GET', 'OPTIONS'])
@require_token
def get_warranties():
    """Get all warranties"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        result = warranty_service.get_all_warranties()
        return jsonify(result), 200 if result['success'] else 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/warranties', methods=['POST', 'OPTIONS'])
@require_token
def create_warranty():
    """Create warranty"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        result = warranty_service.create_warranty(data)
        return jsonify(result), 201 if result['success'] else 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/warranties/<warranty_id>', methods=['PUT', 'OPTIONS'])
@require_token
def update_warranty(warranty_id):
    """Update warranty"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        result = warranty_service.update_warranty(warranty_id, data)
        return jsonify(result), 200 if result['success'] else 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

