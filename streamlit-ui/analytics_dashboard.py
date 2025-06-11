"""
Analytics Dashboard for Translation Bot
Visualizes MongoDB data using Streamlit - Modular Version
"""
import logging
import streamlit as st
import pandas as pd
from datetime import datetime

# Import modules
from modules.config import DEFAULT_DATE_RANGE
from modules.data_connection import init_connection, get_data
from modules.data_processing import (
    prepare_time_series_data,
    get_language_distribution,
    get_user_activity,
    get_translation_pairs,
    filter_by_language
)
from modules.visualizations import (
    create_language_distribution_chart,
    create_message_volume_chart,
    create_user_activity_chart,
    create_translation_pairs_chart
)
from modules.ui_components import (
    setup_page,
    create_date_filter,
    display_overview_metrics,
    display_message_contents,
    display_raw_data,
    create_footer
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Main entry point for the Streamlit dashboard"""
    
    # Setup page layout and styling
    setup_page()
    
    # Initialize MongoDB connection
    client = init_connection()
    
    if client:
        # Create date filter in sidebar
        start_date, end_date, start_datetime, end_datetime = create_date_filter()
        
        # Load data
        if start_date <= end_date:
            df = get_data(client, start_datetime, end_datetime)
            
            # If data is available
            if not df.empty:
                st.success(f"Loaded {len(df)} messages from MongoDB")
                
                # Display overview metrics
                display_overview_metrics(df)
                
                # Create tabs for better organization
                tab1, tab2, tab3, tab4, tab5 = st.tabs([
                    "Language Analysis", 
                    "Message Volume", 
                    "User Activity", 
                    "Message Contents", 
                    "Raw Data"
                ])
                
                with tab1:
                    # Language distribution
                    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                    st.markdown("<h3>Language Distribution</h3>", unsafe_allow_html=True)
                    
                    # Process data for language distribution
                    lang_counts = get_language_distribution(df)
                    if lang_counts is not None:
                        fig_lang = create_language_distribution_chart(lang_counts)
                        if fig_lang:
                            st.plotly_chart(fig_lang)
                        else:
                            st.info("Could not create language distribution chart.")
                    else:
                        st.info("Language information not found in data.")
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with tab2:
                    # Message volume over time
                    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                    st.markdown("<h3>Message Volume</h3>", unsafe_allow_html=True)
                    
                    # Process data for time series
                    daily_counts = prepare_time_series_data(df)
                    if daily_counts is not None:
                        fig_time = create_message_volume_chart(daily_counts)
                        if fig_time:
                            st.plotly_chart(fig_time)
                        else:
                            st.info("Could not create message volume chart.")
                    else:
                        st.info("No timestamp information found in data.")
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with tab3:
                    # User activity
                    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                    st.markdown("<h3>User Activity</h3>", unsafe_allow_html=True)
                    
                    # Process user activity data
                    user_data = get_user_activity(df)
                    if user_data:
                        fig_users = create_user_activity_chart(user_data)
                        if fig_users:
                            st.plotly_chart(fig_users)
                        else:
                            st.info("Could not create user activity chart.")
                    else:
                        st.info("User identification fields not found in data.")
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Translation pairs analysis in the same tab as user activity
                    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                    st.markdown("<h3>Translation Pairs</h3>", unsafe_allow_html=True)
                    
                    # Process translation pair data
                    lang_pairs = get_translation_pairs(df)
                    if lang_pairs is not None:
                        fig_pairs = create_translation_pairs_chart(lang_pairs)
                        if fig_pairs:
                            st.plotly_chart(fig_pairs)
                        else:
                            st.info("Could not create translation pairs chart.")
                    else:
                        st.info("No translation data found for analysis.")
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with tab4:
                    # Message Contents and Analysis
                    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                    st.markdown("<h3>Message Contents</h3>", unsafe_allow_html=True)
                    
                    # Display message contents
                    display_message_contents(df)
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with tab5:
                    # Raw data explorer
                    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                    display_raw_data(df)
                    st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.warning("No data found for the selected date range.")
        else:
            st.error("End date must be after start date.")
    else:
        st.error("Could not connect to MongoDB. Please check your connection settings.")
    
    # Add footer
    create_footer()

# Run the application
if __name__ == "__main__":
    main()
