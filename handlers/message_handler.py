"""Message handling module for the Telegram bot."""
import logging
from langdetect import detect, detect_langs
from telegram import Update
from telegram.ext import ContextTypes

from config import LANG_CONFIDENCE_THRESHOLD, MESSAGE_EMOJIS, MONGODB_URI, FAQ_ENABLED
from services import TranslationService
from services.mongodb_service import MongoDBService
from services.faq_service import FaqService

# Configure logging
logger = logging.getLogger(__name__)

# Initialize services
translation_service = TranslationService()
mongodb_service = MongoDBService() if MONGODB_URI else None
faq_service = FaqService() if FAQ_ENABLED else None

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle incoming user messages and translate non-English messages to English.
    If the message is a question, try to answer it using the FAQ service.
    
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
    
    # Process the message based on language
    if lang_code == 'en':
        # For English messages, check if we can answer from FAQ
        if FAQ_ENABLED and faq_service:
            try:
                answer = faq_service.answer_question(message.text)
                
                # If we have an answer from the FAQ, reply directly
                if answer:
                    logger.info(f"Answering question directly from FAQ")
                    
                    # Format the answer with an emoji
                    formatted_answer = f"{MESSAGE_EMOJIS['faq']} {answer}"
                    
                    # Reply to the user's message
                    await message.reply_text(
                        formatted_answer,
                        disable_notification=False  # Notify the user
                    )
                    
                    # Store in MongoDB if enabled
                    if mongodb_service:
                        mongodb_service.store_message(
                            message.from_user.id,
                            message.from_user.username,
                            message.from_user.first_name,
                            message.from_user.last_name,
                            message.chat_id,
                            message.message_id,
                            message.text,  # Original text
                            lang_code,     # Language code
                            message.text,  # Same as original (already English)
                            None           # Use current timestamp
                        )
                    
                    # No need to process further
                    return
            except Exception as e:
                logger.error(f"Error processing FAQ question: {e}")
        
        # If we reach here, it means the message is in English but not answerable from FAQ
        # or FAQ is disabled - do nothing as per original behavior
        return
    
    # For non-English messages, first translate then check FAQ if confidence is high enough
    elif confidence >= LANG_CONFIDENCE_THRESHOLD:
        try:
            # Translate the message to English
            logger.info(f"Translating message from {lang_code} to English")
            translated_text = translation_service.translate_text(message.text, lang_code)
            
            # Check if the translated message can be answered from FAQ
            if FAQ_ENABLED and faq_service:
                try:
                    answer = faq_service.answer_question(translated_text)
                    
                    # If we have an answer from the FAQ, translate it back and reply
                    if answer:
                        logger.info(f"Answering translated question from FAQ")
                        
                        # Translate the answer back to the original language
                        translated_answer = translation_service.translate_text(answer, "en", lang_code)
                        
                        # Format the answer with an emoji
                        formatted_answer = f"{MESSAGE_EMOJIS['faq']} {translated_answer}"
                        
                        # Reply to the user's message
                        await message.reply_text(
                            formatted_answer,
                            disable_notification=False  # Notify the user
                        )
                        
                        # Store in MongoDB if enabled
                        if mongodb_service:
                            mongodb_service.store_message(
                                message.from_user.id,
                                message.from_user.username,
                                message.from_user.first_name,
                                message.from_user.last_name,
                                message.chat_id,
                                message.message_id,
                                message.text,      # Original text
                                lang_code,         # Language code
                                translated_text,   # Translated text
                                None              # Use current timestamp
                            )
                        
                        # No need to process further
                        return
                except Exception as e:
                    logger.error(f"Error processing translated FAQ question: {e}")
            
            # If we reach here, either the FAQ service didn't provide an answer,
            # or an error occurred, or FAQ is disabled - continue with normal translation flow
            
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
                            'translated_message_id': sent_message.message_id,
                            'original_message_id': message.message_id,
                            'chat_id': message.chat_id,
                            'user_id': message.from_user.id,
                            'original_language': lang_code,
                            'original_text': message.text,
                            'translated_text': translated_text
                        }
                        cache_service.set(sent_message.message_id, cache_data)
                        logger.info(f"Cached translation info for message {sent_message.message_id}")
                else:
                    logger.error("Failed to store translation in database")
            else:
                logger.error("Database service not initialized")
            
            # Store in MongoDB if enabled
            if mongodb_service:
                mongodb_service.store_message(
                    message.from_user.id,
                    message.from_user.username,
                    message.from_user.first_name,
                    message.from_user.last_name,
                    message.chat_id,
                    message.message_id,
                    message.text,
                    lang_code,
                    translated_text,
                    None  # Use current timestamp
                )
                logger.info(f"Stored message in MongoDB for user {message.from_user.id}")
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
