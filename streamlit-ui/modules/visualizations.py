"""
Visualization functions for the analytics dashboard
"""
import logging
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

logger = logging.getLogger(__name__)

def create_language_distribution_chart(lang_counts):
    """Create a pie chart showing language distribution"""
    if lang_counts is None or lang_counts.empty:
        logger.warning("Cannot create language distribution chart: No data")
        return None
    
    try:
        fig = px.pie(
            lang_counts,
            values="Count",
            names="Language",
            title="Messages by Language",
            hole=0.4
        )
        return fig
    except Exception as e:
        logger.error(f"Error creating language distribution chart: {e}")
        return None

def create_message_volume_chart(daily_counts):
    """Create a line or bar chart showing message volume over time"""
    if daily_counts is None or daily_counts.empty:
        logger.warning("Cannot create message volume chart: No data")
        return None
    
    try:
        # If we only have one data point, create a bar chart
        if len(daily_counts) == 1:
            logger.info("Only one data point found, creating bar chart")
            fig = px.bar(
                daily_counts,
                x="date_only",
                y="count",
                title="Daily Message Volume",
                labels={"date_only": "Date", "count": "Number of Messages"}
            )
        else:
            # Otherwise create a line chart
            fig = px.line(
                daily_counts,
                x="date_only",
                y="count",
                title="Daily Message Volume",
                labels={"date_only": "Date", "count": "Number of Messages"}
            )
        return fig
    except Exception as e:
        logger.error(f"Error creating message volume chart: {e}")
        return None

def create_user_activity_chart(user_data):
    """Create a bar chart showing user activity"""
    if user_data is None:
        logger.warning("Cannot create user activity chart: No data")
        return None
    
    try:
        user_counts = user_data['user_counts']
        display_field = user_data['display_field']
        
        fig = px.bar(
            user_counts,
            x=display_field,
            y="message_count",
            title="Top 10 Most Active Users",
            labels={display_field: "User", "message_count": "Number of Messages"}
        )
        return fig
    except Exception as e:
        logger.error(f"Error creating user activity chart: {e}")
        return None

def create_translation_pairs_chart(lang_pairs, max_display=10):
    """Create a bar chart showing translation language pairs"""
    if lang_pairs is None or lang_pairs.empty:
        logger.warning("Cannot create translation pairs chart: No data")
        return None
    
    try:
        # Display top N or less if fewer languages available
        display_count = min(max_display, len(lang_pairs))
        
        fig = px.bar(
            lang_pairs.head(display_count),
            x="Source Language",
            y="Count",
            title=f"Top {display_count} Translation Language Pairs",
            labels={"Source Language": "Source Language", "Count": "Number of Translations"}
        )
        return fig
    except Exception as e:
        logger.error(f"Error creating translation pairs chart: {e}")
        return None
