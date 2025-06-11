"""MongoDB service module for storing translation data."""
import logging
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

from config import MONGODB_URI, MONGODB_DB_NAME, MONGODB_COLLECTION_NAME

# Configure logging
logger = logging.getLogger(__name__)

class MongoDBService:
    """Service for storing translation data in MongoDB."""
    
    def __init__(self):
        """Initialize MongoDB connection."""
        self.client = None
        self.db = None
        self.collection = None
        self.is_connected = False
        
        if not MONGODB_URI:
            logger.warning("MongoDB URI not provided. MongoDB storage disabled.")
            return
            
        try:
            self.client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
            # Test the connection
            self.client.server_info()
            self.db = self.client[MONGODB_DB_NAME]
            self.collection = self.db[MONGODB_COLLECTION_NAME]
            self.is_connected = True
            logger.info(f"Connected to MongoDB: {MONGODB_DB_NAME}.{MONGODB_COLLECTION_NAME}")
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            self.is_connected = False
    
    def store_message(self, user_id, username, first_name, last_name, 
                     chat_id, message_id, original_text, original_lang, 
                     english_text, timestamp=None):
        """
        Store message data in MongoDB.
        
        Args:
            user_id (int): Telegram user ID
            username (str): Telegram username
            first_name (str): User's first name
            last_name (str): User's last name
            chat_id (int): Telegram chat ID
            message_id (int): Telegram message ID
            original_text (str): Original message text
            original_lang (str): Original message language code
            english_text (str): English translation or original text if already English
            timestamp (datetime): Message timestamp (defaults to current time if None)
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_connected:
            logger.warning("MongoDB not connected. Skipping message storage.")
            return False
            
        try:
            # Create document
            document = {
                "user": {
                    "user_id": user_id,
                    "username": username,
                    "first_name": first_name,
                    "last_name": last_name
                },
                "message": {
                    "chat_id": chat_id,
                    "message_id": message_id,
                    "original_text": original_text,
                    "original_lang": original_lang,
                    "english_text": english_text
                },
                "timestamp": timestamp if timestamp else datetime.now(),
                "created_at": datetime.now()
            }
            
            # Insert into MongoDB
            result = self.collection.insert_one(document)
            logger.info(f"Stored message in MongoDB with ID: {result.inserted_id}")
            return True
        except Exception as e:
            logger.error(f"Error storing message in MongoDB: {str(e)}")
            return False
            
    def __del__(self):
        """Close MongoDB connection when object is destroyed."""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed.")
