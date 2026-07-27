# Workspace & Directory Structure Specification

## 1. Top-Level Repository Blueprint

```
health_triage_assistant/
│
├── docs/                        # Complete Technical Documentation (25 Files)
│   ├── README.md
│   ├── SystemArchitecture.md
│   └── ...
│
├── backend/                     # FastAPI Clean Architecture Application
│   ├── app/
│   ├── tests/
│   ├── alembic/
│   ├── Dockerfile
│   ├── alembic.ini
│   ├── pyproject.toml
│   └── requirements.txt
│
├── frontend/                    # React + Vite + Tailwind PWA
│   ├── src/
│   ├── public/
│   ├── tests/
│   ├── Dockerfile
│   ├── index.html
│   ├── package.json
│   ├── tailwind.config.js
│   ├── vite.config.ts
│   └── workbox-config.js
│
├── docker-compose.yml           # Local Development Orchestration
├── .env.example                 # Environment Variable Template
└── README.md                    # Root Project README
```

---

## 2. Backend Directory Layout (`/backend`)

```
backend/
├── app/
│   ├── main.py                  # FastAPI Application Entry Point & Lifespan Setup
│   ├── config.py                # Environment Configuration (Pydantic Settings)
│   │
│   ├── domain/                  # PURE BUSINESS LOGIC LAYER (Zero External Dependencies)
│   │   ├── entities/            # Domain Entities (TriageSession, UserProfile)
│   │   ├── value_objects/       # Value Objects (UrgencyLevel, LanguageCode)
│   │   └── rules/               # Clinical Rule Engine Evaluator & Tree Interfaces
│   │
│   ├── use_cases/               # APPLICATION WORKFLOW LAYER
│   │   ├── evaluate_triage.py   # Triage Execution Use Case
│   │   ├── sync_outbox.py       # Outbox Synchronization Use Case
│   │   └── voice_consult.py     # Voice & Gemini AI Enrichment Use Case
│   │
│   ├── interfaces/              # ADAPTERS & CONTROLLERS LAYER
│   │   ├── api/                 # FastAPI REST & SSE Controllers
│   │   │   └── v1/
│   │   │       ├── router.py
│   │   │       ├── auth.py
│   │   │       ├── triage.py
│   │   │       ├── emergency.py
│   │   │       └── sync.py
│   │   ├── schemas/             # Pydantic v2 DTOs (Request / Response)
│   │   └── repositories/        # SQLAlchemy Database Repository Implementations
│   │
│   └── infrastructure/          # FRAMEWORK & EXTERNAL SERVICES LAYER
│       ├── database/            # Async SQLAlchemy Engine & Session Pool
│       ├── ai/                  # Google Gemini API Client & Prompt Engineering
│       ├── speech/              # Whisper Speech-to-Text Driver
│       └── security/            # JWT Token Utilities & Passlib Hashing
│
├── alembic/                     # Database Migrations Directory
│   ├── versions/                # Generated Migration Scripts
│   └── env.py                   # Migration Execution Environment
│
└── tests/                       # Pytest Suite
    ├── unit/
    ├── integration/
    └── e2e/
```

---

## 3. Frontend Directory Layout (`/frontend`)

```
frontend/
├── public/                      # Static Assets & PWA Manifest
│   ├── manifest.json            # PWA Web App Manifest
│   ├── favicon.ico
│   ├── icons/                   # App Icons (192px, 512px)
│   ├── audio/                   # Pre-Recorded Twi/English Offline Audio Clips
│   └── rule_trees/              # Pre-cached JSON Decision Trees
│
├── src/
│   ├── main.tsx                 # React DOM Root
│   ├── App.tsx                  # Root Routing & Service Worker Registration
│   ├── index.css                # Tailwind Directives & Custom Design System Tokens
│   │
│   ├── components/              # ATOMIC UI COMPONENTS
│   │   ├── common/              # Buttons, Modals, Cards, Header, Footer
│   │   ├── triage/              # SymptomIntake, Questionnaire, TriageCard
│   │   ├── emergency/           # PanicButton, FirstAidCard, SMSDispatcher
│   │   └── voice/               # MicButton, AudioWaveform, SpeechPlayer
│   │
│   ├── stores/                  # ZUSTAND STATE STORES
│   │   ├── useLanguageStore.ts  # Language & i18n State
│   │   ├── useTriageStore.ts    # Triage Execution State
│   │   └── useNetworkStore.ts   # Network Status State
│   │
│   ├── db/                      # INDEXEDDB (DEXIE.JS) LAYER
│   │   ├── schema.ts            # Dexie Database Definition
│   │   └── outboxRepository.ts  # Local Storage & Queue Operations
│   │
│   ├── engine/                  # CLIENT-SIDE RULE ENGINE (TypeScript)
│   │   ├── evaluator.ts         # Deterministic Decision Tree Traversal Logic
│   │   └── types.ts             # Rule Tree Types & Enums
│   │
│   ├── i18n/                    # LOCALIZATION DICTIONARIES
│   │   ├── en.json              # English String Translations
│   │   └── tw.json              # Twi String Translations
│   │
│   ├── services/                # API CLIENT & PWA SYNC
│   │   ├── api.ts               # Axios / Fetch Client Configured with JWT
│   │   └── syncWorker.ts        # Outbox Background Sync Trigger
│   │
│   └── registerServiceWorker.ts # Workbox SW Registration Script
│
└── tests/                       # Vitest Component & Rule Engine Unit Tests
```
