from flask import Flask, request, jsonify
from flask_cors import CORS
from config import Config
from services.email_service import EmailService
from services.order_service import OrderService
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Enable CORS for all origins
CORS(app, origins=['*'])

# Initialize services
email_service = EmailService()
order_service = OrderService()

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
