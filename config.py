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
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here-sni-laptops-2025')
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    PORT = int(os.getenv('PORT', 5000))
    
    # Session Configuration
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    # For cross-origin requests (localhost → Railway), we need None
    SESSION_COOKIE_SECURE = True  # Required for SameSite=None
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'None'  # Allow cross-origin cookies
    SESSION_COOKIE_DOMAIN = None  # Don't restrict domain
    
    # MongoDB Configuration
    MONGODB_USERNAME = os.getenv('MONGODB_USERNAME', 'mongo')
    MONGODB_PASSWORD = os.getenv('MONGODB_PASSWORD', 'UIKMSJBhHBiVyBzQibsBoFXhkjPyTgcj')
    MONGODB_HOST = os.getenv('MONGODB_HOST', 'yamanote.proxy.rlwy.net')
    MONGODB_PORT = os.getenv('MONGODB_PORT', '18859')
    MONGODB_DATABASE = os.getenv('MONGODB_DATABASE', 'sni_laptops')
    
    @property
    def MONGODB_URI(self):
        return f"mongodb://{self.MONGODB_USERNAME}:{self.MONGODB_PASSWORD}@{self.MONGODB_HOST}:{self.MONGODB_PORT}/{self.MONGODB_DATABASE}?authSource=admin"
    
    # Email Templates
    ORDER_CONFIRMATION_TEMPLATE = 'order_confirmation'
    ADMIN_NOTIFICATION_TEMPLATE = 'admin_notification'
