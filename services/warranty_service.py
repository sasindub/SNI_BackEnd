from datetime import datetime
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)

class WarrantyService:
    def __init__(self, db_service):
        """Initialize warranty service with database connection"""
        self.db_service = db_service
        self.warranties = db_service.get_collection('warranties')
    
    def calculate_warranty_status(self, start_date, end_date):
        """Calculate warranty status based on dates"""
        current_date = datetime.utcnow()
        
        # Convert to datetime if they're strings and remove timezone info for comparison
        if isinstance(start_date, str):
            start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00')).replace(tzinfo=None)
        elif hasattr(start_date, 'tzinfo') and start_date.tzinfo is not None:
            start_date = start_date.replace(tzinfo=None)
            
        if isinstance(end_date, str):
            end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00')).replace(tzinfo=None)
        elif hasattr(end_date, 'tzinfo') and end_date.tzinfo is not None:
            end_date = end_date.replace(tzinfo=None)
        
        if current_date < start_date:
            return "Inactive"
        elif start_date <= current_date <= end_date:
            return "Active"
        else:
            return "Expired"
    
    def get_all_warranties(self):
        """Get all warranty records"""
        try:
            warranties = list(self.warranties.find())
            
            # Convert ObjectId to string for JSON serialization
            for warranty in warranties:
                warranty['_id'] = str(warranty['_id'])
                # Convert datetime to ISO format (only if not None)
                if 'warranty_start_date' in warranty and warranty['warranty_start_date']:
                    warranty['warranty_start_date'] = warranty['warranty_start_date'].isoformat()
                if 'warranty_end_date' in warranty and warranty['warranty_end_date']:
                    warranty['warranty_end_date'] = warranty['warranty_end_date'].isoformat()
                if 'created_at' in warranty and warranty['created_at']:
                    warranty['created_at'] = warranty['created_at'].isoformat()
                if 'updated_at' in warranty and warranty['updated_at']:
                    warranty['updated_at'] = warranty['updated_at'].isoformat()
            
            return {
                'success': True,
                'warranties': warranties,
                'count': len(warranties)
            }
        except Exception as e:
            logger.error(f"Error fetching warranties: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_warranty_by_serial(self, serial_number):
        """Get warranty by serial number"""
        try:
            warranty = self.warranties.find_one({'serial_number': serial_number})
            
            if warranty:
                warranty['_id'] = str(warranty['_id'])
                # Convert datetime to ISO format (only if not None)
                if 'warranty_start_date' in warranty and warranty['warranty_start_date']:
                    warranty['warranty_start_date'] = warranty['warranty_start_date'].isoformat()
                if 'warranty_end_date' in warranty and warranty['warranty_end_date']:
                    warranty['warranty_end_date'] = warranty['warranty_end_date'].isoformat()
                if 'created_at' in warranty and warranty['created_at']:
                    warranty['created_at'] = warranty['created_at'].isoformat()
                if 'updated_at' in warranty and warranty['updated_at']:
                    warranty['updated_at'] = warranty['updated_at'].isoformat()
                
                return {
                    'success': True,
                    'warranty': warranty
                }
            else:
                return {
                    'success': False,
                    'error': 'Warranty not found'
                }
        except Exception as e:
            logger.error(f"Error fetching warranty: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_warranty(self, warranty_data):
        """Create a new warranty record"""
        try:
            # Validate required field
            if 'serial_number' not in warranty_data or not warranty_data['serial_number']:
                return {
                    'success': False,
                    'error': 'Serial number is required'
                }
            
            # Check if serial number already exists
            existing = self.warranties.find_one({'serial_number': warranty_data['serial_number']})
            if existing:
                return {
                    'success': False,
                    'error': 'Serial number already exists'
                }
            
            # Parse dates (store as offset-naive for consistency)
            warranty_start_date = None
            warranty_end_date = None
            
            if 'warranty_start_date' in warranty_data and warranty_data['warranty_start_date']:
                warranty_start_date = datetime.fromisoformat(warranty_data['warranty_start_date'].replace('Z', '+00:00')).replace(tzinfo=None)
            
            if 'warranty_end_date' in warranty_data and warranty_data['warranty_end_date']:
                warranty_end_date = datetime.fromisoformat(warranty_data['warranty_end_date'].replace('Z', '+00:00')).replace(tzinfo=None)
            
            # Calculate warranty status
            warranty_status = "Inactive"
            if warranty_start_date and warranty_end_date:
                warranty_status = self.calculate_warranty_status(warranty_start_date, warranty_end_date)
            
            # Prepare warranty document
            warranty_doc = {
                'serial_number': warranty_data['serial_number'],
                'warranty_start_date': warranty_start_date,
                'warranty_end_date': warranty_end_date,
                'windows_key': warranty_data.get('windows_key', ''),
                'nic_number': warranty_data.get('nic_number', ''),
                'passcode': warranty_data.get('passcode', ''),
                'warranty_status': warranty_status,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            
            # Insert into database
            result = self.warranties.insert_one(warranty_doc)
            warranty_doc['_id'] = str(result.inserted_id)
            
            # Convert datetime to ISO format for response
            if warranty_doc['warranty_start_date']:
                warranty_doc['warranty_start_date'] = warranty_doc['warranty_start_date'].isoformat()
            if warranty_doc['warranty_end_date']:
                warranty_doc['warranty_end_date'] = warranty_doc['warranty_end_date'].isoformat()
            warranty_doc['created_at'] = warranty_doc['created_at'].isoformat()
            warranty_doc['updated_at'] = warranty_doc['updated_at'].isoformat()
            
            return {
                'success': True,
                'warranty': warranty_doc,
                'message': 'Warranty created successfully'
            }
        except Exception as e:
            logger.error(f"Error creating warranty: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def update_warranty(self, warranty_id, warranty_data):
        """Update an existing warranty record"""
        try:
            # Validate warranty ID
            if not ObjectId.is_valid(warranty_id):
                return {
                    'success': False,
                    'error': 'Invalid warranty ID'
                }
            
            # Check if warranty exists
            existing = self.warranties.find_one({'_id': ObjectId(warranty_id)})
            if not existing:
                return {
                    'success': False,
                    'error': 'Warranty not found'
                }
            
            # Check if serial number is being changed and if it already exists
            if 'serial_number' in warranty_data and warranty_data['serial_number'] != existing['serial_number']:
                duplicate = self.warranties.find_one({
                    'serial_number': warranty_data['serial_number'],
                    '_id': {'$ne': ObjectId(warranty_id)}
                })
                if duplicate:
                    return {
                        'success': False,
                        'error': 'Serial number already exists'
                    }
            
            # Prepare update data
            update_data = {}
            
            if 'serial_number' in warranty_data:
                update_data['serial_number'] = warranty_data['serial_number']
            
            if 'warranty_start_date' in warranty_data and warranty_data['warranty_start_date']:
                update_data['warranty_start_date'] = datetime.fromisoformat(warranty_data['warranty_start_date'].replace('Z', '+00:00')).replace(tzinfo=None)
            
            if 'warranty_end_date' in warranty_data and warranty_data['warranty_end_date']:
                update_data['warranty_end_date'] = datetime.fromisoformat(warranty_data['warranty_end_date'].replace('Z', '+00:00')).replace(tzinfo=None)
            
            if 'windows_key' in warranty_data:
                update_data['windows_key'] = warranty_data['windows_key']
            
            if 'nic_number' in warranty_data:
                update_data['nic_number'] = warranty_data['nic_number']
            
            if 'passcode' in warranty_data:
                update_data['passcode'] = warranty_data['passcode']
            
            # Calculate warranty status if both dates are available (from update or existing data)
            start_date = update_data.get('warranty_start_date') or existing.get('warranty_start_date')
            end_date = update_data.get('warranty_end_date') or existing.get('warranty_end_date')
            
            if start_date and end_date:
                update_data['warranty_status'] = self.calculate_warranty_status(start_date, end_date)
            elif 'warranty_start_date' in update_data or 'warranty_end_date' in update_data:
                # If updating dates but one is missing, set status to Inactive
                update_data['warranty_status'] = 'Inactive'
            
            update_data['updated_at'] = datetime.utcnow()
            
            # Update in database
            self.warranties.update_one(
                {'_id': ObjectId(warranty_id)},
                {'$set': update_data}
            )
            
            # Fetch updated warranty
            updated_warranty = self.warranties.find_one({'_id': ObjectId(warranty_id)})
            updated_warranty['_id'] = str(updated_warranty['_id'])
            
            # Convert datetime to ISO format (only if not None)
            if 'warranty_start_date' in updated_warranty and updated_warranty['warranty_start_date']:
                updated_warranty['warranty_start_date'] = updated_warranty['warranty_start_date'].isoformat()
            if 'warranty_end_date' in updated_warranty and updated_warranty['warranty_end_date']:
                updated_warranty['warranty_end_date'] = updated_warranty['warranty_end_date'].isoformat()
            if 'created_at' in updated_warranty and updated_warranty['created_at']:
                updated_warranty['created_at'] = updated_warranty['created_at'].isoformat()
            if 'updated_at' in updated_warranty and updated_warranty['updated_at']:
                updated_warranty['updated_at'] = updated_warranty['updated_at'].isoformat()
            
            return {
                'success': True,
                'warranty': updated_warranty,
                'message': 'Warranty updated successfully'
            }
        except Exception as e:
            logger.error(f"Error updating warranty: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }



