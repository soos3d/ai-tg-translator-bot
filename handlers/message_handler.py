"""Message handling module for the Telegram bot."""
import logging
from langdetect import detect, detect_langs
from telegram import Update
from telegram.ext import ContextTypes

from config import LANG_CONFIDENCE_THRESHOLD, MESSAGE_EMOJIS, MONGODB_URI
from services import TranslationService
from services.mongodb_service import MongoDBService

# Configure logging
logger = logging.getLogger(__name__)

# Initialize services
translation_service = TranslationService()
mongodb_service = MongoDBService() if MONGODB_URI else None

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle incoming user messages and translate non-English messages to English.
    
    Args:
        update (Update): The incoming update from Telegram
        context (ContextTypes.DEFAULT_TYPE): The context object for the handler
        
    Returns:
        None
    """
    # Extract message information
    message = update.message
    if not message or not message.text:
        return
    
    # Detect language
    lang_code = detect(message.text)  # Get the language code
    detection = detect_langs(message.text)[0]  # Get detailed detection info
    confidence = detection.prob  # Get the confidence score
    
    # Only proceed if the message is not in English AND we're confident about the detection
    if lang_code != 'en' and confidence >= LANG_CONFIDENCE_THRESHOLD:
        try:
            # Translate the message to English
            logger.info(f"Translating message from {lang_code} to English")
            translated_text = translation_service.translate_text(message.text, lang_code)
            
            # Format user information
            user = message.from_user
            user_info = (
                f"{MESSAGE_EMOJIS['user_info']} User Information:\n"
                f"Username: @{user.username if user.username else 'N/A'}\n"
                f"Name: {user.first_name}{f' {user.last_name}' if user.last_name else ''}"
            )

            # Format language information
            language_info = f"{MESSAGE_EMOJIS['language']} Language Detection:\nDetected Language: {lang_code.upper()}\nConfidence: {confidence:.2%}\n\n"

            # Format message information
            message_info = (
                f"Message Information:\n"
                f"Original Text:\n{message.text}"
            )

            # Combine all information
            info_message = f"{message_info}"
            
            # Add translation to message
            translation_info = translated_text
            info_message += translation_info

            if context.bot_data.get('debug_mode', False):
                logger.debug(f"Message details: \n{info_message}")

            # Send a message that's visually linked to the original but doesn't notify the sender
            sent_message = await context.bot.send_message(
                chat_id=message.chat_id,
                text=translation_info,
                reply_to_message_id=message.message_id,  # This creates the visual thread connection
                disable_notification=True,  # This prevents notification for the message
                allow_sending_without_reply=True  # This ensures the message is sent even if the original is deleted
            )
            
            # Store message info for potential agent replies in local database
            db_service = context.bot_data.get('db_service')
            if db_service:
                success = db_service.store_translation(
                    sent_message.message_id,
                    message.message_id,
                    message.chat_id,
                    message.from_user.id,
                    lang_code,
                    message.text,
                    translated_text
                )
                
                if success:
                    # Also cache in memory for faster lookups
                    cache_service = context.bot_data.get('cache_service')
                    if cache_service:
                        cache_data = {
                            'original_message_id': message.message_id,
                            'original_language': lang_code,
                            'chat_id': message.chat_id,
                            'user_id': message.from_user.id,
                            'original_text': message.text,
                            'translated_text': translated_text
                        }
                        cache_service.set(sent_message.message_id, cache_data)
                        logger.info(f"Stored translation info for message {sent_message.message_id} in local database and cache")
                    else:
                        logger.info(f"Stored translation info for message {sent_message.message_id} in local database only (no cache)")
                else:
                    logger.error(f"Failed to store translation info for message {sent_message.message_id} in local database")
            else:
                logger.error("Local database service not initialized")
                
            # Store user data and English text in MongoDB
            if mongodb_service and mongodb_service.is_connected:
                # Get the English text (either translated or original)
                english_text = translated_text if lang_code != 'en' else message.text
                
                # Store in MongoDB
                mongo_success = mongodb_service.store_message(
                    user_id=message.from_user.id,
                    username=message.from_user.username,
                    first_name=message.from_user.first_name,
                    last_name=message.from_user.last_name,
                    chat_id=message.chat_id,
                    message_id=message.message_id,
                    original_text=message.text,
                    original_lang=lang_code,
                    english_text=english_text
                )
                
                if mongo_success:
                    logger.info(f"Stored message data in MongoDB for user {message.from_user.id}")
                else:
                    logger.error(f"Failed to store message data in MongoDB for user {message.from_user.id}")
            elif MONGODB_URI and not mongodb_service:
                logger.error("MongoDB service failed to initialize")
            elif not MONGODB_URI:
                logger.debug("MongoDB storage is disabled. No data stored in MongoDB.")
        
        except Exception as e:
            error_message = f"Translation error: {e}"
            logger.error(error_message)
            await message.reply_text(f"Sorry, I couldn't translate your message: {e}")


async def handle_agent_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle replies from support agents to translated messages.
    Automatically translates the agent's response back to the user's original language.
    
    Args:
        update (Update): The incoming update from Telegram
        context (ContextTypes.DEFAULT_TYPE): The context object for the handler
        
    Returns:
        None
    """
    # Extract message information
    message = update.message
    if not message or not message.text or not message.reply_to_message:
        return
    
    # Get the message ID that this message is replying to
    replied_to_message_id = message.reply_to_message.message_id
    
    # Check if this is a reply to one of our translated messages
    # First check the memory cache for faster lookup
    translation_info = None
    cache_service = context.bot_data.get('cache_service')
    
    if cache_service:
        # Try to get from cache
        translation_info = cache_service.get(replied_to_message_id)
        if translation_info:
            logger.info(f"Found translation info for message {replied_to_message_id} in memory cache")
    else:
        # Check the database
        db_service = context.bot_data.get('db_service')
        if db_service:
            translation_info = db_service.get_translation_by_msg_id(replied_to_message_id)
            if translation_info:
                # Add to cache for future lookups
                if cache_service:
                    cache_service.set(replied_to_message_id, translation_info)
                    logger.info(f"Found translation info for message {replied_to_message_id} in database and added to cache")
                else:
                    logger.info(f"Found translation info for message {replied_to_message_id} in database (no cache)")
        else:
            logger.error("Database service not initialized")
    
    if translation_info:
        original_lang = translation_info['original_language']
        original_message_id = translation_info['original_message_id']
        chat_id = translation_info['chat_id']
        
        logger.info(f"Agent replying to translated message {replied_to_message_id}. "  
                   f"Original language: {original_lang}")
        
        try:
            # Translate the agent's reply to the user's original language
            translated_reply = translation_service.translate_text(
                message.text, 
                "en",  # Assuming agent reply is in English
                original_lang  # Target language is user's original language
            )
            
            # Send the translated reply to the original message
            await context.bot.send_message(
                chat_id=chat_id,
                text=translated_reply,  # Prefixing with an emoji to indicate translation
                reply_to_message_id=original_message_id,  # Reply to user's original message
                disable_notification=False  # User should be notified of this reply
            )
            
            # Let the agent know their message was translated and sent
          #  await message.reply_text(
          #      f"{MESSAGE_EMOJIS['success']} Your response has been translated to {original_lang.upper()} and sent to the user.",
          #      disable_notification=True  # No need to notify the agent
          #  )
            
        except Exception as e:
            error_message = f"Translation error: {e}"
            logger.error(error_message)
            await message.reply_text(f"Sorry, I couldn't translate your response: {e}")
    else:
        # This is a reply to a regular message, not a translated one - do nothing
        pass
