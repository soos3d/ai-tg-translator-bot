"""Configuration settings for the Telegram bot."""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Bot configuration
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError('TELEGRAM_BOT_TOKEN must be set in .env file')

# Debug mode configuration
DEBUG_MODE = os.getenv('DEBUG_MODE', 'False').lower() == 'true'

# Cache configuration
CACHE_MAX_SIZE = int(os.getenv('CACHE_MAX_SIZE', '100'))  # Maximum number of entries in cache
CACHE_EXPIRATION_SECONDS = int(os.getenv('CACHE_EXPIRATION_SECONDS', '1800'))  # 30 minutes

# Database configuration
DB_CLEANUP_DAYS = int(os.getenv('DB_CLEANUP_DAYS', '7'))  # Number of days to keep translations

# Language detection configuration
LANG_CONFIDENCE_THRESHOLD = float(os.getenv('LANG_CONFIDENCE_THRESHOLD', '0.75'))  # 75% confidence threshold

# Translation configuration
TRANSLATION_MODEL = os.getenv('TRANSLATION_LLM', 'llama-3.3-70b-versatile')  # Default to mixtral model

# Message formatting
MESSAGE_EMOJIS = {
    'user_info': '👤',
    'language': '🌐',
    'message': '📝',
    'translation': '🔄',
    'success': '✅'
}
