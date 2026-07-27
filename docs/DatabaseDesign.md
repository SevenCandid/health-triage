# Database Design & Data Architecture Specification

## 1. Database Architecture Overview

The system uses a **Dual-Database Storage Strategy**:

1. **Server Database (PostgreSQL 16)**: Centralized relational datastore managing synchronized user profiles, triage histories, clinical rule trees, emergency logs, and administrative analytics. Access is managed strictly via **SQLAlchemy 2.0 Async ORM**.
2. **Client Database (IndexedDB via Dexie.js)**: Local browser-based datastore managing offline user profiles, outbox queue for unsynced triage reports, cached clinical decision trees, and offline first-aid protocol manifests.

---

## 2. Entity-Relationship (ER) Diagram (PostgreSQL)

```mermaid
erDiagram
    USERS ||--o{ HEALTH_PROFILES : "has"
    USERS ||--o{ EMERGENCY_CONTACTS : "defines"
    USERS ||--o{ TRIAGE_SESSIONS : "conducts"
    TRIAGE_SESSIONS ||--o| EMERGENCY_LOGS : "triggers"
    RULE_TREES ||--o{ TRIAGE_SESSIONS : "uses rule version"

    USERS {
        uuid id PK
        string phone_number UK
        string password_hash
        string preferred_language
        boolean is_active
        timestamp created_at
        timestamp updated_at
    }

    HEALTH_PROFILES {
        uuid id PK
        uuid user_id FK
        string full_name
        integer age
        string biological_sex
        string blood_group
        jsonb chronic_conditions
        jsonb known_allergies
        timestamp updated_at
    }

    EMERGENCY_CONTACTS {
        uuid id PK
        uuid user_id FK
        string contact_name
        string phone_number
        string relationship
        boolean is_primary
    }

    TRIAGE_SESSIONS {
        uuid id PK
        uuid user_id FK
        uuid rule_tree_id FK
        string urgency_level
        string primary_symptom
        jsonb symptom_details
        text ai_explanation
        string language_code
        boolean created_offline
        timestamp conducted_at
        timestamp synced_at
    }

    EMERGENCY_LOGS {
        uuid id PK
        uuid triage_session_id FK
        float latitude
        float longitude
        string status
        timestamp triggered_at
    }

    RULE_TREES {
        uuid id PK
        string version UK
        string description
        jsonb tree_structure
        boolean is_active
        timestamp published_at
    }
```

---

## 3. PostgreSQL Schema Definitions (DDL & SQLAlchemy 2.0 Mappings)

### 3.1 `users` Table
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    phone_number VARCHAR(20) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    preferred_language VARCHAR(5) DEFAULT 'en' NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_users_phone ON users(phone_number);
```

### 3.2 `triage_sessions` Table
```sql
CREATE TABLE triage_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    rule_tree_id UUID REFERENCES rule_trees(id),
    urgency_level VARCHAR(10) NOT NULL, -- 'RED', 'ORANGE', 'YELLOW', 'GREEN'
    primary_symptom VARCHAR(100) NOT NULL,
    symptom_details JSONB NOT NULL,
    ai_explanation TEXT,
    language_code VARCHAR(5) NOT NULL,
    created_offline BOOLEAN DEFAULT FALSE NOT NULL,
    conducted_at TIMESTAMP WITH TIME ZONE NOT NULL,
    synced_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_triage_user_date ON triage_sessions(user_id, conducted_at DESC);
CREATE INDEX idx_triage_urgency ON triage_sessions(urgency_level);
```

---

## 4. Client IndexedDB Schema (Dexie.js Definition)

The client-side browser IndexedDB database is initialized with Dexie.js using the following store signatures:

```typescript
// Dexie.js Schema Initialization Signature
import Dexie, { Table } from 'dexie';

export interface LocalTriageSession {
  id: string; // UUID v4
  userId?: string;
  urgencyLevel: 'RED' | 'ORANGE' | 'YELLOW' | 'GREEN';
  primarySymptom: string;
  symptomDetails: Record<string, any>;
  languageCode: string;
  createdOffline: boolean;
  conductedAt: string; // ISO Timestamp
  syncStatus: 'PENDING' | 'SYNCED' | 'FAILED';
}

export interface LocalHealthProfile {
  id: string;
  fullName: string;
  age: number;
  biologicalSex: 'MALE' | 'FEMALE' | 'OTHER';
  bloodGroup: string;
  chronicConditions: string[];
  knownAllergies: string[];
  updatedAt: string;
}

export class HealthDatabase extends Dexie {
  triageOutbox!: Table<LocalTriageSession>;
  healthProfile!: Table<LocalHealthProfile>;
  cachedRules!: Table<{ version: string; treeJson: any }>;

  constructor() {
    super('HealthTriageLocalDB');
    this.version(1).stores({
      triageOutbox: 'id, syncStatus, conductedAt, urgencyLevel',
      healthProfile: 'id',
      cachedRules: 'version'
    });
  }
}
```

---

## 5. Migration Workflow (Alembic)

Database schema evolutions are managed exclusively using **Alembic**:

1. **Environment Setup**: `alembic.ini` configured with `sqlalchemy.url = driver://user:pass@localhost/db`.
2. **Async Support**: `env.py` configured to run migrations using `asyncio` and `run_async()`.
3. **Auto-Generation Workflow**:
   ```bash
   alembic revision --autogenerate -m "create_triage_and_users_tables"
   alembic upgrade head
   ```
