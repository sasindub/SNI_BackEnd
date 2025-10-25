"""
Script to reset admin password and verify MongoDB setup
"""

from services.database_service import DatabaseService
from config import Config
import bcrypt
import sys
import os

# Set UTF-8 encoding for Windows console
if os.name == 'nt':
    import sys
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')

def reset_admin_password():
    """Reset admin password to Admin123"""
    print("=" * 60)
    print("Admin Password Reset Tool")
    print("=" * 60)
    
    try:
        # Connect to database
        print("\n1. Connecting to MongoDB...")
        config = Config()
        db_service = DatabaseService(config)
        admin_users = db_service.get_collection('admin_users')
        print("   [OK] Connected successfully")
        
        # Check if admin exists
        print("\n2. Checking for admin user...")
        admin = admin_users.find_one({'username': 'Admin'})
        
        if not admin:
            print("   [ERROR] Admin user not found!")
            print("\n3. Creating new admin user...")
            
            # Create new admin
            password = "Admin123"
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            
            admin_user = {
                "username": "Admin",
                "password": hashed_password,
                "role": "admin"
            }
            
            result = admin_users.insert_one(admin_user)
            print(f"   [OK] Admin user created with ID: {result.inserted_id}")
        else:
            print(f"   [OK] Admin user found with ID: {admin['_id']}")
            
            # Reset password
            print("\n3. Resetting password to 'Admin123'...")
            password = "Admin123"
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            
            admin_users.update_one(
                {'username': 'Admin'},
                {'$set': {'password': hashed_password}}
            )
            print("   [OK] Password reset successfully")
        
        # Verify the password works
        print("\n4. Verifying password...")
        admin = admin_users.find_one({'username': 'Admin'})
        test_password = "Admin123"
        
        if bcrypt.checkpw(test_password.encode('utf-8'), admin['password']):
            print("   [OK] Password verification successful!")
        else:
            print("   [ERROR] Password verification failed!")
            return False
        
        print("\n" + "=" * 60)
        print("[SUCCESS] Admin credentials are ready!")
        print("=" * 60)
        print("\nLogin Credentials:")
        print("  Username: Admin")
        print("  Password: Admin123")
        print("\nYou can now login at: http://localhost:3000/admin")
        print("=" * 60)
        
        db_service.close()
        return True
        
    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        import traceback
        print(traceback.format_exc())
        return False

if __name__ == '__main__':
    success = reset_admin_password()
    sys.exit(0 if success else 1)

