"""
Order routes for handling order submissions
"""

from flask import Blueprint, request, jsonify
import logging
from services.order_service import OrderService
from services.email_service import EmailService

logger = logging.getLogger(__name__)

# Create blueprint
order_bp = Blueprint('orders', __name__, url_prefix='/api/orders')

# Lazy initialization
_order_service = None
_email_service = None

def get_order_service():
    global _order_service
    if _order_service is None:
        _order_service = OrderService()
    return _order_service

def get_email_service():
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service

@order_bp.route('', methods=['POST', 'OPTIONS'])
def create_order():
    """Create a new order and send confirmation emails"""
    
    if request.method == 'OPTIONS':
        response = jsonify({'success': True})
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response, 200
    
    try:
        # Get order data from request
        order_data = request.get_json()
        
        if not order_data:
            return jsonify({
                'success': False,
                'message': 'No order data provided'
            }), 400
        
        logger.info(f"Received order: {order_data.get('product', {}).get('name', 'Unknown')}")
        
        # Initialize services
        order_service = get_order_service()
        email_service = get_email_service()
        
        # Validate order data
        validation_result = order_service.validate_order_data(order_data)
        
        if not validation_result['valid']:
            logger.warning(f"Order validation failed: {validation_result['errors']}")
            return jsonify({
                'success': False,
                'message': 'Invalid order data',
                'errors': validation_result['errors']
            }), 400
        
        # Process the order
        order_result = order_service.process_order(order_data)
        
        if not order_result['success']:
            logger.error(f"Order processing failed: {order_result.get('message')}")
            return jsonify({
                'success': False,
                'message': order_result.get('message', 'Failed to process order')
            }), 500
        
        order_id = order_result['order_id']
        logger.info(f"Order {order_id} processed successfully")
        
        # Send confirmation email to customer (if email provided)
        customer_data = order_data['customer']
        product_data = order_data['product']
        
        email_results = {
            'customer_email': {'success': False, 'message': 'Not sent'},
            'admin_email': {'success': False, 'message': 'Not sent'}
        }
        
        if customer_data.get('email'):
            customer_email_result = email_service.send_order_confirmation(
                customer_data, 
                product_data, 
                order_id
            )
            email_results['customer_email'] = customer_email_result
            logger.info(f"Customer email result: {customer_email_result}")
        else:
            logger.info("No customer email provided, skipping customer notification")
        
        # Send notification email to admin
        admin_email_result = email_service.send_admin_notification(
            customer_data, 
            product_data, 
            order_id
        )
        email_results['admin_email'] = admin_email_result
        logger.info(f"Admin email result: {admin_email_result}")
        
        # Return success response
        return jsonify({
            'success': True,
            'message': 'Order placed successfully',
            'order_id': order_id,
            'email_status': email_results
        }), 200
        
    except Exception as e:
        logger.error(f"Error creating order: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'Failed to create order: {str(e)}'
        }), 500

@order_bp.route('/<order_id>', methods=['GET', 'OPTIONS'])
def get_order(order_id):
    """Get order by ID"""
    
    if request.method == 'OPTIONS':
        response = jsonify({'success': True})
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response, 200
    
    try:
        order_service = get_order_service()
        order = order_service.get_order(order_id)
        
        if order:
            return jsonify({
                'success': True,
                'order': order
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Order not found'
            }), 404
            
    except Exception as e:
        logger.error(f"Error getting order: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@order_bp.route('', methods=['GET', 'OPTIONS'])
def get_all_orders():
    """Get all orders"""
    
    if request.method == 'OPTIONS':
        response = jsonify({'success': True})
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response, 200
    
    try:
        order_service = get_order_service()
        orders = order_service.get_all_orders()
        
        return jsonify({
            'success': True,
            'orders': orders,
            'count': len(orders)
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting orders: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

