"""FAQ answering service using Groq API."""
import os
import logging
from groq import Groq
from dotenv import load_dotenv
from config import FAQ_MODEL, FAQ_SYSTEM_PROMPT

# Load environment variables to ensure API key is available
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

class FaqService:
    """Service for answering questions based on FAQ content using Groq API."""
    
    def __init__(self):
        """Initialize the FAQ service with Groq client."""
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY must be set in .env file")
        
        self.client = Groq(api_key=api_key)
        self.model = FAQ_MODEL
        self.system_prompt = FAQ_SYSTEM_PROMPT
    
    def answer_question(self, question: str) -> str:
        """
        Answer a question using the FAQ reference through Groq LLM.
        
        Args:
            question (str): The user's question
            
        Returns:
            str: The answer to the question or None if not answerable from FAQ
        """
        print(question)
        print(self.system_prompt)
        try:
            # Create the prompt with the FAQ reference included in the system prompt
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": self.system_prompt
                    },
                    {
                        "role": "user",
                        "content": question
                    }
                ],
                model=self.model,
                temperature=0.1,  # Low temperature for more deterministic responses
            )
            
            response = chat_completion.choices[0].message.content.strip()
            print(response)
            # Check if the response indicates the answer is not in the FAQ
            if "I don't have information on that" in response or "not in the FAQ" in response:
                logger.info(f"Question not answerable from FAQ: {question}")
                return None
            
            logger.info(f"Answered question from FAQ: {question}")
            return response
            
        except Exception as e:
            logger.error(f"FAQ answering error: {e}")
            return None
