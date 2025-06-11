"""
MongoDB connection and data fetching utilities
"""
import logging
import streamlit as st
from pymongo import MongoClient
from datetime import datetime
import pandas as pd
from .config import MONGODB_URI, MONGODB_DB_NAME, MONGODB_COLLECTION_NAME

logger = logging.getLogger(__name__)

@st.cache_resource
def init_connection():
    """Initialize MongoDB connection and return client"""
    if not MONGODB_URI:
        error_msg = "MongoDB URI not configured. Please set MONGODB_URI in .env file."
        logger.error(error_msg)
        st.error(error_msg)
        return None
    
    try:
        client = MongoClient(MONGODB_URI)
        # Test connection
        info = client.server_info()
        logger.info(f"Successfully connected to MongoDB. Server info: {info}")
        return client
    except Exception as e:
        error_msg = f"Failed to connect to MongoDB: {e}"
        logger.error(error_msg)
        st.error(error_msg)
        return None

@st.cache_data(ttl=300)  # Cache data for 5 minutes
def get_data(_client, start_date=None, end_date=None):
    """Fetch data from MongoDB with optional date filtering"""
    if not _client:
        logger.error("No MongoDB client provided")
        return pd.DataFrame()
    
    logger.info(f"Fetching data with date range: {start_date} to {end_date}")
    
    db = _client[MONGODB_DB_NAME]
    collection = db[MONGODB_COLLECTION_NAME]
    
    # Build query for date filtering
    query = {}
    if start_date and end_date:
        query["timestamp"] = {
            "$gte": start_date,
            "$lte": end_date
        }
    logger.info(f"MongoDB query: {query}")
    
    # Fetch data
    cursor = collection.find(query)
    logger.info(f"Collection being queried: {MONGODB_DB_NAME}.{MONGODB_COLLECTION_NAME}")
    
    # Convert MongoDB cursor to list of dictionaries
    data = []
    count = 0
    
    # Get the first document to examine the structure
    try:
        first_doc = next(cursor, None)
        if first_doc:
            # Log the document structure to understand its format
            logger.info(f"Document structure: {list(first_doc.keys())}")
            
            # Inspect nested structures
            for key in first_doc.keys():
                if key != '_id':
                    logger.info(f"Key '{key}' type: {type(first_doc[key])}")
                    
                    # For nested dictionaries, show their structure
                    if isinstance(first_doc[key], dict):
                        logger.info(f"  {key} contains: {list(first_doc[key].keys())}")
                        
                        # For deeply nested structures, go one level deeper
                        for subkey, subvalue in first_doc[key].items():
                            logger.info(f"    {key}.{subkey} type: {type(subvalue)}")
                            if isinstance(subvalue, dict):
                                logger.info(f"      {key}.{subkey} contains: {list(subvalue.keys())}")
                
            # Reset the cursor to start from the beginning again
            cursor = collection.find(query)
    except Exception as e:
        logger.error(f"Error examining document structure: {e}")
    
    for doc in cursor:
        try:
            # Create item dictionary with all fields from document
            item = {}
            
            # Extract all fields at top level
            for key, value in doc.items():
                if key != '_id':  # Skip MongoDB's internal ID
                    item[key] = value
            
            # Handle nested structures for user data
            if isinstance(doc.get('user'), dict):
                for key, value in doc['user'].items():
                    item[f'user_{key}'] = value
                    
            # Handle nested structures for chat data
            if isinstance(doc.get('chat'), dict):
                for key, value in doc['chat'].items():
                    item[f'chat_{key}'] = value
            
            # Handle nested message data which may contain content
            if isinstance(doc.get('message'), dict):
                for key, value in doc['message'].items():
                    item[f'message_{key}'] = value
                    
                    # Check for language fields in deeper structures
                    if key == 'content' and isinstance(value, dict):
                        for content_key, content_value in value.items():
                            item[f'message_content_{content_key}'] = content_value
            
            # Handle dedicated content field if it exists
            if isinstance(doc.get('content'), dict):
                for key, value in doc['content'].items():
                    item[f'content_{key}'] = value
                    
            # Standardize critical field names for analysis
            # Find language information (could be in multiple places)
            if 'original_lang' not in item:
                # Check all possible locations for language data
                possible_lang_fields = [
                    'content_original_lang',
                    'message_content_original_lang',
                    'message_original_lang',
                    'lang', 
                    'language'
                ]
                
                for field in possible_lang_fields:
                    if field in item and item[field]:
                        item['original_lang'] = item[field]
                        logger.info(f"Found language in field: {field} = {item[field]}")
                        break
            
            # Find original and translated text
            if 'original_text' not in item:
                for field in ['content_original_text', 'message_content_original_text', 'message_text', 'text']:
                    if field in item and item[field]:
                        item['original_text'] = item[field]
                        break
                        
            if 'english_text' not in item:
                for field in ['content_english_text', 'message_content_english_text', 'translated_text']:
                    if field in item and item[field]:
                        item['english_text'] = item[field]
                        break
                        
            # Log extraction results
            logger.info(f"Extracted item fields: {list(item.keys())}")
            if 'original_lang' in item:
                logger.info(f"Found language: {item['original_lang']}")
            
            # Add to data list
            data.append(item)
            count += 1
        except Exception as e:
            logger.error(f"Error processing document: {e}")
            continue
    
    logger.info(f"Retrieved {count} documents from MongoDB")
    
    # Convert to DataFrame
    df = pd.DataFrame(data)
    logger.info(f"Created DataFrame with shape: {df.shape}")
    return df
