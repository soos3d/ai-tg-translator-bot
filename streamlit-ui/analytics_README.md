# UX Support Bot Analytics Dashboard

This Streamlit dashboard provides visualization and analytics for the UX Support Bot's MongoDB data, helping you gain insights into message patterns, language distributions, and user engagement metrics.

## Features

- 📊 Overview metrics (total messages, unique users, active chats, languages)
- 🌐 Language distribution visualization
- 📈 Message volume trends over time
- 👥 User activity analysis
- 📏 Message length comparison between original and translated text
- 🔄 Translation language pair analysis
- 🔍 Raw data explorer

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure your MongoDB connection details are properly configured in your `.env` file:
```
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
MONGODB_DB_NAME=tg_translator
MONGODB_COLLECTION_NAME=messages
```

## Usage

Run the Streamlit dashboard:
```bash
python3 -m streamlit run streamlit-ui/analytics_dashboard.py 
```

This will start the dashboard on your local machine and automatically open it in your web browser (typically at http://localhost:8501).

## Dashboard Sections

### Filters
- **Date Range Selector**: Filter data by specific time periods

### Overview Metrics
- Quick stats showing total messages, unique users, active chats, and languages

### Language Distribution
- Pie chart showing the distribution of original message languages

### Message Volume
- Line chart displaying message volume trends over time

### User Activity
- Bar chart showing the most active users

### Message Length Analysis
- Box plots comparing character counts of original messages vs. English translations

### Translation Pairs
- Analysis of which languages are most frequently translated to English

### Raw Data Explorer
- Option to view and explore the raw data from MongoDB

## Notes

- The dashboard caches MongoDB data for 5 minutes to improve performance
- For large datasets, consider implementing additional filtering options
