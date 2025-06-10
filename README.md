# AI Translator Telegram Bot

An AI-powered bot that enables real-time multilingual communication in Telegram groups. It automatically detects and translates non-English messages into English, then translates English replies back into the original sender’s language—allowing fluid, two-way conversations across languages.

## Features

- 🌐 Automatic language detection
- 🔄 Bidirectional translation (any language ↔️ English)
- 📝 Preserves message context and threading
- 💾 Message caching for improved performance
- 🗄️ Database storage for translation history
- 🛠️ Highly configurable

## Prerequisites

- Python 3.x
- A Telegram Bot Token (get it from [@BotFather](https://t.me/botfather))
- A Groq API Key (get it from [Groq Console](https://console.groq.com/docs/quickstart))

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ux-support-bot.git
cd ux-support-bot
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .\venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

## Configuration

The bot is configured through environment variables in the `.env` file:

### Required Settings
- `TELEGRAM_BOT_TOKEN`: Your Telegram bot token
- `GROQ_API_KEY`: Your Groq API key

### Optional Settings
- `TRANSLATION_LLM`: LLM model for translations (default: llama-3.3-70b-versatile)
- `DEBUG_MODE`: Enable debug logging (default: False)
- `CACHE_MAX_SIZE`: Maximum number of cached messages (default: 100)
- `CACHE_EXPIRATION_SECONDS`: Cache entry lifetime in seconds (default: 1800)
- `DB_CLEANUP_DAYS`: Days to keep translations in database (default: 7)
- `LANG_CONFIDENCE_THRESHOLD`: Minimum confidence for language detection (default: 0.75)

## Usage

1. Start the bot:
```bash
python bot.py
```

2. Add the bot to your Telegram group
> Important: The bot must be added to the group as an admin.

3. The bot will automatically:
   - Detect non-English messages
   - Translate them to English
   - Translate replies back to the original language (Must reply to the translated message) 

## How It Works

1. **Message Detection**:
   - Bot monitors group messages
   - Uses language detection to identify non-English messages
   - Only processes messages with high confidence (>75% by default)

2. **Translation Flow**:
   - User sends message in their language
   - Bot detects language and confidence level
   - If non-English, translates to English
   - Creates a threaded reply with:
     - User information
     - Original message
     - Detected language
     - English translation

3. **Agent Response**:
   - Support agent replies to the translated message
   - Bot automatically translates the reply to user's language
   - Sends translated response as a reply to original message

4. **Data Management**:
   - Translations are cached for performance
   - Historical data stored in SQLite database
   - Automatic cleanup of old entries

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
