"""
Reusable UI components and layout elements for the analytics dashboard
"""
import logging
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from .config import CUSTOM_CSS
from .data_processing import extract_content, get_original_text, get_english_text

logger = logging.getLogger(__name__)

def setup_page():
    """Configure page settings and apply custom CSS"""
    # Set page config with dark theme and wide layout
    st.set_page_config(
        page_title="Translation Bot Analytics Dashboard", 
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Apply custom CSS
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    
    # Title with better styling
    st.markdown("<h1 class='main-header'>Translation Bot Analytics Dashboard</h1>", unsafe_allow_html=True)
    st.write("This dashboard provides analytics and insights from the translation TG bot (only if you are using MongoDB as permanent storage). Explore message patterns, language distributions, and user engagement metrics.")

def create_date_filter():
    """Create date range filter in sidebar"""
    st.sidebar.header("Filters & Controls")

    # Calculate default date range (last 30 days)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)

    # Add date range with more visual separation
    st.sidebar.subheader("Date Range")
    col1, col2 = st.sidebar.columns(2)
    start_date = col1.date_input("Start", value=start_date)
    end_date = col2.date_input("End", value=end_date)

    # Convert date to datetime for MongoDB query
    start_datetime = datetime.combine(start_date, datetime.min.time())
    end_datetime = datetime.combine(end_date, datetime.max.time())
    
    return start_date, end_date, start_datetime, end_datetime

def display_overview_metrics(df):
    """Display overview metrics in a row of cards"""
    st.markdown("<h2>Overview Metrics</h2>", unsafe_allow_html=True)
    
    metrics_cols = st.columns(4)
    
    total_messages = len(df)
    
    # Handle user metrics with proper field names
    unique_users = 0
    if 'user_id' in df.columns:
        unique_users = df["user_id"].nunique()
    elif 'user_user_id' in df.columns:
        unique_users = df["user_user_id"].nunique()
        
    # Handle chat metrics with proper field names
    active_chats = 0
    if 'chat_id' in df.columns:
        active_chats = df["chat_id"].nunique()
    elif 'chat_chat_id' in df.columns:
        active_chats = df["chat_chat_id"].nunique()
    
    # Handle language metrics with proper field names
    unique_langs = 0
    if 'original_lang' in df.columns:
        unique_langs = df["original_lang"].dropna().nunique()
    elif 'content_original_lang' in df.columns:
        unique_langs = df["content_original_lang"].dropna().nunique()
    
    with metrics_cols[0]:
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.metric("Total Messages", total_messages)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with metrics_cols[1]:
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.metric("Unique Users", unique_users)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with metrics_cols[2]:
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.metric("Active Chats", active_chats)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with metrics_cols[3]:
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.metric("Languages", unique_langs)
        st.markdown('</div>', unsafe_allow_html=True)

def create_language_filter(df):
    """Create language filter dropdown"""
    language_filter = None
    
    if 'original_lang' in df.columns and not df['original_lang'].isna().all():
        languages = ['All'] + sorted(df['original_lang'].dropna().unique().tolist())
        language_filter = st.selectbox('Filter by language:', languages)
    elif 'content.original_lang' in df.columns and not df['content.original_lang'].isna().all():
        languages = ['All'] + sorted(df['content.original_lang'].dropna().unique().tolist()) 
        language_filter = st.selectbox('Filter by language:', languages)
    
    return language_filter

def display_message_contents(df):
    """Display message contents in expandable sections"""
    # Check for content fields
    content_columns = [col for col in df.columns if 'text' in col.lower()]
    logger.info(f"Found these text-related columns: {content_columns}")
    
    # Check if we have any content to show
    has_content = 'message_original_text' in df.columns
    
    if not has_content and 'message' in df.columns:
        if df['message'].apply(lambda x: isinstance(x, dict) and 'original_text' in x).any():
            has_content = True
            logger.info("Found text content in the nested 'message' dictionary field")
    
    if not has_content:
        for col in df.columns:
            if any(content_field in col.lower() for content_field in ['text', 'content', 'message']):
                has_content = True
                break
    
    if not has_content:
        st.info("No message content found in the data.")
        return
    
    # Add language filter
    language_filter = create_language_filter(df)
    
    # Filter dataframe by language if selected
    from .data_processing import filter_by_language
    display_df = filter_by_language(df, language_filter)
    
    # Sort by timestamp if available
    if 'timestamp' in display_df.columns:
        display_df = display_df.sort_values('timestamp', ascending=False)
    elif 'created_at' in display_df.columns:
        display_df = display_df.sort_values('created_at', ascending=False)
    
    st.write(f"Showing {len(display_df)} messages")
    
    # Display each message in an expander
    for i, row in display_df.iterrows():
        # Extract metadata for title
        timestamp = row.get('timestamp') or row.get('created_at')
        
        # Get language
        lang = None
        for lang_field in ['original_lang', 'content.original_lang']:
            if lang_field in row and not pd.isna(row[lang_field]):
                lang = row[lang_field]
                break
        if not lang and isinstance(row.get('content'), dict):
            lang = row['content'].get('original_lang')
            
        # Get username
        username = None
        for user_field in ['username', 'user_username', 'user.username']:
            if user_field in row and not pd.isna(row[user_field]):
                username = row[user_field]
                break
        if not username and isinstance(row.get('user'), dict):
            username = row['user'].get('username')
        
        # Format timestamp
        if timestamp:
            if isinstance(timestamp, pd.Timestamp) or isinstance(timestamp, datetime):
                timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M")
            else:
                timestamp_str = str(timestamp)
        else:
            timestamp_str = "Unknown time"
            
        title = f"{timestamp_str} - {lang.upper() if lang else 'Unknown lang'}"
        if username:
            title += f" - {username}"
            
        # Display message content in expander
        with st.expander(title):
            # Get original text
            original_text = get_original_text(row)
            
            if original_text:
                st.markdown(f"**Original Message:**")
                st.markdown(f"```\n{original_text}\n```")
            
            # Get English translation
            english_text = get_english_text(row)
            if english_text and english_text != original_text:
                st.markdown(f"**English Translation:**")
                st.markdown(f"```\n{english_text}\n```")
            
            # Display metadata
            st.markdown("**Metadata:**")
            metadata = {}
            
            # Check for metadata fields
            for key in ['original_lang', 'user_id', 'chat_id', 'message_id']:
                if key in row and not pd.isna(row[key]):
                    metadata[key] = row[key]
                    
            # Check nested content dict
            if isinstance(row.get('content'), dict):
                for key in ['original_lang']:
                    if key in row['content'] and key not in metadata:
                        metadata[f"content.{key}"] = row['content'][key]
                        
            # Check nested user dict
            if isinstance(row.get('user'), dict):
                for key in ['id', 'username', 'first_name']:
                    if key in row['user'] and f"user_{key}" not in metadata:
                        metadata[f"user.{key}"] = row['user'][key]
                        
            # Check nested chat dict
            if isinstance(row.get('chat'), dict):
                for key in ['id', 'type', 'title']:
                    if key in row['chat'] and f"chat_{key}" not in metadata:
                        metadata[f"chat.{key}"] = row['chat'][key]
                        
            st.json(metadata)

def display_raw_data(df):
    """Display raw data with search functionality"""
    st.markdown("<h3>Raw Data Explorer</h3>", unsafe_allow_html=True)
    
    # Add search functionality
    search_term = st.text_input("Search in data", "")
    if search_term:
        filtered_df = df[df.astype(str).apply(lambda row: row.str.contains(search_term, case=False).any(), axis=1)]
        st.dataframe(filtered_df, use_container_width=True)
    else:
        st.dataframe(df, use_container_width=True)

def create_footer():
    """Create footer with version information"""
    st.sidebar.markdown("---")
    st.sidebar.info("Translation Bot Analytics Dashboard v1.0")
