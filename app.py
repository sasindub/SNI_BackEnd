from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_session import Session
from werkzeug.middleware.proxy_fix import ProxyFix
from config import Config
from services.email_service import EmailService
from services.order_service import OrderService
from services.database_service import DatabaseService
from services.warranty_service import WarrantyService
from services.auth_service import AuthService, require_auth
from services.token_auth_service import TokenAuthService, require_token_auth
from services.hybrid_auth import require_hybrid_auth
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Fix for Railway's reverse proxy
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# Initialize session
Session(app)

# Enable CORS - simplified and more permissive
CORS(app, 
     origins=[
         "http://localhost:3000",
         "http://localhost:5000",
         "https://snibackend-production.up.railway.app",
         "http://snibackend-production.up.railway.app",
         "https://www.snl.lk",
         "http://www.snl.lk",
         "https://snl.lk",
         "http://snl.lk"
     ],
     supports_credentials=True,
     allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     expose_headers=["Content-Type", "Authorization"])

# Initialize services
email_service = EmailService()
order_service = OrderService()

# Initialize database and related services
db_service = None
warranty_service = None
auth_service = None
token_auth_service = None

def initialize_services():
    global db_service, warranty_service, auth_service, token_auth_service
    try:
        config = Config()
        db_service = DatabaseService(config)
        warranty_service = WarrantyService(db_service)
        auth_service = AuthService(db_service)
        token_auth_service = TokenAuthService(db_service, config.SECRET_KEY)
        logger.info("All services initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize services: {str(e)}")
        logger.error("Backend will run in limited mode - warranty features will be unavailable")
        return False

# Try to initialize services
try:
    initialize_services()
except:
    logger.warning("Services initialization deferred")

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'SNI Laptops API is running',
        'version': '1.0.0'
    })

@app.route('/api/orders', methods=['POST'])
def create_order():
    """Create a new order and send confirmation emails"""
    try:
        # Get order data from request
        order_data = request.get_json()
        
        if not order_data:
            return jsonify({
                'success': False,
                'message': 'No order data provided'
            }), 400
        
        # Validate required fields
        validation_result = order_service.validate_order_data(order_data)
        if not validation_result['valid']:
            return jsonify({
                'success': False,
                'message': 'Validation failed',
                'errors': validation_result['errors']
            }), 400
        
        # Process the order
        order_result = order_service.process_order(order_data)
        
        if order_result['success']:
            # Send confirmation email to customer
            customer_email_result = email_service.send_order_confirmation(
                order_data['customer'],
                order_data['product'],
                order_result['order_id']
            )
            
            # Send notification email to admin
            admin_email_result = email_service.send_admin_notification(
                order_data['customer'],
                order_data['product'],
                order_result['order_id']
            )
            
            return jsonify({
                'success': True,
                'message': 'Order created successfully',
                'order_id': order_result['order_id'],
                'customer_email_sent': customer_email_result['success'],
                'admin_email_sent': admin_email_result['success']
            }), 201
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to process order',
                'error': order_result['error']
            }), 500
            
    except Exception as e:
        logger.error(f"Error creating order: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error',
            'error': str(e)
        }), 500

@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    """Admin login endpoint - supports both session and token auth"""
    try:
        if not auth_service or not token_auth_service:
            return jsonify({
                'success': False,
                'message': 'Authentication service not available'
            }), 503
        
        credentials = request.get_json()
        
        if not credentials or 'username' not in credentials or 'password' not in credentials:
            return jsonify({
                'success': False,
                'message': 'Username and password are required'
            }), 400
        
        # Check if client wants token auth (for cross-origin)
        use_token = request.headers.get('X-Auth-Type') == 'token'
        
        if use_token:
            # Token-based auth for cross-origin
            auth_result = token_auth_service.authenticate_admin(
                credentials['username'],
                credentials['password']
            )
            
            if auth_result['success']:
                return jsonify({
                    'success': True,
                    'message': auth_result['message'],
                    'token': auth_result['token'],
                    'user': auth_result['user']
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'message': auth_result['error']
                }), 401
        else:
            # Session-based auth (original)
            auth_result = auth_service.authenticate_admin(
                credentials['username'],
                credentials['password']
            )
            
            if auth_result['success']:
                # Create session
                auth_service.create_session(auth_result['user'])
                
                return jsonify({
                    'success': True,
                    'message': auth_result['message'],
                    'user': auth_result['user']
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'message': auth_result['error']
                }), 401
            
    except Exception as e:
        logger.error(f"Error during admin login: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error',
            'error': str(e)
        }), 500

