# Coding Standards & Architectural Boundaries

## 1. General Engineering Philosophy

1. **Explicit Over Implicit**: Code should be readable, strictly typed, and self-documenting.
2. **Clean Architecture Isolation**: Inner layers MUST NOT import from outer layers.
   - `domain` MUST NOT import `fastapi`, `pydantic`, `sqlalchemy`, or `requests`.
   - `use_cases` MAY import `domain`, but MUST NOT import `fastapi` or database models directly.
3. **Zero Swallowing of Exceptions**: Exceptions must be caught explicitly, logged with tracebacks, and transformed into domain-specific error types or HTTP problem responses.

---

## 2. Python (Backend) Coding Standards

### Tools & Linters:
- **Formatter**: `black` (Line length: 88)
- **Linter / Imports**: `ruff` (Enforces PEP 8, import ordering, type checking checks)
- **Type Checking**: `mypy --strict` (Mandatory strict type hints on all functions and methods)

### Conventions:
- **Naming**: `snake_case` for variables, functions, module names; `PascalCase` for classes and Pydantic models; `UPPER_SNAKE_CASE` for constants.
- **Async Usage**: All API endpoints and database operations MUST use `async def` and `await`. Blocking I/O inside async functions is strictly prohibited.
- **Error Handling**: Use custom Domain Exceptions (`TriageEngineException`, `OutboxSyncFailedException`) caught by global FastAPI exception middleware.

```python
# GOOD: Explicit Async Type-Hinted Function
async def evaluate_symptoms(
    session_data: TriageInputSchema,
    repo: ITriageRepository
) -> TriageResultEntity:
    """Evaluates symptoms and persists session.
    
    Raises:
        InvalidSymptomException: If symptom payload is malformed.
    """
    ...
```

---

## 3. TypeScript / React (Frontend) Coding Standards

### Tools & Linters:
- **Formatter**: `prettier` (`semi: true`, `singleQuote: true`, `tabWidth: 2`)
- **Linter**: `eslint` with `@typescript-eslint` and `react-hooks/recommended` rules.
- **Type Checking**: `tsc --noImplicitAny --strict`

### Conventions:
- **Naming**: `PascalCase` for React Component files (`.tsx`); `camelCase` for utilities, hooks (`useTriageStore.ts`), and variables.
- **Component Pattern**: Functional Components only with TypeScript Interfaces for Component Props.
- **Custom Hooks**: Isolate business logic, voice recording, and network handlers into reusable custom hooks (`useVoiceRecorder`, `useOfflineSync`).

```typescript
// GOOD: Explicit Typed React Component
interface TriageCardProps {
  urgencyLevel: 'RED' | 'ORANGE' | 'YELLOW' | 'GREEN';
  primaryActionText: string;
  onConfirmEmergency: () => void;
}

export const TriageCard: React.FC<TriageCardProps> = ({
  urgencyLevel,
  primaryActionText,
  onConfirmEmergency,
}) => {
  ...
};
```

---

## 4. Git & Commit Message Guidelines

Commits must follow the **Conventional Commits** specification:

- `feat(triage)`: Add new pediatric fever decision tree node
- `fix(offline)`: Resolve outbox queue race condition during reconnect
- `docs(api)`: Update OpenAPI spec for voice transcription endpoint
- `test(rule-engine)`: Add unit tests for RED flag chest pain evaluation
