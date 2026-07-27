import httpx
import json

# Step 1: Start session
r = httpx.post('http://localhost:8000/api/v1/assessment/start', json={
    'language_code': 'en', 'consultation_mode': 'TEXT', 'created_offline': False
})
session_id = r.json()['session_id']
print('Session ID:', session_id)

# Step 2: Submit symptom
r2 = httpx.post('http://localhost:8000/api/v1/assessment/symptoms', json={
    'session_id': session_id, 'symptom_slug': 'headache'
})
data2 = r2.json()
print('Symptom status:', r2.status_code)
nq = data2.get('next_question', {})
print('Next question node_id:', nq.get('node_id'))

# Step 3: Submit answer
r3 = httpx.post('http://localhost:8000/api/v1/assessment/answer', json={
    'session_id': session_id,
    'node_id': nq.get('node_id'),
    'answer_value': 'sudden',
    'answer_raw_text': None
})
print('Answer status:', r3.status_code)
print('Answer response:', json.dumps(r3.json(), indent=2, ensure_ascii=True))
