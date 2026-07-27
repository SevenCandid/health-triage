# REST API Specification (OpenAPI 3.0 Baseline)

## 1. Overview & Base Parameters

- **Base URL**: `https://api.healthtriage.org/api/v1`
- **Protocol**: HTTPS (TLS 1.3 Required)
- **Content-Type**: `application/json` (except SSE endpoints: `text/event-stream`)
- **Authentication**: `Authorization: Bearer <JWT_TOKEN>`

---

## 2. API Endpoint Matrix

| Method | Endpoint Path | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `POST` | `/auth/register` | Register new user account. | No |
| `POST` | `/auth/login` | Authenticate user & receive JWT token. | No |
| `POST` | `/triage/evaluate` | Evaluate symptom session & return urgency. | Optional |
| `GET` | `/triage/rules/latest` | Fetch latest versioned clinical rule tree. | No |
| `POST` | `/consultation/stream` | Stream Gemini AI enriched consultation (SSE). | Yes |
| `POST` | `/emergency/dispatch` | Send emergency alert log & GPS location. | Yes |
| `POST` | `/voice/transcribe` | Transcribe uploaded audio blob (Whisper STT). | Yes |
| `POST` | `/sync/outbox` | Bulk sync offline outbox queue items. | Yes |
| `GET` | `/users/me/profile` | Get logged-in user profile & emergency contacts.| Yes |
| `PUT` | `/users/me/profile` | Update user profile & emergency contacts. | Yes |
| `GET` | `/analytics/dashboard` | Get aggregate health triage analytics metrics.| Admin Only |

---

## 3. Key Endpoint Schemas & Payloads

### 3.1 `POST /api/v1/triage/evaluate`

Evaluates symptom inputs against backend rule tree.

#### Request Payload (JSON):
```json
{
  "primarySymptom": "fever",
  "languageCode": "tw",
  "patientAge": 28,
  "patientSex": "FEMALE",
  "answers": {
    "q_fever_duration": "more_than_3_days",
    "q_stiff_neck": "no",
    "q_rash_present": "yes"
  }
}
```

#### Response Payload (HTTP 200 OK):
```json
{
  "sessionId": "e4d7a840-77a8-48b4-a4f6-8c442c8d2a10",
  "urgencyLevel": "ORANGE",
  "primaryAction": {
    "en": "Visit a hospital or health centre today.",
    "tw": "Kɔ asopiti anaa akwahosan bea nnɛ."
  },
  "timeframeHours": 24,
  "firstAidProtocolId": "protocol_fever_rash",
  "evaluatedAt": "2026-07-26T12:00:00Z"
}
```

---

### 3.2 `POST /api/v1/sync/outbox`

Bulk ingests client-side IndexedDB outbox items created while offline.

#### Request Payload (JSON):
```json
{
  "batchId": "b3e04169-2a91-4475-9c8e-5b1234567890",
  "sessions": [
    {
      "localId": "local_101",
      "urgencyLevel": "YELLOW",
      "primarySymptom": "joint_pain",
      "symptomDetails": { "durationDays": 4 },
      "languageCode": "en",
      "conductedAt": "2026-07-26T10:15:00Z"
    }
  ]
}
```

#### Response Payload (HTTP 200 OK):
```json
{
  "processedCount": 1,
  "syncedIds": [
    { "localId": "local_101", "serverId": "f5c9e2b1-1234-4567-89ab-cdef01234567" }
  ],
  "errors": []
}
```

---

### 3.3 Standard Error Response Format

All error responses strictly follow the RFC 7807 Problem Details specification:

```json
{
  "type": "https://api.healthtriage.org/errors/validation-error",
  "title": "Invalid Input Data",
  "status": 422,
  "detail": "Field 'patientAge' must be an integer between 0 and 120.",
  "instance": "/api/v1/triage/evaluate"
}
```
