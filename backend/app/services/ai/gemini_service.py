import os
import json
import logging
from typing import Optional, List, Dict, Any

from google import genai
from google.genai import types

logger = logging.getLogger(__name__)

class GeminiService:
    """Service to interact with Google Gemini AI for health triage language understanding."""

    def __init__(self, api_key: Optional[str] = None):
        if not api_key:
            api_key = os.getenv("GEMINI_API_KEY")
        self.api_key = api_key
        
        self.client = None
        self.is_available = False
        
        if self.api_key and self.api_key != "mock-dev-gemini-key":
            try:
                self.client = genai.Client(api_key=self.api_key)
                self.is_available = True
                logger.info("GeminiService initialized successfully.")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini Client: {e}")
        else:
            logger.warning("GeminiService initialized in mock/fallback mode. Invalid or missing API key.")

    def extract_symptom(self, text: str, allowed_slugs: List[str], language_code: str = "en") -> Optional[str]:
        """Extracts a canonical symptom slug from free-form user text."""
        if not self.is_available:
            return None
            
        lang = "English" if language_code == "en" else "Akan/Twi"
        
        prompt = (
            f"You are a medical triage assistant. The user is speaking in {lang}. "
            "Your task is to identify the primary symptom they are describing and map it to exactly ONE "
            "of the allowed canonical symptom slugs. If the user mentions multiple, pick the most severe/primary one. "
            "If none match or it's unclear, return 'unclear'.\n\n"
            f"Allowed slugs: {json.dumps(allowed_slugs)}\n\n"
            f"User text: \"{text}\"\n\n"
            "Return ONLY the exact slug string or 'unclear'."
        )
        
        try:
            response = self.client.models.generate_content(
                model='gemini-2.0-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.0,
                )
            )
            result = response.text.strip().lower()
            if result in allowed_slugs:
                return result
            return None
        except Exception as e:
            logger.error(f"Gemini extract_symptom error: {e}")
            return None

    def translate_question(self, question_en: str, language_code: str) -> str:
        """Translates a follow-up question to the target language if necessary."""
        if not self.is_available or language_code == "en":
            return question_en
            
        lang = "Akan/Twi (Ghana)"
        prompt = (
            f"Translate the following medical triage follow-up question into natural, conversational {lang}. "
            "Keep the terminology simple and suitable for the general public, while preserving the exact medical meaning. "
            "Return ONLY the translated text, without quotes or extra explanation.\n\n"
            f"Question: \"{question_en}\""
        )
        
        try:
            response = self.client.models.generate_content(
                model='gemini-2.0-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.2,
                )
            )
            return response.text.strip()
        except Exception as e:
            logger.error(f"Gemini translate_question error: {e}")
            return question_en

    def generate_explanation(self, conversation_context: str, recommendation_summary: str, is_emergency: bool, language_code: str) -> str:
        """Generates a natural, reassuring explanation of the assessment results."""
        if not self.is_available:
            # Fallback to the rule engine's raw recommendation
            return recommendation_summary
            
        lang = "English" if language_code == "en" else "Akan/Twi (Ghana)"
        tone = "urgent and direct, advising immediate medical attention" if is_emergency else "calm, reassuring, and providing clear guidance"
        
        prompt = (
            f"You are a helpful and professional health triage assistant. "
            f"Summarize the following health assessment and provide the final recommendation to the user. "
            f"Your response must be in {lang}. Your tone should be {tone}.\n\n"
            "Important Rules:\n"
            "1. Do NOT make a medical diagnosis. Say 'Based on what you've shared...' rather than 'You have...'\n"
            "2. Convey the recommendation clearly.\n"
            "3. Keep it concise (3-4 sentences max).\n\n"
            f"Conversation Context:\n{conversation_context}\n\n"
            f"Rule Engine Recommendation:\n{recommendation_summary}"
        )
        
        try:
            response = self.client.models.generate_content(
                model='gemini-2.0-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.4,
                )
            )
            return response.text.strip()
        except Exception as e:
            logger.error(f"Gemini generate_explanation error: {e}")
            return recommendation_summary
