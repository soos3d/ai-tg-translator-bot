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

2. Set up your Streamlit secrets:
```bash
# Copy the template file
cp .streamlit/secrets.toml.template .streamlit/secrets.toml

# Edit secrets.toml with your MongoDB credentials
```

3. Configure your `secrets.toml` with your MongoDB settings:
```toml
# MongoDB connection settings
mongodb_uri = "mongodb+srv://username:password@cluster.mongodb.net/"
mongodb_db_name = "tg_translator"
mongodb_collection_name = "messages"
```

> **Important**: Never commit your `secrets.toml` file to version control. It's already added to `.gitignore`.

## Usage

1. Run the Streamlit dashboard:
```bash
python3 -m streamlit run streamlit-ui/analytics_dashboard.py
```

2. Access the dashboard in your web browser:
- Local URL: http://localhost:8501
- Network URL: Will be shown in the terminal

### Deployment

When deploying to Streamlit Community Cloud:
1. Go to your app dashboard
2. Navigate to "Settings" → "Secrets"
3. Add your secrets in the same TOML format as your local `secrets.toml`

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
