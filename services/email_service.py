import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content
from config import Config
import logging
import os

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        # Get API key from environment or config
        api_key = Config.SENDGRID_API_KEY
        if not api_key:
            logger.warning("SENDGRID_API_KEY is not set. Email functionality will be disabled.")
            logger.warning("To enable emails, set SENDGRID_API_KEY in your .env file or environment variables.")
            self.sg = None
            self.from_email = None
        else:
            self.sg = sendgrid.SendGridAPIClient(api_key=api_key)
            # Use a verified sender email from SendGrid
            self.from_email = Email("sasindub01@gmail.com", Config.FROM_NAME)
    
    def send_order_confirmation(self, customer_data, product_data, order_id):
        """Send order confirmation email to customer"""
        try:
            # Check if SendGrid is configured
            if not self.sg:
                logger.warning("SendGrid not configured, skipping customer email")
                return {'success': False, 'message': 'Email service not configured'}
            
            # Check if customer has email
            if not customer_data.get('email'):
                logger.warning("No customer email provided, skipping email")
                return {'success': False, 'message': 'No customer email provided'}
            
            # Customer email
            to_email = To(customer_data['email'])
            
            # Email content
            subject = f"Order Confirmation - {product_data['name']} - Order #{order_id}"
            
            html_content = self._generate_customer_email_html(customer_data, product_data, order_id)
            text_content = self._generate_customer_email_text(customer_data, product_data, order_id)
            
            # Create mail object
            mail = Mail(
                from_email=self.from_email,
                to_emails=to_email,
                subject=subject,
                html_content=Content("text/html", html_content),
                plain_text_content=Content("text/plain", text_content)
            )
            
            # Send email
            response = self.sg.send(mail)
            
            if response.status_code in [200, 201, 202]:
                logger.info(f"Order confirmation email sent successfully to {customer_data.get('email')}")
                return {'success': True, 'message': 'Email sent successfully'}
            else:
                logger.error(f"Failed to send email. Status code: {response.status_code}")
                return {'success': False, 'message': f'Email sending failed with status {response.status_code}'}
                
        except Exception as e:
            logger.error(f"Error sending customer email: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    def send_admin_notification(self, customer_data, product_data, order_id):
        """Send order notification email to admin"""
        try:
            # Check if SendGrid is configured
            if not self.sg:
                logger.warning("SendGrid not configured, skipping admin email")
                return {'success': False, 'message': 'Email service not configured'}
            
            # Admin email
            to_email = To(Config.ADMIN_EMAIL)
            
            # Email content
            subject = f"New Order Received - {product_data['name']} - Order #{order_id}"
            
            html_content = self._generate_admin_email_html(customer_data, product_data, order_id)
            text_content = self._generate_admin_email_text(customer_data, product_data, order_id)
            
            # Create mail object
            mail = Mail(
                from_email=self.from_email,
                to_emails=to_email,
                subject=subject,
                html_content=Content("text/html", html_content),
                plain_text_content=Content("text/plain", text_content)
            )
            
            # Send email
            response = self.sg.send(mail)
            
            if response.status_code in [200, 201, 202]:
                logger.info(f"Admin notification email sent successfully")
                return {'success': True, 'message': 'Email sent successfully'}
            else:
                logger.error(f"Failed to send admin email. Status code: {response.status_code}")
                return {'success': False, 'message': f'Email sending failed with status {response.status_code}'}
                
        except Exception as e:
            logger.error(f"Error sending admin email: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    def _generate_customer_email_html(self, customer_data, product_data, order_id):
        """Generate HTML content for customer email"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Order Confirmation</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #2563eb; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background: #f9fafb; }}
                .order-details {{ background: white; padding: 20px; margin: 20px 0; border-radius: 8px; }}
                .footer {{ text-align: center; padding: 20px; color: #666; }}
                .highlight {{ color: #2563eb; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Order Confirmation</h1>
                    <p>Thank you for your purchase!</p>
                </div>
                
                <div class="content">
                    <h2>Order Details</h2>
                    <div class="order-details">
                        <p><strong>Order ID:</strong> <span class="highlight">#{order_id}</span></p>
                        <p><strong>Product:</strong> {product_data['name']}</p>
                        <p><strong>Color:</strong> {product_data['selectedColor']}</p>
                        <p><strong>Memory:</strong> {product_data['selectedRam']}</p>
                        <p><strong>Storage:</strong> {product_data['selectedStorage']}</p>
                        <p><strong>Total Price:</strong> <span class="highlight">${product_data.get('finalPrice', 0):,}</span></p>
                    </div>
                    
                    <h2>Shipping Information</h2>
                    <div class="order-details">
                        <p><strong>Name:</strong> {customer_data['firstName']} {customer_data['lastName']}</p>
                        <p><strong>Address:</strong> {customer_data['address']}</p>
                        <p><strong>City:</strong> {customer_data['city']}, {customer_data['zipCode']}</p>
                        <p><strong>Mobile:</strong> {customer_data['mobile']}</p>
                        {f'<p><strong>Email:</strong> {customer_data["email"]}</p>' if customer_data.get('email') else ''}
                    </div>
                    
                    <p>We will process your order and send you tracking information soon.</p>
                </div>
                
                <div class="footer">
                    <p>Thank you for choosing SNI Laptops!</p>
                    <p>If you have any questions, please contact us.</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _generate_customer_email_text(self, customer_data, product_data, order_id):
        """Generate plain text content for customer email"""
        return f"""
        Order Confirmation - Order #{order_id}
        
        Thank you for your purchase!
        
        Order Details:
        - Order ID: #{order_id}
        - Product: {product_data['name']}
        - Color: {product_data['selectedColor']}
        - Memory: {product_data['selectedRam']}
        - Storage: {product_data['selectedStorage']}
        - Total Price: ${product_data.get('finalPrice', 0):,}
        
        Shipping Information:
        - Name: {customer_data['firstName']} {customer_data['lastName']}
        - Address: {customer_data['address']}
        - City: {customer_data['city']}, {customer_data['zipCode']}
        - Mobile: {customer_data['mobile']}
        {f'- Email: {customer_data["email"]}' if customer_data.get('email') else ''}
        
        We will process your order and send you tracking information soon.
        
        Thank you for choosing SNI Laptops!
        """
    
    def _generate_admin_email_html(self, customer_data, product_data, order_id):
        """Generate HTML content for admin email"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>New Order Notification</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #dc2626; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background: #f9fafb; }}
                .order-details {{ background: white; padding: 20px; margin: 20px 0; border-radius: 8px; }}
                .highlight {{ color: #dc2626; font-weight: bold; }}
                .urgent {{ background: #fef2f2; border-left: 4px solid #dc2626; padding: 10px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>New Order Received</h1>
                    <p>Order #{order_id}</p>
                </div>
                
                <div class="content">
                    <div class="urgent">
                        <h2>Action Required</h2>
                        <p>A new order has been placed and requires processing.</p>
                    </div>
                    
                    <h2>Order Details</h2>
                    <div class="order-details">
                        <p><strong>Order ID:</strong> <span class="highlight">#{order_id}</span></p>
                        <p><strong>Product:</strong> {product_data['name']}</p>
                        <p><strong>Color:</strong> {product_data['selectedColor']}</p>
                        <p><strong>Memory:</strong> {product_data['selectedRam']}</p>
                        <p><strong>Storage:</strong> {product_data['selectedStorage']}</p>
                        <p><strong>Total Price:</strong> <span class="highlight">${product_data.get('finalPrice', 0):,}</span></p>
                    </div>
                    
                    <h2>Customer Information</h2>
                    <div class="order-details">
                        <p><strong>Name:</strong> {customer_data['firstName']} {customer_data['lastName']}</p>
                        <p><strong>Address:</strong> {customer_data['address']}</p>
                        <p><strong>City:</strong> {customer_data['city']}, {customer_data['zipCode']}</p>
                        <p><strong>Mobile:</strong> {customer_data['mobile']}</p>
                        {f'<p><strong>Email:</strong> {customer_data["email"]}</p>' if customer_data.get('email') else ''}
                    </div>
                    
                    <p><strong>Next Steps:</strong> Please process this order and update the customer with tracking information.</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _generate_admin_email_text(self, customer_data, product_data, order_id):
        """Generate plain text content for admin email"""
        return f"""
        New Order Received - Order #{order_id}
        
        A new order has been placed and requires processing.
        
        Order Details:
        - Order ID: #{order_id}
        - Product: {product_data['name']}
        - Color: {product_data['selectedColor']}
        - Memory: {product_data['selectedRam']}
        - Storage: {product_data['selectedStorage']}
        - Total Price: ${product_data.get('finalPrice', 0):,}
        
        Customer Information:
        - Name: {customer_data['firstName']} {customer_data['lastName']}
        - Address: {customer_data['address']}
        - City: {customer_data['city']}, {customer_data['zipCode']}
        - Mobile: {customer_data['mobile']}
        {f'- Email: {customer_data["email"]}' if customer_data.get('email') else ''}
        
        Next Steps: Please process this order and update the customer with tracking information.
        """
