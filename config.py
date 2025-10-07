import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # SendGrid Configuration
    SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
    FROM_EMAIL = os.getenv('FROM_EMAIL', 'sasindub01@gmail.com')
    FROM_NAME = os.getenv('FROM_NAME', 'SNI Laptops')
    ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@snilaptops.com')
    
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    PORT = int(os.getenv('PORT', 5000))
    
    # Email Templates
    ORDER_CONFIRMATION_TEMPLATE = 'order_confirmation'
    ADMIN_NOTIFICATION_TEMPLATE = 'admin_notification'
