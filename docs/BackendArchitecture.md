# Backend Architecture Specification

## 1. Architectural Style: Clean Architecture

The backend of the **Health Triage Assistant** is engineered using **FastAPI**, adhering strictly to **Clean Architecture** (Ports and Adapters) principles. This ensures that core medical domain logic is decoupled from external frameworks, web servers, databases, and third-party APIs (such as Google Gemini).

```
                      +----------------------------------+
                      |         Infrastructure           |
                      |  (FastAPI, PostgreSQL, Gemini)   |
                      +----------------------------------+
                                       |
                                       v
                      +----------------------------------+
                      |     Interface Adapters           |
                      | (Controllers, Presenters, DB Repo)|
                      +----------------------------------+
                                       |
                                       v
                      +----------------------------------+
                      |        Use Cases                 |
                      | (EvaluateTriage, SyncOutbox)     |
                      +----------------------------------+
                                       |
                                       v
                      +----------------------------------+
                      |         Domain Layer             |
                      |  (Entities, Clinical Rules, Value|
                      |          Objects)                |
                      +----------------------------------+
```

---

## 2. Layer Separation & Responsibilities

### 2.1 Domain Layer (`app/domain`)
- **Responsibility**: Contains enterprise clinical business rules, entities, and value objects. Has **zero dependencies** on external Python libraries (no FastAPI, no SQLAlchemy, no Pydantic).
- **Key Modules**:
  - `entities/triage_session.py`: Core `TriageSession` entity and state transitions.
  - `entities/rule_tree.py`: Rule node tree data structure and evaluator interfaces.
  - `value_objects/urgency_level.py`: Enum defining `RED`, `ORANGE`, `YELLOW`, `GREEN`.

### 2.2 Use Cases Layer (`app/use_cases`)
- **Responsibility**: Orchestrates domain entities to execute application workflows.
- **Key Use Cases**:
  - `evaluate_triage_use_case.py`: Receives patient symptoms, invokes domain rule engine, queries user history, and requests AI enrichment.
  - `sync_outbox_use_case.py`: Validates and bulk-ingests client outbox items.
  - `manage_profile_use_case.py`: CRUD operations for user health profiles.

### 2.3 Interface Adapters Layer (`app/interfaces`)
- **Responsibility**: Converts data between Use Case format and external formats (HTTP/Database).
- **Components**:
  - `api/v1/controllers/`: FastAPI APIRouter handlers.
  - `schemas/`: Pydantic v2 DTOs (Data Transfer Objects) for request validation and response serialization.
  - `repositories/`: Concrete implementations of database repository interfaces using SQLAlchemy 2.0.

### 2.4 Infrastructure Layer (`app/infrastructure`)
- **Responsibility**: Framework-specific configuration, database drivers, external API clients, and application entry point.
- **Components**:
  - `database/session.py`: Async engine configuration using `asyncpg`.
  - `ai/gemini_client.py`: Google Gemini API wrapper with rate-limiting and circuit breaker.
  - `config.py`: pydantic-settings environment settings validator.

---

## 3. Asynchronous Execution Pipeline & DB Repositories

### 3.1 SQLAlchemy 2.0 Async Repository Pattern
All database operations use **SQLAlchemy 2.0 declarative async mappings** with explicit `AsyncSession` handling.

```python
# Conceptual Architecture Interface (Repository Pattern)
class ITriageRepository(ABC):
    @abstractmethod
    async def save_session(self, session: TriageSession) -> TriageSession:
        ...
        
    @abstractmethod
    async def get_by_user_id(self, user_id: UUID) -> List[TriageSession]:
        ...
```

### 3.2 FastAPI Middleware Pipeline Order

```mermaid
graph TD
    ClientRequest[Incoming HTTP Request] --> CORS[1. CORSMiddleware]
    CORS --> TrustedHost[2. TrustedHostMiddleware]
    TrustedHost --> RateLimit[3. RateLimitingMiddleware (Redis/Memory)]
    RateLimit --> ExceptionHandler[4. GlobalExceptionHandlerMiddleware]
    ExceptionHandler --> Auth[5. JWTAuthMiddleware]
    Auth --> Router[6. APIRouter Route Handler]
    Router --> Service[7. UseCase Execution]
    Service --> Response[Return JSON / SSE Stream]
```

---

## 4. Pydantic v2 Data Validation Architecture

All input payloads pass through strict **Pydantic v2** models utilizing custom field validators and `Strict` mode setting to prevent type coercion vulnerabilities.

### Key Validation Guards:
- **String Sanitization**: Trims whitespace, strips HTML tags, and escapes SQL/script characters.
- **Age Constraints**: Enforces integer age range ($0 \le \text{age} \le 120$).
- **Latitude / Longitude**: Enforces valid geographical coordinate ranges ($\pm 90^\circ, \pm 180^\circ$).

---

## 5. Background Task Management

Long-running or non-blocking operations (e.g., dispatching push notifications, processing batch analytics, sending emergency email alerts) use FastAPI `BackgroundTasks` or Celery/Redis queue for deferred execution:

```
[HTTP Controller] ---> Returns 200 OK Triage Response (Sub-50ms)
       |
       +---> [FastAPI Background Task] ---> Ingest Anonymized Analytics Metrics
```
