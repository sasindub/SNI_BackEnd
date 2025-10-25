from pymongo import MongoClient, ASCENDING
from pymongo.errors import ConnectionFailure, OperationFailure
import bcrypt
import logging
from datetime import datetime, timedelta
from bson import ObjectId

logger = logging.getLogger(__name__)

class DatabaseService:
    def __init__(self, config):
        """Initialize MongoDB connection"""
        self.config = config
        self.client = None
        self.db = None
        self.connect()
        
    def connect(self):
        """Establish connection to MongoDB"""
        try:
            mongodb_uri = self.config.MONGODB_URI
            logger.info(f"Connecting to MongoDB at {self.config.MONGODB_HOST}:{self.config.MONGODB_PORT}")
            
            self.client = MongoClient(
                mongodb_uri,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=10000,
                socketTimeoutMS=10000
            )
            
            # Test the connection
            self.client.admin.command('ping')
            
            self.db = self.client[self.config.MONGODB_DATABASE]
            logger.info(f"Successfully connected to MongoDB database: {self.config.MONGODB_DATABASE}")
            
            # Initialize collections and indexes
            self.initialize_collections()
            
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
            raise
    
    def initialize_collections(self):
        """Create collections and indexes if they don't exist"""
        try:
            # Create indexes for warranties collection
            warranties = self.db.warranties
            warranties.create_index([("serial_number", ASCENDING)], unique=True)
            warranties.create_index([("nic_number", ASCENDING)])
            warranties.create_index([("warranty_status", ASCENDING)])
            
            # Create indexes for admin_users collection
            admin_users = self.db.admin_users
            admin_users.create_index([("username", ASCENDING)], unique=True)
            
            logger.info("Collections and indexes initialized successfully")
            
            # Initialize default admin user if not exists
            self.initialize_default_admin()
            
            # Initialize sample warranties if collection is empty
            self.initialize_sample_warranties()
            
        except Exception as e:
            logger.error(f"Error initializing collections: {str(e)}")
            raise
    
    def initialize_default_admin(self):
        """Create default admin user if not exists"""
        try:
            admin_users = self.db.admin_users
            
            # Check if admin user already exists
            existing_admin = admin_users.find_one({"username": "Admin"})
            
            if not existing_admin:
                # Hash the password
                password = "Admin123"
                hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                
                # Create admin user
                admin_user = {
                    "username": "Admin",
                    "password": hashed_password,
                    "created_at": datetime.utcnow(),
                    "role": "admin"
                }
                
                admin_users.insert_one(admin_user)
                logger.info("Default admin user created successfully")
            else:
                logger.info("Admin user already exists")
                
        except Exception as e:
            logger.error(f"Error initializing default admin: {str(e)}")
            raise
    
    def initialize_sample_warranties(self):
        """Create sample warranty records if collection is empty"""
        try:
            warranties = self.db.warranties
            
            # Check if warranties collection is empty
            if warranties.count_documents({}) == 0:
                # Create sample warranties
                sample_warranties = [
                    {
                        "serial_number": "SNI-LP-2024-001",
                        "warranty_start_date": datetime.utcnow() - timedelta(days=30),
                        "warranty_end_date": datetime.utcnow() + timedelta(days=335),
                        "windows_key": "XXXXX-XXXXX-XXXXX-XXXXX-XXXXX",
                        "nic_number": "199512345678",
                        "passcode": "Pass@2024",
                        "warranty_status": "Active",
                        "created_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    },
                    {
                        "serial_number": "SNI-LP-2024-002",
                        "warranty_start_date": datetime.utcnow() + timedelta(days=5),
                        "warranty_end_date": datetime.utcnow() + timedelta(days=370),
                        "windows_key": "YYYYY-YYYYY-YYYYY-YYYYY-YYYYY",
                        "nic_number": "200123456789",
                        "passcode": "SecurePass@123",
                        "warranty_status": "Inactive",
                        "created_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    },
                    {
                        "serial_number": "SNI-LP-2023-005",
                        "warranty_start_date": datetime.utcnow() - timedelta(days=400),
                        "warranty_end_date": datetime.utcnow() - timedelta(days=35),
                        "windows_key": "ZZZZZ-ZZZZZ-ZZZZZ-ZZZZZ-ZZZZZ",
                        "nic_number": "198823456789",
                        "passcode": "OldPass@456",
                        "warranty_status": "Expired",
                        "created_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    }
                ]
                
                warranties.insert_many(sample_warranties)
                logger.info(f"Inserted {len(sample_warranties)} sample warranty records")
            else:
                logger.info("Warranties collection already has data")
                
        except Exception as e:
            logger.error(f"Error initializing sample warranties: {str(e)}")
            raise
    
    def get_collection(self, collection_name):
        """Get a specific collection"""
        if self.db is None:
            raise Exception("Database not connected")
        return self.db[collection_name]
    
    def close(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            logger.info("Database connection closed")



