# Health Triage Assistant — Production Technical Documentation

Welcome to the central technical documentation suite for the **Health Triage Assistant** — a production-grade, offline-first medical triage and consultation web application.

---

## Document Index

| Document | Description | Target Audience |
| :--- | :--- | :--- |
| [Project Overview](file:///c:/Users/DELL/health_triage_assistant/docs/ProjectOverview.md) | High-level vision, core philosophy, and problem statement. | All Stakeholders |
| [Product Requirements](file:///c:/Users/DELL/health_triage_assistant/docs/ProductRequirements.md) | Target demographics, core modules, operational boundaries, and KPIs. | Product / Engineering |
| [Functional Requirements](file:///c:/Users/DELL/health_triage_assistant/docs/FunctionalRequirements.md) | Detailed FR-IDs and specifications for all platform capabilities. | Engineering / QA |
| [Non-Functional Requirements](file:///c:/Users/DELL/health_triage_assistant/docs/NonFunctionalRequirements.md) | Latency, availability, security, accessibility, and scalability rules. | Architects / DevOps |
| [User Journey](file:///c:/Users/DELL/health_triage_assistant/docs/UserJourney.md) | End-to-end user interaction flows and state transitions. | UX / Engineering |
| [System Architecture](file:///c:/Users/DELL/health_triage_assistant/docs/SystemArchitecture.md) | C4 diagrams, system topology, and network interaction boundaries. | System Architects |
| [Backend Architecture](file:///c:/Users/DELL/health_triage_assistant/docs/BackendArchitecture.md) | FastAPI Clean Architecture layout, async handlers, and middleware pipelines. | Backend Engineers |
| [Frontend Architecture](file:///c:/Users/DELL/health_triage_assistant/docs/FrontendArchitecture.md) | React + Vite + Tailwind PWA architecture, state stores, and rendering rules. | Frontend Engineers |
| [Database Design](file:///c:/Users/DELL/health_triage_assistant/docs/DatabaseDesign.md) | PostgreSQL relational schema, IndexedDB local schema, and Alembic workflow. | Database / Backend |
| [Rule Engine Design](file:///c:/Users/DELL/health_triage_assistant/docs/RuleEngineDesign.md) | Deterministic clinical decision tree algorithm and rule format specs. | Clinical / Backend / Frontend |
| [AI Architecture](file:///c:/Users/DELL/health_triage_assistant/docs/AIArchitecture.md) | Gemini AI integration, prompt design, safety guardrails, and streaming. | AI / Backend |
| [Emergency System](file:///c:/Users/DELL/health_triage_assistant/docs/EmergencySystem.md) | Panic button workflow, emergency dispatch payload, and offline SMS fallback. | Mobile / Systems |
| [Voice System](file:///c:/Users/DELL/health_triage_assistant/docs/VoiceSystem.md) | Speech-to-Text and Text-to-Speech pipeline for English and Twi. | Voice / Audio / Frontend |
| [Offline Strategy](file:///c:/Users/DELL/health_triage_assistant/docs/OfflineStrategy.md) | Service Worker caching, IndexedDB outbox pattern, and background sync. | Frontend / PWA |
| [API Reference](file:///c:/Users/DELL/health_triage_assistant/docs/APIReference.md) | Complete OpenAPI/REST endpoint specifications and JSON payload schemas. | API Consumers / FE |
| [Folder Structure](file:///c:/Users/DELL/health_triage_assistant/docs/FolderStructure.md) | Directory trees for `/backend` and `/frontend` codebases. | All Engineers |
| [Coding Standards](file:///c:/Users/DELL/health_triage_assistant/docs/CodingStandards.md) | Linting, formatting, Clean Architecture conventions, and error patterns. | All Engineers |
| [Security](file:///c:/Users/DELL/health_triage_assistant/docs/Security.md) | JWT auth, encryption at rest/transit, rate limiting, and sanitization. | Security / DevOps |
| [Privacy](file:///c:/Users/DELL/health_triage_assistant/docs/Privacy.md) | Data protection, HIPAA/GDPR alignment, consent, and user data retention. | Compliance / Legal |
| [Deployment](file:///c:/Users/DELL/health_triage_assistant/docs/Deployment.md) | Docker Compose, production server configs, CI/CD, and PWA hosting. | DevOps / SRE |
| [Testing Strategy](file:///c:/Users/DELL/health_triage_assistant/docs/TestingStrategy.md) | Pytest, Vitest, Playwright E2E, and clinical decision tree unit tests. | QA / Testing |
| [Future Roadmap](file:///c:/Users/DELL/health_triage_assistant/docs/FutureRoadmap.md) | Multi-phase feature progression from Hackathon MVP to Telemedicine platform. | Management / Product |
| [Decisions (ADRs)](file:///c:/Users/DELL/health_triage_assistant/docs/Decisions.md) | Architectural Decision Records (ADR 001 - ADR 012) detailing design trade-offs. | Architects / Lead Devs |

---

## Architectural Principles

1. **Zero-Delay Emergency Safety**: Triage evaluation must never fail due to lost connectivity. Emergency severity is calculated deterministically on the client.
2. **Deterministic Triage Primacy**: AI (Gemini) enhances context and empathy but can **never** override a higher severity assigned by the clinical decision tree engine.
3. **Local Sovereignty**: User health records, profile information, and emergency contacts are saved locally first (IndexedDB) and synchronized opportunistically.
4. **Inclusive Accessibility**: Designed for low-literacy users through native multilingual audio (Twi/English) and voice-driven interactions.
