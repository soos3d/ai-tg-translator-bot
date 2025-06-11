"""
Configuration settings for the Analytics Dashboard
"""
import os
import logging
import streamlit as st

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MongoDB connection parameters
# Try to get from Streamlit secrets first, then fallback to environment variables
try:
    MONGODB_URI = st.secrets['MONGODB_URI']
    MONGODB_DB_NAME = st.secrets['MONGODB_DB_NAME']
    MONGODB_COLLECTION_NAME = st.secrets['MONGODB_COLLECTION_NAME']

except FileNotFoundError:
    # Fallback to environment variables if secrets.toml doesn't exist
    logger.warning('No secrets.toml file found. Falling back to environment variables.')
    MONGODB_URI = os.environ.get('MONGODB_URI')
    MONGODB_DB_NAME = os.environ.get('MONGODB_DB_NAME', 'tg_translator')
    MONGODB_COLLECTION_NAME = os.environ.get('MONGODB_COLLECTION_NAME', 'messages')
    DB_CREDENTIALS = {}

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
