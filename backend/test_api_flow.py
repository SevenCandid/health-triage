import httpx
import json

# Test full flow
r = httpx.post('http://localhost:8000/api/v1/assessment/start', json={
    'language_code': 'en',
    'consultation_mode': 'TEXT',
    'created_offline': False
})
print('Start status:', r.status_code)
session_id = r.json().get('session_id')
print('Session ID:', session_id)

r2 = httpx.post('http://localhost:8000/api/v1/assessment/symptoms', json={
    'session_id': session_id,
    'symptom_slug': 'headache'
})
print('Symptom status:', r2.status_code)
data = r2.json()
print('next_question:', json.dumps(data.get('next_question'), indent=2, ensure_ascii=True))
print('is_emergency:', data.get('is_emergency'))
print('severity:', data.get('severity'))