@app.route('/api/admin/logout', methods=['POST'])
@require_auth
def admin_logout():
    """Admin logout endpoint"""
    try:
        if not auth_service:
            return jsonify({
                'success': False,
                'message': 'Authentication service not available'
            }), 503
        
        auth_service.destroy_session()
        
        return jsonify({
            'success': True,
            'message': 'Logout successful'
        }), 200
            
    except Exception as e:
        logger.error(f"Error during admin logout: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error',
            'error': str(e)
        }), 500

@app.route('/api/admin/check-auth', methods=['GET'])
def check_auth():
    """Check if user is authenticated - supports both session and token"""
    try:
        if not auth_service or not token_auth_service:
            return jsonify({
                'success': False,
                'authenticated': False,
                'message': 'Authentication service not available'
            }), 503
        
        # Check for token auth first
        token = token_auth_service.get_token_from_request()
        if token:
            result = token_auth_service.verify_token(token)
            return jsonify({
                'success': True,
                'authenticated': result['success'],
                'user': result.get('user') if result['success'] else None
            }), 200
        
        # Fall back to session auth
        is_authenticated = auth_service.is_authenticated()
        current_user = auth_service.get_current_user() if is_authenticated else None
        
        return jsonify({
            'success': True,
            'authenticated': is_authenticated,
            'user': current_user
        }), 200
            
    except Exception as e:
        logger.error(f"Error checking authentication: {str(e)}")
        return jsonify({
            'success': False,
            'authenticated': False,
            'message': 'Internal server error',
            'error': str(e)
        }), 500

@app.route('/api/warranties', methods=['GET'])
@require_hybrid_auth
def get_warranties():
    """Get all warranty records"""
    try:
        if not warranty_service:
            return jsonify({
                'success': False,
                'message': 'Warranty service not available'
            }), 503
        
        result = warranty_service.get_all_warranties()
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 500
            
    except Exception as e:
        logger.error(f"Error fetching warranties: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error',
            'error': str(e)
        }), 500

@app.route('/api/warranties/<serial_number>', methods=['GET'])
@require_hybrid_auth
def get_warranty(serial_number):
    """Get warranty by serial number"""
    try:
        if not warranty_service:
            return jsonify({
                'success': False,
                'message': 'Warranty service not available'
            }), 503
        
        result = warranty_service.get_warranty_by_serial(serial_number)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 404
            
    except Exception as e:
        logger.error(f"Error fetching warranty: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error',
            'error': str(e)
        }), 500

@app.route('/api/warranties', methods=['POST'])
@require_hybrid_auth
def create_warranty():
    """Create a new warranty record"""
    try:
        if not warranty_service:
            return jsonify({
                'success': False,
                'message': 'Warranty service not available'
            }), 503
        
        warranty_data = request.get_json()
        
        if not warranty_data:
            return jsonify({
                'success': False,
                'message': 'No warranty data provided'
            }), 400
        
        result = warranty_service.create_warranty(warranty_data)
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Error creating warranty: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error',
            'error': str(e)
        }), 500

@app.route('/api/warranties/<warranty_id>', methods=['PUT'])
@require_hybrid_auth
def update_warranty(warranty_id):
    """Update an existing warranty record"""
    try:
        if not warranty_service:
            return jsonify({
                'success': False,
                'message': 'Warranty service not available'
            }), 503
        
        warranty_data = request.get_json()
        
        if not warranty_data:
            return jsonify({
                'success': False,
                'message': 'No warranty data provided'
            }), 400
        
        result = warranty_service.update_warranty(warranty_id, warranty_data)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Error updating warranty: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error',
            'error': str(e)
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'message': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'message': 'Internal server error'
    }), 500

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=app.config['PORT'],
        debug=app.config['DEBUG']
    )
