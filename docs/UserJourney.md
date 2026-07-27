# User Journey Specifications

## 1. Overview

This document illustrates the primary user journeys and interaction flows within the **Health Triage Assistant**. It covers both offline and online scenarios, detailing how users navigate through acute symptom evaluation, voice input, emergency handling, and profile configuration.

---

## 2. Key User Journeys

### Journey 1: Offline Acute Symptom Triage (Kwame in Ejura)

**Context**: Kwame is in a rural area with no cellular internet. He develops severe fever and joint pains at midnight. He speaks Twi.

```mermaid
sequenceDiagram
    autonumber
    actor User as Kwame (User)
    participant PWA as React PWA (Offline)
    participant SW as Service Worker
    participant DB as IndexedDB
    participant Engine as JS Rule Engine

    User->>PWA: Opens PWA App
    SW->>PWA: Serves cached app shell & Twi assets (Sub-1s)
    User->>PWA: Toggles language to "Twi"
    PWA->>User: Renders Twi UI text & spoken audio option
    User->>PWA: Selects "Triage Intake" (Symptom Assessment)
    PWA->>Engine: Launches Offline Triage Flow
    Engine->>PWA: Prompt: "What is your main symptom?"
    User->>PWA: Selects "Fever / Abiyede"
    Engine->>PWA: Prompt: "Any stiff neck, confusion, or dark spots?"
    User->>PWA: Answers "No"
    Engine->>PWA: Evaluate Rule Node (Fever + High Temp + Duration > 3 days)
    Engine->>PWA: Returns Urgency: YELLOW (Urgent - Visit Clinic within 24h)
    PWA->>DB: Store Triage Record in IndexedDB Outbox
    PWA->>User: Render Twi Triage Card & Spoken Audio Summary
```

#### Step-by-Step Breakdown:
1. **Launch**: App opens instantly from Service Worker cache without network check.
2. **Language Selection**: Kwame taps "Twi". Interface re-renders immediately with localized labels.
3. **Intake Assessment**: Interactive step-through presents clear, single-question screens with large touch targets and optional audio playback.
4. **Offline Evaluation**: The JS Rule Engine evaluates responses in memory ($<10$ ms), identifying a moderate risk fever without red flags.
5. **Output**: Displays a **YELLOW (Urgent)** care card in Twi, instructing him to visit the local health post in the morning, listing hydration first-aid steps, and saving the report locally.

---

### Journey 2: Online Voice Consultation with Gemini AI Enhancement (Abena)

**Context**: Abena has an active 4G data connection. Her toddler has a cough and skin rash. She wants to speak her symptoms in English.

```mermaid
sequenceDiagram
    autonumber
    actor User as Abena (User)
    participant PWA as React PWA
    participant STT as Web Speech API
    participant API as FastAPI Backend
    participant Engine as Python Rule Engine
    participant Gemini as Google Gemini AI
    participant DB as PostgreSQL

    User->>PWA: Taps "Voice Consultation"
    User->>PWA: Speaks: "My child has been coughing for 2 days and developed a red rash on his arms."
    PWA->>STT: Record & Transcribe Audio
    STT->>PWA: Text Transcript String
    PWA->>API: POST /api/v1/consultation/evaluate (Transcript + Profile)
    API->>Engine: Parse Symptoms & Run Rule Tree
    Engine->>API: Rule Result (Urgency: ORANGE, Symptom: Pediatric Rash + Cough)
    API->>Gemini: Prompt (Rule Result + User Transcript + Empathetic Guardrails)
    Gemini->>API: Streamed Response ("I understand you are concerned about your child's rash...")
    API->>PWA: Stream JSON Response (Severity + AI Text)
    API->>DB: Persist Consultation Record
    PWA->>User: Display ORANGE Triage Card + Audio Synthesis of Advice
```

#### Step-by-Step Breakdown:
1. **Voice Input**: Abena presses and holds the mic button to speak naturally.
2. **Transcription**: Web Speech API converts audio to text transcript.
3. **Backend Rule Evaluation**: FastAPI passes extracted entities to the backend Rule Engine, which assigns **ORANGE (Very Urgent)** due to pediatric cough + rash guidelines.
4. **Gemini AI Augmentation**: Gemini AI generates a supportive, easy-to-understand explanation emphasizing urgent clinic evaluation while comforting the parent.
5. **Streaming Output**: The UI streams Gemini's response token-by-token and renders an ORANGE alert banner.

---

### Journey 3: Emergency Panic Activation & SMS Dispatch

**Context**: A user experiences sudden, crushing chest pain.

```mermaid
sequenceDiagram
    autonumber
    actor User as Patient / Bystander
    participant PWA as React PWA
    participant Geo as Browser Geolocation API
    participant SMS as Native SMS Handler / Tel Link

    User->>PWA: Taps Red "EMERGENCY" Button (Any Screen)
    PWA->>PWA: Immediately Trigger RED Severity State
    PWA->>Geo: Request Current GPS Coordinates
    Geo-->>PWA: Lat: 5.6037, Long: -0.1870 (Accuracy 12m)
    PWA->>User: Display Emergency Action Screen
    PWA->>User: Render Offline CPR / Chest Pain First-Aid Card
    User->>PWA: Taps "Send SMS Alert to Emergency Contacts"
    PWA->>SMS: Launch sms: protocol with pre-filled payload
    Note over SMS: "EMERGENCY ALERT: Kwame needs immediate help! GPS: https://maps.google.com/?q=5.6037,-0.1870"
    User->>SMS: Confirm Send SMS
```

---

### Journey 4: Profile & Sync Status Journey

```mermaid
stateDiagram-v2
    [*] --> OfflineState: App Launch (No Network)
    OfflineState --> CreateTriage: User completes triage
    CreateTriage --> SaveIndexedDB: Saved to Outbox Table
    SaveIndexedDB --> WaitingForNetwork: Status: "Pending Sync"
    WaitingForNetwork --> OnlineState: Network Connection Detected
    OnlineState --> TriggerSync: Service Worker Background Sync Fired
    TriggerSync --> APIPost: POST /api/v1/sync/outbox
    APIPost --> SyncSuccess: Server returns HTTP 200 OK
    SyncSuccess --> UpdateIndexedDB: Status: "Synced" in Local DB
```
