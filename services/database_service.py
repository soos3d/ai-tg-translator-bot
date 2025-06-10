"""Database service for persisting bot data using SQLite."""
import os
import sqlite3
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class DatabaseService:
    """Service for handling persistent storage of bot data in SQLite."""
    
    def __init__(self, db_path="bot_data.db"):
        """
        Initialize the database service.
        
        Args:
            db_path (str): Path to the SQLite database file
        """
        # Ensure the directory exists
        db_directory = os.path.dirname(db_path)
        if db_directory and not os.path.exists(db_directory):
            Path(db_directory).mkdir(parents=True, exist_ok=True)
            
        self.db_path = db_path
        self._init_db()
        
    def _init_db(self):
        """Initialize the database with required tables."""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create a table for storing translated messages
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS translated_messages (
                id INTEGER PRIMARY KEY,
                translated_message_id INTEGER NOT NULL,
                original_message_id INTEGER NOT NULL,
                chat_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                original_language TEXT NOT NULL,
                original_text TEXT NOT NULL,
                translated_text TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            conn.commit()
            logger.info(f"Database initialized at {self.db_path}")
        except sqlite3.Error as e:
            logger.error(f"Database initialization error: {e}")
        finally:
            if conn:
                conn.close()
    
    def store_translation(self, translated_message_id, original_message_id, chat_id, user_id, 
                         original_language, original_text, translated_text):
        """
        Store a translation record in the database.
        
        Args:
            translated_message_id (int): ID of the bot's translated message
            original_message_id (int): ID of the user's original message
            chat_id (int): ID of the chat where the message was sent
            user_id (int): ID of the user who sent the message
            original_language (str): Language code of the original message
            original_text (str): Text of the original message
            translated_text (str): Translated text
            
        Returns:
            bool: True if successful, False otherwise
        """
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
            INSERT INTO translated_messages (
                translated_message_id, original_message_id, chat_id, user_id, 
                original_language, original_text, translated_text
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                translated_message_id, original_message_id, chat_id, user_id,
                original_language, original_text, translated_text
            ))
            
            conn.commit()
            logger.info(f"Translation stored for message {translated_message_id}")
            return True
        except sqlite3.Error as e:
            logger.error(f"Database error storing translation: {e}")
            return False
        finally:
            if conn:
                conn.close()
    
    def get_translation_by_msg_id(self, translated_message_id):
        """
        Retrieve translation info for a specific message ID.
        
        Args:
            translated_message_id (int): ID of the translated message
            
        Returns:
            dict: Translation information or None if not found
        """
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Enable row factory to get dict-like results
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT * FROM translated_messages 
            WHERE translated_message_id = ?
            ''', (translated_message_id,))
            
            row = cursor.fetchone()
            if row:
                # Convert row to dictionary
                return {
                    'translated_message_id': row['translated_message_id'],
                    'original_message_id': row['original_message_id'],
                    'chat_id': row['chat_id'],
                    'user_id': row['user_id'],
                    'original_language': row['original_language'],
                    'original_text': row['original_text'],
                    'translated_text': row['translated_text']
                }
            return None
        except sqlite3.Error as e:
            logger.error(f"Database error retrieving translation: {e}")
            return None
        finally:
            if conn:
                conn.close()
    
    def delete_old_translations(self, days=7):
        """
        Delete translations older than the specified number of days.
        
        Args:
            days (int): Number of days to keep in history
            
        Returns:
            int: Number of rows deleted
        """
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
            DELETE FROM translated_messages 
            WHERE datetime(timestamp) < datetime('now', '-? days')
            ''', (days,))
            
            deleted_count = cursor.rowcount
            conn.commit()
            logger.info(f"Deleted {deleted_count} old translation records")
            return deleted_count
        except sqlite3.Error as e:
            logger.error(f"Database error deleting old translations: {e}")
            return 0
        finally:
            if conn:
                conn.close()
