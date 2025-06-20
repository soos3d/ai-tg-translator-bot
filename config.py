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

# MongoDB configuration
MONGODB_URI = os.getenv('MONGODB_URI')
MONGODB_DB_NAME = os.getenv('MONGODB_DB_NAME', 'tg_translator')
MONGODB_COLLECTION_NAME = os.getenv('MONGODB_COLLECTION_NAME', 'messages')
if not MONGODB_URI:
    logger = __import__('logging').getLogger(__name__)
    logger.warning('MONGODB_URI not set in .env file. MongoDB storage will be disabled.')

# Language detection configuration
LANG_CONFIDENCE_THRESHOLD = float(os.getenv('LANG_CONFIDENCE_THRESHOLD', '0.75'))  # 75% confidence threshold

# Translation configuration
TRANSLATION_MODEL = os.getenv('TRANSLATION_LLM', 'llama-3.3-70b-versatile')  # Default to mixtral model

# FAQ answering configuration
FAQ_MODEL = os.getenv('FAQ_LLM', 'llama-3.3-70b-versatile')  # Default to same model as translation
FAQ_ENABLED = os.getenv('FAQ_ENABLED', 'True').lower() == 'true'  # Enable/disable FAQ answering

FAQ_CONTENT="""
Q: I can’t log into my account. What should I do?
A: Please try resetting your password using the “Forgot Password” option. If that doesn’t work, contact support with your registered email.

Q: How do I change the email linked to my account?
A: You can change your email by going to Settings > Account > Email, and following the verification steps.

Q: Why is my payment failing?
A: Payment failures can happen due to insufficient funds, expired cards, or bank restrictions. Please check your payment method or try another one.

Q: Is the app available in other languages?
A: Yes, you can change the language in Settings > Preferences > Language.

Q: How can I delete my account?
A: Go to Settings > Account > Delete Account. Follow the confirmation steps. This process is irreversible.

Q: I made a purchase but didn’t receive the item.
A: We’re sorry! Please share the purchase receipt or transaction ID, and we’ll look into it immediately.

Q: Can I use the app offline?
A: Some features work offline, but you’ll need internet access for real-time updates and syncing.

Q: The app keeps crashing. What should I do?
A: Try updating the app, clearing the cache, or reinstalling. If the issue persists, contact support with your device info and app version.

Q: How do I invite someone to my team/project?
A: Tap on the project, select “Team” or “Share,” then enter the email of the person you’d like to invite.

Q: Do you support dark mode?
A: Yes! Enable it in Settings > Appearance > Theme.

Q: I signed up with the wrong email. Can I fix it?
A: Yes, but you’ll need to verify a new email. Contact support if you’re locked out.

Q: How do I export my data?
A: Go to Settings > Data > Export, and choose your preferred format.

Q: What should I do if I see inappropriate content in the app?
A: Tap on the content and select “Report.” Our team will review it promptly.

Q: I want to cancel my subscription. Will I get a refund?
A: You can cancel anytime from Settings > Subscription. Refunds depend on your billing cycle and our refund policy.

Q: Is there a desktop version of the app?
A: Yes, we offer web and desktop apps for Windows and macOS.

Q: Can I use the app on multiple devices?
A: Absolutely. Just log in with the same account across all your devices.

Q: How often is my data backed up?
A: Data is backed up daily on our servers for all active accounts.

Q: Can I customize notifications?
A: Yes. Go to Settings > Notifications to choose which alerts you receive.

Q: How do I reset the app to default settings?
A: In Settings > Advanced > Reset App, you’ll find the option to restore defaults. This won’t delete your account.
"""

# The system prompt that contains FAQ information
FAQ_SYSTEM_PROMPT = os.getenv('FAQ_SYSTEM_PROMPT', '''
You are a support agent that answers questions based on the FAQ information provided.
If the answer to a question is clearly covered in the FAQ, provide a concise and accurate response.
If the question is not covered in the FAQ or you're unsure, respond with "I don't have information on that topic in the FAQ."
Do not make up information that isn't in the FAQ.

FAQ CONTENT:
{0}
''').format(FAQ_CONTENT)

# Message formatting
MESSAGE_EMOJIS = {
    'user_info': '👤',
    'language': '🌐',
    'message': '📝',
    'translation': '🔄',
    'success': '✅',
    'faq': '❓'
}
