import os
import json
import re
import difflib
from typing import Optional, Dict, List

class SymptomNormalizer:
    def __init__(self):
        self.dictionary: Dict[str, List[str]] = {}
        self.load_dictionary()

    def load_dictionary(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        dict_path = os.path.join(current_dir, "symptom_dictionary.json")
        try:
            with open(dict_path, "r", encoding="utf-8") as f:
                self.dictionary = json.load(f)
        except Exception:
            self.dictionary = {}

    def clean_text(self, text: str) -> str:
        text = text.lower().strip()
        # Remove punctuation
        text = re.sub(r"[^\w\s-]", "", text)
        # Normalise multiple spaces
        text = re.sub(r"\s+", " ", text)
        return text

    def normalize(self, user_text: str) -> Optional[str]:
        cleaned = self.clean_text(user_text)
        if not cleaned:
            return None

        # 1. Exact or Substring Mappings first
        for slug, phrases in self.dictionary.items():
            for phrase in phrases:
                phrase_cleaned = self.clean_text(phrase)
                if cleaned == phrase_cleaned or phrase_cleaned in cleaned or cleaned in phrase_cleaned:
                    return slug

        # 2. Token overlap and Fuzzy matching using difflib
        best_slug = None
        best_ratio = 0.0

        user_tokens = set(cleaned.split())

        for slug, phrases in self.dictionary.items():
            for phrase in phrases:
                phrase_cleaned = self.clean_text(phrase)
                phrase_tokens = set(phrase_cleaned.split())
                
                # Jaccard-like token intersection
                intersection = user_tokens.intersection(phrase_tokens)
                if intersection:
                    overlap_ratio = len(intersection) / max(len(user_tokens), len(phrase_tokens))
                    if overlap_ratio > best_ratio and overlap_ratio >= 0.3:
                        best_ratio = overlap_ratio
                        best_slug = slug

                # difflib sequence matcher
                ratio = difflib.SequenceMatcher(None, cleaned, phrase_cleaned).ratio()
                if ratio > best_ratio and ratio >= 0.5:
                    best_ratio = ratio
                    best_slug = slug

        return best_slug

    def normalize_with_ai(self, user_text: str, language_code: str, gemini_service) -> tuple[Optional[str], Optional[str]]:
        """Attempts to normalize using AI, then falls back to fuzzy matching. Returns (slug, clarification_msg)"""
        if not user_text.strip():
            return None, None
            
        allowed_slugs = list(self.dictionary.keys())
        ai_slug, clarification = gemini_service.extract_symptom(user_text, allowed_slugs, language_code)
        
        if ai_slug and ai_slug in allowed_slugs:
            return ai_slug, None
        
        if clarification:
            return None, clarification
            
        fuzzy_slug = self.normalize(user_text)
        return fuzzy_slug, None
