import uuid
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class OrderService:
    def __init__(self):
        self.orders = {}  # In-memory storage for demo purposes
    
    def validate_order_data(self, order_data):
        """Validate order data"""
        errors = []
        
        # Check if order_data exists
        if not order_data:
            errors.append("Order data is required")
            return {'valid': False, 'errors': errors}
        
        # Validate product data
        if 'product' not in order_data:
            errors.append("Product information is required")
        else:
            product = order_data['product']
            required_product_fields = ['name', 'basePrice', 'selectedColor', 'selectedRam', 'selectedStorage', 'finalPrice']
            for field in required_product_fields:
                if field not in product:
                    errors.append(f"Product {field} is required")
        
        # Validate customer data
        if 'customer' not in order_data:
            errors.append("Customer information is required")
        else:
            customer = order_data['customer']
            required_customer_fields = ['firstName', 'lastName', 'address', 'city', 'mobile', 'zipCode']
            for field in required_customer_fields:
                if field not in customer or not customer[field].strip():
                    errors.append(f"Customer {field} is required")
            
            # Validate email format if provided
            if customer.get('email') and '@' not in customer['email']:
                errors.append("Invalid email format")
        
        return {'valid': len(errors) == 0, 'errors': errors}
    
    def process_order(self, order_data):
        """Process the order and generate order ID"""
        try:
            # Generate unique order ID
            order_id = str(uuid.uuid4())[:8].upper()
            
            # Create order record
            order_record = {
                'order_id': order_id,
                'created_at': datetime.now().isoformat(),
                'status': 'pending',
                'product': order_data['product'],
                'customer': order_data['customer'],
                'order_date': order_data.get('orderDate', datetime.now().isoformat())
            }
            
            # Store order (in production, this would be saved to database)
            self.orders[order_id] = order_record
            
            logger.info(f"Order {order_id} processed successfully")
            
            return {
                'success': True,
                'order_id': order_id,
                'message': 'Order processed successfully'
            }
            
        except Exception as e:
            logger.error(f"Error processing order: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to process order'
            }
    
    def get_order(self, order_id):
        """Get order by ID"""
        return self.orders.get(order_id)
    
    def get_all_orders(self):
        """Get all orders"""
        return list(self.orders.values())
    
    def update_order_status(self, order_id, status):
        """Update order status"""
        if order_id in self.orders:
            self.orders[order_id]['status'] = status
            self.orders[order_id]['updated_at'] = datetime.now().isoformat()
            return True
        return False
