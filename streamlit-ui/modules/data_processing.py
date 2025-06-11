"""
Data processing and transformation utilities
"""
import logging
import pandas as pd
from datetime import datetime
from .config import ORIGINAL_TEXT_PATHS, ENGLISH_TEXT_PATHS

logger = logging.getLogger(__name__)

def extract_content(row, field_paths):
    """Extract content from a row using a list of possible field paths"""
    logger.info(f"Trying to extract content from row with keys: {list(row.keys())}")
    
    # First try direct column access for flattened fields (most likely scenario based on logs)
    for path in field_paths:
        if path in row and row[path]:
            logger.info(f"Found text content in field '{path}': {row[path][:50]}...(truncated)" if isinstance(row[path], str) else f"Found non-string value: {row[path]}")
            return row[path]
    
    # Then try nested dictionary fields with dot notation
    for path in field_paths:
        if '.' in path:
            parts = path.split('.')
            if parts[0] in row and isinstance(row[parts[0]], dict):
                nested_dict = row[parts[0]]
                if parts[1] in nested_dict and nested_dict[parts[1]]:
                    value = nested_dict[parts[1]]
                    logger.info(f"Found content in nested path '{path}': {value[:50]}...(truncated)" if isinstance(value, str) else value)
                    return value
    
    # Finally check if message is a direct dictionary containing our target fields
    if 'message' in row and isinstance(row['message'], dict):
        nested_keys = list(row['message'].keys())
        for key in ['original_text', 'english_text', 'text']:
            if key in nested_keys and row['message'][key]:
                logger.info(f"Found text in message.{key}: {row['message'][key][:50]}...")
                return row['message'][key]
    
    logger.warning("Failed to extract content using any of the provided paths")
    return None

def get_original_text(row):
    """Extract original text from a row using various possible paths"""
    return extract_content(row, ORIGINAL_TEXT_PATHS)

def get_english_text(row):
    """Extract English text from a row using various possible paths"""
    return extract_content(row, ENGLISH_TEXT_PATHS)

def prepare_time_series_data(df):
    """Process dataframe for time series visualizations"""
    timestamp_field = 'timestamp'
    if timestamp_field not in df.columns or df[timestamp_field].isna().all():
        timestamp_field = 'created_at'
        logger.info(f"Using '{timestamp_field}' for time series visualization instead of timestamp")
    
    if timestamp_field not in df.columns or df[timestamp_field].isna().all():
        logger.warning("No valid timestamp field found in data")
        return None
    
    try:
        # Convert timestamps to datetime objects
        df["date"] = pd.to_datetime(df[timestamp_field], errors='coerce')
        
        # Extract just the date portion for grouping
        df["date_only"] = df["date"].dt.date
        
        # Drop NaT values and group by date
        valid_dates = df.dropna(subset=["date_only"])
        
        if valid_dates.empty:
            logger.warning("No valid dates found after conversion")
            return None
            
        # Group by date and create daily counts
        daily_counts = valid_dates.groupby("date_only").size().reset_index(name="count")
        return daily_counts
    except Exception as e:
        logger.error(f"Error processing timestamp data: {e}")
        import traceback
        logger.error(f"Timestamp processing error: {traceback.format_exc()}")
        return None

def get_language_distribution(df):
    """Process dataframe for language distribution visualizations"""
    if 'original_lang' not in df.columns or df['original_lang'].isna().all():
        logger.warning("No language data available for visualization")
        return None
        
    # Remove NaN values and count languages
    valid_langs = df['original_lang'].dropna()
    if valid_langs.empty:
        logger.warning("No valid language data found after filtering")
        return None
        
    lang_counts = valid_langs.value_counts().reset_index()
    lang_counts.columns = ["Language", "Count"]
    return lang_counts

def get_translation_pairs(df):
    """Process dataframe for translation pairs visualization"""
    if "original_lang" not in df.columns or df["original_lang"].isna().all():
        logger.warning("No language data available for translation pair analysis")
        return None
    
    try:
        # Only consider non-English original messages with valid language data
        non_en_df = df[df["original_lang"].astype(str).str.lower() != "en"].dropna(subset=["original_lang"])
        
        if non_en_df.empty:
            logger.warning("No non-English messages found for translation pair analysis")
            return None
            
        lang_pairs = non_en_df["original_lang"].value_counts().reset_index()
        lang_pairs.columns = ["Source Language", "Count"]
        lang_pairs["Target Language"] = "English"
        return lang_pairs
    except Exception as e:
        logger.error(f"Error processing translation pair data: {e}")
        return None

def get_user_activity(df):
    """Process dataframe for user activity visualizations"""
    user_fields = []
    if 'user_id' in df.columns:
        user_fields.append('user_id')
    if 'username' in df.columns:
        user_fields.append('username')
    elif 'user_username' in df.columns:
        user_fields.append('user_username')
    
    if not user_fields:
        logger.warning("No user identification fields found in data")
        return None
    
    try:
        # Group by available user fields
        user_counts = df.groupby(user_fields).size().reset_index(name="message_count")
        user_counts = user_counts.sort_values("message_count", ascending=False).head(10)
        
        # Select display field (prefer username over user_id)
        display_field = user_fields[-1]  # Last field in list (usually username if available)
        
        return {
            'user_counts': user_counts,
            'display_field': display_field
        }
    except Exception as e:
        logger.error(f"Error processing user activity data: {e}")
        return None

def filter_by_language(df, language_filter):
    """Filter dataframe by selected language"""
    if not language_filter or language_filter == 'All':
        return df
    
    if 'original_lang' in df.columns:
        return df[df['original_lang'] == language_filter]
    elif 'content.original_lang' in df.columns:
        return df[df['content.original_lang'] == language_filter]
    else:
        return df
