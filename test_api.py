#!/usr/bin/env python3
"""
Test script for SNI Laptops Backend API
"""
import requests
import json

# API base URL
BASE_URL = "http://localhost:5000"

def test_health_check():
    """Test health check endpoint"""
    print("Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_create_order():
    """Test order creation endpoint"""
    print("\nTesting order creation...")
    
    # Sample order data
    order_data = {
        "product": {
            "id": "laptop-1",
            "name": "SNI Gaming Laptop",
            "basePrice": 2000,
            "selectedColor": "black",
            "selectedRam": "16GB",
            "selectedStorage": "512GB",
            "finalPrice": 2249
        },
        "customer": {
            "firstName": "John",
            "lastName": "Doe",
            "address": "123 Main Street, Apt 4B",
            "city": "New York",
            "mobile": "1234567890",
            "email": "john.doe@example.com",
            "zipCode": "10001"
        },
        "orderDate": "2024-01-01T00:00:00.000Z"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/orders",
            json=order_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code in [200, 201]
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """Run all tests"""
    print("SNI Laptops API Test Suite")
    print("=" * 40)
    
    # Test health check
    health_ok = test_health_check()
    
    # Test order creation
    order_ok = test_create_order()
    
    # Summary
    print("\n" + "=" * 40)
    print("Test Results:")
    print(f"Health Check: {'PASS' if health_ok else 'FAIL'}")
    print(f"Order Creation: {'PASS' if order_ok else 'FAIL'}")
    
    if health_ok and order_ok:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed!")

if __name__ == "__main__":
    main()
