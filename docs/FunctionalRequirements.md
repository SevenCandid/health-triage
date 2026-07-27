# Functional Requirements Specification

## 1. Overview & Traceability Matrix

This document defines the functional requirements for the **Health Triage Assistant**. Each requirement is uniquely identified (`FR-xxx`) for system traceability across backend, frontend, database, and testing specifications.

---

## 2. Detailed Functional Requirements

### 2.1 Triage Engine & Decision Tree (`FR-TRG`)

| ID | Title | Priority | Requirement Description |
| :--- | :--- | :--- | :--- |
| **FR-TRG-001** | Rule Evaluation | **P0** | The system MUST evaluate symptom inputs against a deterministic clinical decision tree (Manchester/ESI inspired) and assign one of 4 severity levels: `RED` (Emergency), `ORANGE` (Very Urgent), `YELLOW` (Urgent), `GREEN` (Non-Urgent). |
| **FR-TRG-002** | Red-Flag Override | **P0** | If any "Red Flag" condition is true (e.g., severe dyspnea, central chest pain, unresponsiveness, severe bleeding), the system MUST immediately terminate evaluation and output a `RED` triage severity card. |
| **FR-TRG-003** | Offline Rule Execution | **P0** | The triage rule engine MUST execute 100% locally in the browser JavaScript engine without requesting network connectivity. |
| **FR-TRG-004** | Triage Result Summary | **P0** | The system MUST generate a structured triage report containing: Severity Level, Immediate Action Steps, Recommended Healthcare Facility Type, Timeframe to Care, and Relevant First-Aid Protocol. |
| **FR-TRG-005** | Rule Versioning | **P1** | The engine MUST support versioned rule trees in JSON format, updating client-side cached rules whenever connected to the server. |

---

### 2.2 Voice & Text Consultation (`FR-CNS`)

| ID | Title | Priority | Requirement Description |
| :--- | :--- | :--- | :--- |
| **FR-CNS-001** | Multimodal Input | **P0** | Users MUST be able to initiate a consultation via text typing or voice speech input. |
| **FR-CNS-002** | Natural Language Extraction | **P1** | When online, the system MUST pass user text/speech transcripts to Google Gemini AI to extract symptom entities, duration, and anatomical location. |
| **FR-CNS-003** | AI Summary & Guidance | **P1** | When online, Gemini AI MUST produce an empathetic, conversational explanation of the rule engine's triage result, adhering strictly to the assigned severity level. |
| **FR-CNS-004** | Offline Consultation Fallback | **P0** | When offline, the consultation interface MUST switch to interactive questionnaire mode, walking the user step-by-step through decision tree nodes. |
| **FR-CNS-005** | Audio Playback | **P0** | Users MUST be able to tap an audio button to listen to the triage output spoken in their selected language (English or Twi). |

---

### 2.3 Emergency Centre (`FR-EMG`)

| ID | Title | Priority | Requirement Description |
| :--- | :--- | :--- | :--- |
| **FR-EMG-001** | Panic Button | **P0** | A dedicated, high-contrast Emergency button MUST be visible on all primary UI screens, triggering instant Emergency Mode upon single tap. |
| **FR-EMG-002** | Automatic Location Fetch | **P0** | Emergency Mode MUST automatically request device GPS coordinates (Latitude, Longitude, Accuracy) via the Geolocation API. |
| **FR-EMG-003** | Emergency Contact SMS | **P0** | The system MUST offer a one-tap action to generate a pre-formatted SMS message to the user's saved emergency contacts containing their GPS location and triage alert. |
| **FR-EMG-004** | Offline First-Aid Library | **P0** | The Emergency Centre MUST contain offline, step-by-step graphical first-aid instructions for CPR, Choking, Severe Bleeding, Burns, and Poisoning. |
| **FR-EMG-005** | Direct Emergency Dialing | **P0** | The UI MUST provide direct `tel:` links to regional emergency numbers (e.g., 112, 999). |

---

### 2.4 Multilingual System (`FR-MLG`)

| ID | Title | Priority | Requirement Description |
| :--- | :--- | :--- | :--- |
| **FR-MLG-001** | Instant Language Toggle | **P0** | Users MUST be able to toggle the entire application interface between English (`en`) and Twi (`tw`) at any time with immediate UI update. |
| **FR-MLG-002** | Localized Decision Content | **P0** | Clinical decision tree nodes, question texts, option labels, and first-aid instructions MUST be stored with localized translation strings for English and Twi. |
| **FR-MLG-003** | Speech Recognition Engine | **P1** | Voice consultation MUST support speech recognition for English via Web Speech API and Twi via audio file upload to server Whisper fine-tuned model (when online). |
| **FR-MLG-004** | Text-to-Speech Output | **P0** | The system MUST support audio synthesis of Twi and English responses using pre-recorded offline audio chips or SpeechSynthesis API. |

---

### 2.5 User Health Profile & History (`FR-PRF`)

| ID | Title | Priority | Requirement Description |
| :--- | :--- | :--- | :--- |
| **FR-PRF-001** | Profile Management | **P0** | Users MUST be able to create and update a local health profile containing: Full Name, Age, Sex, Blood Group, Chronic Conditions, Known Allergies, and Emergency Contacts. |
| **FR-PRF-002** | Triage History Log | **P0** | The system MUST log every completed triage session locally, displaying a historical list sorted chronologically with status badges. |
| **FR-PRF-003** | Data Export | **P1** | Users MUST be able to export their health profile and triage history as a encrypted JSON file or formatted PDF for medical providers. |
| **FR-PRF-004** | Profile Ingestion into Triage | **P0** | The triage rule engine MUST automatically pull user profile data (e.g., age, chronic diseases like diabetes or hypertension) into risk evaluation math. |

---

### 2.6 Offline Storage & Background Sync (`FR-SYN`)

| ID | Title | Priority | Requirement Description |
| :--- | :--- | :--- | :--- |
| **FR-SYN-001** | Local Storage Persistence | **P0** | All user profiles, emergency contacts, and triage history MUST be saved locally in IndexedDB. |
| **FR-SYN-002** | Outbox Queue | **P0** | Triage reports created while offline MUST be placed in an IndexedDB `outbox` queue. |
| **FR-SYN-003** | Automatic Background Sync | **P0** | When network connectivity is restored, the Service Worker MUST automatically process the `outbox` queue and post pending records to the FastAPI backend. |
| **FR-SYN-004** | Conflict Resolution | **P1** | If a record is modified both locally and on the server, the system MUST resolve conflicts using Last-Write-Wins (LWW) based on UTC timestamp vectors. |

---

### 2.7 Analytics & Administrative Dashboard (`FR-ANL`)

| ID | Title | Priority | Requirement Description |
| :--- | :--- | :--- | :--- |
| **FR-ANL-001** | Aggregate Metrics | **P1** | The backend MUST aggregate anonymized triage logs to calculate total consultations, severity breakdown ratios, top presenting symptoms, and geographic distribution. |
| **FR-ANL-002** | Data Anonymization | **P0** | Patient identity fields (Name, Phone, Emergency Contacts) MUST be stripped before records are ingested into the analytics pipeline. |
| **FR-ANL-003** | Admin Dashboard UI | **P2** | Authorized healthcare administrators MUST be provided with a web dashboard rendering real-time charts of symptom frequency and emergency rates. |
