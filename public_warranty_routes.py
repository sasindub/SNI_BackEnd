"""
Public warranty checker routes - NO AUTHENTICATION REQUIRED
For customers to check their warranty status
"""

from flask import Blueprint, request, jsonify

# Create blueprint
warranty_public_bp = Blueprint('warranty_public', __name__, url_prefix='/api/warranty')

# Global variables - lazy initialization
_warranty_service = None

def get_warranty_service():
    """Lazy initialization of warranty service"""
    global _warranty_service
    if _warranty_service is None:
        from services.warranty_service import WarrantyService
        from services.database_service import DatabaseService
        from config import Config
        config = Config()
        db_service = DatabaseService(config)
        _warranty_service = WarrantyService(db_service)
    return _warranty_service

@warranty_public_bp.route('/check', methods=['POST', 'OPTIONS'])
def check_warranty():
    """Check if warranty exists by serial number - PUBLIC endpoint"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        
        if not data or 'serial_number' not in data:
            return jsonify({
                'success': False,
                'message': 'Serial number is required'
            }), 400
        
        serial_number = data['serial_number'].strip()
        
        if not serial_number:
            return jsonify({
                'success': False,
                'message': 'Serial number cannot be empty'
            }), 400
        
        # Get warranty by serial number
        warranty_service = get_warranty_service()
        result = warranty_service.get_warranty_by_serial(serial_number)
        
        if not result['success']:
            return jsonify({
                'success': False,
                'message': f'Serial number not found',
                'found': False
            }), 404
        
        warranty = result['warranty']
        
        # Check if warranty is active or expired (both can view details)
        if warranty['warranty_status'] not in ['Active', 'Expired']:
            return jsonify({
                'success': False,
                'message': f'Warranty is not active for serial number {serial_number}',
                'found': True,
                'status': warranty['warranty_status'],
                'requires_passcode': False
            }), 200
        
        # Warranty exists and is active/expired - ask for passcode
        return jsonify({
            'success': True,
            'message': 'Warranty found. Please enter passcode to view details.',
            'found': True,
            'status': warranty['warranty_status'],
            'requires_passcode': True,
            'serial_number': serial_number
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'An error occurred while checking warranty',
            'error': str(e)
        }), 500

@warranty_public_bp.route('/verify', methods=['POST', 'OPTIONS'])
def verify_passcode():
    """Verify passcode and return warranty details - PUBLIC endpoint"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        
        if not data or 'serial_number' not in data or 'passcode' not in data:
            return jsonify({
                'success': False,
                'message': 'Serial number and passcode are required'
            }), 400
        
        serial_number = data['serial_number'].strip()
        passcode = data['passcode']
        
        # Get warranty by serial number
        warranty_service = get_warranty_service()
        result = warranty_service.get_warranty_by_serial(serial_number)
        
        if not result['success']:
            return jsonify({
                'success': False,
                'message': 'Serial number not found'
            }), 404
        
        warranty = result['warranty']
        
        # Verify passcode
        if warranty.get('passcode') != passcode:
            return jsonify({
                'success': False,
                'message': 'Invalid passcode'
            }), 401
        
        # Passcode is correct - return warranty details
        return jsonify({
            'success': True,
            'message': 'Warranty details retrieved successfully',
            'warranty': {
                'serial_number': warranty['serial_number'],
                'windows_key': warranty.get('windows_key', 'N/A'),
                'warranty_start_date': warranty.get('warranty_start_date'),
                'warranty_end_date': warranty.get('warranty_end_date'),
                'warranty_status': warranty['warranty_status'],
                'nic_number': warranty.get('nic_number', 'N/A')
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'An error occurred while verifying passcode',
            'error': str(e)
        }), 500

