import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from app.services.symptom_understanding.symptom_normalizer import SymptomNormalizer

def test():
    normalizer = SymptomNormalizer()
    cases = {
        "My head hurts": "headache",
        "My head is killing me": "headache",
        "I've had a headache all day": "headache",
        "I'm feeling hot": "fever",
        "My whole body feels warm": "fever",
        "I keep coughing": "cough",
        "I can't stop coughing": "cough",
        "I'm finding it hard to breathe": "shortness-of-breath",
        "My chest feels tight": "chest-pain",
    }
    
    passed = 0
    for text, expected in cases.items():
        res = normalizer.normalize(text)
        if res == expected:
            print(f"PASS: '{text}' -> {res}")
            passed += 1
        else:
            print(f"FAIL: '{text}' -> expected {expected}, got {res}")
            
    print(f"Score: {passed}/{len(cases)}")

if __name__ == "__main__":
    test()
