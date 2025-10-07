#!/usr/bin/env python3
"""
Simple email test for SNI Laptops Backend
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.email_service import EmailService

def test_email():
    """Test email sending functionality"""
    print("🧪 Testing Email Functionality")
    print("=" * 40)
    
    try:
        # Initialize email service
        email_service = EmailService()
        print("✅ Email service initialized")
        
        # Test data
        customer_data = {
            'firstName': 'Test',
            'lastName': 'User',
            'email': 'test@example.com',  # Replace with your email
            'address': '123 Test Street',
            'city': 'Test City',
            'zipCode': '12345',
            'mobile': '1234567890'
        }
        
        product_data = {
            'name': 'SNI Test Laptop',
            'selectedColor': 'Black',
            'selectedRam': '16GB',
            'selectedStorage': '512GB SSD',
            'finalPrice': 1199
        }
        
        order_id = 'TEST-001'
        
        print("📧 Testing customer email...")
        result = email_service.send_order_confirmation(customer_data, product_data, order_id)
        
        if result['success']:
            print("✅ Customer email sent successfully!")
        else:
            print(f"❌ Customer email failed: {result['message']}")
        
        print("📧 Testing admin email...")
        admin_result = email_service.send_admin_notification(customer_data, product_data, order_id)
        
        if admin_result['success']:
            print("✅ Admin email sent successfully!")
        else:
            print(f"❌ Admin email failed: {admin_result['message']}")
        
        return result['success'] and admin_result['success']
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_email()
    if success:
        print("\n🎉 Email functionality is working!")
    else:
        print("\n⚠️  Email functionality needs configuration")
        print("Please check your SendGrid settings in .env file")
