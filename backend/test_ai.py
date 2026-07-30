import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

from app.services.ai.gemini_service import GeminiService

async def test_ai():
    service = GeminiService()
    print("Is available:", service.is_available)
    
    if service.is_available:
        symptom = service.extract_symptom("me ti y3 me ya, na me nsa nso y3 me ya", ["headache", "chest-pain", "fever", "joint-pain"], "tw")
        print("Extracted symptom:", symptom)
        
        translation = service.translate_question("Do you have a severe headache that came on suddenly?", "tw")
        print("Translation:", translation)
        
        explanation = service.generate_explanation("Symptoms: headache | Answers: node_1: yes", "Please seek immediate medical attention", True, "tw")
        print("Explanation:", explanation)
        
if __name__ == "__main__":
    asyncio.run(test_ai())
