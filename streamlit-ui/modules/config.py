"""
Configuration settings for the Analytics Dashboard
"""
import os
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# MongoDB connection parameters
MONGODB_URI = os.getenv('MONGODB_URI')
MONGODB_DB_NAME = os.getenv('MONGODB_DB_NAME', 'tg_translator')
MONGODB_COLLECTION_NAME = os.getenv('MONGODB_COLLECTION_NAME', 'messages')

# UI Configuration
PAGE_TITLE = "Translation Bot Analytics Dashboard"
LAYOUT = "wide"
SIDEBAR_STATE = "expanded"

# CSS Styling
CUSTOM_CSS = """
<style>
    .main-header {margin-bottom: 0px;}
    .block-container {padding-top: 2rem;}
    .metric-container {background-color: #1E1E1E; padding: 10px; border-radius: 5px; margin: 5px;}
    .chart-container {background-color: #1E1E1E; padding: 15px; border-radius: 5px; margin-bottom: 15px;}
    .stTabs [data-baseweb="tab-list"] {gap: 10px;}
    .stTabs [data-baseweb="tab"] {background-color: #1E1E1E; border-radius: 4px 4px 0px 0px;}
    .stTabs [aria-selected="true"] {background-color: #2C2C2C;}
</style>
"""

# Field path configurations for data extraction
ORIGINAL_TEXT_PATHS = [
    'message_original_text',
    'original_text',
    'message.original_text',
    'text'
]

ENGLISH_TEXT_PATHS = [
    'message_english_text',
    'english_text',
    'message.english_text',
    'translated_text'
]

# Default date range in days
DEFAULT_DATE_RANGE = 30
