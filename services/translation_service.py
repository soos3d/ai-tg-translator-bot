"""Translation service module using Groq API."""
import os
from groq import Groq
from dotenv import load_dotenv
from config import TRANSLATION_MODEL

# Load environment variables to ensure API key is available
load_dotenv()

class TranslationService:
    """Service for translating text between languages using Groq API."""
    
    def __init__(self):
        """Initialize the translation service with Groq client."""
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY must be set in .env file")
        
        self.client = Groq(api_key=api_key)
        self.model = TRANSLATION_MODEL
    
    def translate_text(self, text: str, source_language: str, target_language: str = "en") -> str:
        """
        Translate text between languages using Groq LLM.
        
        Args:
            text (str): The text to translate
            source_language (str): The source language code (e.g., 'es', 'fr')
            target_language (str): The target language code (default: 'en' for English)
            
        Returns:
            str: The translated text in the target language
        """
        # Determine translation direction
        if source_language == target_language:
            return text  # No translation needed
            
        prompt = f"""
        Translate the following text from {source_language} to {target_language}:
        
        "{text}"
        
        Provide ONLY the translated text without any additional explanations, notes, or quotation marks around the text.
        """
        
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model=self.model,
            )
            
            return chat_completion.choices[0].message.content.strip()
        except Exception as e:
            # Log the error and return a default message
            print(f"Translation error: {e}")
            return f"[Translation failed: {e}]"
