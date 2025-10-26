"""
Test script to verify MongoDB connection and warranty system setup
"""

from services.database_service import DatabaseService
from config import Config
import sys

def test_mongodb_connection():
    """Test MongoDB connection and data"""
    print("=" * 60)
    print("MongoDB Connection Test")
    print("=" * 60)
    
    try:
        # Initialize database service
        print("\n1. Connecting to MongoDB...")
        config = Config()
        db_service = DatabaseService(config)
        print("   ✓ Successfully connected to MongoDB")
        
        # Test admin users collection
        print("\n2. Checking admin users...")
        admin_users = db_service.get_collection('admin_users')
        admin_count = admin_users.count_documents({})
        print(f"   ✓ Found {admin_count} admin user(s)")
        
        # Display admin usernames (not passwords)
        for admin in admin_users.find():
            print(f"   - Username: {admin['username']}, Role: {admin.get('role', 'N/A')}")
        
        # Test warranties collection
        print("\n3. Checking warranties...")
        warranties = db_service.get_collection('warranties')
        warranty_count = warranties.count_documents({})
        print(f"   ✓ Found {warranty_count} warranty record(s)")
        
        # Display warranty summary
        for warranty in warranties.find():
            print(f"   - Serial: {warranty['serial_number']}, Status: {warranty['warranty_status']}")
        
        # Test warranty status counts
        print("\n4. Warranty Status Summary:")
        active_count = warranties.count_documents({'warranty_status': 'Active'})
        expired_count = warranties.count_documents({'warranty_status': 'Expired'})
        inactive_count = warranties.count_documents({'warranty_status': 'Inactive'})
        print(f"   - Active: {active_count}")
        print(f"   - Expired: {expired_count}")
        print(f"   - Inactive: {inactive_count}")
        
        print("\n" + "=" * 60)
        print("✓ All tests passed successfully!")
        print("=" * 60)
        print("\nYou can now start the backend server with: python app.py")
        print("Login credentials: Username: Admin, Password: Admin123")
        
        db_service.close()
        return True
        
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Verify MongoDB is running on Railway")
        print("2. Check MongoDB credentials in config.py")
        print("3. Ensure network connectivity to Railway")
        return False

if __name__ == '__main__':
    success = test_mongodb_connection()
    sys.exit(0 if success else 1)




