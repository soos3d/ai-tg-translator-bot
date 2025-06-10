"""Main bot module that initializes and runs the Telegram bot."""
import logging
import os
from telegram.ext import ApplicationBuilder, MessageHandler, filters

from config import (BOT_TOKEN, DEBUG_MODE, CACHE_MAX_SIZE,
                  CACHE_EXPIRATION_SECONDS, DB_CLEANUP_DAYS)
from handlers import handle_message, handle_agent_reply
from services import DatabaseService, CacheService

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG if DEBUG_MODE else logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    """Initialize and run the bot."""
    # Create the Application and pass it your bot's token
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Set debug mode in bot_data
    application.bot_data['debug_mode'] = DEBUG_MODE
    
    # Initialize database service
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'bot_data.db')
    db_service = DatabaseService(db_path)
    application.bot_data['db_service'] = db_service
    
    # Initialize cache service with configured values
    cache_service = CacheService(max_size=CACHE_MAX_SIZE, expiration_seconds=CACHE_EXPIRATION_SECONDS)
    application.bot_data['cache_service'] = cache_service

    # Perform database maintenance - cleanup old entries (older than 30 days)
    db_service.delete_old_translations(days=DB_CLEANUP_DAYS)
    logger.info("Database maintenance completed")

    # Add message handlers
    # Handle regular user messages (non-replies)
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND & ~filters.REPLY, 
        handle_message
    ))
    
    # Handle agent replies to translated messages
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND & filters.REPLY, 
        handle_agent_reply
    ))

    # Start the bot
    logger.info("Starting bot...")
    application.run_polling()

if __name__ == '__main__':
    main()
