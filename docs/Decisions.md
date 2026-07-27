# Architecture Decision Records (ADR Log)

## Index of Architectural Decisions

- [ADR-001: Offline-First Architecture via Client-Side Rule Engine](#adr-001-offline-first-architecture-via-client-side-rule-engine)
- [ADR-002: Deterministic Rule Primacy over AI Severity Override](#adr-002-deterministic-rule-primacy-over-ai-severity-override)
- [ADR-003: Selection of FastAPI for Backend Framework](#adr-003-selection-of-fastapi-for-backend-framework)
- [ADR-004: Selection of PostgreSQL 16 & Async SQLAlchemy 2.0](#adr-004-selection-of-postgresql-16--async-sqlalchemy-20)
- [ADR-005: Client-Side Database Selection (IndexedDB via Dexie.js)](#adr-005-client-side-database-selection-indexeddb-via-dexiejs)
- [ADR-006: Integration Strategy for Google Gemini AI](#adr-006-integration-strategy-for-google-gemini-ai)
- [ADR-007: PWA Service Worker & Workbox Caching Strategy](#adr-007-pwa-service-worker--workbox-caching-strategy)
- [ADR-008: Outbox Pattern for Background Offline Sync](#adr-008-outbox-pattern-for-background-offline-sync)
- [ADR-009: Multilingual Architecture & Native Twi Support](#adr-009-multilingual-architecture--native-twi-support)
- [ADR-010: Hybrid Speech-to-Text Strategy (Web Speech + Whisper)](#adr-010-hybrid-speech-to-text-strategy-web-speech--whisper)
- [ADR-011: Pydantic v2 for Data Validation & Schema Enforcement](#adr-011-pydantic-v2-for-data-validation--schema-enforcement)
- [ADR-012: Clean Architecture Layer Separation Rules](#adr-012-clean-architecture-layer-separation-rules)

---

## ADR-001: Offline-First Architecture via Client-Side Rule Engine

### Status: Accepted
### Context
The application targets users in regions with unreliable or non-existent 3G/4G connectivity. A acute medical assessment cannot depend on an active network connection.

### Decision
Implement a zero-dependency TypeScript rule engine running directly inside the user's browser runtime. The decision tree JSON manifests are pre-cached in the Service Worker.

### Consequences
- **Positive**: Sub-100ms triage evaluation; 100% clinical decision availability without internet.
- **Negative**: Rule trees must be bundled or updated via Service Worker when online.

---

## ADR-002: Deterministic Rule Primacy over AI Severity Override

### Status: Accepted
### Context
Generative AI models (LLMs) can hallucinate or output inconsistent classifications, creating unacceptable risk in emergency medical triage.

### Decision
The urgency level (`RED`, `ORANGE`, `YELLOW`, `GREEN`) is computed **exclusively** by the deterministic clinical rule engine. Google Gemini AI is restricted to generating natural, empathetic explanations that strictly adhere to the pre-computed severity.

### Consequences
- **Positive**: Zero risk of AI hallucination causing a missed emergency (`RED` flag).
- **Negative**: AI cannot independently re-classify a symptom outside the rule tree parameters.

---

## ADR-003: Selection of FastAPI for Backend Framework

### Status: Accepted
### Context
The backend requires high-performance async concurrency, automatic OpenAPI documentation, strict type validation, and native support for streaming HTTP responses (SSE).

### Decision
Use Python 3.11+ with **FastAPI**.

### Alternatives Considered
- *Node.js / Express*: Lacks native Python ecosystem integration for ML/Whisper libraries.
- *Django*: Heavier framework overhead; less suited for lightweight async microservices and SSE streaming.

---

## ADR-004: Selection of PostgreSQL 16 & Async SQLAlchemy 2.0

### Status: Accepted
### Context
The backend datastore requires robust JSONB support for flexible symptom logs, strong relational integrity for user accounts, and high-performance async I/O.

### Decision
Adopt **PostgreSQL 16** with **SQLAlchemy 2.0 (Async Engine via `asyncpg`)** and **Alembic** migrations.

---

## ADR-005: Client-Side Database Selection (IndexedDB via Dexie.js)

### Status: Accepted
### Context
The client needs to store health profiles, outbox queues, and decision tree caches persistently in browser storage. LocalStorage is synchronous, limited to 5MB, and string-only.

### Decision
Use **IndexedDB** wrapped with **Dexie.js** for promise-based async storage.

---

## ADR-006: Integration Strategy for Google Gemini AI

### Status: Accepted
### Context
When online, users benefit from conversational, empathetic guidance in local context.

### Decision
Use the official `google-genai` SDK with **Server-Sent Events (SSE)** token streaming from FastAPI to React.

---

## ADR-007: PWA Service Worker & Workbox Caching Strategy

### Status: Accepted
### Context
The PWA must load instantly on mobile devices even when offline.

### Decision
Use **Workbox v7** with `Cache-First` for app shell assets and `Stale-While-Revalidate` for rule tree manifests and locale JSON files.

---

## ADR-008: Outbox Pattern for Background Offline Sync

### Status: Accepted
### Context
Triage logs generated offline must be synced reliably to PostgreSQL without data loss or duplicate entries.

### Decision
Implement an IndexedDB `triageOutbox` table. The Service Worker listens to `online` events and posts queued items to `/api/v1/sync/outbox` using idempotent UUIDs.

---

## ADR-009: Multilingual Architecture & Native Twi Support

### Status: Accepted
### Context
Sub-Saharan Africa target demographics include native speakers of Twi (Ghana).

### Decision
Build a key-value i18n translation matrix (`en.json`, `tw.json`) for UI strings and pre-rendered audio clips for offline speech output.

---

## ADR-010: Hybrid Speech-to-Text Strategy (Web Speech + Whisper)

### Status: Accepted
### Context
Browser Web Speech API support for regional languages like Twi is limited.

### Decision
Use browser `Web Speech API` for English speech recognition, and fallback to server-side `Whisper` fine-tuned model for Twi voice audio uploads when online.

---

## ADR-011: Pydantic v2 for Data Validation & Schema Enforcement

### Status: Accepted
### Context
Backend requests must be strictly validated to prevent malformed data or security exploits.

### Decision
Use **Pydantic v2** across all FastAPI request/response DTOs for fast Rust-backed validation.

---

## ADR-012: Clean Architecture Layer Separation Rules

### Status: Accepted
### Context
Framework dependencies must not pollute core clinical logic.

### Decision
Enforce 4 strict layers (`domain`, `use_cases`, `interfaces`, `infrastructure`). The `domain` layer has 0 external dependencies.
